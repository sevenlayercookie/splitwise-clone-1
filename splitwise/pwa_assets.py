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
          <button id="open-tools-button" class="icon-button" type="button" aria-label="Open tools">☰</button>
          <div class="app-bar-copy">
            <p class="eyebrow">Splitwise PWA Console</p>
            <h1 id="screen-title">Add an expense</h1>
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

        <section class="panel auth-panel" id="auth-panel">
          <div class="panel-heading compact-heading">
            <div>
              <h2>Local account</h2>
              <p>Create an account or sign in to use this app without Splitwise credentials.</p>
            </div>
          </div>
          <div id="auth-logged-out" class="auth-stack">
            <form id="register-form" class="form-stack auth-form">
              <h3>Create account</h3>
              <label>
                First name
                <input name="first_name" autocomplete="given-name" placeholder="Alex" required>
              </label>
              <label>
                Last name
                <input name="last_name" autocomplete="family-name" placeholder="Example">
              </label>
              <label>
                Email
                <input name="email" type="email" autocomplete="email" placeholder="alex@example.com" required>
              </label>
              <label>
                Password
                <input name="password" type="password" autocomplete="new-password" placeholder="At least 8 characters" required>
              </label>
              <button type="submit">Create local account</button>
            </form>
            <form id="login-form" class="form-stack auth-form">
              <h3>Sign in</h3>
              <label>
                Email
                <input name="email" type="email" autocomplete="email" placeholder="alex@example.com" required>
              </label>
              <label>
                Password
                <input name="password" type="password" autocomplete="current-password" placeholder="Your password" required>
              </label>
              <button type="submit">Sign in</button>
            </form>
          </div>
          <div id="auth-logged-in" class="auth-state hidden">
            <p id="auth-user-copy" class="auth-user-copy">Signed in.</p>
            <button id="logout-button" class="ghost" type="button">Log out</button>
          </div>
        </section>

        <section class="participant-panel" id="dashboard-panel">
          <div class="participant-copy">
            <p id="participant-label" class="participant-label">With you and:</p>
            <small id="session-summary">Reading configuration…</small>
          </div>
          <div id="dashboard-actions" class="participant-chips" aria-label="Primary mobile context"></div>
        </section>

        <nav class="screen-switcher" aria-label="Mobile screens">
          <button class="screen-tab" type="button" data-screen="add">Add</button>
          <button class="screen-tab" type="button" data-screen="group">Group</button>
          <button class="screen-tab" type="button" data-screen="activity">Activity</button>
          <button class="screen-tab" type="button" data-screen="balances">Balances</button>
        </nav>

        <main class="layout">
          <section class="screen-panel" data-screen="add">
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
                <div class="composer-grid">
                  <label>
                    Paid by
                    <select id="quick-paid-by" name="quick_paid_by">
                      <option value="self">You</option>
                      <option value="friend">Selected friend</option>
                    </select>
                  </label>
                  <label>
                    Split
                    <select id="quick-split-mode" name="quick_split_mode">
                      <option value="equal">Split equally</option>
                      <option value="custom">Custom split</option>
                    </select>
                  </label>
                </div>
                <div id="quick-custom-split-row" class="composer-grid hidden">
                  <label>
                    <span id="quick-your-share-label">Your share</span>
                    <input id="quick-your-share" name="quick_your_share" inputmode="decimal" autocomplete="off" placeholder="0.00">
                  </label>
                  <label>
                    <span id="quick-friend-share-label">Friend share</span>
                    <input id="quick-friend-share" name="quick_friend_share" inputmode="decimal" autocomplete="off" placeholder="0.00">
                  </label>
                </div>
                <label id="quick-note-row" class="note-row hidden">
                  Note
                  <textarea id="quick-note-input" name="quick_note" rows="3" placeholder="Add a note or receipt context"></textarea>
                </label>
                <div class="composer-grid">
                  <label>
                    Repeat
                    <select id="quick-repeat-interval" name="quick_repeat_interval">
                      <option value="never">Never</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                  </label>
                  <label class="toggle-row">
                    <input id="quick-email-reminder" name="quick_email_reminder" type="checkbox">
                    <span>Email reminder</span>
                  </label>
                </div>
                <label id="quick-reminder-days-row" class="note-row hidden">
                  Remind me this many days before
                  <input id="quick-reminder-days" name="quick_reminder_days" type="number" min="0" step="1" placeholder="1">
                </label>
              </form>
            </section>

            <section class="toolbar-card panel" aria-label="Expense details">
              <button id="quick-date-button" class="toolbar-item toolbar-date" type="button">Today</button>
              <button id="quick-group-button" class="toolbar-item toolbar-group" type="button">No group</button>
              <button id="quick-receipt-button" class="toolbar-item toolbar-icon toolbar-receipt" type="button" aria-label="Receipt">📷</button>
              <button id="quick-note-button" class="toolbar-item toolbar-icon toolbar-note" type="button" aria-label="Notes">✎</button>
            </section>
          </section>

          <section class="screen-panel" data-screen="group">
            <section class="panel screen-card group-hero-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2 id="group-screen-title">Group screen</h2>
                  <p id="group-screen-summary">Choose a group to inspect balances, members, and recent expenses.</p>
                </div>
              </div>
              <div id="group-balance-summary" class="summary-pills"></div>
              <form id="update-group-form" class="form-stack compact-form">
                <label>
                  Group name
                  <input id="update-group-name" name="name" autocomplete="off" placeholder="Selected group name">
                </label>
                <label>
                  Notes
                  <input id="update-group-whiteboard" name="whiteboard" autocomplete="off" placeholder="Update the group summary">
                </label>
                <div class="action-row">
                  <button type="submit">Save group</button>
                  <button id="delete-group-button" class="ghost danger" type="button">Delete group</button>
                </div>
              </form>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Create group</h2>
                  <p>Start a new group and add existing friends immediately.</p>
                </div>
              </div>
              <form id="create-group-form" class="form-stack compact-form">
                <label>
                  Group name
                  <input name="name" autocomplete="off" placeholder="Weekend trip" required>
                </label>
                <label>
                  Notes
                  <input name="whiteboard" autocomplete="off" placeholder="Snacks, tickets, gas">
                </label>
                <div>
                  <strong class="selection-label">Friends to include</strong>
                  <div id="create-group-members" class="selection-list"></div>
                </div>
                <button type="submit">Create group</button>
              </form>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Members</h2>
                  <p>Balances mirror the local backend’s Splitwise-style payloads.</p>
                </div>
              </div>
              <div id="group-member-list" class="collection-list"></div>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Recent group expenses</h2>
                  <p>Latest activity for the selected group.</p>
                </div>
              </div>
              <div id="group-expense-list" class="collection-list"></div>
            </section>
          </section>

          <section class="screen-panel" data-screen="activity">
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Recent activity</h2>
                  <p>Notifications and expense updates from the local backend.</p>
                </div>
              </div>
              <div id="activity-stats" class="summary-pills"></div>
              <div id="activity-feed" class="activity-feed"></div>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Expense details</h2>
                  <p>Inspect comments, edit the expense in the composer, or delete it.</p>
                </div>
              </div>
              <div id="expense-detail-card" class="detail-card"></div>
              <div class="action-row">
                <button id="edit-expense-button" class="ghost" type="button">Edit selected expense</button>
                <button id="delete-expense-button" class="ghost danger" type="button">Delete selected expense</button>
              </div>
              <div id="expense-comment-list" class="collection-list"></div>
              <form id="expense-comment-form" class="form-stack compact-form">
                <label>
                  Add comment
                  <input id="expense-comment-input" name="content" autocomplete="off" placeholder="Add a note for this expense">
                </label>
                <button type="submit">Post comment</button>
              </form>
            </section>
          </section>

          <section class="screen-panel" data-screen="balances">
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Send friend request</h2>
                  <p>Invite an existing local account by email and let them accept it.</p>
                </div>
              </div>
              <form id="friend-form" class="form-stack compact-form">
                <label>
                  Friend email
                  <input name="email" type="email" autocomplete="email" placeholder="friend@example.com" required>
                </label>
                <button type="submit">Send request</button>
              </form>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Pending requests</h2>
                  <p>Accept incoming requests and track requests you already sent.</p>
                </div>
              </div>
              <div id="incoming-request-list" class="collection-list"></div>
              <div id="outgoing-request-list" class="collection-list"></div>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Friend balances</h2>
                  <p>Outstanding balances and per-group context for each friend.</p>
                </div>
              </div>
              <div id="balance-list" class="collection-list"></div>
            </section>
            <section class="panel screen-card">
              <div class="panel-heading compact-heading">
                <div>
                  <h2>Profile</h2>
                  <p>Update your local account details without leaving the app.</p>
                </div>
              </div>
              <form id="profile-form" class="form-stack compact-form">
                <label>
                  First name
                  <input id="profile-first-name" name="first_name" autocomplete="given-name" placeholder="Alex" required>
                </label>
                <label>
                  Last name
                  <input id="profile-last-name" name="last_name" autocomplete="family-name" placeholder="Example">
                </label>
                <label>
                  Email
                  <input id="profile-email" name="email" type="email" autocomplete="email" placeholder="alex@example.com" required>
                </label>
                <button type="submit">Save profile</button>
              </form>
              <form id="password-form" class="form-stack compact-form">
                <label>
                  Current password
                  <input name="current_password" type="password" autocomplete="current-password" placeholder="Current password" required>
                </label>
                <label>
                  New password
                  <input name="new_password" type="password" autocomplete="new-password" placeholder="New password" required>
                </label>
                <button type="submit">Update password</button>
              </form>
            </section>
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
                <h2>Advanced session credentials</h2>
                <p>Optional developer tools for manual SDK sessions and token testing.</p>
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
  --text: #2d3138;
  --muted: #8a97a8;
  --accent: #18b394;
  --accent-strong: #12957a;
  --orange: #ff6b2c;
  --purple: #a86ef7;
  --teal: #20c8ba;
  --blue: #226ca7;
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
  font-size: 1.45rem;
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

