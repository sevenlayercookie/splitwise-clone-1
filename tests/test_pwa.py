import io
import json
import unittest
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
        self.assertTrue(cookie)

        status, _, manifest, _ = self._request(app, 'GET', '/manifest.json', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertIn('Splitwise PWA Console', manifest)

        status, _, config, _ = self._request(app, 'GET', '/api/config', cookie=cookie)
        self.assertEqual(status, '200 OK')
        self.assertTrue(config['configured'])
        self.assertEqual(config['sdk_methods'], SDK_METHODS)

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
                'split_equally': True,
                'category_id': 12,
                'users': [
                    {'id': 1, 'paid_share': '24.50', 'owed_share': '12.25'},
                    {'id': 2, 'paid_share': '0.00', 'owed_share': '12.25'},
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
        self.assertTrue(created_expense.split_equally)
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


if __name__ == '__main__':
    unittest.main()
