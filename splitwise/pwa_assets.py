INDEX_HTML = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">
    <meta name=\"theme-color\" content=\"#2563eb\">
    <meta name=\"description\" content=\"Mobile-first Splitwise progressive web app powered by the Python SDK.\">
    <title>Splitwise PWA Console</title>
    <link rel=\"manifest\" href=\"/manifest.json\">
    <link rel=\"icon\" href=\"/icon.svg\" type=\"image/svg+xml\">
    <link rel=\"stylesheet\" href=\"/styles.css\">
  </head>
  <body>
    <div class=\"shell\">
      <header class=\"hero\">
        <div>
          <p class=\"eyebrow\">Progressive Web App</p>
          <h1>Splitwise PWA Console</h1>
          <p class=\"lede\">
            A mobile-first dashboard that exposes every SDK API call, caches its shell for
            offline use, and keeps recent responses on-device.
          </p>
        </div>
        <button id=\"install-button\" class=\"secondary hidden\" type=\"button\">Install app</button>
      </header>

      <section class=\"status-grid\" aria-label=\"Application status\">
        <article class=\"status-card\">
          <span class=\"status-label\">Connectivity</span>
          <strong id=\"connectivity-status\">Checking…</strong>
          <small>Offline-ready shell with local response cache.</small>
        </article>
        <article class=\"status-card\">
          <span class=\"status-label\">Credentials</span>
          <strong id=\"credentials-status\">Loading…</strong>
          <small id=\"session-summary\">Reading configuration…</small>
        </article>
        <article class=\"status-card\">
          <span class=\"status-label\">API coverage</span>
          <strong id=\"coverage-status\">0/0</strong>
          <small>Each SDK method has a dedicated action below.</small>
        </article>
      </section>

      <main class=\"layout\">
        <section class=\"panel\" id=\"credentials-panel\">
          <div class=\"panel-heading\">
            <div>
              <h2>Session credentials</h2>
              <p>Store consumer keys, API key, and tokens in the server session for this browser tab.</p>
            </div>
            <button id=\"clear-session\" class=\"ghost\" type=\"button\">Clear session</button>
          </div>
          <form id=\"session-form\" class=\"form-stack\">
            <label>
              Consumer key
              <input name=\"consumer_key\" autocomplete=\"off\" placeholder=\"Splitwise consumer key\">
            </label>
            <label>
              Consumer secret
              <input name=\"consumer_secret\" autocomplete=\"off\" placeholder=\"Splitwise consumer secret\">
            </label>
            <label>
              API key
              <input name=\"api_key\" autocomplete=\"off\" placeholder=\"Optional bearer API key\">
            </label>
            <label>
              OAuth 1 access token JSON
              <textarea
                name=\"access_token\"
                rows=\"3\"
                placeholder='{"oauth_token":"...","oauth_token_secret":"..."}'
              ></textarea>
            </label>
            <label>
              OAuth 2 access token JSON
              <textarea
                name=\"oauth2_access_token\"
                rows=\"3\"
                placeholder='{"access_token":"...","token_type":"bearer"}'
              ></textarea>
            </label>
            <button type=\"submit\">Save session credentials</button>
          </form>
        </section>

        <section class=\"panel\" id=\"dashboard-panel\">
          <div class=\"panel-heading\">
            <div>
              <h2>Quick dashboard</h2>
              <p>Tap the most common resources to populate a mobile-friendly live snapshot.</p>
            </div>
            <button id=\"refresh-dashboard\" type=\"button\">Refresh dashboard</button>
          </div>
          <div class=\"quick-actions\" id=\"dashboard-actions\"></div>
          <div class=\"dashboard-grid\" id=\"dashboard-grid\"></div>
        </section>

        <section class=\"panel\" id=\"coverage-panel\">
          <div class=\"panel-heading\">
            <div>
              <h2>SDK coverage</h2>
              <p>Every public Splitwise SDK method is surfaced in the action lab.</p>
            </div>
          </div>
          <div id=\"coverage-board\" class=\"coverage-board\"></div>
        </section>

        <section class=\"panel\" id=\"lab-panel\">
          <div class=\"panel-heading\">
            <div>
              <h2>Action lab</h2>
              <p>Invoke every API call with focused forms and JSON payload templates designed for mobile screens.</p>
            </div>
          </div>
          <div id=\"operation-groups\" class=\"operation-groups\"></div>
        </section>

        <section class=\"panel\" id=\"result-panel\">
          <div class=\"panel-heading\">
            <div>
              <h2>Latest response</h2>
              <p>Results are cached locally so the most recent successful response remains available offline.</p>
            </div>
          </div>
          <p id=\"result-meta\" class=\"result-meta\">No API call made yet.</p>
          <pre id=\"result-output\" class=\"result-output\">Awaiting input…</pre>
        </section>
      </main>
    </div>
    <script src=\"/app.js\" defer></script>
  </body>
