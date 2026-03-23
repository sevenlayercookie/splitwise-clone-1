INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="theme-color" content="#18b394">
    <meta name="description" content="Mobile-first Splitwise progressive web app powered by the Python SDK.">
    <title>Splitwise PWA Console</title>
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" href="/icon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    <div class="app-shell">
      <div class="phone-frame shell">
        <header class="app-bar">
          <button id="open-tools-button" class="icon-button" type="button" aria-label="Open tools">✕</button>
          <div class="app-bar-copy">
            <p class="eyebrow">Splitwise PWA Console</p>
            <h1>Add an expense</h1>
          </div>
          <button id="quick-expense-save" class="save-button" type="button">Save</button>
        </header>

        <section class="status-strip" aria-label="Application status">
          <article class="status-pill">
            <span class="status-label">Connectivity</span>
            <strong id="connectivity-status">Checking…</strong>
          </article>
          <article class="status-pill">
            <span class="status-label">Status</span>
            <strong id="credentials-status">Loading…</strong>
          </article>
          <button id="refresh-dashboard" class="ghost compact-button" type="button">Sync</button>
          <button id="install-button" class="ghost compact-button hidden" type="button">Install</button>
        </section>

        <section class="participant-panel" id="dashboard-panel">
          <div class="participant-copy">
            <p class="participant-label">With you and:</p>
            <small id="session-summary">Reading configuration…</small>
          </div>
          <div id="dashboard-actions" class="participant-chips" aria-label="Expense participants"></div>
        </section>

        <main class="layout">
          <section class="composer-card panel">
            <form id="quick-expense-form" class="expense-form">
              <label class="input-row">
                <span class="input-icon">🧾</span>
                <input id="quick-description" name="quick_description" autocomplete="off" placeholder="Enter a description">
              </label>
              <label class="input-row amount-row">
                <span class="input-icon amount-icon">$</span>
                <input id="quick-cost" name="quick_cost" inputmode="decimal" autocomplete="off" placeholder="0.00">
              </label>
              <button id="quick-split-button" class="split-pill" type="button">Paid by you and split equally</button>
              <label id="quick-note-row" class="note-row hidden">
                Note
                <textarea id="quick-note-input" name="quick_note" rows="3" placeholder="Add a note or receipt context"></textarea>
              </label>
            </form>
          </section>

          <section class="toolbar-card panel" aria-label="Expense details">
            <button id="quick-date-button" class="toolbar-item toolbar-date" type="button">Today</button>
            <button id="quick-group-button" class="toolbar-item toolbar-group" type="button">No group</button>
            <button id="quick-receipt-button" class="toolbar-item toolbar-icon" type="button" aria-label="Receipt">📷</button>
            <button id="quick-note-button" class="toolbar-item toolbar-icon" type="button" aria-label="Notes">✎</button>
          </section>

          <section class="panel" id="result-panel">
            <div class="panel-heading compact-heading">
              <div>
                <h2>Latest response</h2>
                <p id="result-meta" class="result-meta">No API call made yet.</p>
              </div>
            </div>
            <pre id="result-output" class="result-output">Awaiting input…</pre>
          </section>

          <section class="panel snapshot-panel">
            <div class="panel-heading compact-heading">
              <div>
                <h2>Live snapshot</h2>
                <p>Recent people, groups, expenses, and reference data from the SDK.</p>
              </div>
            </div>
            <div class="dashboard-grid" id="dashboard-grid"></div>
          </section>

          <details class="panel developer-panel" id="credentials-panel">
            <summary class="developer-summary">
              <div>
                <h2>Session credentials</h2>
                <p>Store consumer keys, API key, and tokens for this browser tab.</p>
              </div>
              <span class="chevron">⌄</span>
            </summary>
            <div class="developer-content">
              <button id="clear-session" class="ghost" type="button">Clear session</button>
              <form id="session-form" class="form-stack">
                <label>
                  Consumer key
                  <input name="consumer_key" autocomplete="off" placeholder="Splitwise consumer key">
                </label>
                <label>
                  Consumer secret
                  <input name="consumer_secret" autocomplete="off" placeholder="Splitwise consumer secret">
                </label>
                <label>
                  API key
                  <input name="api_key" autocomplete="off" placeholder="Optional bearer API key">
                </label>
                <label>
                  OAuth 1 access token JSON
                  <textarea name="access_token" rows="3" placeholder='{"oauth_token":"...","oauth_token_secret":"..."}'></textarea>
                </label>
                <label>
                  OAuth 2 access token JSON
                  <textarea name="oauth2_access_token" rows="3" placeholder='{"access_token":"...","token_type":"bearer"}'></textarea>
                </label>
                <button type="submit">Save session credentials</button>
              </form>
            </div>
          </details>

          <details class="panel developer-panel" id="coverage-panel">
            <summary class="developer-summary">
              <div>
                <h2>SDK coverage</h2>
                <p><strong id="coverage-status">0/0</strong> methods exercised in this browser.</p>
              </div>
              <span class="chevron">⌄</span>
            </summary>
            <div id="coverage-board" class="coverage-board developer-content"></div>
          </details>

          <details class="panel developer-panel" id="lab-panel">
            <summary class="developer-summary">
              <div>
                <h2>Developer tools</h2>
                <p>Run every public SDK operation from the same mobile shell.</p>
              </div>
              <span class="chevron">⌄</span>
            </summary>
            <div id="operation-groups" class="operation-groups developer-content"></div>
          </details>
        </main>
      </div>
    </div>
    <script src="/app.js" defer></script>
  </body>