.status-pill,
.summary-pill {
  min-width: 7rem;
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
}

.status-label,
.summary-label,
.row-meta,
.activity-meta {
  display: block;
  font-size: 0.72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.compact-button {
  padding: 0.7rem 0.9rem;
  white-space: nowrap;
}

.participant-panel,
.screen-switcher {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.participant-panel {
  padding: 1rem 1rem 0.9rem;
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
.developer-summary p,
.empty-copy,
.muted-copy {
  color: var(--muted);
}

.participant-chips,
.screen-switcher {
  display: flex;
  gap: 0.65rem;
  overflow-x: auto;
}

.participant-chips {
  padding-bottom: 0.25rem;
}

.screen-switcher {
  padding: 0.8rem 1rem;
}

.participant-chip,
.screen-tab {
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

.screen-tab {
  padding: 0.55rem 0.95rem;
  color: var(--muted);
}

.participant-chip.selected,
.screen-tab.active {
  border-color: rgba(24, 179, 148, 0.45);
  box-shadow: 0 10px 18px rgba(24, 179, 148, 0.16);
  color: var(--accent-strong);
}

.participant-avatar,
.row-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffd4c5, #f0b8e6);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #5b4650;
  flex: none;
}

.layout {
  display: grid;
  gap: 0.95rem;
  padding: 1rem;
}

.screen-panel {
  display: none;
  gap: 0.95rem;
}

.screen-panel.active {
  display: grid;
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
.dashboard-card,
.screen-card {
  padding: 1rem;
}

.expense-form,
.collection-list,
.activity-feed,
.balance-list {
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

.toolbar-date { color: var(--blue); }
.toolbar-group { color: var(--orange); }
.toolbar-receipt { color: var(--purple); }
.toolbar-note { color: var(--teal); }

.toolbar-icon {
  width: 3.3rem;
  padding: 0;
  font-size: 1.35rem;
}

.panel-heading,
.compact-heading,
.developer-summary,
.row-main,
.timeline-head {
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

.summary-pills {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.summary-value,
.amount-copy strong {
  display: block;
  font-size: 1rem;
}

.collection-list {
  margin-top: 0.25rem;
}

.list-row,
.activity-item {
  display: grid;
  gap: 0.35rem;
  padding: 0.9rem 0;
  border-bottom: 1px solid #edf1f5;
}

.list-row:last-child,
.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.row-main {
  align-items: flex-start;
}

.row-copy {
  flex: 1;
}

.row-copy strong,
.activity-title {
  display: block;
  font-size: 0.98rem;
}

.row-copy p,
.activity-body,
.dashboard-card p,
.dashboard-card ul,
.dashboard-card pre,
.dashboard-card li,
.empty-copy,
.muted-copy {
  margin: 0.2rem 0 0;
}

.amount-positive { color: var(--accent-strong); }
.amount-negative { color: #c73c52; }
.amount-neutral { color: var(--muted); }

.amount-copy {
  text-align: right;
}

.inline-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.45rem;
}

.mini-badge,
.timeline-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  background: #eef2f5;
  color: #59667a;
  font-size: 0.75rem;
  font-weight: 700;
}

.timeline-badge.expense { color: var(--orange); }
.timeline-badge.notification { color: var(--purple); }

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

.auth-stack {
  display: grid;
  gap: 0.9rem;
}

.composer-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  align-items: end;
}

.auth-form h3 {
  margin: 0;
  font-size: 1rem;
}

.auth-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
}

.auth-user-copy {
  margin: 0;
  color: var(--muted);
}

.compact-form {
  gap: 0.7rem;
}

.selection-label {
  display: block;
  margin-bottom: 0.55rem;
  font-size: 0.92rem;
}

.selection-list {
  display: grid;
  gap: 0.55rem;
}

.selection-option {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: #f8fafc;
}

.selection-option input {
  width: 1rem;
  height: 1rem;
  margin: 0;
}

.selection-option span:last-child {
  color: var(--muted);
  font-size: 0.85rem;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-weight: 600;
}

.toggle-row input {
  width: 1rem;
  height: 1rem;
  margin: 0;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.detail-card {
  display: grid;
  gap: 0.5rem;
  padding: 0.95rem;
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: #f8fafc;
}

.detail-card strong {
  font-size: 1rem;
}

.danger {
  color: #c73c52;
  border-color: rgba(199, 60, 82, 0.25);
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

.auth-panel,
#result-panel,
.snapshot-panel,
#credentials-panel,
#coverage-panel,
#lab-panel {
  grid-column: span 2;
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
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: start;
  }

  .screen-panel {
    grid-column: span 2;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .screen-panel[data-screen="activity"],
  .screen-panel[data-screen="balances"] {
    grid-template-columns: 1fr;
  }

  .screen-panel > :first-child:last-child {
    grid-column: span 2;
  }

  .auth-stack {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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

const SCREEN_KEY = 'splitwise-pwa-screen';
const SCREEN_META = {
  add: { title: 'Add an expense', action: 'Save', label: 'With you and:' },
  group: { title: 'Group screen', action: 'Add', label: 'Choose a group:' },
  activity: { title: 'Recent activity', action: 'Add', label: 'Filter activity:' },
  balances: { title: 'Balances', action: 'Add', label: 'Focus on:' },
};
const ACTIVITY_FILTERS = [
  { id: 'all', label: 'All' },
  { id: 'expenses', label: 'Expenses' },
  { id: 'updates', label: 'Updates' },
];

const state = {
  config: null,
  usedOperations: new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')),
  dashboard: JSON.parse(localStorage.getItem(DASHBOARD_CACHE_KEY) || '{}'),
  installPrompt: null,
  workspaceHydrated: false,
  screen: localStorage.getItem(SCREEN_KEY) || 'add',
  groupViewId: null,
  selectedExpenseId: null,
  activityFilter: 'all',
  composer: {
    editingExpenseId: null,
    friendId: null,
    groupId: 0,
    paidBy: 'self',
    splitMode: 'equal',
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
  renderCurrentScreen();
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
  elements.authLoggedOut = document.getElementById('auth-logged-out');
  elements.authLoggedIn = document.getElementById('auth-logged-in');
  elements.authUserCopy = document.getElementById('auth-user-copy');
  elements.registerForm = document.getElementById('register-form');
  elements.loginForm = document.getElementById('login-form');
  elements.logoutButton = document.getElementById('logout-button');
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
  elements.quickPaidBy = document.getElementById('quick-paid-by');
  elements.quickSplitMode = document.getElementById('quick-split-mode');
  elements.quickCustomSplitRow = document.getElementById('quick-custom-split-row');
  elements.quickYourShareLabel = document.getElementById('quick-your-share-label');
  elements.quickFriendShareLabel = document.getElementById('quick-friend-share-label');
  elements.quickYourShare = document.getElementById('quick-your-share');
  elements.quickFriendShare = document.getElementById('quick-friend-share');
  elements.quickDateButton = document.getElementById('quick-date-button');
  elements.quickGroupButton = document.getElementById('quick-group-button');
  elements.quickReceiptButton = document.getElementById('quick-receipt-button');
  elements.quickNoteButton = document.getElementById('quick-note-button');
  elements.quickNoteRow = document.getElementById('quick-note-row');
  elements.quickNoteInput = document.getElementById('quick-note-input');
  elements.quickRepeatInterval = document.getElementById('quick-repeat-interval');
  elements.quickEmailReminder = document.getElementById('quick-email-reminder');
  elements.quickReminderDaysRow = document.getElementById('quick-reminder-days-row');
  elements.quickReminderDays = document.getElementById('quick-reminder-days');
  elements.openToolsButton = document.getElementById('open-tools-button');
  elements.credentialsPanel = document.getElementById('credentials-panel');
  elements.participantLabel = document.getElementById('participant-label');
  elements.screenTitle = document.getElementById('screen-title');
  elements.screenTabs = Array.from(document.querySelectorAll('.screen-tab'));
  elements.screenPanels = Array.from(document.querySelectorAll('.screen-panel'));
  elements.groupScreenTitle = document.getElementById('group-screen-title');
  elements.groupScreenSummary = document.getElementById('group-screen-summary');
  elements.groupBalanceSummary = document.getElementById('group-balance-summary');
  elements.updateGroupForm = document.getElementById('update-group-form');
  elements.updateGroupName = document.getElementById('update-group-name');
  elements.updateGroupWhiteboard = document.getElementById('update-group-whiteboard');
  elements.deleteGroupButton = document.getElementById('delete-group-button');
  elements.createGroupForm = document.getElementById('create-group-form');
  elements.createGroupMembers = document.getElementById('create-group-members');
  elements.groupMemberList = document.getElementById('group-member-list');
  elements.groupExpenseList = document.getElementById('group-expense-list');
  elements.activityStats = document.getElementById('activity-stats');
  elements.activityFeed = document.getElementById('activity-feed');
  elements.expenseDetailCard = document.getElementById('expense-detail-card');
  elements.editExpenseButton = document.getElementById('edit-expense-button');
  elements.deleteExpenseButton = document.getElementById('delete-expense-button');
  elements.expenseCommentList = document.getElementById('expense-comment-list');
  elements.expenseCommentForm = document.getElementById('expense-comment-form');
  elements.expenseCommentInput = document.getElementById('expense-comment-input');
  elements.friendForm = document.getElementById('friend-form');
  elements.incomingRequestList = document.getElementById('incoming-request-list');
  elements.outgoingRequestList = document.getElementById('outgoing-request-list');
  elements.balanceList = document.getElementById('balance-list');
  elements.profileForm = document.getElementById('profile-form');
  elements.profileFirstName = document.getElementById('profile-first-name');
  elements.profileLastName = document.getElementById('profile-last-name');
  elements.profileEmail = document.getElementById('profile-email');
  elements.passwordForm = document.getElementById('password-form');
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

  elements.screenTabs.forEach((button) => {
    button.addEventListener('click', () => navigateToScreen(button.dataset.screen));
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
      state.workspaceHydrated = false;
      await loadConfig();
    }
  });

  elements.registerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const response = await request('/api/local/register', {
      first_name: (form.get('first_name') || '').toString().trim(),
      last_name: (form.get('last_name') || '').toString().trim(),
      email: (form.get('email') || '').toString().trim(),
      password: (form.get('password') || '').toString(),
    });
    if (response) {
      resetWorkspaceCache();
      formElement.reset();
      showToast('Local account created', 'success');
      await loadConfig();
    }
  });

  elements.loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const response = await request('/api/local/login', {
      email: (form.get('email') || '').toString().trim(),
      password: (form.get('password') || '').toString(),
    });
    if (response) {
      resetWorkspaceCache();
      formElement.reset();
      showToast('Signed in', 'success');
      await loadConfig();
    }
  });

  elements.logoutButton.addEventListener('click', async () => {
    const response = await request('/api/local/logout', {});
    if (response) {
      resetWorkspaceCache();
      showToast('Signed out', 'success');
      await loadConfig();
    }
  });

  elements.clearSession.addEventListener('click', async () => {
    const response = await request('/api/session/clear', {});
    if (response) {
      resetWorkspaceCache();
      showToast('Session cleared', 'success');
      renderCoverage();
      renderDashboardCache();
      renderCurrentScreen();
      await loadConfig();
    }
  });

  elements.refreshDashboard.addEventListener('click', async () => {
    await hydrateWorkspace(true);
    showToast('Dashboard refreshed', 'success');
  });

  elements.friendForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!ensureAuthenticated('Add a friend')) {
      return;
    }
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const response = await request('/api/local/friend-requests', {
      email: (form.get('email') || '').toString().trim(),
    });
    if (response) {
      formElement.reset();
      await hydrateWorkspace(true);
      showToast('Friend request sent', 'success');
    }
  });

  elements.profileForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!ensureAuthenticated('Update your profile')) {
      return;
    }
    const form = new FormData(event.currentTarget);
    const response = await request('/api/local/profile', {
      first_name: (form.get('first_name') || '').toString().trim(),
      last_name: (form.get('last_name') || '').toString().trim(),
      email: (form.get('email') || '').toString().trim(),
    });
    if (response) {
      await loadConfig();
      await hydrateWorkspace(true);
      showToast('Profile updated', 'success');
    }
  });

  elements.passwordForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!ensureAuthenticated('Update your password')) {
      return;
    }
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const response = await request('/api/local/password', {
      current_password: (form.get('current_password') || '').toString(),
      new_password: (form.get('new_password') || '').toString(),
    });
    if (response) {
      formElement.reset();
      showToast('Password updated', 'success');
    }
  });

  elements.createGroupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!ensureAuthenticated('Create a group')) {
      return;
    }
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const friends = Array.from(elements.createGroupMembers.querySelectorAll('input[name="member_id"]:checked'))
      .map((input) => availableFriends().find((friend) => friend.id === Number(input.value)))
      .filter(Boolean)
      .map((friend) => ({
        id: friend.id,
        first_name: friend.first_name,
        last_name: friend.last_name,
        email: friend.email,
      }));
    const response = await invokeOperation('createGroup', {
      group: {
        name: (form.get('name') || '').toString().trim(),
        whiteboard: (form.get('whiteboard') || '').toString().trim() || undefined,
        members: friends,
      },
    });
    if (response) {
      formElement.reset();
      await hydrateWorkspace(true);
      const group = response.data && response.data.group ? response.data.group : null;
      if (group && group.id) {
        state.groupViewId = group.id;
        state.composer.groupId = group.id;
      }
      navigateToScreen('group');
    }
  });

  elements.updateGroupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!ensureAuthenticated('Update a group')) {
      return;
    }
    const group = currentGroup();
    if (!group) {
      showToast('Select a group first', 'error');
      return;
    }
    const form = new FormData(event.currentTarget);
    const response = await request('/api/local/groups/update', {
      group_id: group.id,
      name: (form.get('name') || '').toString().trim(),
      whiteboard: (form.get('whiteboard') || '').toString().trim(),
    });
    if (response) {
      await hydrateWorkspace(true);
      showToast('Group updated', 'success');
    }
  });

  elements.deleteGroupButton.addEventListener('click', async () => {
    if (!ensureAuthenticated('Delete a group')) {
      return;
    }
    const group = currentGroup();
    if (!group) {
      showToast('Select a group first', 'error');
      return;
    }
    const response = await invokeOperation('deleteGroup', { id: group.id }, { silent: true });
    if (response) {
      state.groupViewId = null;
      state.composer.groupId = 0;
      await hydrateWorkspace(true);
      showToast('Group deleted', 'success');
    }
  });

  elements.quickExpenseForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await saveQuickExpense();
  });

  elements.quickExpenseSave.addEventListener('click', async () => {
    if (state.screen === 'add') {
      await saveQuickExpense();
      return;
    }
    navigateToScreen('add');
    showToast('Switched to add expense', 'success');
  });

  elements.quickSplitButton.addEventListener('click', () => {
    state.composer.splitMode = state.composer.splitMode === 'equal' ? 'custom' : 'equal';
    elements.quickSplitMode.value = state.composer.splitMode;
    initializeCustomSplitValues(state.composer.splitMode === 'custom');
    renderComposerState();
    showToast(state.composer.splitMode === 'custom' ? 'Custom split enabled' : 'Equal split enabled', 'success');
  });

  elements.quickPaidBy.addEventListener('change', () => {
    state.composer.paidBy = elements.quickPaidBy.value;
    renderComposerState();
  });

  elements.quickSplitMode.addEventListener('change', () => {
    state.composer.splitMode = elements.quickSplitMode.value;
    initializeCustomSplitValues(state.composer.splitMode === 'custom');
    renderComposerState();
  });

  elements.quickCost.addEventListener('input', () => {
    initializeCustomSplitValues(false);
    renderComposerState();
  });

  elements.quickYourShare.addEventListener('input', () => {
    initializeCustomSplitValues(false);
  });

  elements.quickFriendShare.addEventListener('input', () => {
    initializeCustomSplitValues(false);
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

  elements.quickEmailReminder.addEventListener('change', () => {
    renderComposerState();
  });

  elements.quickReceiptButton.addEventListener('click', () => {
    elements.credentialsPanel.open = true;
    document.getElementById('lab-panel').open = true;
    document.getElementById('lab-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('Advanced receipt workflows are available below', 'success');
  });

  elements.dashboardActions.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-friend-id], button[data-group-id], button[data-filter]');
    if (!button) {
      return;
    }
    if (button.dataset.friendId) {
      state.composer.friendId = Number(button.dataset.friendId);
      if (state.screen === 'balances') {
        navigateToScreen('add');
      } else {
        renderCurrentScreen();
      }
      return;
    }
    if (button.dataset.groupId) {
      state.groupViewId = Number(button.dataset.groupId);
      state.composer.groupId = state.groupViewId;
      renderCurrentScreen();
      return;
    }
    if (button.dataset.filter) {
      state.activityFilter = button.dataset.filter;
      renderCurrentScreen();
    }
  });

  elements.groupExpenseList.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-expense-id]');
    if (!button) {
      return;
    }
    selectExpense(Number(button.dataset.expenseId), true);
  });

  elements.activityFeed.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-expense-id]');
    if (!button) {
      return;
    }
    selectExpense(Number(button.dataset.expenseId), false);
  });

  elements.incomingRequestList.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-request-id][data-accept]');
    if (!button) {
      return;
    }
    const response = await request('/api/local/friend-requests/respond', {
      request_id: Number(button.dataset.requestId),
      accept: button.dataset.accept === 'true',
    });
    if (response) {
      await hydrateWorkspace(true);
      showToast(button.dataset.accept === 'true' ? 'Friend request accepted' : 'Friend request declined', 'success');
    }
  });

  elements.balanceList.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-settle-friend-id]');
    if (!button) {
      return;
    }
    const friend = availableFriends().find((item) => item.id === Number(button.dataset.settleFriendId));
    if (!friend) {
      return;
    }
    const primary = Array.isArray(friend.balances || friend.balance) ? (friend.balances || friend.balance)[0] : null;
    const amount = primary ? Math.abs(Number(primary.amount || 0)) : 0;
    if (!amount) {
      showToast('This balance is already settled', 'success');
      return;
    }
    const currentUser = state.dashboard.getCurrentUser;
    const payerId = Number(primary.amount || 0) < 0 ? currentUser.id : friend.id;
    const receiverId = payerId === currentUser.id ? friend.id : currentUser.id;
    const response = await request('/api/local/settlements', {
      other_user_id: friend.id,
      amount: formatMoney(amount),
      from_user_id: payerId,
      to_user_id: receiverId,
      note: `Settlement between ${displayName(currentUser)} and ${displayName(friend)}`,
    });
    if (response) {
      await hydrateWorkspace(true);
      showToast('Settlement recorded', 'success');
    }
  });

  elements.editExpenseButton.addEventListener('click', () => {
    const expense = currentExpense();
    if (!expense) {
      showToast('Select an expense first', 'error');
      return;
    }
    if (!Array.isArray(expense.users) || expense.users.length !== 2) {
      showToast('Inline editing currently supports two-person expenses', 'error');
      return;
    }
    populateComposerFromExpense(expense);
    navigateToScreen('add');
  });

  elements.deleteExpenseButton.addEventListener('click', async () => {
    const expense = currentExpense();
    if (!expense) {
      showToast('Select an expense first', 'error');
      return;
    }
    const response = await invokeOperation('deleteExpense', { id: expense.id }, { silent: true });
    if (response) {
      state.selectedExpenseId = null;
      state.composer.editingExpenseId = null;
      await hydrateWorkspace(true);
      renderCurrentScreen();
      showToast('Expense deleted', 'success');
    }
  });

  elements.expenseCommentForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const expense = currentExpense();
    if (!expense) {
      showToast('Select an expense first', 'error');
      return;
    }
    const content = elements.expenseCommentInput.value.trim();
    if (!content) {
      showToast('Comment text is required', 'error');
      return;
    }
    const response = await invokeOperation('createComment', { expense_id: expense.id, content }, { silent: true, preserveResult: true });
    if (response) {
      elements.expenseCommentInput.value = '';
      await hydrateWorkspace(true);
      await loadExpenseComments(expense.id);
      showToast('Comment added', 'success');
    }
  });
}