</html>
"""

STYLES_CSS = """:root {
  color-scheme: light;
  --bg: #eff6ff;
  --panel: #ffffff;
  --border: #dbeafe;
  --text: #0f172a;
  --muted: #475569;
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --success: #15803d;
  --warning: #b45309;
  --danger: #b91c1c;
  --shadow: 0 18px 45px rgba(37, 99, 235, 0.12);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: linear-gradient(180deg, #dbeafe 0%, var(--bg) 32%, #f8fafc 100%);
  color: var(--text);
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  border: none;
  border-radius: 999px;
  padding: 0.85rem 1.2rem;
  background: var(--primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

button:hover,
button:focus-visible {
  background: var(--primary-dark);
}

button.secondary {
  background: #0f172a;
}

button.ghost {
  background: #e2e8f0;
  color: var(--text);
}

button.hidden {
  display: none;
}

.shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.hero {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1.5rem;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(219, 234, 254, 0.9);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}

.eyebrow {
  margin: 0 0 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 700;
}

.hero h1,
.panel h2 {
  margin: 0;
}

.lede,
.panel-heading p,
.status-card small,
label,
.result-meta,
summary small,
.hint {
  color: var(--muted);
}

.status-grid,
.dashboard-grid {
  display: grid;
  gap: 1rem;
}

.status-grid {
  grid-template-columns: 1fr;
  margin-top: 1rem;
}

.status-card,
.panel,
.dashboard-card,
.operation-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 1.25rem;
  box-shadow: var(--shadow);
}

.status-card,
.panel,
.dashboard-card {
  padding: 1rem;
}

.status-label,
.dashboard-card h3,
.operation-card summary strong {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 0.35rem;
}

.layout {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
}

.panel-heading {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.form-stack,
.operation-form {
  display: grid;
  gap: 0.85rem;
}

label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.95rem;
}

input,
textarea,
select {
  width: 100%;
  padding: 0.9rem 1rem;
  border: 1px solid #bfdbfe;
  border-radius: 0.9rem;
  background: #f8fafc;
  color: var(--text);
}

textarea {
  min-height: 7rem;
  resize: vertical;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.quick-actions button {
  flex: 1 1 8rem;
}

.dashboard-grid {
  grid-template-columns: 1fr;
}

.dashboard-card h3 {
  margin-top: 0;
}

.dashboard-card pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--muted);
}

.coverage-board {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.coverage-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  background: #dbeafe;
  color: #1e3a8a;
  font-size: 0.85rem;
  font-weight: 600;
}

.coverage-chip.used {
  background: #dcfce7;
  color: #166534;
}

.operation-groups {
  display: grid;
  gap: 1rem;
}

.operation-group {
  display: grid;
  gap: 0.8rem;
}

.operation-card {
  overflow: hidden;
}

.operation-card summary {
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  cursor: pointer;
}

.operation-card summary::-webkit-details-marker {
  display: none;
}

.operation-card .content {
  padding: 0 1rem 1rem;
}

.operation-card .tag {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: #e2e8f0;
  color: #0f172a;
  font-size: 0.8rem;
  font-weight: 700;
}

.result-output {
  margin: 0;
  padding: 1rem;
  border-radius: 1rem;
  background: #0f172a;
  color: #e2e8f0;
  min-height: 18rem;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 1rem;
  transform: translateX(-50%);
  padding: 0.85rem 1rem;
  border-radius: 999px;
  color: #fff;
  background: #0f172a;
  box-shadow: var(--shadow);
  z-index: 20;
}

.toast.success {
  background: var(--success);
}

.toast.error {
  background: var(--danger);
}

@media (min-width: 700px) {
  .shell {
    padding: 1.5rem;
  }

  .hero {
    align-items: flex-end;
    flex-direction: row;
    justify-content: space-between;
  }

  .status-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .panel-heading {
    align-items: center;
    flex-direction: row;
    justify-content: space-between;
  }
}

@media (min-width: 1024px) {
  .layout {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: start;
  }

  #lab-panel,
  #result-panel {
    grid-column: span 2;
  }
}
"""

APP_JS = """const STORAGE_KEY = 'splitwise-pwa-used-operations';
const RESULT_CACHE_KEY = 'splitwise-pwa-last-result';
const DASHBOARD_CACHE_KEY = 'splitwise-pwa-dashboard';