</html>"""

STYLES_CSS = """:root {
  color-scheme: light;
  --bg: #f3f4f6;
  --surface: #ffffff;
  --surface-soft: #fbfbfc;
  --border: #dde1e6;
  --border-strong: #cfd4dc;
  --text: #2d3138;
  --muted: #8a97a8;
  --accent: #18b394;
  --accent-strong: #12957a;
  --orange: #ff6b2c;
  --purple: #a86ef7;
  --teal: #20c8ba;
  --shadow: 0 14px 34px rgba(64, 71, 86, 0.12);
  --radius: 1.35rem;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  min-height: 100%;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  color: var(--text);
}

body {
  padding: 0;
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  border: none;
  border-radius: 1rem;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}

button:hover,
button:focus-visible {
  background: var(--accent-strong);
}

button.ghost {
  background: #eef2f5;
  color: var(--text);
}

button.hidden,
.hidden {
  display: none !important;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 1rem 0.75rem 2rem;
}

.phone-frame {
  width: min(100%, 27rem);
  background: var(--surface-soft);
  border: 1px solid rgba(207, 212, 220, 0.75);
  border-radius: 2rem;
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.14);
  overflow: hidden;
}

.shell {
  padding: 0;
}

.app-bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.9rem;
  padding: 1.25rem 1.1rem 0.65rem;
  background: var(--surface);
}

.icon-button {
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 50%;
  background: transparent;
  color: var(--text);
  font-size: 2rem;
  line-height: 1;
  padding: 0;
}

.icon-button:hover,
.icon-button:focus-visible {
  background: #edf1f5;
}

.app-bar-copy {
  text-align: center;
}