function navigateToScreen(screen) {
  state.screen = screen;
  localStorage.setItem(SCREEN_KEY, screen);
  if (screen === 'group') {
    const group = currentGroup();
    if (group) {
      state.composer.groupId = group.id;
    }
  }
  renderCurrentScreen();
}

async function loadConfig() {
  const config = await fetchJson('/api/config');
  if (!config) {
    return;
  }
  state.config = config;
  renderSessionState();
  renderAuthState();
  renderCoverage();
  renderDashboardCache();
  renderCurrentScreen();
  if (config.configured && !state.workspaceHydrated) {
    await hydrateWorkspace(false);
  }
}

async function hydrateWorkspace(forceRefresh) {
  if (!state.config || !state.config.configured) {
    return;
  }
  if (state.workspaceHydrated && !forceRefresh) {
    return;
  }
  state.workspaceHydrated = true;
  for (const [, operation] of QUICK_ACTIONS) {
    await invokeOperation(operation, {}, { silent: true, preserveResult: true });
  }
  const requestsResponse = await request('/api/local/friend-requests/list', {}, true);
  state.dashboard.localFriendRequests = requestsResponse && requestsResponse.requests ? requestsResponse.requests : { incoming: [], outgoing: [] };
  localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
  if (state.selectedExpenseId) {
    await loadExpenseComments(state.selectedExpenseId);
  }
  renderCurrentScreen();
  renderDashboardCache();
}