const QUICK_ACTIONS = [
  ['Profile', 'getCurrentUser'],
  ['Friends', 'getFriends'],
  ['Groups', 'getGroups'],
  ['Expenses', 'getExpenses'],
  ['Notifications', 'getNotifications'],
  ['Currencies', 'getCurrencies'],
  ['Categories', 'getCategories'],
];

const DASHBOARD_BINDINGS = {
  getCurrentUser: { title: 'Current user' },
  getFriends: { title: 'Friends' },
  getGroups: { title: 'Groups' },
  getExpenses: { title: 'Expenses' },
  getNotifications: { title: 'Notifications' },
  getCurrencies: { title: 'Currencies' },
  getCategories: { title: 'Categories' },
};

const OPERATION_GROUPS = [
  {
    title: 'Authentication flows',
    description: 'Use OAuth 1, OAuth 2, or API key access from the same installable shell.',
    operations: [
      {
        operation: 'getAuthorizeURL',
        label: 'Start OAuth 1',
        description: 'Generates the OAuth 1 authorization URL and stores the temporary secret in session.',
      },
      {
        operation: 'getAccessToken',
        label: 'Exchange OAuth 1 verifier',
        description: 'Redeems an OAuth 1 verifier for an access token and saves it to the browser session.',
        fields: [
          { name: 'oauth_token', label: 'OAuth token', placeholder: 'oauth token from callback' },
          { name: 'oauth_verifier', label: 'OAuth verifier', placeholder: 'oauth verifier from callback' },
          {
            name: 'oauth_token_secret',
            label: 'OAuth token secret (optional)',
            placeholder: 'leave empty to use stored session secret',
          },
        ],
      },
      {
        operation: 'getOAuth2AuthorizeURL',
        label: 'Start OAuth 2',
        description: 'Builds an OAuth 2 authorization URL for the supplied redirect URI.',
        fields: [
          { name: 'redirect_uri', label: 'Redirect URI', placeholder: 'https://example.com/callback', required: true },
          { name: 'state', label: 'State (optional)', placeholder: 'optional anti-forgery state' },
        ],
      },
      {
        operation: 'getOAuth2AccessToken',
        label: 'Exchange OAuth 2 code',
        description: 'Redeems an OAuth 2 authorization code and stores the resulting bearer token in session.',
        fields: [
          { name: 'code', label: 'Authorization code', placeholder: 'code from callback', required: true },
          { name: 'redirect_uri', label: 'Redirect URI', placeholder: 'must match the authorize request', required: true },
        ],
      },
    ],
  },
  {
    title: 'People and profile',
    description: 'Browse and update the people data exposed by the SDK.',
    operations: [
      {
        operation: 'getCurrentUser',
        label: 'Get current user',
        description: 'Loads the authenticated Splitwise profile.',
      },
      {
        operation: 'getUser',
        label: 'Get user',
        description: 'Fetches a single acquaintance by id.',
        fields: [{ name: 'id', label: 'User id', placeholder: '12345', required: true }],
      },
      {
        operation: 'updateUser',
        label: 'Update user',
        description: 'Sends a partial User payload to Splitwise.',
        jsonTemplate:
          '{\\n' +
          '  "user": {\\n' +
          '    "id": 12345,\\n' +
          '    "first_name": "Alex",\\n' +
          '    "last_name": "Example",\\n' +
          '    "email": "alex@example.com"\\n' +
          '  }\\n' +
          '}',
      },
      {
        operation: 'getFriends',
        label: 'Get friends',
        description: 'Lists friends and per-friend balances.',
      },
    ],
  },
  {
    title: 'Groups',
    description: 'Create, inspect, mutate, and delete groups from the same surface.',
    operations: [
      {
        operation: 'getGroups',
        label: 'Get groups',
        description: 'Loads every group for the authenticated account.',
      },
      {
        operation: 'getGroup',
        label: 'Get group',
        description: 'Fetch a single group or use 0 for non-group expenses.',
        fields: [{ name: 'id', label: 'Group id', placeholder: '0 or an existing group id', required: true }],
      },
      {
        operation: 'createGroup',
        label: 'Create group',
        description: 'Creates a new group and optional starter members.',
        jsonTemplate:
          '{\\n' +
          '  "group": {\\n' +
          '    "name": "Weekend trip",\\n' +
          '    "group_type": "trip",\\n' +
          '    "whiteboard": "Bring snacks",\\n' +
          '    "country_code": "US",\\n' +
          '    "members": [\\n' +
          '      {"first_name": "Sam", "last_name": "Guest", "email": "sam@example.com"}\\n' +
          '    ]\\n' +
          '  }\\n' +
          '}',
      },
      {
        operation: 'addUserToGroup',
        label: 'Add user to group',
        description: 'Adds a new or existing member to a group.',
        jsonTemplate:
          '{\\n' +
          '  "group_id": 123,\\n' +
          '  "user": {\\n' +
          '    "id": 456,\\n' +
          '    "first_name": "Pat",\\n' +
          '    "last_name": "Member",\\n' +
          '    "email": "pat@example.com"\\n' +
          '  }\\n' +
          '}',
      },
      {
        operation: 'deleteGroup',
        label: 'Delete group',
        description: 'Deletes a group by id.',
        fields: [{ name: 'id', label: 'Group id', placeholder: '123', required: true }],
      },
    ],
  },
  {
    title: 'Expenses',
    description: 'Review, create, update, and delete expense records.',
    operations: [
      {
        operation: 'getExpenses',
        label: 'Get expenses',
        description: 'Reads the expense feed with optional filters.',
        jsonTemplate: '{\\n  "offset": 0,\\n  "limit": 20,\\n  "visible": true\\n}',
      },
      {
        operation: 'getExpense',
        label: 'Get expense',
        description: 'Fetches a single expense by id.',
        fields: [{ name: 'id', label: 'Expense id', placeholder: '123', required: true }],
      },
      {
        operation: 'createExpense',
        label: 'Create expense',
        description: 'Creates a new expense with manual or equal splits.',
        jsonTemplate:
          '{\\n' +
          '  "expense": {\\n' +
          '    "cost": "24.50",\\n' +
          '    "description": "Dinner",\\n' +
          '    "currency_code": "USD",\\n' +
          '    "group_id": 123,\\n' +
          '    "split_equally": true,\\n' +
          '    "users": [\\n' +
          '      {"id": 12345, "paid_share": "24.50", "owed_share": "12.25"},\\n' +
          '      {"id": 67890, "paid_share": "0.00", "owed_share": "12.25"}\\n' +
          '    ]\\n' +
          '  }\\n' +
          '}',
      },
      {
        operation: 'updateExpense',
        label: 'Update expense',
        description: 'Updates an existing expense using a partial payload.',
        jsonTemplate:
          '{\\n' +
          '  "expense": {\\n' +
          '    "id": 555,\\n' +
          '    "description": "Updated dinner",\\n' +
          '    "details": "Added dessert",\\n' +
          '    "cost": "30.00"\\n' +
          '  }\\n' +
          '}',
      },
      {
        operation: 'deleteExpense',
        label: 'Delete expense',
        description: 'Deletes an expense by id.',
        fields: [{ name: 'id', label: 'Expense id', placeholder: '123', required: true }],
      },
    ],
  },
  {
    title: 'Catalogs, comments, and notifications',
    description: 'Surface supporting reference data and conversation tools.',
    operations: [
      { operation: 'getCurrencies', label: 'Get currencies', description: 'Lists every supported currency.' },
      { operation: 'getCategories', label: 'Get categories', description: 'Loads categories and subcategories.' },
      {
        operation: 'getComments',
        label: 'Get comments',
        description: 'Lists comments for an expense.',
        fields: [{ name: 'expense_id', label: 'Expense id', placeholder: '123', required: true }],
      },
      {
        operation: 'createComment',
        label: 'Create comment',
        description: 'Adds a new comment to an expense.',
        fields: [
          { name: 'expense_id', label: 'Expense id', placeholder: '123', required: true },
          { name: 'content', label: 'Comment text', placeholder: 'Looks good to me', required: true },
        ],
      },
      {
        operation: 'getNotifications',
        label: 'Get notifications',
        description: 'Fetches recent notifications.',
        jsonTemplate: '{\\n  "limit": 20\\n}',
      },
    ],
  },
];