.eyebrow {
  margin: 0 0 0.15rem;
  font-size: 0.75rem;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.app-bar h1,
.panel h2,
.developer-summary h2 {
  margin: 0;
}

.app-bar h1 {
  font-size: 1.05rem;
  font-weight: 600;
}

.save-button {
  background: transparent;
  color: var(--accent);
  font-weight: 700;
  padding: 0.35rem 0.5rem;
}

.save-button:hover,
.save-button:focus-visible {
  background: rgba(24, 179, 148, 0.12);
}

.status-strip {
  display: none;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1rem 0.85rem;
  overflow-x: auto;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.status-pill {
  min-width: 7rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
}

.status-label {
  display: block;
  font-size: 0.7rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.compact-button {
  padding: 0.7rem 0.9rem;
  white-space: nowrap;
}

.participant-panel {
  padding: 1rem 1rem 0.9rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.participant-copy {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.participant-label {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text);
}

.participant-copy small,
.panel-heading p,
label,
.result-meta,
.hint,
.developer-summary p {
  color: var(--muted);
}

.participant-chips {
  display: flex;
  gap: 0.65rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.participant-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  min-width: max-content;
  padding: 0.45rem 0.85rem 0.45rem 0.45rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
  color: var(--text);
  box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
}

.participant-chip.selected {
  border-color: rgba(24, 179, 148, 0.45);
  box-shadow: 0 10px 18px rgba(24, 179, 148, 0.16);
}

.participant-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffd4c5, #f0b8e6);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #5b4650;
}

.layout {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
}

.panel,
.operation-card,
.dashboard-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.composer-card,
.toolbar-card,
.snapshot-panel,
#result-panel,
.developer-content,
.dashboard-card {
  padding: 1rem;
}

.expense-form {
  display: grid;
  gap: 1rem;
}

.input-row {
  display: grid;
  grid-template-columns: 4.2rem 1fr;
  align-items: center;
  gap: 0.9rem;
}

.input-icon {
  width: 4rem;
  height: 4rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  border: 1px solid var(--border);
  background: #fff;
  font-size: 1.8rem;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
}

.amount-icon {
  font-size: 2.3rem;
}

input,
textarea,
select {
  width: 100%;
  border: none;
  border-bottom: 3px solid #d6e3df;
  border-radius: 0;
  background: transparent;
  color: var(--text);
  padding: 0.5rem 0;
}

.amount-row input,
.input-row input {
  font-size: 1.15rem;
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-bottom-color: var(--accent);
}

input::placeholder,
textarea::placeholder {
  color: #c3cedb;
}

.split-pill {
  justify-self: center;
  padding: 0.85rem 1.4rem;
  background: #fff;
  color: var(--text);
  border: 1px solid var(--border);
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
}

.split-pill:hover,
.split-pill:focus-visible {
  background: #f9fbfd;
}

.note-row {
  display: grid;
  gap: 0.45rem;
}

.note-row textarea {
  min-height: 5rem;
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: #f9fbfd;
  padding: 0.85rem 1rem;
}

.toolbar-card {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr auto auto;
  gap: 0.65rem;
  align-items: center;
  padding-top: 0.8rem;
  padding-bottom: 0.8rem;
}

.toolbar-item {
  background: #fff;
  color: var(--text);
  border: 1px solid var(--border);
  min-height: 3.3rem;
  padding: 0.75rem 0.9rem;
}

.toolbar-date { color: #226ca7; }
.toolbar-group { color: var(--orange); }
.toolbar-icon:nth-of-type(3) { color: var(--purple); }
.toolbar-icon:nth-of-type(4) { color: var(--teal); }

.toolbar-icon {
  width: 3.3rem;
  padding: 0;
  font-size: 1.35rem;
}

.panel-heading,
.compact-heading,
.developer-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.panel-heading p,
.developer-summary p {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
}

.result-output {
  margin: 0;
  padding: 0.9rem;
  border-radius: 1rem;
  min-height: 10rem;
  background: #f7f9fb;
  color: #384152;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.dashboard-grid {
  display: grid;
  gap: 0.8rem;
}

.dashboard-card h3 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}

.dashboard-card p,
.dashboard-card ul,
.dashboard-card pre {
  margin: 0;
  color: var(--muted);
}

.dashboard-card ul {
  padding-left: 1rem;
}

.dashboard-card pre {
  white-space: pre-wrap;
  word-break: break-word;
}

.coverage-board,
.form-stack,
.operation-form,
.operation-groups {
  display: grid;
  gap: 0.75rem;
}

.coverage-board {
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
}

.coverage-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 0.75rem;
  border-radius: 999px;
  background: #edf1f5;
  color: #546173;
  font-size: 0.8rem;
  font-weight: 600;
}

.coverage-chip.used {
  background: rgba(24, 179, 148, 0.16);
  color: var(--accent-strong);
}

.developer-panel {
  padding: 0;
  overflow: hidden;
}

.developer-summary {
  list-style: none;
  cursor: pointer;
  padding: 1rem;
}

.developer-summary::-webkit-details-marker {
  display: none;
}

.chevron {
  font-size: 1.25rem;
  color: var(--muted);
}

.developer-panel[open] .chevron {
  transform: rotate(180deg);
}

.developer-content {
  border-top: 1px solid var(--border);
}

.form-stack label,
.operation-form label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.92rem;
}

.form-stack input,
.form-stack textarea,
.operation-form input,
.operation-form textarea,
.operation-form select {
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: #f8fafc;
  padding: 0.9rem 1rem;
}

.form-stack textarea,
.operation-form textarea {
  min-height: 7rem;
  resize: vertical;
}

.operation-group {
  display: grid;
  gap: 0.75rem;
}

.operation-card {
  overflow: hidden;
}

.operation-card summary {
  list-style: none;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
}

.operation-card summary::-webkit-details-marker {
  display: none;
}

.operation-card .content {
  padding: 0 1rem 1rem;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: #eef2f5;
  color: #59667a;
  font-size: 0.78rem;
  font-weight: 700;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 1rem;
  transform: translateX(-50%);
  padding: 0.8rem 1rem;
  border-radius: 999px;
  color: #fff;
  background: #343b46;
  box-shadow: var(--shadow);
  z-index: 30;
}

.toast.success { background: var(--accent-strong); }
.toast.error { background: #c73c52; }

@media (min-width: 700px) {
  .status-strip {
    display: flex;
  }

  .phone-frame {
    width: min(100%, 68rem);
  }

  .layout {
    grid-template-columns: 1.15fr 0.85fr;
    align-items: start;
  }

  .composer-card,
  .toolbar-card,
  #result-panel,
  .snapshot-panel,
  #credentials-panel,
  #coverage-panel,
  #lab-panel {
    grid-column: span 2;
  }

  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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
  hydrated: false,
  composer: {
    friendId: null,
    groupId: 0,
    date: new Date().toISOString().slice(0, 10),
    noteVisible: false,
  },
};

const elements = {};

document.addEventListener('DOMContentLoaded', () => {
  bindElements();
  wireBaseInteractions();
  renderOperationGroups();
  renderCachedResult();
  renderCoverage();
  renderDashboardCache();
  renderParticipantChips();
  renderComposerState();
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
  elements.quickExpenseForm = document.getElementById('quick-expense-form');
  elements.quickExpenseSave = document.getElementById('quick-expense-save');
  elements.quickDescription = document.getElementById('quick-description');
  elements.quickCost = document.getElementById('quick-cost');
  elements.quickSplitButton = document.getElementById('quick-split-button');
  elements.quickDateButton = document.getElementById('quick-date-button');
  elements.quickGroupButton = document.getElementById('quick-group-button');
  elements.quickReceiptButton = document.getElementById('quick-receipt-button');
  elements.quickNoteButton = document.getElementById('quick-note-button');
  elements.quickNoteRow = document.getElementById('quick-note-row');
  elements.quickNoteInput = document.getElementById('quick-note-input');
  elements.openToolsButton = document.getElementById('open-tools-button');
  elements.credentialsPanel = document.getElementById('credentials-panel');
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

  elements.openToolsButton.addEventListener('click', () => {
    elements.credentialsPanel.open = !elements.credentialsPanel.open;
    elements.credentialsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
      state.hydrated = false;
      await loadConfig();
    }
  });

  elements.clearSession.addEventListener('click', async () => {
    const response = await request('/api/session/clear', {});
    if (response) {
      state.usedOperations.clear();
      persistUsedOperations();
      state.dashboard = {};
      state.hydrated = false;
      state.composer.friendId = null;
      state.composer.groupId = 0;
      localStorage.removeItem(DASHBOARD_CACHE_KEY);
      showToast('Session cleared', 'success');
      renderCoverage();
      renderDashboardCache();
      renderParticipantChips();
      renderComposerState();
      await loadConfig();
    }
  });

  elements.refreshDashboard.addEventListener('click', async () => {
    await hydrateWorkspace(true);
    showToast('Dashboard refreshed', 'success');
  });

  elements.quickExpenseForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await saveQuickExpense();
  });

  elements.quickExpenseSave.addEventListener('click', async () => {
    await saveQuickExpense();
  });

  elements.quickSplitButton.addEventListener('click', () => {
    showToast('Equal split is enabled', 'success');
  });

  elements.quickDateButton.addEventListener('click', () => {
    state.composer.date = new Date().toISOString().slice(0, 10);
    renderComposerState();
    showToast('Expense date set to today', 'success');
  });

  elements.quickGroupButton.addEventListener('click', () => {
    cycleComposerGroup();
  });

  elements.quickNoteButton.addEventListener('click', () => {
    state.composer.noteVisible = !state.composer.noteVisible;
    renderComposerState();
    if (state.composer.noteVisible) {
      elements.quickNoteInput.focus();
    }
  });

  elements.quickReceiptButton.addEventListener('click', () => {
    elements.credentialsPanel.open = true;
    document.getElementById('lab-panel').open = true;
    document.getElementById('lab-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('Advanced receipt workflows are available below', 'success');
  });

  elements.dashboardActions.addEventListener('click', (event) => {
    const button = event.target.closest('[data-friend-id]');
    if (!button) {
      return;
    }
    state.composer.friendId = Number(button.dataset.friendId);
    renderParticipantChips();
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
  renderDashboardCache();
  renderParticipantChips();
  renderComposerState();
  if (config.configured && !state.hydrated) {
    await hydrateWorkspace(false);
  }
}

async function hydrateWorkspace(forceRefresh) {
  if (!state.config || !state.config.configured) {
    return;
  }
  if (state.hydrated && !forceRefresh) {
    return;
  }
  state.hydrated = true;
  for (const [, operation] of QUICK_ACTIONS) {
    await invokeOperation(operation, {}, { silent: true, preserveResult: true, dashboardOnly: true });
  }
  renderParticipantChips();
  renderComposerState();
  renderDashboardCache();
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
    : 'Save credentials below to create expenses from this device.';
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
    wrapper.innerHTML = `<div><h3>${group.title}</h3><p class="hint">${group.description}</p></div>`;

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

async function saveQuickExpense() {
  if (!state.config || !state.config.configured) {
    showToast('Save credentials before creating expenses', 'error');
    elements.credentialsPanel.open = true;
    return;
  }

  const description = elements.quickDescription.value.trim();
  const cost = elements.quickCost.value.trim();
  if (!description || !cost) {
    showToast('Description and amount are required', 'error');
    return;
  }

  const currentUser = state.dashboard.getCurrentUser;
  const participants = state.dashboard.getFriends || [];
  const selectedFriend = participants.find((friend) => friend.id === state.composer.friendId) || participants[0];
  if (!currentUser || !selectedFriend) {
    await hydrateWorkspace(true);
  }
  const owner = state.dashboard.getCurrentUser;
  const companion = (state.dashboard.getFriends || []).find((friend) => friend.id === state.composer.friendId) || (state.dashboard.getFriends || [])[0];
  if (!owner || !companion) {
    showToast('Load at least one friend before creating an expense', 'error');
    return;
  }

  const half = splitAmount(cost, 2);
  const expense = {
    description,
    cost,
    currency_code: defaultCurrencyCode(),
    split_equally: true,
    details: elements.quickNoteInput.value.trim() || undefined,
    date: `${state.composer.date}T12:00:00Z`,
    users: [
      { id: owner.id, paid_share: formatMoney(cost), owed_share: half },
      { id: companion.id, paid_share: '0.00', owed_share: half },
    ],
  };
  if (state.composer.groupId) {
    expense.group_id = state.composer.groupId;
  }

  const response = await invokeOperation('createExpense', { expense });
  if (!response) {
    return;
  }

  const createdExpense = response.data && response.data.expense ? response.data.expense : null;
  if (createdExpense) {
    const existingExpenses = Array.isArray(state.dashboard.getExpenses) ? state.dashboard.getExpenses : [];
    state.dashboard.getExpenses = [createdExpense, ...existingExpenses].slice(0, 6);
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
    renderDashboardCache();
  }

  elements.quickDescription.value = '';
  elements.quickCost.value = '';
  elements.quickNoteInput.value = '';
  state.composer.noteVisible = false;
  renderComposerState();
}

async function invokeOperation(operation, payload = {}, options = {}) {
  const response = await request(`/api/operations/${operation}`, payload, options.silent);
  if (!response) {
    return null;
  }

  state.usedOperations.add(operation);
  persistUsedOperations();
  renderCoverage();

  if (!options.preserveResult) {
    renderResult(operation, response);
  }

  if (DASHBOARD_BINDINGS[operation]) {
    state.dashboard[operation] = response.data;
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
    renderDashboardCache();
    if (operation === 'getFriends') {
      renderParticipantChips();
    }
    if (operation === 'getGroups') {
      renderComposerState();
    }
  }

  if (!options.silent) {
    showToast(`${operation} completed`, 'success');
  }
  return response;
}

function renderParticipantChips() {
  elements.dashboardActions.innerHTML = '';
  const friends = Array.isArray(state.dashboard.getFriends) ? state.dashboard.getFriends : [];
  if (!friends.length) {
    const placeholder = document.createElement('button');
    placeholder.type = 'button';
    placeholder.className = 'participant-chip';
    placeholder.textContent = 'Load friends to start';
    placeholder.addEventListener('click', async () => {
      await hydrateWorkspace(true);
    });
    elements.dashboardActions.appendChild(placeholder);
    return;
  }

  if (!state.composer.friendId || !friends.some((friend) => friend.id === state.composer.friendId)) {
    state.composer.friendId = friends[0].id;
  }

  friends.slice(0, 6).forEach((friend) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `participant-chip${state.composer.friendId === friend.id ? ' selected' : ''}`;
    button.dataset.friendId = String(friend.id);
    const initials = [friend.first_name, friend.last_name].filter(Boolean).map((part) => part[0]).join('').slice(0, 2) || '?';
    button.innerHTML = `
      <span class="participant-avatar">${escapeHtml(initials.toUpperCase())}</span>
      <span>${escapeHtml(friend.first_name)}${friend.last_name ? ` ${escapeHtml(friend.last_name)}` : ''}</span>
    `;
    elements.dashboardActions.appendChild(button);
  });
}

function renderComposerState() {
  elements.quickNoteRow.classList.toggle('hidden', !state.composer.noteVisible);
  const groups = Array.isArray(state.dashboard.getGroups) ? state.dashboard.getGroups.filter((group) => group.id !== 0) : [];
  const selectedGroup = groups.find((group) => group.id === state.composer.groupId);
  elements.quickGroupButton.textContent = selectedGroup ? selectedGroup.name : 'No group';
  const today = new Date().toISOString().slice(0, 10);
  elements.quickDateButton.textContent = state.composer.date === today ? 'Today' : state.composer.date;
  const friend = (state.dashboard.getFriends || []).find((item) => item.id === state.composer.friendId);
  if (friend) {
    elements.quickSplitButton.textContent = `Paid by you and split equally with ${friend.first_name}`;
  }
}

function cycleComposerGroup() {
  const groups = Array.isArray(state.dashboard.getGroups) ? state.dashboard.getGroups.filter((group) => group.id !== 0) : [];
  if (!groups.length) {
    showToast('No groups available yet', 'error');
    return;
  }
  const currentIndex = groups.findIndex((group) => group.id === state.composer.groupId);
  if (currentIndex === -1) {
    state.composer.groupId = groups[0].id;
  } else if (currentIndex === groups.length - 1) {
    state.composer.groupId = 0;
  } else {
    state.composer.groupId = groups[currentIndex + 1].id;
  }
  renderComposerState();
}

function renderDashboardCache() {
  elements.dashboardGrid.innerHTML = '';
  Object.entries(DASHBOARD_BINDINGS).forEach(([operation, meta]) => {
    const article = document.createElement('article');
    article.className = 'dashboard-card';
    article.innerHTML = `<h3>${meta.title}</h3>${formatDashboardCard(operation, state.dashboard[operation])}`;
    elements.dashboardGrid.appendChild(article);
  });
}

function formatDashboardCard(operation, data) {
  if (!data) {
    return '<p>No cached data yet.</p>';
  }
  if (operation === 'getCurrentUser') {
    return `<p>${escapeHtml(data.first_name || 'Unknown user')} • default currency ${escapeHtml(data.default_currency || defaultCurrencyCode())}</p>`;
  }
  if (operation === 'getFriends') {
    if (!Array.isArray(data) || !data.length) {
      return '<p>No friends available.</p>';
    }
    return `<ul>${data.slice(0, 3).map((friend) => `<li>${escapeHtml(friend.first_name)}${friend.last_name ? ` ${escapeHtml(friend.last_name)}` : ''}</li>`).join('')}</ul>`;
  }
  if (operation === 'getGroups') {
    if (!Array.isArray(data) || !data.length) {
      return '<p>No groups available.</p>';
    }
    return `<ul>${data.slice(0, 3).map((group) => `<li>${escapeHtml(group.name)}</li>`).join('')}</ul>`;
  }
  if (operation === 'getExpenses') {
    if (!Array.isArray(data) || !data.length) {
      return '<p>No expenses yet.</p>';
    }
    return `<ul>${data.slice(0, 3).map((expense) => `<li>${escapeHtml(expense.description || 'Expense')} · ${escapeHtml(expense.cost || '0.00')}</li>`).join('')}</ul>`;
  }
  if (operation === 'getNotifications') {
    if (!Array.isArray(data) || !data.length) {
      return '<p>No recent notifications.</p>';
    }
    return `<p>${escapeHtml(data[0].content || 'No activity yet.')}</p>`;
  }
  if (operation === 'getCurrencies') {
    return `<p>${Array.isArray(data) ? data.slice(0, 3).map((currency) => escapeHtml(currency.currency_code || currency.code || '')).join(', ') : 'No currencies loaded.'}</p>`;
  }
  if (operation === 'getCategories') {
    return `<p>${Array.isArray(data) && data.length ? escapeHtml(data[0].name) : 'No categories loaded.'}</p>`;
  }
  return `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
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

function defaultCurrencyCode() {
  const currentUser = state.dashboard.getCurrentUser;
  if (currentUser && currentUser.default_currency) {
    return currentUser.default_currency;
  }
  const currencies = state.dashboard.getCurrencies;
  if (Array.isArray(currencies) && currencies[0]) {
    return currencies[0].currency_code || currencies[0].code || 'USD';
  }
  return 'USD';
}

function splitAmount(value, count) {
  const amount = Number.parseFloat(value || '0');
  if (!Number.isFinite(amount) || count <= 0) {
    return '0.00';
  }
  return formatMoney((amount / count).toFixed(2));
}

function formatMoney(value) {
  const number = Number.parseFloat(value || '0');
  if (!Number.isFinite(number)) {
    return '0.00';
  }
  return number.toFixed(2);
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
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
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