function renderCurrentScreen() {
  const meta = SCREEN_META[state.screen] || SCREEN_META.add;
  elements.screenTitle.textContent = meta.title;
  elements.quickExpenseSave.textContent = meta.action;
  elements.participantLabel.textContent = meta.label;
  elements.screenTabs.forEach((button) => {
    button.classList.toggle('active', button.dataset.screen === state.screen);
  });
  elements.screenPanels.forEach((panel) => {
    panel.classList.toggle('active', panel.dataset.screen === state.screen);
  });
  renderParticipantChips();
  renderComposerState();
  renderGroupScreen();
  renderActivityScreen();
  renderBalancesScreen();
}

function renderSessionState() {
  const summary = state.config && state.config.session ? state.config.session : {};
  if (state.config && state.config.authenticated && state.config.local_user) {
    elements.credentialsStatus.textContent = 'Signed in';
    elements.sessionSummary.textContent = `Using local account ${displayName(state.config.local_user)}.`;
    return;
  }
  elements.credentialsStatus.textContent = state.config.configured ? 'Ready' : 'Needs setup';
  const parts = [];
  if (summary.local_account) parts.push('local account ready');
  if (summary.consumer_key) parts.push('consumer key saved');
  if (summary.consumer_secret) parts.push('consumer secret saved');
  if (summary.api_key) parts.push('API key saved');
  if (summary.access_token) parts.push('OAuth 1 token saved');
  if (summary.oauth2_access_token) parts.push('OAuth 2 token saved');
  elements.sessionSummary.textContent = parts.length
    ? parts.join(' • ')
    : 'Create a local account to use the app, or save advanced credentials below.';
}