const state = {
  config: null,
  usedOperations: new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')),
  dashboard: JSON.parse(localStorage.getItem(DASHBOARD_CACHE_KEY) || '{}'),
  installPrompt: null,
};

const elements = {};

document.addEventListener('DOMContentLoaded', () => {
  bindElements();
  wireBaseInteractions();
  renderOperationGroups();
  renderDashboardCache();
  renderCachedResult();
  updateConnectivity();
  window.addEventListener('online', updateConnectivity);
  window.addEventListener('offline', updateConnectivity);
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    state.installPrompt = event;
    elements.installButton.classList.remove('hidden');
  });
  registerServiceWorker();
  loadConfig();
});

function bindElements() {
  elements.installButton = document.getElementById('install-button');
  elements.connectivityStatus = document.getElementById('connectivity-status');
  elements.credentialsStatus = document.getElementById('credentials-status');
  elements.sessionSummary = document.getElementById('session-summary');
  elements.coverageStatus = document.getElementById('coverage-status');
  elements.coverageBoard = document.getElementById('coverage-board');
  elements.operationGroups = document.getElementById('operation-groups');
  elements.resultMeta = document.getElementById('result-meta');
  elements.resultOutput = document.getElementById('result-output');
  elements.sessionForm = document.getElementById('session-form');
  elements.clearSession = document.getElementById('clear-session');
  elements.dashboardActions = document.getElementById('dashboard-actions');
  elements.dashboardGrid = document.getElementById('dashboard-grid');
  elements.refreshDashboard = document.getElementById('refresh-dashboard');
}

