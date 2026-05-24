/* =============================================
   ADMIN DASHBOARD CSS
   ============================================= */

:root {
  --bg-primary: #0d0d0f;
  --bg-secondary: #151518;
  --bg-card: #1a1a1f;
  --bg-card-hover: #202028;
  --accent: #f7931a;
  --accent-hover: #e8820a;
  --accent-green: #00c896;
  --accent-red: #ff4757;
  --accent-yellow: #ffd32a;
  --text-primary: #f0f0f5;
  --text-secondary: #9999aa;
  --text-muted: #666677;
  --border: #2a2a35;
  --radius: 12px;
  --radius-sm: 8px;
  --sidebar-width: 220px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg-primary); color: var(--text-primary); font-family: var(--font); min-height: 100vh; }
a { color: inherit; text-decoration: none; }
button { cursor: pointer; border: none; font-family: var(--font); }
input, textarea, select { font-family: var(--font); }

/* =============================================
   LAYOUT
   ============================================= */

.admin-layout { display: flex; min-height: 100vh; }

/* SIDEBAR */
.admin-sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 50;
  transition: transform 0.3s;
}

.sidebar-logo {
  padding: 20px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
}

.sidebar-logo-icon { color: var(--accent); font-size: 22px; }

.sidebar-nav { flex: 1; padding: 12px 8px; overflow-y: auto; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 2px;
  transition: all 0.2s;
  cursor: pointer;
}

.nav-item:hover { background: var(--bg-card); color: var(--text-primary); }
.nav-item.active { background: rgba(247, 147, 26, 0.15); color: var(--accent); }
.nav-item-icon { font-size: 18px; flex-shrink: 0; }

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--border);
}

/* MAIN CONTENT */
.admin-main {
  margin-left: var(--sidebar-width);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-topbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 40;
}

.topbar-title { font-size: 16px; font-weight: 700; }
.topbar-actions { display: flex; align-items: center; gap: 12px; }

.admin-content { padding: 24px; flex: 1; }

/* =============================================
   COMPONENTS
   ============================================= */

/* Stats Cards */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}

.stat-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 800; }
.stat-change { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.stat-up { color: var(--accent-green); }
.stat-down { color: var(--accent-red); }

/* Table */
.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.table-header h3 { font-size: 15px; font-weight: 700; }

table { width: 100%; border-collapse: collapse; }
th { padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border); background: var(--bg-secondary); }
td { padding: 14px 16px; font-size: 13px; border-bottom: 1px solid var(--border); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-card-hover); }

.table-empty { padding: 40px; text-align: center; color: var(--text-muted); font-size: 14px; }

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary { background: var(--accent); color: #000; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-secondary { background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border); }
.btn-secondary:hover { border-color: var(--accent); }
.btn-danger { background: #ff475722; color: var(--accent-red); border: 1px solid #ff475744; }
.btn-danger:hover { background: #ff475744; }
.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-icon { padding: 6px 8px; }

/* Forms */
.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 20px;
}

.form-card h3 { font-size: 15px; font-weight: 700; margin-bottom: 20px; }

.form-group { margin-bottom: 16px; }
.form-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }
.form-required { color: var(--accent-red); }

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font);
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus, .form-select:focus, .form-textarea:focus { border-color: var(--accent); }
.form-textarea { resize: vertical; min-height: 120px; line-height: 1.5; }
.form-select option { background: var(--bg-secondary); }
.form-hint { font-size: 11px; color: var(--text-muted); margin-top: 5px; }

/* Toggle Switch */
.toggle-wrapper { display: flex; align-items: center; gap: 10px; }
.toggle { position: relative; width: 42px; height: 24px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
  position: absolute; inset: 0;
  background: var(--border);
  border-radius: 24px;
  cursor: pointer;
  transition: 0.3s;
}
.toggle-slider:before {
  content: '';
  position: absolute;
  width: 18px; height: 18px;
  left: 3px; top: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}
.toggle input:checked + .toggle-slider { background: var(--accent); }
.toggle input:checked + .toggle-slider:before { transform: translateX(18px); }
.toggle-label { font-size: 13px; color: var(--text-secondary); }

/* Badge */
.badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-green { background: #00c89622; color: var(--accent-green); }
.badge-red { background: #ff475722; color: var(--accent-red); }
.badge-yellow { background: #ffd32a22; color: var(--accent-yellow); }
.badge-gray { background: var(--bg-secondary); color: var(--text-muted); }
.badge-buy { background: #00c89622; color: var(--accent-green); }
.badge-sell { background: #ff475722; color: var(--accent-red); }
.badge-hold { background: #ffd32a22; color: var(--accent-yellow); }

/* Alert */
.alert {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  margin-bottom: 16px;
  display: none;
}
.alert.show { display: block; }
.alert-success { background: #00c89622; color: var(--accent-green); border: 1px solid #00c89644; }
.alert-error { background: #ff475722; color: var(--accent-red); border: 1px solid #ff475744; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  display: none; align-items: center; justify-content: center;
  z-index: 200;
}
.modal-overlay.open { display: flex; }
.modal {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  width: 100%; max-width: 500px;
  margin: 16px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-header h3 { font-size: 16px; font-weight: 700; }
.modal-close { padding: 4px; color: var(--text-muted); font-size: 20px; background: none; }

/* Loading spinner */
.spinner {
  width: 20px; height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Hamburger (mobile) */
.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
}

/* =============================================
   RESPONSIVE
   ============================================= */

@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .admin-sidebar { transform: translateX(-100%); }
  .admin-sidebar.open { transform: translateX(0); }
  .admin-main { margin-left: 0; }
  .mobile-toggle { display: block; }
  .form-row { grid-template-columns: 1fr; }
  .admin-content { padding: 16px; }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr 1fr; }
  table { font-size: 12px; }
  td, th { padding: 10px 10px; }
}
