import io
import json
import threading
import unittest
from contextlib import contextmanager
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

from splitwise import Splitwise
from splitwise.backend import create_backend_app
from splitwise.expense import Expense, ExpenseUser
from splitwise.group import Group
from splitwise.pwa import create_app
from splitwise.user import User


class BackendAppTestCase(unittest.TestCase):
    def _request(self, app, method, path, payload=None, content_type='application/json'):
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