function wireBaseInteractions() {
  elements.installButton.addEventListener('click', async () => {
    if (!state.installPrompt) {
      return;
    }
    state.installPrompt.prompt();
    await state.installPrompt.userChoice;
    state.installPrompt = null;
    elements.installButton.classList.add('hidden');
  });

  elements.sessionForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {};
    for (const key of ['consumer_key', 'consumer_secret', 'api_key']) {
      const value = (form.get(key) || '').toString().trim();
      if (value) {
        payload[key] = value;
      }
    }
    for (const key of ['access_token', 'oauth2_access_token']) {
      const rawValue = (form.get(key) || '').toString().trim();
      if (!rawValue) {
        continue;
      }
      try {
        payload[key] = JSON.parse(rawValue);
      } catch (error) {
        showToast(`${key} must be valid JSON`, 'error');
        return;
      }
    }
    const response = await request('/api/session', payload);
    if (response) {
      showToast('Session updated', 'success');
      elements.sessionForm.reset();
      await loadConfig();
    }
  });

  elements.clearSession.addEventListener('click', async () => {
    const response = await request('/api/session/clear', {});
    if (response) {
      state.usedOperations.clear();
      persistUsedOperations();
      state.dashboard = {};
      localStorage.removeItem(DASHBOARD_CACHE_KEY);
      showToast('Session cleared', 'success');
      renderDashboardCache();
      renderCoverage();
      await loadConfig();
    }
  });

  QUICK_ACTIONS.forEach(([label, operation]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.addEventListener('click', () => invokeOperation(operation));
    elements.dashboardActions.appendChild(button);
  });

  elements.refreshDashboard.addEventListener('click', async () => {
    for (const [, operation] of QUICK_ACTIONS) {
      await invokeOperation(operation, {}, { silent: true });
    }
    showToast('Dashboard refreshed', 'success');
  });
}

async function loadConfig() {
  const config = await fetchJson('/api/config');
  if (!config) {
    return;
  }
  state.config = config;
  renderSessionState();
  renderCoverage();
}