function renderAuthState() {
  const authenticated = Boolean(state.config && state.config.authenticated && state.config.local_user);
  elements.authLoggedOut.classList.toggle('hidden', authenticated);
  elements.authLoggedIn.classList.toggle('hidden', !authenticated);
  if (authenticated) {
    const user = state.config.local_user;
    elements.authUserCopy.textContent = `${displayName(user)} • ${user.email || 'Local account'}`;
    elements.profileFirstName.value = user.first_name || '';
    elements.profileLastName.value = user.last_name || '';
    elements.profileEmail.value = user.email || '';
  } else {
    elements.authUserCopy.textContent = 'Signed out.';
    elements.profileFirstName.value = '';
    elements.profileLastName.value = '';
    elements.profileEmail.value = '';
  }
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
  if (!ensureAuthenticated('Create expenses', true)) {
    showToast('Create a local account or sign in before creating expenses', 'error');
    return;
  }
  if (!state.config || !state.config.configured) {
    showToast('The app is still loading your local account session', 'error');
    return;
  }

  const description = elements.quickDescription.value.trim();
  const cost = elements.quickCost.value.trim();
  if (!description || !cost) {
    showToast('Description and amount are required', 'error');
    return;
  }

  let owner = state.dashboard.getCurrentUser;
  let companion = selectedFriend();
  if (!owner || !companion) {
    await hydrateWorkspace(true);
    owner = state.dashboard.getCurrentUser;
    companion = selectedFriend();
  }
  if (!owner || !companion) {
    showToast('Load at least one friend before creating an expense', 'error');
    return;
  }

  const totalCost = Number.parseFloat(cost);
  if (!Number.isFinite(totalCost) || totalCost <= 0) {
    showToast('Enter a valid amount greater than zero', 'error');
    return;
  }
  let yourShare = splitAmount(cost, 2);
  let friendShare = splitAmount(cost, 2);
  if (state.composer.splitMode === 'custom') {
    const customShares = resolveCustomShares(totalCost);
    if (!customShares) {
      showToast('Custom shares must add up to the full expense amount', 'error');
      return;
    }
    yourShare = customShares.yourShare;
    friendShare = customShares.friendShare;
  }
  const ownerPaid = state.composer.paidBy === 'friend' ? '0.00' : formatMoney(cost);
  const friendPaid = state.composer.paidBy === 'friend' ? formatMoney(cost) : '0.00';
  const repeats = elements.quickRepeatInterval.value !== 'never';
  const expense = {
    description,
    cost,
    currency_code: defaultCurrencyCode(),
    split_equally: state.composer.splitMode === 'equal',
    details: elements.quickNoteInput.value.trim() || undefined,
    date: `${state.composer.date}T12:00:00Z`,
    repeats,
    repeat_interval: elements.quickRepeatInterval.value,
    email_reminder: elements.quickEmailReminder.checked,
    email_reminder_in_advance: elements.quickEmailReminder.checked ? Number(elements.quickReminderDays.value || 0) : -1,
    users: [
      { id: owner.id, paid_share: ownerPaid, owed_share: yourShare },
      { id: companion.id, paid_share: friendPaid, owed_share: friendShare },
    ],
  };
  if (state.composer.editingExpenseId) {
    expense.id = state.composer.editingExpenseId;
  }
  if (state.composer.groupId) {
    expense.group_id = state.composer.groupId;
  }

  const operation = state.composer.editingExpenseId ? 'updateExpense' : 'createExpense';
  const response = await invokeOperation(operation, { expense });
  if (!response) {
    return;
  }

  const createdExpense = response.data && response.data.expense ? response.data.expense : null;
  if (createdExpense) {
    const existingExpenses = Array.isArray(state.dashboard.getExpenses) ? state.dashboard.getExpenses : [];
    state.dashboard.getExpenses = [createdExpense, ...existingExpenses].slice(0, 8);
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
    renderDashboardCache();
  }

  elements.quickDescription.value = '';
  elements.quickCost.value = '';
  elements.quickNoteInput.value = '';
  elements.quickPaidBy.value = 'self';
  elements.quickSplitMode.value = 'equal';
  elements.quickYourShare.value = '';
  elements.quickFriendShare.value = '';
  elements.quickRepeatInterval.value = 'never';
  elements.quickEmailReminder.checked = false;
  elements.quickReminderDays.value = '';
  state.composer.editingExpenseId = null;
  state.composer.paidBy = 'self';
  state.composer.splitMode = 'equal';
  state.composer.noteVisible = false;
  renderCurrentScreen();
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
    renderCurrentScreen();
  }

  if (!options.silent) {
    showToast(`${operation} completed`, 'success');
  }
  return response;
}

function renderParticipantChips() {
  elements.dashboardActions.innerHTML = '';
  if (!ensureAuthenticated(null, true)) {
    renderChipPlaceholder('Create a local account to get started');
    return;
  }
  if (state.screen === 'group') {
    renderGroupChips();
    return;
  }
  if (state.screen === 'activity') {
    renderActivityFilterChips();
    return;
  }
  renderFriendChips();
}

