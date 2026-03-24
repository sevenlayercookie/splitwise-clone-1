import io
import json
import tempfile
import unittest
from http import cookies
from importlib import import_module
from wsgiref.util import setup_testing_defaults

from splitwise.expense import Expense
from splitwise.group import Group
from splitwise.pwa import SDK_METHODS, create_app
from splitwise.user import ExpenseUser, User


class RecordingSplitwise(object):
    instances = []

    def __init__(self, consumer_key, consumer_secret, access_token=None, oauth2_access_token=None, api_key=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.oauth2_access_token = oauth2_access_token
        self.api_key = api_key
        self.created_group = None
        self.updated_user = None
        self.group_member = None
        self.created_expense = None
        self.oauth1_exchange = None
        self.oauth2_exchange = None
        RecordingSplitwise.instances.append(self)

    @classmethod
    def last(cls):
        return cls.instances[-1]

    def getAuthorizeURL(self):
        return 'https://example.test/oauth1', 'oauth-secret'

    def getAccessToken(self, oauth_token, oauth_token_secret, oauth_verifier):
        self.oauth1_exchange = (oauth_token, oauth_token_secret, oauth_verifier)
        return {'oauth_token': 'access-token', 'oauth_token_secret': 'access-secret'}

    def getOAuth2AuthorizeURL(self, redirect_uri, state=None):
        return 'https://example.test/oauth2', state or 'generated-state'

    def getOAuth2AccessToken(self, code, redirect_uri):
        self.oauth2_exchange = (code, redirect_uri)
        return {'access_token': 'oauth2-token', 'token_type': 'bearer'}

    def getCurrentUser(self):
        return {'id': 1, 'first_name': 'Alex'}

    def getUser(self, id):
        return {'id': id}

    def updateUser(self, user):
        self.updated_user = user
        return {'id': user.id, 'first_name': getattr(user, 'first_name', None)}, None

    def getFriends(self):
        return [{'id': 2}]

    def getGroups(self):
        return [{'id': 3}]

    def getGroup(self, id=0):
        return {'id': id}

    def createGroup(self, group):
        self.created_group = group
        return {'id': 40, 'name': group.name}, None

    def deleteGroup(self, id):
        return True, None

    def addUserToGroup(self, user, group_id):
        self.group_member = (user, group_id)
        return True, {'id': getattr(user, 'id', None), 'group_id': group_id}, None

    def getExpenses(self, **filters):
        return [{'id': 50, 'filters': filters}]

    def getExpense(self, id):
        return {'id': id}

    def createExpense(self, expense):
        self.created_expense = expense
        return {'id': 60, 'description': expense.description}, None

    def updateExpense(self, expense):
        self.created_expense = expense
        return {'id': expense.id, 'description': expense.description}, None

    def deleteExpense(self, id):
        return True, None

    def getCurrencies(self):
        return [{'currency_code': 'USD'}]

    def getCategories(self):
        return [{'id': 70, 'name': 'General'}]

    def getComments(self, expense_id):
        return [{'id': 80, 'expense_id': expense_id}]

    def createComment(self, expense_id, content):
        return {'id': 81, 'expense_id': expense_id, 'content': content}, None

    def getNotifications(self, updated_since=None, limit=None):
        return [{'id': 90, 'updated_since': updated_since, 'limit': limit}]


class PwaAppTestCase(unittest.TestCase):
    def setUp(self):
        RecordingSplitwise.instances = []

    def _request(self, app, method, path, payload=None, cookie=None):
        body = b''
        if payload is not None:
            body = json.dumps(payload).encode('utf-8')

        environ = {}
        setup_testing_defaults(environ)
        environ['REQUEST_METHOD'] = method
        environ['PATH_INFO'] = path
        environ['CONTENT_LENGTH'] = str(len(body))
        environ['CONTENT_TYPE'] = 'application/json'
        environ['wsgi.input'] = io.BytesIO(body)
        if cookie:
            environ['HTTP_COOKIE'] = cookie

        captured = {}

        def start_response(status, headers):
            captured['status'] = status
            captured['headers'] = headers

        raw = b''.join(app(environ, start_response))
        headers = dict(captured['headers'])
        response_cookie = headers.get('Set-Cookie') or cookie
        content_type = headers.get('Content-Type', '')
        if 'application/json' in content_type:
            parsed = json.loads(raw.decode('utf-8'))
        else:
            parsed = raw.decode('utf-8')
        return captured['status'], headers, parsed, response_cookie

    def test_static_assets_and_config_are_served(self):
        app = create_app(RecordingSplitwise, {
            'SPLITWISE_CONSUMER_KEY': 'env-key',
            'SPLITWISE_CONSUMER_SECRET': 'env-secret',
        })

        status, _, html, cookie = self._request(app, 'GET', '/')
        self.assertEqual(status, '200 OK')
        self.assertIn('Splitwise PWA Console', html)
        self.assertIn('manifest.json', html)
        self.assertIn('Recent activity', html)
        self.assertIn('Friend balances', html)
        self.assertIn('Paid by', html)
        self.assertIn('Custom split', html)
        self.assertIn('Split by percentage', html)
        self.assertIn('Split by shares', html)
        self.assertTrue(cookie)

        status, _, manifest, _ = self._request(app, 'GET', '/manifest.json', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertIn('Splitwise PWA Console', manifest)

        status, _, config, _ = self._request(app, 'GET', '/api/config', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertTrue(config['configured'])
        self.assertEqual(config['sdk_methods'], SDK_METHODS)

    def test_vercel_entrypoint_exports_wsgi_app(self):
        module = import_module('api.index')
        self.assertTrue(callable(module.app))

    def test_session_credentials_can_be_saved_and_cleared(self):
        app = create_app(RecordingSplitwise, {})

        status, _, data, cookie = self._request(
            app,
            'POST',
            '/api/session',
            payload={'consumer_key': 'key', 'consumer_secret': 'secret', 'api_key': 'token'},
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(data['session']['api_key'])

        status, _, config, cookie = self._request(app, 'GET', '/api/config', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertTrue(config['configured'])
        self.assertTrue(config['session']['consumer_key'])

        status, _, _, cookie = self._request(app, 'POST', '/api/session/clear', payload={}, cookie=cookie)
        self.assertEqual(status, '200 OK')

        status, _, cleared_config, _ = self._request(app, 'GET', '/api/config', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertFalse(cleared_config['configured'])

    def test_oauth_operations_store_access_tokens_in_session(self):
        app = create_app(RecordingSplitwise, {'SPLITWISE_CONSUMER_KEY': 'env-key', 'SPLITWISE_CONSUMER_SECRET': 'env-secret'})

        status, _, oauth1, cookie = self._request(app, 'POST', '/api/operations/getAuthorizeURL', payload={})
        self.assertEqual(status, '200 OK')
        self.assertEqual(oauth1['data']['oauth_token_secret'], 'oauth-secret')

        status, _, access_token, cookie = self._request(
            app,
            'POST',
            '/api/operations/getAccessToken',
            payload={'oauth_token': 'temp-token', 'oauth_verifier': 'verifier'},
            cookie=cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(access_token['data']['oauth_token'], 'access-token')
        self.assertEqual(RecordingSplitwise.last().oauth1_exchange, ('temp-token', 'oauth-secret', 'verifier'))

        status, _, oauth2, cookie = self._request(
            app,
            'POST',
            '/api/operations/getOAuth2AuthorizeURL',
            payload={'redirect_uri': 'https://example.test/callback', 'state': 'state-123'},
            cookie=cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(oauth2['data']['state'], 'state-123')

        status, _, token2, cookie = self._request(
            app,
            'POST',
            '/api/operations/getOAuth2AccessToken',
            payload={'code': 'code-1', 'redirect_uri': 'https://example.test/callback'},
            cookie=cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(token2['data']['access_token'], 'oauth2-token')
        self.assertEqual(RecordingSplitwise.last().oauth2_exchange, ('code-1', 'https://example.test/callback'))

        status, _, config, _ = self._request(app, 'GET', '/api/config', cookie=cookie)
        self.assertTrue(config['session']['access_token'])
        self.assertTrue(config['session']['oauth2_access_token'])

    def test_create_expense_operation_builds_sdk_expense_objects(self):
        app = create_app(RecordingSplitwise, {'SPLITWISE_CONSUMER_KEY': 'env-key', 'SPLITWISE_CONSUMER_SECRET': 'env-secret'})

        payload = {
            'expense': {
                'id': 99,
                'group_id': 77,
                'description': 'Dinner',
                'cost': '24.50',
                'currency_code': 'USD',
                'details': 'Shared meal',
                'split_equally': False,
                'split_method': 'percentage',
                'category_id': 12,
                'users': [
                    {'id': 1, 'paid_share': '24.50', 'owed_share': '12.25'},
                    {'id': 2, 'paid_share': '0.00', 'owed_share': '12.25'},
                ],
                'payers': [
                    {'user_id': 1, 'paid_share': '18.00'},
                    {'user_id': 2, 'paid_share': '6.50'},
                ],
                'participants': [
                    {'user_id': 1, 'included': True, 'split_value': '50'},
                    {'user_id': 2, 'included': True, 'split_value': '50'},
                ],
            }
        }
        status, _, response, _ = self._request(app, 'POST', '/api/operations/createExpense', payload=payload)
        self.assertEqual(status, '200 OK')
        self.assertEqual(response['data']['expense']['description'], 'Dinner')

        created_expense = RecordingSplitwise.last().created_expense
        self.assertIsInstance(created_expense, Expense)
        self.assertEqual(created_expense.id, 99)
        self.assertEqual(created_expense.group_id, 77)
        self.assertEqual(created_expense.description, 'Dinner')
        self.assertEqual(created_expense.cost, '24.50')
        self.assertEqual(created_expense.currency_code, 'USD')
        self.assertEqual(created_expense.details, 'Shared meal')
        self.assertEqual(created_expense.category.id, 12)
        self.assertFalse(created_expense.split_equally)
        self.assertEqual(created_expense.split_method, 'percentage')
        self.assertEqual(created_expense.payers[0]['paid_share'], '18.00')
        self.assertTrue(created_expense.participants[0]['included'])
        self.assertEqual(len(created_expense.users), 2)
        self.assertIsInstance(created_expense.users[0], ExpenseUser)
        self.assertEqual(created_expense.users[0].id, 1)

    def test_group_and_user_operations_build_sdk_models(self):
        app = create_app(RecordingSplitwise, {'SPLITWISE_CONSUMER_KEY': 'env-key', 'SPLITWISE_CONSUMER_SECRET': 'env-secret'})

        self._request(
            app,
            'POST',
            '/api/operations/updateUser',
            payload={'user': {'id': 5, 'first_name': 'Jamie', 'last_name': 'Doe', 'email': 'jamie@example.com'}},
        )
        updated_user = RecordingSplitwise.last().updated_user
        self.assertIsInstance(updated_user, User)
        self.assertEqual(updated_user.id, 5)
        self.assertEqual(updated_user.first_name, 'Jamie')

        self._request(
            app,
            'POST',
            '/api/operations/createGroup',
            payload={'group': {'name': 'Trip', 'group_type': 'trip', 'members': [{'id': 4, 'first_name': 'Pat'}]}},
        )
        created_group = RecordingSplitwise.last().created_group
        self.assertIsInstance(created_group, Group)
        self.assertEqual(created_group.name, 'Trip')
        self.assertEqual(created_group.group_type, 'trip')
        self.assertEqual(created_group.members[0].id, 4)

        self._request(
            app,
            'POST',
            '/api/operations/addUserToGroup',
            payload={'group_id': 11, 'user': {'id': 7, 'first_name': 'Chris'}},
        )
        member, group_id = RecordingSplitwise.last().group_member
        self.assertIsInstance(member, User)
        self.assertEqual(member.id, 7)
        self.assertEqual(group_id, 11)

    def test_local_account_flow_supports_register_login_friends_and_groups(self):
        app = create_app(environment={})

        status, _, register_one, cookie_one = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={
                'first_name': 'Taylor',
                'last_name': 'Tester',
                'email': 'taylor@example.com',
                'password': 'password123',
            },
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(register_one['user']['email'], 'taylor@example.com')

        status, _, _, cookie_one = self._request(app, 'POST', '/api/local/logout', payload={}, cookie=cookie_one)
        self.assertEqual(status, '200 OK')

        status, _, login_one, cookie_one = self._request(
            app,
            'POST',
            '/api/local/login',
            payload={'email': 'taylor@example.com', 'password': 'password123'},
            cookie=cookie_one,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(login_one['user']['first_name'], 'Taylor')

        status, _, register_two, _ = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={
                'first_name': 'Jordan',
                'email': 'jordan@example.com',
                'password': 'password123',
            },
        )
        self.assertEqual(status, '200 OK')

        status, _, added_friend, cookie_one = self._request(
            app,
            'POST',
            '/api/local/friends',
            payload={'email': 'jordan@example.com'},
            cookie=cookie_one,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(added_friend['friend']['email'], 'jordan@example.com')

        status, _, friends_response, cookie_one = self._request(
            app,
            'POST',
            '/api/operations/getFriends',
            payload={},
            cookie=cookie_one,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual([item['email'] for item in friends_response['data']], ['jordan@example.com'])

        status, _, create_group, cookie_one = self._request(
            app,
            'POST',
            '/api/operations/createGroup',
            payload={
                'group': {
                    'name': 'Demo group',
                    'members': [{'id': register_two['user']['id'], 'email': 'jordan@example.com', 'first_name': 'Jordan'}],
                },
            },
            cookie=cookie_one,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(create_group['data']['group']['name'], 'Demo group')
        self.assertEqual(len(create_group['data']['group']['members']), 2)
        self.assertEqual(create_group['data']['group']['members'][1]['email'], 'jordan@example.com')

        status, _, groups_response, _ = self._request(
            app,
            'POST',
            '/api/operations/getGroups',
            payload={},
            cookie=cookie_one,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(any(group['name'] == 'Demo group' for group in groups_response['data']))

    def test_local_pwa_supports_friend_requests_profile_updates_settlements_and_comments(self):
        app = create_app(environment={})

        status, _, alex, alex_cookie = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={
                'first_name': 'Alex',
                'email': 'alex-local@example.com',
                'password': 'password123',
            },
        )
        self.assertEqual(status, '200 OK')

        status, _, _, alex_cookie = self._request(app, 'POST', '/api/local/logout', payload={}, cookie=alex_cookie)
        self.assertEqual(status, '200 OK')

        status, _, jamie, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={
                'first_name': 'Jamie',
                'email': 'jamie-local@example.com',
                'password': 'password123',
            },
        )
        self.assertEqual(status, '200 OK')

        status, _, _, jamie_cookie = self._request(app, 'POST', '/api/local/logout', payload={}, cookie=jamie_cookie)
        self.assertEqual(status, '200 OK')

        status, _, _, alex_cookie = self._request(
            app,
            'POST',
            '/api/local/login',
            payload={'email': 'alex-local@example.com', 'password': 'password123'},
            cookie=alex_cookie,
        )
        self.assertEqual(status, '200 OK')

        status, _, request_response, alex_cookie = self._request(
            app,
            'POST',
            '/api/local/friend-requests',
            payload={'email': 'jamie-local@example.com'},
            cookie=alex_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(request_response['request']['status'], 'pending')

        status, _, _, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/login',
            payload={'email': 'jamie-local@example.com', 'password': 'password123'},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')

        status, _, pending, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/friend-requests/list',
            payload={},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(len(pending['requests']['incoming']), 1)

        status, _, accepted, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/friend-requests/respond',
            payload={'request_id': pending['requests']['incoming'][0]['id'], 'accept': True},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(accepted['result']['status'], 'accepted')

        status, _, updated_profile, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/profile',
            payload={'first_name': 'Jamie Updated', 'email': 'jamie-updated@example.com'},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(updated_profile['user']['email'], 'jamie-updated@example.com')

        status, _, password_response, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/password',
            payload={'current_password': 'password123', 'new_password': 'newpassword123'},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(password_response['result']['updated'])

        status, _, expense_response, jamie_cookie = self._request(
            app,
            'POST',
            '/api/operations/createExpense',
            payload={
                'expense': {
                    'description': 'Dinner',
                    'cost': '20.00',
                    'currency_code': 'USD',
                    'users': [
                        {'id': jamie['user']['id'], 'paid_share': '20.00', 'owed_share': '10.00'},
                        {'id': alex['user']['id'], 'paid_share': '0.00', 'owed_share': '10.00'},
                    ],
                }
            },
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        expense_id = expense_response['data']['expense']['id']

        status, _, settlement_response, jamie_cookie = self._request(
            app,
            'POST',
            '/api/local/settlements',
            payload={
                'other_user_id': alex['user']['id'],
                'amount': '10.00',
                'from_user_id': alex['user']['id'],
                'to_user_id': jamie['user']['id'],
            },
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(settlement_response['settlement']['amount'], '10.00')

        status, _, comment_response, jamie_cookie = self._request(
            app,
            'POST',
            '/api/operations/createComment',
            payload={'expense_id': expense_id, 'content': 'Paid back in cash'},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(comment_response['data']['comment']['content'], 'Paid back in cash')

        status, _, friends_response, _ = self._request(
            app,
            'POST',
            '/api/operations/getFriends',
            payload={},
            cookie=jamie_cookie,
        )
        self.assertEqual(status, '200 OK')
        alex_friend = next(item for item in friends_response['data'] if item['email'] == 'alex-local@example.com')
        self.assertEqual(alex_friend['balance'][0]['amount'], '0.00')

    def test_local_pwa_supports_recurring_series_and_group_management_polish(self):
        app = create_app(environment={})

        status, _, owner, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={'first_name': 'Owner', 'email': 'owner-local@example.com', 'password': 'password123'},
        )
        self.assertEqual(status, '200 OK')

        status, _, admin, admin_cookie = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={'first_name': 'Admin', 'email': 'admin-local@example.com', 'password': 'password123'},
        )
        self.assertEqual(status, '200 OK')

        status, _, member, member_cookie = self._request(
            app,
            'POST',
            '/api/local/register',
            payload={'first_name': 'Member', 'email': 'member-local@example.com', 'password': 'password123'},
        )
        self.assertEqual(status, '200 OK')

        status, _, _, owner_cookie = self._request(
            app,
            'POST',
            '/api/operations/createGroup',
            payload={'group': {'name': 'Road trip', 'members': [
                {'id': admin['user']['id'], 'first_name': 'Admin', 'email': 'admin-local@example.com'},
                {'id': member['user']['id'], 'first_name': 'Member', 'email': 'member-local@example.com'},
            ]}},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')

        status, _, groups_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/operations/getGroups',
            payload={},
            cookie=owner_cookie,
        )
        group = next(item for item in groups_response['data'] if item['name'] == 'Road trip')

        status, _, admin_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/groups/admin',
            payload={'group_id': group['id'], 'user_id': admin['user']['id'], 'is_admin': True},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertIn(admin['user']['id'], admin_response['group']['admin_ids'])

        status, _, archived_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/groups/archive',
            payload={'group_id': group['id'], 'archived': True},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(archived_response['group']['archived'])

        status, _, unarchived_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/groups/archive',
            payload={'group_id': group['id'], 'archived': False},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertFalse(unarchived_response['group']['archived'])

        status, _, recurring_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/operations/createExpense',
            payload={
                'expense': {
                    'group_id': group['id'],
                    'description': 'Recurring hotel',
                    'cost': '120.00',
                    'date': '2026-03-20T12:00:00Z',
                    'repeats': True,
                    'repeat_interval': 'daily',
                    'users': [
                        {'id': owner['user']['id'], 'paid_share': '120.00', 'owed_share': '60.00'},
                        {'id': admin['user']['id'], 'paid_share': '0.00', 'owed_share': '60.00'},
                    ],
                },
            },
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        series_id = recurring_response['data']['expense']['series_id']

        status, _, expenses_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/operations/getExpenses',
            payload={},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(any(item['series_id'] == series_id and item['id'] != recurring_response['data']['expense']['id'] for item in expenses_response['data']))

        status, _, paused_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/expense-series/pause',
            payload={'series_id': series_id},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(paused_response['expense']['series_paused'])

        status, _, updated_series, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/expense-series/update',
            payload={'series_id': series_id, 'expense': {'description': 'Recurring hotel updated', 'cost': '130.00', 'users': [
                {'id': owner['user']['id'], 'paid_share': '130.00', 'owed_share': '65.00'},
                {'id': admin['user']['id'], 'paid_share': '0.00', 'owed_share': '65.00'},
            ]}},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertEqual(updated_series['expense']['description'], 'Recurring hotel updated')

        status, _, cancelled_response, owner_cookie = self._request(
            app,
            'POST',
            '/api/local/expense-series/cancel',
            payload={'series_id': series_id},
            cookie=owner_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(cancelled_response['expense']['series_cancelled'])

        status, _, _, admin_cookie = self._request(
            app,
            'POST',
            '/api/local/login',
            payload={'email': 'admin-local@example.com', 'password': 'password123'},
            cookie=admin_cookie,
        )
        self.assertEqual(status, '200 OK')

        status, _, leave_response, admin_cookie = self._request(
            app,
            'POST',
            '/api/local/groups/leave',
            payload={'group_id': group['id']},
            cookie=admin_cookie,
        )
        self.assertEqual(status, '200 OK')
        self.assertTrue(leave_response['result']['left'])

    def test_local_pwa_can_persist_accounts_and_saved_session_settings(self):
        with tempfile.TemporaryDirectory() as tempdir:
            environment = {'SPLITWISE_PERSISTENCE_DIR': tempdir}
            first_app = create_app(environment=environment)

            status, _, register_response, cookie = self._request(
                first_app,
                'POST',
                '/api/local/register',
                payload={'first_name': 'Persisted', 'email': 'persisted-local@example.com', 'password': 'password123'},
            )
            self.assertEqual(status, '200 OK')

            status, _, _, cookie = self._request(
                first_app,
                'POST',
                '/api/session',
                payload={'consumer_key': 'demo-key', 'consumer_secret': 'demo-secret'},
                cookie=cookie,
            )
            self.assertEqual(status, '200 OK')

            second_app = create_app(environment=environment)

            status, _, config_response, cookie = self._request(second_app, 'GET', '/api/config', cookie=cookie)
            self.assertEqual(status, '200 OK')
            self.assertTrue(config_response['authenticated'])
            self.assertEqual(config_response['local_user']['email'], 'persisted-local@example.com')
            self.assertTrue(config_response['session']['consumer_key'])
            self.assertTrue(config_response['session']['consumer_secret'])
            jar = cookies.SimpleCookie()
            jar.load(cookie)
            session_id = jar['splitwise_pwa'].value
            self.assertEqual(second_app.sessions[session_id]['consumer_key'], 'demo-key')
            self.assertEqual(second_app.sessions[session_id]['consumer_secret'], 'demo-secret')

            status, _, _, cookie = self._request(
                second_app,
                'POST',
                '/api/local/logout',
                payload={},
                cookie=cookie,
            )
            self.assertEqual(status, '200 OK')

            third_app = create_app(environment=environment)
            status, _, config_after_logout, _ = self._request(third_app, 'GET', '/api/config', cookie=cookie)
            self.assertEqual(status, '200 OK')
            self.assertFalse(config_after_logout['authenticated'])
            self.assertTrue(config_after_logout['session']['consumer_key'])
            self.assertEqual(third_app.sessions[session_id]['consumer_key'], 'demo-key')


if __name__ == '__main__':
    unittest.main()