function renderSessionState() {
  const summary = state.config && state.config.session ? state.config.session : {};
  elements.credentialsStatus.textContent = state.config.configured ? 'Ready' : 'Needs setup';
  const parts = [];
  if (summary.consumer_key) parts.push('consumer key saved');
  if (summary.consumer_secret) parts.push('consumer secret saved');
  if (summary.api_key) parts.push('API key saved');
  if (summary.access_token) parts.push('OAuth 1 token saved');
  if (summary.oauth2_access_token) parts.push('OAuth 2 token saved');
  elements.sessionSummary.textContent = parts.length
    ? parts.join(' • ')
    : 'Provide consumer credentials or a token to start calling the API.';
}

function renderCoverage() {
  const methods = state.config ? state.config.sdk_methods : [];
  elements.coverageBoard.innerHTML = '';
  methods.forEach((method) => {
    const chip = document.createElement('span');
    chip.className = `coverage-chip${state.usedOperations.has(method) ? ' used' : ''}`;
    chip.textContent = method;
    elements.coverageBoard.appendChild(chip);
  });
  elements.coverageStatus.textContent = `${state.usedOperations.size}/${methods.length}`;
}

function renderOperationGroups() {
  elements.operationGroups.innerHTML = '';
  OPERATION_GROUPS.forEach((group) => {
    const wrapper = document.createElement('section');
    wrapper.className = 'operation-group';
    wrapper.innerHTML = `<div><h3>${group.title}</h3><p class=\"hint\">${group.description}</p></div>`;

    group.operations.forEach((operation) => {
      const details = document.createElement('details');
      details.className = 'operation-card';
      const fieldsMarkup = (operation.fields || []).map((field) => `
        <label>
          ${field.label}
          <input name="${field.name}" placeholder="${field.placeholder || ''}" ${field.required ? 'required' : ''}>
        </label>
      `).join('');
      const jsonMarkup = operation.jsonTemplate ? `
        <label>
          JSON payload
          <textarea name="payload" rows="10">${operation.jsonTemplate}</textarea>
        </label>
      ` : '';
      details.innerHTML = `
        <summary>
          <div>
            <strong>${operation.label}</strong>
            <small>${operation.description}</small>
          </div>
          <span class="tag">${operation.operation}</span>
        </summary>
        <div class="content">
          <form class="operation-form" data-operation="${operation.operation}">
            ${fieldsMarkup}
            ${jsonMarkup}
            <button type="submit">Run ${operation.label}</button>
          </form>
        </div>
      `;
      wrapper.appendChild(details);
    });

    elements.operationGroups.appendChild(wrapper);
  });

  elements.operationGroups.addEventListener('submit', async (event) => {
    const form = event.target;
    if (!form.matches('.operation-form')) {
      return;
    }
    event.preventDefault();
    const payload = collectOperationPayload(form);
    if (payload === null) {
      return;
    }
    await invokeOperation(form.dataset.operation, payload);
  });
}

function collectOperationPayload(form) {
  const payloadField = form.querySelector('textarea[name="payload"]');
  if (payloadField) {
    const rawJson = payloadField.value.trim();
    if (!rawJson) {
      return {};
    }
    try {
      return JSON.parse(rawJson);
    } catch (error) {
      showToast('JSON payload is invalid', 'error');
      return null;
    }
  }

  const data = {};
  for (const field of form.querySelectorAll('input[name]')) {
    const value = field.value.trim();
    if (!value) {
      continue;
    }
    data[field.name] = normalizeScalar(value);
  }
  return data;
}

function normalizeScalar(value) {
  if (value === 'true') return true;
  if (value === 'false') return false;
  if (/^-?\\d+$/.test(value)) return Number(value);
  return value;
}

async function invokeOperation(operation, payload = {}, options = {}) {
  const response = await request(`/api/operations/${operation}`, payload, options.silent);
  if (!response) {
    return null;
  }

  state.usedOperations.add(operation);
  persistUsedOperations();
  renderCoverage();
  renderResult(operation, response);

  if (DASHBOARD_BINDINGS[operation]) {
    state.dashboard[operation] = response.data;
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
    renderDashboardCache();
  }

  if (!options.silent) {
    showToast(`${operation} completed`, 'success');
  }
  return response;
}

