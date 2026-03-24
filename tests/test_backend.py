import io
import json
import tempfile
import threading
import unittest
from contextlib import contextmanager
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

from splitwise import Splitwise
from splitwise.backend import create_backend_app
from splitwise.expense import Expense, ExpenseUser
from splitwise.group import Group
from splitwise.persistence import PersistenceStore
from splitwise.pwa import create_app
from splitwise.user import User


class BackendAppTestCase(unittest.TestCase):
    def _request(self, app, method, path, payload=None, content_type='application/json', headers=None):
        body = b''
        if payload is not None:
            if content_type == 'application/json':
                body = json.dumps(payload).encode('utf-8')
            else:
                body = payload.encode('utf-8')

        environ = {}
        setup_testing_defaults(environ)
        environ['REQUEST_METHOD'] = method
        environ['PATH_INFO'] = path
        environ['QUERY_STRING'] = ''
        if '?' in path:
            environ['PATH_INFO'], environ['QUERY_STRING'] = path.split('?', 1)
        environ['CONTENT_LENGTH'] = str(len(body))
        environ['CONTENT_TYPE'] = content_type
        environ['wsgi.input'] = io.BytesIO(body)
        for key, value in (headers or {}).items():
            environ[key] = value

        captured = {}

        def start_response(status, headers):
            captured['status'] = status
            captured['headers'] = dict(headers)

        raw = b''.join(app(environ, start_response))
        parsed = raw.decode('utf-8')
        if 'application/json' in captured['headers'].get('Content-Type', ''):
            parsed = json.loads(parsed)
        return captured['status'], captured['headers'], parsed

    def test_backend_serves_splitwise_api_routes(self):
        app = create_backend_app()

        status, _, current = self._request(app, 'GET', '/api/v3.0/get_current_user')
        self.assertEqual(status, '200 OK')
        self.assertEqual(current['user']['first_name'], 'Alex')

        status, _, groups = self._request(app, 'GET', '/api/v3.0/get_groups')
        self.assertEqual(status, '200 OK')
        self.assertGreaterEqual(len(groups['groups']), 2)

        status, _, expenses = self._request(app, 'GET', '/api/v3.0/get_expenses?group_id=1&visible=true')
        self.assertEqual(status, '200 OK')
        self.assertEqual(expenses['expenses'][0]['description'], 'Groceries')

    def test_pwa_app_exposes_backend_routes(self):
        app = create_app(environment={})
        status, _, current = self._request(app, 'GET', '/api/v3.0/get_current_user')
        self.assertEqual(status, '200 OK')
        self.assertEqual(current['user']['id'], 1)

    def test_backend_can_scope_current_user_and_friendships(self):
        app = create_backend_app()
        account = app.register_account('Taylor', 'taylor@example.com', 'password123')
        friend = app.add_friend(account['id'], email='sam@example.com')
        self.assertEqual(friend['email'], 'sam@example.com')

        status, _, current = self._request(
            app,
            'GET',
            '/api/v3.0/get_current_user',
            headers={'HTTP_X_SPLITWISE_USER_ID': str(account['id'])},
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(current['user']['email'], 'taylor@example.com')

        status, _, friends = self._request(
            app,
            'GET',
            '/api/v3.0/get_friends',
            headers={'HTTP_X_SPLITWISE_USER_ID': str(account['id'])},
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual([item['email'] for item in friends['friends']], ['sam@example.com'])

    def test_backend_supports_friend_requests_profile_updates_settlements_and_recurring_metadata(self):
        app = create_backend_app()
        taylor = app.register_account('Taylor', 'taylor@example.com', 'password123')
        jordan = app.register_account('Jordan', 'jordan@example.com', 'password123')

        request_payload = app.send_friend_request(taylor['id'], email='jordan@example.com')
        self.assertEqual(request_payload['status'], 'pending')

        pending = app.list_friend_requests(jordan['id'])
        self.assertEqual(len(pending['incoming']), 1)
        self.assertEqual(pending['incoming'][0]['user']['email'], 'taylor@example.com')

        accepted = app.respond_friend_request(jordan['id'], pending['incoming'][0]['id'], accept=True)
        self.assertEqual(accepted['status'], 'accepted')
        self.assertEqual(accepted['friend']['email'], 'taylor@example.com')

        updated = app.update_account(taylor['id'], first_name='Taylor Updated', email='taylor+updated@example.com')
        self.assertEqual(updated['first_name'], 'Taylor Updated')
        self.assertEqual(updated['email'], 'taylor+updated@example.com')

        password_update = app.update_password(taylor['id'], 'password123', 'newpassword123')
        self.assertTrue(password_update['updated'])
        self.assertEqual(app.authenticate_account('taylor+updated@example.com', 'newpassword123')['id'], taylor['id'])

        status, _, created = self._request(
            app,
            'POST',
            '/api/v3.0/create_expense',
            payload={
                'description': 'Gym membership',
                'cost': '30.00',
                'repeats': True,
                'repeat_interval': 'monthly',
                'email_reminder': True,
                'email_reminder_in_advance': 2,
                'users__0__user_id': taylor['id'],
                'users__0__paid_share': '30.00',
                'users__0__owed_share': '15.00',
                'users__1__user_id': jordan['id'],
                'users__1__paid_share': '0.00',
                'users__1__owed_share': '15.00',
            },
            headers={'HTTP_X_SPLITWISE_USER_ID': str(taylor['id'])},
        )
        self.assertEqual(status, '200 OK')
        expense = created['expenses'][0]
        self.assertTrue(expense['repeats'])
        self.assertEqual(expense['repeat_interval'], 'monthly')
        self.assertTrue(expense['email_reminder'])
        self.assertEqual(expense['email_reminder_in_advance'], 2)
        self.assertIsNotNone(expense['next_repeat'])

        settlement = app.record_settlement(jordan['id'], taylor['id'], '15.00', from_user_id=jordan['id'], to_user_id=taylor['id'])
        self.assertEqual(settlement['amount'], '15.00')

        status, _, friends = self._request(
            app,
            'GET',
            '/api/v3.0/get_friends',
            headers={'HTTP_X_SPLITWISE_USER_ID': str(taylor['id'])},
        )
        self.assertEqual(status, '200 OK')
        jordan_friend = next(item for item in friends['friends'] if item['email'] == 'jordan@example.com')
        self.assertEqual(jordan_friend['balance'][0]['amount'], '0.00')

    def test_backend_supports_group_split_metadata_with_multiple_payers(self):
        app = create_backend_app()

        status, _, created = self._request(
            app,
            'POST',
            '/api/v3.0/create_expense',
            payload={
                'group_id': 1,
                'description': 'Cabin supplies',
                'cost': '90.00',
                'split_method': 'percentage',
                'users__0__user_id': 1,
                'users__0__paid_share': '60.00',
                'users__0__owed_share': '54.00',
                'users__1__user_id': 2,
                'users__1__paid_share': '30.00',
                'users__1__owed_share': '36.00',
                'payers__0__user_id': 1,
                'payers__0__paid_share': '60.00',
                'payers__1__user_id': 2,
                'payers__1__paid_share': '30.00',
                'participants__0__user_id': 1,
                'participants__0__included': True,
                'participants__0__split_value': '60',
                'participants__1__user_id': 2,
                'participants__1__included': True,
                'participants__1__split_value': '40',
                'participants__2__user_id': 3,
                'participants__2__included': False,
                'participants__2__split_value': '0',
            },
        )
        self.assertEqual(status, '200 OK')
        expense = created['expenses'][0]
        self.assertEqual(expense['split_method'], 'percentage')
        self.assertEqual(expense['split_equally'], False)
        self.assertEqual(expense['payers'][0]['paid_share'], '60.00')
        self.assertEqual(expense['payers'][1]['paid_share'], '30.00')
        self.assertEqual(expense['participants'][2]['user_id'], 3)
        self.assertFalse(expense['participants'][2]['included'])
        user_two = next(item for item in expense['users'] if item['user_id'] == 2)
        self.assertEqual(user_two['payer_amount'], '30.00')
        self.assertEqual(user_two['split_value'], '40')

    def test_backend_materializes_recurring_series_and_supports_group_management(self):
        app = create_backend_app()
        owner = app.register_account('Owner', 'owner@example.com', 'password123')
        admin = app.register_account('Admin', 'admin@example.com', 'password123')
        member = app.register_account('Member', 'member@example.com', 'password123')
        outsider = app.register_account('Out', 'out@example.com', 'password123')

        created = app._handle_create_group(
            {
                'name': 'Trip fund',
                'users__0__user_id': admin['id'],
                'users__1__user_id': member['id'],
            },
            owner['id'],
        )[1]['group']
        group_id = created['id']

        app.set_group_admin(owner['id'], group_id, admin['id'], True)
        group = app.add_group_member(owner['id'], group_id, outsider['id'])
        self.assertEqual(group['owner_id'], owner['id'])
        self.assertIn(admin['id'], group['admin_ids'])
        self.assertEqual(len(group['members']), 4)

        group = app.remove_group_member(admin['id'], group_id, outsider['id'])
        self.assertEqual(len(group['members']), 3)

        leave_result = app.leave_group(owner['id'], group_id)
        self.assertTrue(leave_result['left'])
        promoted_group = app._group_payload(group_id, admin['id'])
        self.assertEqual(promoted_group['owner_id'], admin['id'])

        archived = app.set_group_archived(admin['id'], group_id, True)
        self.assertTrue(archived['archived'])

        status, _, created_expense = self._request(
            app,
            'POST',
            '/api/v3.0/create_expense',
            payload={
                'group_id': group_id,
                'description': 'Monthly rent',
                'cost': '90.00',
                'date': '2026-03-20T12:00:00Z',
                'repeats': True,
                'repeat_interval': 'daily',
                'users__0__user_id': admin['id'],
                'users__0__paid_share': '90.00',
                'users__0__owed_share': '45.00',
                'users__1__user_id': member['id'],
                'users__1__paid_share': '0.00',
                'users__1__owed_share': '45.00',
            },
            headers={'HTTP_X_SPLITWISE_USER_ID': str(admin['id'])},
        )
        self.assertEqual(status, '200 OK')
        series_id = created_expense['expenses'][0]['series_id']

        status, _, expenses = self._request(
            app,
            'GET',
            '/api/v3.0/get_expenses?group_id=%s' % group_id,
            headers={'HTTP_X_SPLITWISE_USER_ID': str(admin['id'])},
        )
        self.assertEqual(status, '200 OK')
        self.assertGreaterEqual(len(expenses['expenses']), 2)
        generated = [item for item in expenses['expenses'] if item['series_id'] == series_id and item['id'] != created_expense['expenses'][0]['id']]
        self.assertTrue(generated)

        paused = app.pause_expense_series(admin['id'], series_id)
        self.assertTrue(paused['series_paused'])
        updated = app.update_expense_series(admin['id'], series_id, {'description': 'Updated rent', 'cost': '100.00'})
        self.assertEqual(updated['description'], 'Updated rent')
        resumed = app.resume_expense_series(admin['id'], series_id)
        self.assertFalse(resumed['series_paused'])
        cancelled = app.cancel_expense_series(admin['id'], series_id)
        self.assertTrue(cancelled['series_cancelled'])
        self.assertFalse(cancelled['repeats'])

    def test_backend_can_persist_accounts_and_groups(self):
        with tempfile.TemporaryDirectory() as tempdir:
            environment = {'SPLITWISE_PERSISTENCE_DIR': tempdir}
            persistence = PersistenceStore(environment)
            app = create_backend_app(persistence=persistence)
            user = app.register_account('Persisted', 'persisted@example.com', 'password123')
            created = app._handle_create_group({'name': 'Persisted group'}, user['id'])[1]['group']

            reloaded = create_backend_app(persistence=PersistenceStore(environment))
            self.assertEqual(reloaded.authenticate_account('persisted@example.com', 'password123')['id'], user['id'])

            status, _, groups = self._request(
                reloaded,
                'GET',
                '/api/v3.0/get_groups',
                headers={'HTTP_X_SPLITWISE_USER_ID': str(user['id'])},
            )
            self.assertEqual(status, '200 OK')
            self.assertTrue(any(item['id'] == created['id'] for item in groups['groups']))


@contextmanager
def running_backend_server(app):
    server = make_server('127.0.0.1', 0, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield 'http://127.0.0.1:%s/' % server.server_port
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


class BackendSdkCompatibilityTestCase(unittest.TestCase):
    def test_sdk_can_use_local_backend_for_crud_and_oauth_flows(self):
        with running_backend_server(create_backend_app()) as base_url:
            s_obj = Splitwise('consumerkey', 'consumersecret', base_url=base_url, oauth_base_url=base_url)

            authorize_url, oauth_secret = s_obj.getAuthorizeURL()
            self.assertTrue(authorize_url.startswith(base_url + 'authorize?oauth_token='))
            access_token = s_obj.getAccessToken('temp-token', oauth_secret, 'verifier')
            self.assertIn('oauth_token', access_token)

            oauth2_token = s_obj.getOAuth2AccessToken('code-123', base_url + 'callback')
            self.assertEqual(oauth2_token['token_type'], 'bearer')

            current_user = s_obj.getCurrentUser()
            self.assertEqual(current_user.getFirstName(), 'Alex')

            updated_user = User()
            updated_user.setId(2)
            updated_user.setFirstName('Taylor')
            updated_user.setEmail('taylor@example.com')
            user_result, user_errors = s_obj.updateUser(updated_user)
            self.assertIsNone(user_errors)
            self.assertEqual(user_result.getFirstName(), 'Taylor')

            group = Group()
            group.setName('Weekend trip')
            group.setGroupType('trip')
            new_group, group_errors = s_obj.createGroup(group)
            self.assertIsNone(group_errors)
            self.assertEqual(new_group.getName(), 'Weekend trip')

            member = User()
            member.setFirstName('Morgan')
            member.setEmail('morgan@example.com')
            added, added_user, add_errors = s_obj.addUserToGroup(member, new_group.getId())
            self.assertTrue(added)
            self.assertIsNone(add_errors)
            self.assertEqual(added_user.getFirstName(), 'Morgan')

            expense = Expense()
            expense.setGroupId(new_group.getId())
            expense.setCost('24.50')
            expense.setDescription('Dinner')
            user_one = ExpenseUser()
            user_one.setId(1)
            user_one.setPaidShare('24.50')
            user_one.setOwedShare('12.25')
            user_two = ExpenseUser()
            user_two.setId(added_user.getId())
            user_two.setPaidShare('0.00')
            user_two.setOwedShare('12.25')
            expense.setUsers([user_one, user_two])

            created_expense, expense_errors = s_obj.createExpense(expense)
            self.assertIsNone(expense_errors)
            self.assertEqual(created_expense.getDescription(), 'Dinner')

            loaded_expense = s_obj.getExpense(created_expense.getId())
            self.assertEqual(loaded_expense.getId(), created_expense.getId())
            self.assertEqual(len(s_obj.getExpenses(group_id=new_group.getId(), visible=True)), 1)

            comment, comment_errors = s_obj.createComment(created_expense.getId(), 'Split evenly')
            self.assertIsNone(comment_errors)
            self.assertEqual(comment.getContent(), 'Split evenly')
            self.assertEqual(len(s_obj.getComments(created_expense.getId())), 1)

            notifications = s_obj.getNotifications(limit=5)
            self.assertGreaterEqual(len(notifications), 1)

            deleted, delete_errors = s_obj.deleteExpense(created_expense.getId())
            self.assertTrue(deleted)
            self.assertIsNone(delete_errors)
            self.assertEqual(len(s_obj.getExpenses(group_id=new_group.getId(), visible=True)), 0)

            deleted_group, group_delete_errors = s_obj.deleteGroup(new_group.getId())
            self.assertTrue(deleted_group)
            self.assertIsNone(group_delete_errors)