function renderFriendChips() {
  const friends = Array.isArray(state.dashboard.getFriends) ? state.dashboard.getFriends : [];
  if (!friends.length) {
    renderChipPlaceholder('Load friends to start');
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
    button.innerHTML = `
      <span class="participant-avatar">${escapeHtml(getInitials(friend.first_name, friend.last_name))}</span>
      <span>${escapeHtml(displayName(friend))}</span>
    `;
    elements.dashboardActions.appendChild(button);
  });
}

function renderGroupChips() {
  const groups = availableGroups();
  if (!groups.length) {
    renderChipPlaceholder('Load groups to start');
    return;
  }
  if (!state.groupViewId || !groups.some((group) => group.id === state.groupViewId)) {
    state.groupViewId = groups[0].id;
  }
  groups.forEach((group) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `participant-chip${state.groupViewId === group.id ? ' selected' : ''}`;
    button.dataset.groupId = String(group.id);
    button.innerHTML = `
      <span class="participant-avatar">${escapeHtml(getInitials(group.name))}</span>
      <span>${escapeHtml(group.name)}</span>
    `;
    elements.dashboardActions.appendChild(button);
  });
}

function renderActivityFilterChips() {
  ACTIVITY_FILTERS.forEach((filter) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `participant-chip${state.activityFilter === filter.id ? ' selected' : ''}`;
    button.dataset.filter = filter.id;
    button.textContent = filter.label;
    elements.dashboardActions.appendChild(button);
  });
}

function renderChipPlaceholder(label) {
  const placeholder = document.createElement('button');
  placeholder.type = 'button';
  placeholder.className = 'participant-chip';
  placeholder.textContent = label;
  placeholder.addEventListener('click', async () => {
    await hydrateWorkspace(true);
  });
  elements.dashboardActions.appendChild(placeholder);
}

function renderComposerState() {
  elements.quickNoteRow.classList.toggle('hidden', !state.composer.noteVisible);
  elements.quickReminderDaysRow.classList.toggle('hidden', !elements.quickEmailReminder.checked);
  elements.quickCustomSplitRow.classList.toggle('hidden', state.composer.splitMode !== 'custom');
  const groups = availableGroups();
  const selectedGroup = groups.find((group) => group.id === state.composer.groupId);
  elements.quickGroupButton.textContent = selectedGroup ? selectedGroup.name : 'No group';
  const today = new Date().toISOString().slice(0, 10);
  elements.quickDateButton.textContent = state.composer.date === today ? 'Today' : state.composer.date;
  const friend = selectedFriend();
  if (!friend && state.composer.paidBy === 'friend') {
    state.composer.paidBy = 'self';
  }
  elements.quickPaidBy.value = state.composer.paidBy;
  elements.quickSplitMode.value = state.composer.splitMode;
  const payerLabel = state.composer.paidBy === 'friend' && friend ? friend.first_name : 'you';
  elements.quickSplitButton.textContent = friend
    ? (state.composer.splitMode === 'custom'
      ? `Paid by ${payerLabel} with custom shares`
      : `Paid by ${payerLabel} and split equally with ${friend.first_name}`)
    : (state.composer.splitMode === 'custom'
      ? `Paid by ${payerLabel} with custom shares`
      : `Paid by ${payerLabel} and split equally`);
  elements.quickPaidBy.options[1].textContent = friend ? friend.first_name : 'Selected friend';
  elements.quickYourShareLabel.textContent = 'Your share';
  elements.quickFriendShareLabel.textContent = friend ? `${friend.first_name}'s share` : 'Friend share';
  initializeCustomSplitValues(false);
  if (state.composer.editingExpenseId) {
    elements.quickExpenseSave.textContent = 'Update';
  } else {
    elements.quickExpenseSave.textContent = 'Save';
  }
}