function renderDashboardCache() {
  elements.dashboardGrid.innerHTML = '';
  const entries = Object.entries(DASHBOARD_BINDINGS);
  entries.forEach(([operation, meta]) => {
    const article = document.createElement('article');
    article.className = 'dashboard-card';
    const data = state.dashboard[operation];
    article.innerHTML = `
      <h3>${meta.title}</h3>
      <pre>${data ? escapeHtml(JSON.stringify(data, null, 2)) : 'No cached data yet.'}</pre>
    `;
    elements.dashboardGrid.appendChild(article);
  });
}

function renderResult(operation, response) {
  const snapshot = {
    operation,
    timestamp: new Date().toISOString(),
    response,
  };
  localStorage.setItem(RESULT_CACHE_KEY, JSON.stringify(snapshot));
  elements.resultMeta.textContent = `${operation} • ${new Date(snapshot.timestamp).toLocaleString()}`;
  elements.resultOutput.textContent = JSON.stringify(response, null, 2);
}

function renderCachedResult() {
  const raw = localStorage.getItem(RESULT_CACHE_KEY);
  if (!raw) {
    return;
  }
  try {
    const cached = JSON.parse(raw);
    elements.resultMeta.textContent = `${cached.operation} • ${new Date(cached.timestamp).toLocaleString()} (cached)`;
    elements.resultOutput.textContent = JSON.stringify(cached.response, null, 2);
  } catch (error) {
    localStorage.removeItem(RESULT_CACHE_KEY);
  }
}

function persistUsedOperations() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.usedOperations]));
}

function updateConnectivity() {
  elements.connectivityStatus.textContent = navigator.onLine ? 'Online' : 'Offline';
}

async function request(url, payload = {}, silent = false) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'same-origin',
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Unknown request failure');
    }
    return data;
  } catch (error) {
    if (!silent) {
      showToast(error.message, 'error');
    }
    return null;
  }
}

async function fetchJson(url) {
  try {
    const response = await fetch(url, { credentials: 'same-origin' });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    showToast(error.message, 'error');
    return null;
  }
}

function showToast(message, kind = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${kind}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  window.setTimeout(() => toast.remove(), 2500);
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    return;
  }
  try {
    await navigator.serviceWorker.register('/sw.js');
  } catch (error) {
    console.warn('Service worker registration failed', error);
  }
}
"""

MANIFEST_JSON = """{
  \"name\": \"Splitwise PWA Console\",
  \"short_name\": \"Splitwise PWA\",
  \"start_url\": \"/\",
  \"display\": \"standalone\",
  \"background_color\": \"#eff6ff\",
  \"theme_color\": \"#2563eb\",
  \"description\": \"Mobile-first progressive web app for exercising every Splitwise SDK API call.\",
  \"icons\": [
    {
      \"src\": \"/icon.svg\",
      \"sizes\": \"any\",
      \"type\": \"image/svg+xml\",
      \"purpose\": \"any maskable\"
    }
  ]
}
"""

SERVICE_WORKER_JS = """const CACHE_NAME = 'splitwise-pwa-shell-v1';
const SHELL_ASSETS = ['/', '/styles.css', '/app.js', '/manifest.json', '/icon.svg'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const requestUrl = new URL(event.request.url);
  if (requestUrl.origin !== self.location.origin) {
    return;
  }

  if (requestUrl.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const networkFetch = fetch(event.request).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      }).catch(() => cached);
      return cached || networkFetch;
    })
  );
});
"""

ICON_SVG = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 128 128\" role=\"img\" aria-label=\"Splitwise PWA icon\">
  <rect width=\"128\" height=\"128\" rx=\"28\" fill=\"#2563eb\"/>
  <path
    d=\"M33 43c0-7.732 6.268-14 14-14h34c7.732 0 14 6.268 14 14v42c0 7.732-6.268 14-14 14H47c-7.732 0-14-6.268-14-14V43Z\"
    fill=\"#eff6ff\"
  />
  <path
    d=\"M46 49h36M46 64h24M46 79h18\"
    stroke=\"#2563eb\"
    stroke-width=\"8\"
    stroke-linecap=\"round\"
  />
</svg>
"""