function renderGroupScreen() {
  renderGroupComposer();
  const group = currentGroup();
  if (!group) {
    elements.groupScreenTitle.textContent = 'No group data yet';
    elements.groupScreenSummary.textContent = 'Sync the dashboard to load a group screen.';
    elements.groupBalanceSummary.innerHTML = '<div class="summary-pill"><span class="summary-label">Status</span><strong class="summary-value">Awaiting data</strong></div>';
    elements.groupMemberList.innerHTML = '<p class="empty-copy">No members available.</p>';
    elements.groupExpenseList.innerHTML = '<p class="empty-copy">No group expenses available.</p>';
    elements.updateGroupName.value = '';
    elements.updateGroupWhiteboard.value = '';
    return;
  }

  const balances = group.members || [];
  const expenses = (state.dashboard.getExpenses || []).filter((expense) => expense.group_id === group.id);
  elements.groupScreenTitle.textContent = group.name;
  elements.groupScreenSummary.textContent = group.whiteboard || `${balances.length} members • ${expenses.length} tracked expenses`;
  elements.groupBalanceSummary.innerHTML = `
    <div class="summary-pill">
      <span class="summary-label">Members</span>
      <strong class="summary-value">${balances.length}</strong>
    </div>
    <div class="summary-pill">
      <span class="summary-label">Recent expenses</span>
      <strong class="summary-value">${expenses.length}</strong>
    </div>
  `;
  elements.updateGroupName.value = group.name || '';
  elements.updateGroupWhiteboard.value = group.whiteboard || '';
  elements.groupMemberList.innerHTML = balances.length
    ? balances.map((member) => `
        <article class="list-row">
          <div class="row-main">
            <span class="row-avatar">${escapeHtml(getInitials(member.first_name, member.last_name))}</span>
            <div class="row-copy">
              <strong>${escapeHtml(displayName(member))}</strong>
              <span class="row-meta">${member.email ? escapeHtml(member.email) : 'Group member'}</span>
            </div>
            <div class="amount-copy ${balanceClass(member.balances || member.balance)}">
              <strong>${escapeHtml(formatBalance(member.balances || member.balance))}</strong>
              <span class="row-meta">${escapeHtml(balanceLabel(member.balances || member.balance))}</span>
            </div>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No members available.</p>';
  elements.groupExpenseList.innerHTML = expenses.length
    ? expenses.slice(0, 6).map((expense) => `
        <article class="list-row">
          <div class="row-main">
            <div class="row-copy">
              <strong>${escapeHtml(expense.description || 'Expense')}</strong>
              <p class="muted-copy">${escapeHtml(expense.details || 'Split expense')} • ${escapeHtml(formatDateLabel(expense.date || expense.created_at))}</p>
              <div class="inline-badges">
                ${expense.repeats ? `<span class="mini-badge">Repeats ${escapeHtml(expense.repeat_interval || 'monthly')}</span>` : ''}
                ${expense.email_reminder ? `<span class="mini-badge">Reminder ${escapeHtml(String(expense.email_reminder_in_advance || 0))}d</span>` : ''}
                ${expense.payment ? '<span class="mini-badge">Payment</span>' : ''}
              </div>
            </div>
            <div class="amount-copy amount-negative">
              <strong>${escapeHtml((expense.currency_code || defaultCurrencyCode()) + ' ' + formatMoney(expense.cost || '0'))}</strong>
              <span class="row-meta">${escapeHtml(expense.group_id === 0 ? 'non-group' : 'group expense')}</span>
            </div>
          </div>
          <div class="action-row">
            <button class="ghost compact-button" type="button" data-expense-id="${expense.id}">Manage expense</button>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No expenses for this group yet.</p>';
}

function renderActivityScreen() {
  const notifications = Array.isArray(state.dashboard.getNotifications) ? state.dashboard.getNotifications : [];
  const expenses = Array.isArray(state.dashboard.getExpenses) ? state.dashboard.getExpenses : [];
  const items = buildActivityItems(notifications, expenses).filter((item) => {
    if (state.activityFilter === 'expenses') {
      return item.kind === 'expense';
    }
    if (state.activityFilter === 'updates') {
      return item.kind === 'notification';
    }
    return true;
  });

  elements.activityStats.innerHTML = `
    <div class="summary-pill">
      <span class="summary-label">Updates</span>
      <strong class="summary-value">${notifications.length}</strong>
    </div>
    <div class="summary-pill">
      <span class="summary-label">Expenses</span>
      <strong class="summary-value">${expenses.length}</strong>
    </div>
  `;

  elements.activityFeed.innerHTML = items.length
    ? items.map((item) => `
        <article class="activity-item">
          <div class="timeline-head">
            <span class="timeline-badge ${item.kind}">${escapeHtml(item.label)}</span>
            <span class="activity-meta">${escapeHtml(formatDateLabel(item.date))}</span>
          </div>
          <strong class="activity-title">${escapeHtml(item.title)}</strong>
          <p class="activity-body">${escapeHtml(item.body)}</p>
          ${item.expenseId ? `<div class="action-row"><button class="ghost compact-button" type="button" data-expense-id="${item.expenseId}">Open comments</button></div>` : ''}
        </article>
      `).join('')
    : '<p class="empty-copy">No recent activity yet.</p>';
  renderExpenseDetail();
}

function renderBalancesScreen() {
  const friends = availableFriends();
  const requests = state.dashboard.localFriendRequests || { incoming: [], outgoing: [] };
  elements.incomingRequestList.innerHTML = requests.incoming && requests.incoming.length
    ? requests.incoming.map((request) => `
        <article class="list-row">
          <div class="row-main">
            <div class="row-copy">
              <strong>${escapeHtml(displayName(request.user))}</strong>
              <span class="row-meta">${escapeHtml(request.user.email || 'Local account')}</span>
            </div>
          </div>
          <div class="action-row">
            <button class="compact-button" type="button" data-request-id="${request.id}" data-accept="true">Accept</button>
            <button class="ghost compact-button danger" type="button" data-request-id="${request.id}" data-accept="false">Decline</button>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No incoming requests.</p>';
  elements.outgoingRequestList.innerHTML = requests.outgoing && requests.outgoing.length
    ? requests.outgoing.map((request) => `
        <article class="list-row">
          <div class="row-main">
            <div class="row-copy">
              <strong>${escapeHtml(displayName(request.user))}</strong>
              <span class="row-meta">Waiting for response</span>
            </div>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No outgoing requests.</p>';
  elements.balanceList.innerHTML = friends.length
    ? friends.slice(0, 8).map((friend) => `
        <article class="list-row">
          <div class="row-main">
            <span class="row-avatar">${escapeHtml(getInitials(friend.first_name, friend.last_name))}</span>
            <div class="row-copy">
              <strong>${escapeHtml(displayName(friend))}</strong>
              <span class="row-meta">${(friend.groups || []).length} shared groups</span>
              <div class="inline-badges">
                ${(friend.groups || []).slice(0, 3).map((group) => `<span class="mini-badge">${escapeHtml(groupName(group.group_id || group.id))}</span>`).join('')}
              </div>
            </div>
            <div class="amount-copy ${balanceClass(friend.balances || friend.balance)}">
              <strong>${escapeHtml(formatBalance(friend.balances || friend.balance))}</strong>
              <span class="row-meta">${escapeHtml(balanceLabel(friend.balances || friend.balance))}</span>
            </div>
          </div>
          <div class="action-row">
            <button class="ghost compact-button" type="button" data-settle-friend-id="${friend.id}">Record settlement</button>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No friend balances available.</p>';
}

function cycleComposerGroup() {
  const groups = availableGroups();
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
  state.groupViewId = state.composer.groupId || state.groupViewId;
  renderCurrentScreen();
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
    return `<ul>${data.slice(0, 3).map((friend) => `<li>${escapeHtml(displayName(friend))}</li>`).join('')}</ul>`;
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

function availableGroups() {
  return Array.isArray(state.dashboard.getGroups) ? state.dashboard.getGroups.filter((group) => group.id !== 0) : [];
}

function availableFriends() {
  return Array.isArray(state.dashboard.getFriends) ? state.dashboard.getFriends : [];
}

function currentGroup() {
  const groups = availableGroups();
  if (!groups.length) {
    return null;
  }
  if (!state.groupViewId || !groups.some((group) => group.id === state.groupViewId)) {
    state.groupViewId = groups[0].id;
  }
  return groups.find((group) => group.id === state.groupViewId) || groups[0];
}

function selectedFriend() {
  const friends = availableFriends();
  return friends.find((friend) => friend.id === state.composer.friendId) || friends[0] || null;
}

function initializeCustomSplitValues(force) {
  if (state.composer.splitMode !== 'custom') {
    return;
  }
  const total = Number.parseFloat(elements.quickCost.value || '0');
  if (!Number.isFinite(total) || total <= 0) {
    return;
  }
  const yourValue = elements.quickYourShare.value.trim();
  const friendValue = elements.quickFriendShare.value.trim();
  if (force || (!yourValue && !friendValue)) {
    const equalShare = splitAmount(total, 2);
    elements.quickYourShare.value = equalShare;
    elements.quickFriendShare.value = equalShare;
    return;
  }
  if (yourValue && !friendValue) {
    const yourShare = Number.parseFloat(yourValue);
    if (Number.isFinite(yourShare)) {
      elements.quickFriendShare.value = formatMoney(Math.max(total - yourShare, 0));
    }
    return;
  }
  if (!yourValue && friendValue) {
    const friendShare = Number.parseFloat(friendValue);
    if (Number.isFinite(friendShare)) {
      elements.quickYourShare.value = formatMoney(Math.max(total - friendShare, 0));
    }
  }
}

function resolveCustomShares(total) {
  const yourInput = elements.quickYourShare.value.trim();
  const friendInput = elements.quickFriendShare.value.trim();
  let yourShare = yourInput ? Number.parseFloat(yourInput) : NaN;
  let friendShare = friendInput ? Number.parseFloat(friendInput) : NaN;
  if (!Number.isFinite(yourShare) && Number.isFinite(friendShare)) {
    yourShare = total - friendShare;
  }
  if (Number.isFinite(yourShare) && !Number.isFinite(friendShare)) {
    friendShare = total - yourShare;
  }
  if (!Number.isFinite(yourShare) || !Number.isFinite(friendShare)) {
    return null;
  }
  if (yourShare < 0 || friendShare < 0) {
    return null;
  }
  if (Math.abs((yourShare + friendShare) - total) > 0.01) {
    return null;
  }
  return {
    yourShare: formatMoney(yourShare),
    friendShare: formatMoney(friendShare),
  };
}

function currentExpense() {
  const expenses = Array.isArray(state.dashboard.getExpenses) ? state.dashboard.getExpenses : [];
  if (!expenses.length) {
    return null;
  }
  if (!state.selectedExpenseId || !expenses.some((expense) => expense.id === state.selectedExpenseId)) {
    state.selectedExpenseId = expenses[0].id;
  }
  return expenses.find((expense) => expense.id === state.selectedExpenseId) || expenses[0];
}

async function selectExpense(expenseId, navigate) {
  state.selectedExpenseId = expenseId;
  await loadExpenseComments(expenseId);
  if (navigate) {
    navigateToScreen('activity');
    return;
  }
  renderCurrentScreen();
}

async function loadExpenseComments(expenseId) {
  const response = await invokeOperation('getComments', { expense_id: expenseId }, { silent: true, preserveResult: true });
  if (!state.dashboard.expenseComments) {
    state.dashboard.expenseComments = {};
  }
  state.dashboard.expenseComments[String(expenseId)] = response ? response.data : [];
  localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(state.dashboard));
}

function renderExpenseDetail() {
  const expense = currentExpense();
  if (!expense) {
    elements.expenseDetailCard.innerHTML = '<p class="empty-copy">Select an expense from activity or a group to manage it here.</p>';
    elements.expenseCommentList.innerHTML = '<p class="empty-copy">No comments to show yet.</p>';
    return;
  }
  const group = groupName(expense.group_id);
  const comments = state.dashboard.expenseComments && state.dashboard.expenseComments[String(expense.id)]
    ? state.dashboard.expenseComments[String(expense.id)]
    : [];
  elements.expenseDetailCard.innerHTML = `
    <strong>${escapeHtml(expense.description || 'Expense')}</strong>
    <span class="muted-copy">${escapeHtml(group)} • ${escapeHtml(formatDateLabel(expense.date || expense.created_at))}</span>
    <span class="muted-copy">${escapeHtml((expense.currency_code || defaultCurrencyCode()) + ' ' + formatMoney(expense.cost || '0'))}</span>
    <span class="muted-copy">${escapeHtml(expense.details || 'No extra note')}</span>
    <div class="inline-badges">
      ${expense.repeats ? `<span class="mini-badge">Repeats ${escapeHtml(expense.repeat_interval || 'monthly')}</span>` : ''}
      ${expense.email_reminder ? `<span class="mini-badge">Reminder ${escapeHtml(String(expense.email_reminder_in_advance || 0))}d</span>` : ''}
      ${expense.payment ? '<span class="mini-badge">Payment</span>' : ''}
    </div>
  `;
  elements.expenseCommentList.innerHTML = comments.length
    ? comments.map((comment) => `
        <article class="list-row">
          <div class="row-main">
            <div class="row-copy">
              <strong>${escapeHtml(displayName(comment.user || {}))}</strong>
              <p class="muted-copy">${escapeHtml(comment.content || '')}</p>
            </div>
            <span class="row-meta">${escapeHtml(formatDateLabel(comment.created_at))}</span>
          </div>
        </article>
      `).join('')
    : '<p class="empty-copy">No comments yet for this expense.</p>';
}

function populateComposerFromExpense(expense) {
  const currentUser = state.dashboard.getCurrentUser;
  const otherUser = Array.isArray(expense.users)
    ? expense.users.find((item) => item.user_id !== currentUser.id)
    : null;
  elements.quickDescription.value = expense.description || '';
  elements.quickCost.value = expense.cost || '';
  elements.quickNoteInput.value = expense.details || '';
  elements.quickRepeatInterval.value = expense.repeats ? (expense.repeat_interval || 'monthly') : 'never';
  elements.quickEmailReminder.checked = Boolean(expense.email_reminder);
  elements.quickReminderDays.value = expense.email_reminder && expense.email_reminder_in_advance >= 0
    ? String(expense.email_reminder_in_advance)
    : '';
  state.composer.editingExpenseId = expense.id;
  state.composer.noteVisible = Boolean(expense.details);
  state.composer.date = (expense.date || '').slice(0, 10) || new Date().toISOString().slice(0, 10);
  state.composer.groupId = expense.group_id || 0;
  if (otherUser) {
    state.composer.friendId = otherUser.user_id;
  }
  const currentUserShare = Array.isArray(expense.users)
    ? expense.users.find((item) => item.user_id === currentUser.id)
    : null;
  const otherUserShare = Array.isArray(expense.users)
    ? expense.users.find((item) => item.user_id !== currentUser.id)
    : null;
  state.composer.paidBy = otherUserShare && Number(otherUserShare.paid_share || 0) > Number((currentUserShare && currentUserShare.paid_share) || 0)
    ? 'friend'
    : 'self';
  state.composer.splitMode = expense.split_equally ? 'equal' : 'custom';
  elements.quickPaidBy.value = state.composer.paidBy;
  elements.quickSplitMode.value = state.composer.splitMode;
  elements.quickYourShare.value = currentUserShare ? formatMoney(currentUserShare.owed_share || '0') : '';
  elements.quickFriendShare.value = otherUserShare ? formatMoney(otherUserShare.owed_share || '0') : '';
}

function renderGroupComposer() {
  const friends = availableFriends();
  elements.createGroupMembers.innerHTML = friends.length
    ? friends.map((friend) => `
        <label class="selection-option">
          <input type="checkbox" name="member_id" value="${friend.id}">
          <strong>${escapeHtml(displayName(friend))}</strong>
          <span>${escapeHtml(friend.email || 'Local friend')}</span>
        </label>
      `).join('')
    : '<p class="empty-copy">Add friends first to include them in a group.</p>';
}

function displayName(person) {
  return [person.first_name, person.last_name].filter(Boolean).join(' ') || 'Unknown';
}

function getInitials(firstName, lastName = '') {
  return [firstName, lastName]
    .filter((part) => part && part.length)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || '?';
}

function buildActivityItems(notifications, expenses) {
  const notificationItems = notifications.map((item) => ({
    kind: 'notification',
    label: 'Update',
    title: item.content || 'Notification',
    body: item.source && item.source.type ? `${item.source.type} • ${item.source.id}` : 'Recent update',
    date: item.created_at,
  }));
  const expenseItems = expenses.map((item) => ({
    kind: 'expense',
    label: 'Expense',
    title: item.description || 'Expense',
    body: `${item.currency_code || defaultCurrencyCode()} ${formatMoney(item.cost || '0')} • ${groupName(item.group_id)}`,
    date: item.date || item.created_at,
    expenseId: item.id,
  }));
  return [...notificationItems, ...expenseItems].sort((left, right) => new Date(right.date || 0) - new Date(left.date || 0));
}

function groupName(groupId) {
  const groups = Array.isArray(state.dashboard.getGroups) ? state.dashboard.getGroups : [];
  const group = groups.find((item) => item.id === groupId);
  return group ? group.name : 'No group';
}

function formatBalance(balances) {
  const primary = Array.isArray(balances) && balances[0] ? balances[0] : null;
  if (!primary) {
    return `${defaultCurrencyCode()} 0.00`;
  }
  return `${primary.currency_code || defaultCurrencyCode()} ${formatMoney(Math.abs(Number(primary.amount || 0)))}`;
}

function balanceLabel(balances) {
  const primary = Array.isArray(balances) && balances[0] ? balances[0] : null;
  if (!primary) {
    return 'settled up';
  }
  const amount = Number(primary.amount || 0);
  if (amount > 0) {
    return 'gets back';
  }
  if (amount < 0) {
    return 'owes';
  }
  return 'settled up';
}

function balanceClass(balances) {
  const primary = Array.isArray(balances) && balances[0] ? balances[0] : null;
  const amount = primary ? Number(primary.amount || 0) : 0;
  if (amount > 0) return 'amount-positive';
  if (amount < 0) return 'amount-negative';
  return 'amount-neutral';
}

function formatDateLabel(value) {
  if (!value) {
    return 'today';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
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
  if (!Number.isFinite(amount) || !Number.isInteger(count) || count <= 0) {
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

function resetWorkspaceCache() {
  state.usedOperations.clear();
  persistUsedOperations();
  state.dashboard = {};
  state.workspaceHydrated = false;
  state.groupViewId = null;
  state.selectedExpenseId = null;
  state.composer.editingExpenseId = null;
  state.composer.friendId = null;
  state.composer.groupId = 0;
  state.composer.paidBy = 'self';
  state.composer.splitMode = 'equal';
  localStorage.removeItem(DASHBOARD_CACHE_KEY);
}

function ensureAuthenticated(actionLabel, silent = false) {
  const ready = Boolean(state.config && state.config.authenticated);
  if (!ready && !silent) {
    showToast(`${actionLabel || 'Use the app'} after signing in or creating a local account`, 'error');
  }
  return ready;
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

SERVICE_WORKER_JS = """const CACHE_NAME = 'splitwise-pwa-shell-v2';
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
