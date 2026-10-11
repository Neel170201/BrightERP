import streamlit as st
import pandas as pd
from db import connect, initialize, read_frame, hash_pw, verify_pw, fingerprint
import os
import base64
from pathlib import Path
from html import escape
from zoneinfo import ZoneInfo
from datetime import datetime as _datetime, timedelta

class datetime(_datetime):
    @classmethod
    def now(cls, tz=None):
        return super().now(tz or ZoneInfo("Asia/Kolkata"))

# Self-contained official Bright Trading copper monogram (transparent PNG).
# Embedded so deployments need no separate logo image file.
COMPANY_LOGO_URI = 'data:image/png;base64,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'
BRAND_MARK_HTML = f'<div class="brand-mark"><img src="{COMPANY_LOGO_URI}" alt="Bright Trading logo"></div>'

# ── PAGE CONFIG (must be first st call) ───────────────────────────────────
st.set_page_config(page_title="Bright • Diamond ERP", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# ── BRIGHT / NAVY & TEAL INTERFACE ──────────────────────────────────────
st.markdown("""
<style>

:root { --bg:#f4f7fb; --surface:#ffffff; --border:#e1e8f0; --border-strong:#cbd5e1; --text:#15263f; --muted:#64748b; --accent:#087f8c; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] { background:var(--bg); color:var(--text); font-family:Inter,"Segoe UI",sans-serif; }
[data-testid="stAppViewContainer"] {position:relative; overflow-x:hidden;}
[data-testid="stAppViewContainer"]::before {content:""; position:fixed; inset:0; background:url("__COMPANY_LOGO__") no-repeat center 58%; background-size:min(42vw, 490px); opacity:0.085; pointer-events:none; z-index:0;}
[data-testid="stAppViewContainer"] > .main {position:relative; z-index:1;}
[data-testid="stHeader"] {background:transparent;}
.block-container {padding-top:2rem; padding-bottom:3rem; width:94% !important; max-width:1500px !important; margin-left:auto !important; margin-right:auto !important; padding-left:1.5rem !important; padding-right:1.5rem !important;}
h1,h2,h3 {color:var(--text); letter-spacing:-.035em;}
[data-testid="stSidebar"] {background:#edf3f8; border-right:1px solid var(--border);}
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stVerticalBlock"][style*="border: 1px"] {background:white; border-radius:18px; border-color:var(--border); box-shadow:0 4px 20px #15263f05;}
.brand-header {display:flex;align-items:center;gap:14px;padding:12px 0 20px;}
.brand-mark {display:flex;align-items:center;justify-content:center;width:50px;height:50px;background:#0f2236;border-radius:14px;overflow:hidden;flex-shrink:0;box-shadow:0 6px 16px rgba(16,40,66,.10);}
.brand-mark img {width:100%;height:100%;object-fit:contain;display:block;padding:7px;}
.brand-name {font-size:16px;font-weight:750;letter-spacing:.04em;margin:0;}
.breadcrumb {font-size:12px;color:var(--muted);margin-top:4px;}
.hero {position:relative;overflow:hidden;background:linear-gradient(115deg,#102842 0%,#163b54 68%,#14656c 100%);border-radius:24px;padding:34px 38px;margin:4px 0 26px;color:white;}
.hero:after {content:"";position:absolute;right:22px;top:-20px;width:260px;height:260px;background:url("__COMPANY_LOGO__") center/contain no-repeat;opacity:.20;pointer-events:none;}
.eyebrow {font-size:11px;font-weight:700;letter-spacing:.17em;text-transform:uppercase;color:#88dcd8;margin-bottom:14px;}
.hero h1 {font-size:34px;font-weight:700;line-height:1.2;color:white;margin:0 0 10px;padding:0;}
.hero p {color:#cfdee9;font-size:14px;margin:0;max-width:640px;}
.hero-footer {display:flex;gap:10px;flex-wrap:wrap;margin-top:24px;}
.hero-chip {border:1px solid #ffffff28;border-radius:30px;padding:6px 12px;font-size:11px;color:#e1f1f7;background:#ffffff08;}
.login-brand {text-align:center;padding:14px 4px 20px;}
.login-brand .brand-mark {margin:0 auto 18px;width:72px;height:72px;}
.login-brand h2 {font-size:24px;margin:8px 0;}
.login-brand p {font-size:13px;color:var(--muted);}
.module-card {position:relative;min-height:110px;padding:2px 4px 0;border-radius:18px;transition:transform .24s ease, filter .24s ease;}
.module-card::after {content:"";position:absolute;inset:auto 0 -10px 0;height:18px;background:radial-gradient(circle, rgba(16,40,66,.12) 0%, rgba(16,40,66,0) 72%);filter:blur(10px);opacity:0;transition:opacity .24s ease;pointer-events:none;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card) {transition:transform .24s ease, box-shadow .24s ease, border-color .24s ease, background .24s ease;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card):hover {transform:translateY(-7px); box-shadow:0 18px 38px rgba(21,38,63,.12); border-color:#bfd0e3; background:linear-gradient(180deg,#ffffff 0%,#fbfdff 100%);}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card):hover .module-card {transform:translateY(-1px);}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card):hover .module-card::after {opacity:1;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card):hover .module-icon {transform:scale(1.05) translateY(-1px); box-shadow:0 14px 26px rgba(21,38,63,.16);} 
.module-icon {position:relative;display:inline-flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:14px;font-size:21px;font-weight:700;margin-bottom:12px;background:linear-gradient(145deg,var(--icon-bg,#e6f5f4),#ffffff);color:var(--icon-color,#102842);box-shadow:0 10px 22px rgba(21,38,63,.10), inset 0 1px 0 rgba(255,255,255,.95);border:1px solid rgba(255,255,255,.92);transition:transform .24s ease, box-shadow .24s ease;}
.module-icon::before {content:"";position:absolute;inset:4px;border-radius:11px;background:linear-gradient(180deg, rgba(255,255,255,.78), rgba(255,255,255,0));pointer-events:none;}
.module-icon .glyph {position:relative;line-height:1; display:block; transform:translateY(-.5px);} 
.module-title {font-size:14px;font-weight:800;color:var(--text);margin:0 0 6px;letter-spacing:-.01em;}
.module-copy {font-size:12px;line-height:1.5;color:var(--muted);margin:0 0 4px;}
.kpi-card {background:white;border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:15px;padding:18px 16px;min-height:148px;box-shadow:0 4px 16px #15263f04;}
.kpi-icon {display:block;font-size:19px;margin-bottom:10px;}
.kpi-label {font-size:10px;letter-spacing:.07em;font-weight:650;color:var(--muted);margin:0 0 6px;}
.kpi-value {font-size:clamp(19px,2vw,29px);font-weight:750;color:var(--text);margin:0;letter-spacing:-.035em;overflow-wrap:anywhere;}
.kpi-sub {font-size:11px;color:var(--muted);margin:6px 0 0;}
.kpi-up {color:#15803d;} .kpi-down {color:#b91c1c;}
.section-header {display:flex;align-items:center;gap:10px;margin:12px 0;}
.section-header .icon {background:#e5f3f3;padding:9px;border-radius:12px;font-size:20px;}
.section-header .title {font-size:24px;font-weight:700;letter-spacing:-.03em;color:var(--text);}
.section-divider {height:1px;background:var(--border);margin-bottom:22px;}
.stButton button,.stDownloadButton button,[data-testid="stFormSubmitButton"] button {border-radius:14px;min-height:44px;border:1px solid #c9d6e6;background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%);color:#18324b;font-weight:700;letter-spacing:.01em;box-shadow:0 8px 20px rgba(21,38,63,.06), inset 0 1px 0 rgba(255,255,255,.95);transition:transform .18s ease, box-shadow .18s ease, background .18s ease, border-color .18s ease, color .18s ease;}
.stButton button:hover,.stDownloadButton button:hover,[data-testid="stFormSubmitButton"] button:hover {transform:translateY(-2px);border-color:#8eb9c0;color:#0f5160;background:linear-gradient(180deg,#ffffff 0%,#effafa 100%);box-shadow:0 14px 26px rgba(8,127,140,.14);} 
button[kind="primary"] {background:linear-gradient(135deg,#0a8d98 0%,#0f6f86 100%)!important;border-color:#0a8d98!important;color:white!important;box-shadow:0 12px 24px rgba(8,127,140,.24)!important;}
button[kind="primary"] p {color:white!important;}
button[kind="primary"]:hover {background:linear-gradient(135deg,#0c9ca6 0%,#0b6c82 100%)!important;transform:translateY(-2px);box-shadow:0 16px 28px rgba(8,127,140,.30)!important;}
button:focus-visible {outline:3px solid #38b6c0!important;outline-offset:3px;}
[data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stDateInput"] [data-baseweb="input"], [data-baseweb="select"] > div, [data-testid="stTextArea"] textarea {border-radius:10px;background:white;color:var(--text);border-color:var(--border-strong);}
[data-testid="stWidgetLabel"] p {font-size:12px;font-weight:600;color:#52647b;}
[data-testid="stDataFrame"], [data-testid="stDataEditor"], [data-testid="stPlotlyChart"] {border:1px solid var(--border);border-radius:14px;overflow:hidden;}
[data-testid="stFileUploaderDropzone"] {background:#edf7f9;border:1px dashed #76b8c0;border-radius:16px;padding:26px;}
[data-baseweb="tab-list"] {gap:8px;border-bottom:1px solid var(--border);}
[data-baseweb="tab"] {border-radius:9px 9px 0 0;padding:10px 16px;color:var(--muted);}
[data-baseweb="tab"][aria-selected="true"] {background:#e5f3f3;color:#076b76;}
[data-baseweb="tab-highlight"] {background:#087f8c;}
[data-testid="stExpander"] {background:white;border-color:var(--border);border-radius:12px;}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stMetric"] {background:white;border:1px solid var(--border);border-radius:14px;padding:16px;}
@media(max-width:700px) {.block-container {width:100% !important; padding:1rem !important;} .hero {padding:26px 22px;} .hero h1 {font-size:26px;} .brand-name {font-size:12px;} .module-card {min-height:0;} .kpi-card {min-height:125px;} }
@media(max-width:700px) {[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card):hover {transform:none;}}
@media(prefers-reduced-motion:reduce) {* {transition:none!important;}}
</style>
""".replace("__COMPANY_LOGO__", COMPANY_LOGO_URI), unsafe_allow_html=True)

# ── SHARED UI HELPERS ───────────────────────────────────────────────────────
def _section_header(icon, title):
    """Big page-section title with icon and gradient divider (used across all tabs)."""
    return (
        f'<div class="section-header"><span class="icon">{icon}</span>'
        f'<span class="title">{title}</span></div>'
        f'<div class="section-divider"></div>'
    )

def _label(text, margin_bottom=8):
    """Small muted label used above filters / sub-sections."""
    return (
        f'<p style="font-size:12px;color:#737373;'
        f'margin-bottom:{margin_bottom}px;">{text}</p>'
    )

def bulk_upload_stock(conn, df, upload_time, progress=None, batch_size=1000):
    """Upload stock in batches, retaining existing lot/export and return rules."""
    import math
    columns = ['buyer_name', 'buying_date', 'party_name', 'report_no', 'lab',
               'diamond_type', 'shape', 'cts', 'color', 'clarity', 'per_carat',
               'amount', 'bank_rate', 'inr_pc', 'inr_total', 'location', 'remark',
               'upload_time']
    inputs = ['BUYER NAME', 'DATE', 'PARTY NAME', 'REPORT', 'LAB', 'TYPE', 'SHAPE',
              'CTS', 'COL', 'CLA', 'PER CARAT', 'AMT', 'BANK RATE', 'INR_PC',
              'INR_TOTAL', 'LOCATION', 'REMARK']
    numeric = {'CTS', 'PER CARAT', 'AMT', 'BANK RATE', 'INR_PC', 'INR_TOTAL'}
    rows = []
    # Validate before any writes and adapt numpy values to ordinary Python values.
    for number, values in enumerate(df[inputs].itertuples(index=False, name=None), 2):
        record = []
        for name, value in zip(inputs, values):
            if name in numeric:
                try:
                    value = float(value)
                    if not math.isfinite(value):
                        raise ValueError()
                except (ValueError, TypeError):
                    raise ValueError(f'Excel row {number}: invalid number in {name}. No data saved.') from None
            else:
                value = str(value)
                if name == 'REPORT':
                    value = value.strip()
                    if not value:
                        raise ValueError(f'Excel row {number}: REPORT is blank. No data saved.')
            record.append(value)
        rows.append(tuple(record) + (upload_time,))
    if not rows:
        return 0, 0, []
    updates = ', '.join(f'{col}=EXCLUDED.{col}' for col in columns if col != 'report_no')
    updates += ", stock_status=CASE WHEN buying_stock.stock_status='RETURN' THEN CASE WHEN COALESCE(buying_stock.lot_no,'')<>'' THEN 'LOT' ELSE 'LIVE' END ELSE buying_stock.stock_status END"
    updates += ", return_date=CASE WHEN buying_stock.stock_status='RETURN' THEN NULL ELSE buying_stock.return_date END"
    inserted = updated = 0
    lot_warnings = []
    cur = conn.raw.cursor()
    try:
        # Same transaction lock as lot generation; no overlapping lot assignment/upload.
        cur.execute('SELECT pg_advisory_xact_lock(728190402)')
        for start in range(0, len(rows), batch_size):
            batch = rows[start:start + batch_size]
            reports = list(dict.fromkeys(row[3] for row in batch))
            cur.execute('SELECT report_no,stock_status,lot_no FROM buying_stock WHERE report_no=ANY(%s) FOR UPDATE', (reports,))
            existing = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
            unique = {}
            for row in batch:
                report = row[3]
                if report in existing:
                    status, lot = existing[report]
                    if status == 'LOT' and lot:
                        lot_warnings.append(f'{report} (Lot: {lot})')
                    if status == 'RETURN':
                        existing[report] = ('LOT' if lot else 'LIVE', lot)
                    updated += 1
                else:
                    inserted += 1
                    existing[report] = ('LIVE', None)
                # Last occurrence wins, as with the previous sequential uploader.
                unique[report] = row
            values = list(unique.values())
            template = '(' + ','.join(['%s'] * len(columns)) + ",'LIVE')"
            query = 'INSERT INTO buying_stock (' + ','.join(columns) + ',stock_status) VALUES '
            query += ','.join([template] * len(values))
            query += ' ON CONFLICT (report_no) DO UPDATE SET ' + updates
            cur.execute(query, tuple(value for row in values for value in row))
            if progress:
                progress(min((start + len(batch)) / len(rows), 1.0))
        conn.commit()
        return inserted, updated, lot_warnings
    except BaseException:
        conn.rollback()
        raise
    finally:
        cur.close()


def read_uploaded_excel(uploaded):
    import hashlib
    import io
    payload = uploaded.getvalue()
    token = hashlib.sha256(payload).hexdigest()
    cached = st.session_state.get("parsed_excel")
    if cached is None or cached[0] != token:
        cached = (token, pd.read_excel(io.BytesIO(payload)))
        st.session_state["parsed_excel"] = cached
    return cached[1].copy(deep=True)


# ── DATABASE ──────────────────────────────────────────────────────────────
def setting(name):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets.get(name, "")
    except FileNotFoundError:
        return ""

url = setting("DATABASE_URL")
if not url:
    st.info("Set DATABASE_URL in Streamlit Secrets to connect to Neon. See README.md.")
    st.stop()

@st.cache_resource(show_spinner=False)
def prepare_database(database_url, admin_username, admin_password):
    initialize(database_url, admin_username, admin_password)
    return True

try:
    prepare_database(url, setting("BOOTSTRAP_ADMIN_USERNAME") or "admin", setting("BOOTSTRAP_ADMIN_PASSWORD"))
    conn = connect(url)
except Exception as exc:
    # Classify internally; never print exception text or connection credentials.
    detail = str(exc).lower()
    state = getattr(exc, "sqlstate", None)
    if "bootstrap_admin_password" in detail:
        message = "ADMIN_PASSWORD: Set BOOTSTRAP_ADMIN_PASSWORD in Streamlit Secrets to a quoted password with at least 12 characters."
    elif "password authentication failed" in detail or state == "28P01":
        message = "DB_PASSWORD: Neon rejected the database password. Copy the latest full connection URL after resetting the Neon password."
    elif "could not translate host name" in detail or "name or service not known" in detail or "failed to resolve" in detail:
        message = "DB_HOST: The Neon hostname could not be resolved. Re-copy the full connection URL and check Neon project status."
    elif "timeout" in detail or "timed out" in detail:
        message = "DB_TIMEOUT: Neon did not respond in time. Check project status, then reboot the Streamlit app."
    elif "channel binding" in detail or "ssl" in detail or "tls" in detail:
        message = "DB_TLS: Secure connection failed. Use a freshly copied Neon connection URL including its sslmode settings."
    elif state == "42501":
        message = "DB_PERMISSION: The selected Neon role does not have permission to create the app tables."
    elif "missing \"=\"" in detail or "invalid dsn" in detail or "invalid uri" in detail:
        message = "DB_URL: DATABASE_URL must contain only the full postgresql:// URL, without psql or surrounding single quotes."
    else:
        # Whitelist diagnostic identifiers instead of exposing a potentially sensitive error.
        kind = type(exc).__name__
        safe_kind = kind if kind.isidentifier() else "UnknownError"
        safe_state = state if isinstance(state, str) and len(state) == 5 and state.isalnum() else "none"
        message = f"DB_SETUP: {safe_kind}; SQLSTATE={safe_state}. Share this error code for troubleshooting."
    st.error(message)
    st.stop()
try:
    cursor = conn.cursor()

    def check_login(username: str, password: str):
        cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if not row or password == "admin123" or not verify_pw(password, row[0]):
            return None
        if not row[0].startswith("pbkdf2_sha256$"):
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hash_pw(password), username))
            conn.commit()
        return row[1]

    def login_screen():
        st.markdown("""
<style>
[data-testid="stAppViewContainer"]:has(.bt-login-brand)::before {display:none;}
.block-container:has(.bt-login-brand) {max-width:1240px!important;padding-top:5vh!important;}
[data-testid="stHorizontalBlock"]:has(.bt-login-brand) {gap:0!important;align-items:stretch;background:white;border-radius:24px;overflow:hidden;box-shadow:0 24px 70px #10284218;border:1px solid #e5eaf0;}
[data-testid="stColumn"]:has(.bt-login-brand) {background:linear-gradient(145deg,#102842,#071a2c);}
.bt-login-brand {position:relative;min-height:650px;padding:48px 46px 32px;overflow:hidden;color:white;box-sizing:border-box;}
.bt-login-brand img {width:76px;height:76px;object-fit:contain;margin-bottom:14px;}
.bt-company {font-size:12px;letter-spacing:.22em;color:#d6a17b;}
.bt-rule {width:48px;height:1px;background:#c89570;margin:28px 0;}
.bt-login-brand h1 {font-size:43px;line-height:1.16;letter-spacing:-.035em;color:#fff;font-weight:600;margin:0 0 20px;max-width:450px;}
.bt-login-brand p {font-size:16px;line-height:1.7;color:#9dbacf;max-width:390px;position:relative;z-index:1;}
.bt-diamond {display:block;width:85%;height:220px;margin:4px 0 0 auto;filter:drop-shadow(0 12px 24px #b8733340);}
.bt-tagline {font-size:12px;color:#cf9b75;margin-top:18px;}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .bt-login-heading) {padding:64px 42px 26px;}
.bt-login-heading h2 {font-size:34px;margin:0 0 6px;color:#102842;}
.bt-login-heading p {color:#79869a;font-size:16px;margin:0 0 24px;}
[data-testid="stForm"]:has(input[aria-label="Username"]) {border:0;padding:0;}
.bt-login-help {text-align:center;color:#64748b;font-size:13px;line-height:1.8;margin:22px 0 18px;}
.bt-login-help strong {color:#102842;font-weight:500;}
.bt-login-footer {text-align:center;font-size:11px;letter-spacing:.08em;color:#8793a4;margin:28px 0 0;}
@media(max-width:760px) {
[data-testid="stHorizontalBlock"]:has(.bt-login-brand) {flex-direction:column;}
[data-testid="stHorizontalBlock"]:has(.bt-login-brand)>[data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;}
.bt-login-brand {min-height:0;padding:28px;}
.bt-login-brand img {width:50px;height:50px;}
.bt-login-brand h1 {font-size:30px;}
.bt-diamond,.bt-tagline {display:none;}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .bt-login-heading) {padding:30px 24px;}
}
</style>
""", unsafe_allow_html=True)
        brand, form_panel = st.columns([1.08, 1], gap="small")
        with brand:
            st.markdown(
                '<div class="bt-login-brand">'
                f'<img src="{COMPANY_LOGO_URI}" alt="Bright Trading logo">'
                '<div class="bt-company">BRIGHT TRADING INDIA LLP</div><div class="bt-rule"></div>'
                '<h1>Your diamond operations, beautifully organised.</h1>'
                '<p>Manage inventory, lots, and trading operations in one workspace.</p>'
                '<svg class="bt-diamond" viewBox="0 0 460 240" aria-hidden="true">'
                '<defs><linearGradient id="facet" x2="1" y2="1"><stop stop-color="#d8ab83" stop-opacity=".38"/><stop offset="1" stop-color="#b87333" stop-opacity=".03"/></linearGradient></defs>'
                '<g fill="url(#facet)" stroke="#d6a17b" stroke-width="1.2" stroke-linejoin="round">'
                '<path d="M35 70 120 20 330 20 425 70 230 220Z"/>'
                '<path d="M35 70H425M120 20 145 70 230 220 305 70 330 20M145 70 230 20 305 70M35 70 230 220 425 70M120 20 230 20 330 20"/>'
                '</g></svg><div class="bt-tagline">Built for clarity. Designed for your business.</div></div>',
                unsafe_allow_html=True,
            )
        with form_panel:
            with st.container():
                st.markdown('<div class="bt-login-heading"><h2>Welcome back</h2><p>Sign in to your workspace</p></div>', unsafe_allow_html=True)
                with st.form("bright_login", clear_on_submit=False):
                    username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                    password = st.text_input("Password", key="login_pass", placeholder="Enter your password", type="password")
                    submitted = st.form_submit_button("Sign in →", type="primary", use_container_width=True)
                if submitted:
                    role = check_login(username.strip(), password.strip())
                    if role:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username.strip()
                        st.session_state["role"] = role
                        _save_session_to_params(username.strip(), role)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                st.markdown('<div class="bt-login-help"><strong>Trouble signing in?</strong><br>Contact your administrator</div>', unsafe_allow_html=True)
                with st.expander("Change password"):
                    fp_uname     = st.text_input("USERNAME", key="fp_uname", placeholder="Your username")
                    fp_old_pass  = st.text_input("CURRENT PASSWORD", key="fp_old_pass", placeholder="Enter current password", type="password")
                    fp_new_pass  = st.text_input("NEW PASSWORD", key="fp_new_pass", placeholder="Enter new password", type="password")
                    fp_new_pass2 = st.text_input("CONFIRM NEW PASSWORD", key="fp_new_pass2", placeholder="Re-enter new password", type="password")
                    if st.button("Update password", key="fp_reset_btn", use_container_width=True):
                        if not fp_uname.strip() or not fp_old_pass.strip() or not fp_new_pass.strip() or not fp_new_pass2.strip():
                            st.warning("Please fill in all fields.")
                        elif fp_new_pass != fp_new_pass2:
                            st.warning("New password and confirm password do not match.")
                        elif len(fp_new_pass.strip()) < 12:
                            st.warning("New password should be at least 12 characters.")
                        else:
                            role_check = check_login(fp_uname.strip(), fp_old_pass.strip())
                            if not role_check:
                                st.error("❌ Username or current password is incorrect.")
                            else:
                                cursor.execute(
                                    "UPDATE users SET password=? WHERE username=?",
                                    (hash_pw(fp_new_pass.strip()), fp_uname.strip()),
                                )
                                conn.commit()
                                st.success("✅ Password updated successfully. Please sign in with your new password.")

                st.markdown('<div class="bt-login-footer">Bright Trading India LLP</div>', unsafe_allow_html=True)

    # Login stays in server-side session state; never restore authentication from a URL.
    SESSION_EXPIRY_HOURS = 24

    def _save_session_to_params(username, role):
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        st.session_state["credential_fingerprint"] = fingerprint(cursor.fetchone()[0])
        st.session_state["login_time"] = datetime.now().timestamp()
        st.query_params.clear()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"]  = ""
        st.session_state["role"]      = ""

    if st.session_state["logged_in"]:
        cursor.execute("SELECT password, role FROM users WHERE username=?", (st.session_state["username"],))
        user = cursor.fetchone()
        expired = datetime.now().timestamp() - st.session_state.get("login_time", 0) > 24 * 3600
        if not user or expired or fingerprint(user[0]) != st.session_state.get("credential_fingerprint"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()
        st.session_state["role"] = user[1]

    if not st.session_state["logged_in"]:
        login_screen()
        st.stop()

    # ── HEADER BANNER ──────────────────────────────────────────────────────────
    is_admin = st.session_state["role"] == "admin"
    is_video = st.session_state["role"] == "video"

    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    # Full catalogue of sections, keyed by the same names used below for routing.
    # Each entry: (icon, label, visible_to_video, visible_to_others)
    _NAV_ITEMS = [
        ("upload", "↥", "Buying Upload",   False, True),
        ("stock",  "◈", "Buying Stock",    False, True),
        ("lot",    "⌘", "Lot Generated",   True,  True),
        ("return", "↺", "Return Stones",   False, True),
        ("export", "➜", "Export Stones",   False, True),
        ("admin",  "⚙", "Admin",           False, is_admin),
    ]

    def _visible_nav_items():
        items = []
        for key, icon, label, vis_video, vis_other in _NAV_ITEMS:
            if is_video and vis_video:
                items.append((key, icon, label))
            elif not is_video and vis_other:
                items.append((key, icon, label))
        return items

    _nav = _visible_nav_items()
    _page_labels = {key: (icon, label) for key, icon, label in _nav}

    h_col1, h_col2 = st.columns([5, 1.4])
    with h_col1:
        if st.session_state["page"] == "home":
            _crumb = "Home"
        else:
            _icon, _lbl = _page_labels.get(st.session_state["page"], ("💎", "Home"))
            _crumb = f"Home / {_lbl}"
        st.markdown(
            '<div class="brand-header">' + BRAND_MARK_HTML + '<div>'
            '<div class="brand-name">BRIGHT TRADING INDIA LLP</div>'
            f'<div class="breadcrumb">Diamond operations &nbsp; / &nbsp; {escape(_crumb)}</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    with h_col2:
        with st.container(border=True):
            st.markdown(
                f'<p style="font-size:13px;color:#171717;margin:0 0 2px;font-weight:500;">{escape(str(st.session_state["username"]))}</p>'
                f'<p style="font-size:12px;color:#737373;margin:0 0 8px;">{escape(str(st.session_state["role"]))}</p>',
                unsafe_allow_html=True,
            )
            if st.button("Sign Out", key="logout_btn", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["username"]  = ""
                st.session_state["role"]      = ""
                st.query_params.clear()
                st.rerun()

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

    # ── BACK-TO-HOME BAR (shown on every page except Home) ────────────────────
    if st.session_state["page"] != "home":
        if st.button("← Back to Home", key="back_home_btn"):
            st.session_state["page"] = "home"
            st.rerun()
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    # ── HOME GRID (Lattice-style card launcher) ────────────────────────────────
    if st.session_state["page"] == "home":
        st.markdown(
            '<div class="hero"><div class="eyebrow">YOUR OPERATIONS, CONNECTED</div>'
            f'<h1>Welcome, {escape(str(st.session_state["username"]))}.</h1>'
            '<p>From buying to export. Keep every stone, every lot and every next step in view.</p>'
            '<div class="hero-footer"><span class="hero-chip">Diamond inventory ERP</span>'
            f'<span class="hero-chip">{datetime.now().strftime("%d %b %Y")} · IST</span>'
            f'<span class="hero-chip">{len(_nav)} available modules</span></div></div>',
            unsafe_allow_html=True,
        )

        _search = st.text_input(
            "Search for Actions",
            key="home_search",
            placeholder="Search your workspace — stock, lots, exports…",
            label_visibility="collapsed",
        )

        st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

        _filtered = [
            (key, icon, label) for key, icon, label in _nav
            if _search.strip().lower() in label.lower()
        ] if _search.strip() else _nav

        st.markdown(_section_header("◇", "Your workspace"), unsafe_allow_html=True)
        _module_details = {
            "upload": {"tint":"#eef8f3", "desc":"Import buying files and review incoming stones.", "icon":"⤴", "icon_bg":"#e4f5ea", "icon_color":"#1e7a46"},
            "stock": {"tint":"#eef4ff", "desc":"Explore inventory, filter stones and review values.", "icon":"⬢", "icon_bg":"#e5eeff", "icon_color":"#315ea8"},
            "lot": {"tint":"#f4efff", "desc":"Create lots and follow your processing workflow.", "icon":"✦", "icon_bg":"#ece3ff", "icon_color":"#6d43c6"},
            "return": {"tint":"#fff2ef", "desc":"Manage returned stones and review return records.", "icon":"↩", "icon_bg":"#ffe2db", "icon_color":"#d6523c"},
            "export": {"tint":"#eef8ff", "desc":"Prepare shipments and manage exported stones.", "icon":"➤", "icon_bg":"#e1f1ff", "icon_color":"#1f7db5"},
            "admin": {"tint":"#fff8e9", "desc":"Manage users, access and shape mappings.", "icon":"✧", "icon_bg":"#fff0c8", "icon_color":"#a06a00"},
        }
        _cards_per_row = 4
        for _row_start in range(0, len(_filtered), _cards_per_row):
            _row_items = _filtered[_row_start:_row_start + _cards_per_row]
            _cols = st.columns(_cards_per_row)
            for _i, _col in enumerate(_cols):
                if _i < len(_row_items):
                    _key, _icon, _label = _row_items[_i]
                    _meta = _module_details[_key]
                    with _col:
                        with st.container(border=True):
                            st.markdown(
                                f'<div class="module-card" style="--tint:{_meta["tint"]}; --icon-bg:{_meta["icon_bg"]}; --icon-color:{_meta["icon_color"]};">'
                                f'<div class="module-icon"><span class="glyph">{_meta["icon"]}</span></div>'
                                f'<p class="module-title">{_label}</p>'
                                f'<p class="module-copy">{_meta["desc"]}</p></div>',
                                unsafe_allow_html=True,
                            )
                            if st.button(f"Open {_label} →", key=f"nav_card_{_key}", use_container_width=True):
                                st.session_state["page"] = _key
                                st.rerun()
        if not _filtered:
            st.info("No matching actions found.")
        st.stop()

    # ── ROUTING FLAGS (replace the old st.tabs() tab objects) ─────────────────
    _page = st.session_state["page"]
    tab1        = _page == "upload"
    tab2        = _page == "stock"
    tab3        = _page == "lot"
    tab4        = _page == "return"
    tab_export  = _page == "export"
    tab5        = _page == "admin"

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — BUYING FILE UPLOAD
    # ══════════════════════════════════════════════════════════════════════════
    if not is_video:
        if tab1:
            st.markdown(_section_header("📂", "Upload Buying File"), unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload Buying Excel File (.xlsx)",
                type=["xlsx"],
                key="buying_upload",
            )

            if uploaded_file:
                df = read_uploaded_excel(uploaded_file)

                # Normalise column names
                df.columns = df.columns.str.strip().str.upper()

                # Coerce numeric columns
                for col in ["CTS", "PER CARAT", "BANK RATE"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

                # ── AMT ab file se nahi, PER CARAT * CTS se calculate hoga ──────
                if "CTS" in df.columns and "PER CARAT" in df.columns:
                    df["AMT"] = (
                        pd.to_numeric(df["CTS"], errors="coerce").fillna(0)
                        * pd.to_numeric(df["PER CARAT"], errors="coerce").fillna(0)
                    )

                # ── INR P/C aur INR TOTAL upload time pe hi calculate ───────────
                if "BANK RATE" in df.columns:
                    _br = pd.to_numeric(df["BANK RATE"], errors="coerce").fillna(0)
                    df["INR_PC"]    = round(pd.to_numeric(df.get("PER CARAT", 0), errors="coerce").fillna(0) * _br, 2)
                    df["INR_TOTAL"] = round(pd.to_numeric(df.get("AMT", 0),       errors="coerce").fillna(0) * _br, 2)
                else:
                    df["INR_PC"]    = 0
                    df["INR_TOTAL"] = 0

                # Date column ab jaisi upload hui waisi hi rakhni hai (no reformatting)
                if "DATE" in df.columns:
                    def _keep_date_as_is(v):
                        if pd.isna(v):
                            return ""
                        if hasattr(v, "strftime"):
                            return v.strftime("%d-%m-%Y")
                        return str(v).strip()
                    df["DATE"] = df["DATE"].apply(_keep_date_as_is)

                df = df.fillna("")

                if "LOCATION" not in df.columns:
                    df["LOCATION"] = ""

                # ── Uppercase: in columns ko upper case karna he ────────────────
                for _uc in ["BUYER NAME", "PARTY NAME", "LAB", "TYPE", "SHAPE", "COL", "CLA", "LOCATION", "REMARK"]:
                    if _uc in df.columns:
                        df[_uc] = df[_uc].astype(str).str.strip().str.upper()

                # ── Apply shape mappings from DB ───────────────────────────────
                _shape_maps = read_frame(
                    "SELECT alias, mapped_to FROM shape_mappings", conn
                )
                _shape_map_dict = {
                    str(r["alias"]).strip().upper(): str(r["mapped_to"]).strip().upper()
                    for _, r in _shape_maps.iterrows()
                }
                if "SHAPE" in df.columns and _shape_map_dict:
                    df["SHAPE"] = df["SHAPE"].apply(
                        lambda s: _shape_map_dict.get(s, s)
                    )

                st.subheader("📄 File Preview (first 20 rows)")
                st.dataframe(df.head(20), use_container_width=True)

                REQUIRED = [
                    "BUYER NAME", "DATE", "PARTY NAME", "REPORT", "LAB",
                    "TYPE", "SHAPE", "CTS", "COL", "CLA",
                    "PER CARAT", "BANK RATE", "REMARK",
                ]
                missing = [c for c in REQUIRED if c not in df.columns]

                if missing:
                    st.error(f"❌ Missing columns: {missing}")
                else:
                    if st.button("🚀 Upload to SQL", key="upload_sql_btn"):
                        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        progress = st.progress(0)
                        try:
                            inserted, reactivated, lot_already_certs = bulk_upload_stock(
                                conn, df, upload_time, progress=progress.progress
                            )
                        except ValueError as exc:
                            st.error(str(exc))
                            st.stop()
                        except Exception:
                            st.error("Upload failed. No changes from this upload were saved. Please retry; if it repeats, contact your app administrator.")
                            st.stop()
                        st.success(f"✅ {inserted} new stones uploaded")
                        if reactivated:
                            st.info(f"♻️ {reactivated} existing stones updated (data overwritten)")
                        if lot_already_certs:
                            st.markdown(
                                f'<div style="background:#fef2f2;border:1px solid #fecaca;border-left:4px solid #ef4444;'
                                f'border-radius:8px;padding:14px 18px;margin-top:10px;">'
                                f'<p style="color:#991b1b;font-size:13px;font-weight:700;margin:0 0 8px;">🚫 Already Lot Generated — {len(lot_already_certs)} Certificate(s)</p>'
                                f'<p style="color:#b91c1c;font-size:12px;margin:0 0 6px;">A lot has already been generated for the following certificates:</p>'
                                f'<ul style="color:#991b1b;font-size:12px;margin:4px 0 0 16px;padding:0;line-height:1.9;">'
                                + "".join(f"<li>{c}</li>" for c in lot_already_certs) +
                                f'</ul></div>',
                                unsafe_allow_html=True,
                            )

        # ══════════════════════════════════════════════════════════════════════════
        # TAB 2 — Buying Stock
        # ══════════════════════════════════════════════════════════════════════════
    if not is_video:
        if tab2:
            # Header
            st.markdown(_section_header("📦", "Buying Stock"), unsafe_allow_html=True)

            # Filters — 6 columns including Status
            st.markdown(_label("🔎  Filters", margin_bottom=6), unsafe_allow_html=True)
            fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
            report_filter = fc1.text_input("REPORT NO",  key="report_filter",  placeholder="LG123…")
            party_filter  = fc2.text_input("PARTY",       key="party_filter",   placeholder="Party name…")
            shape_filter  = fc3.text_input("SHAPE",       key="shape_filter",   placeholder="ROUND, OVAL…")
            date_filter_d = fc4.date_input("DATE", value=None, key="date_filter", format="DD-MM-YYYY")
            date_filter   = date_filter_d.strftime("%d-%m-%Y") if date_filter_d else ""
            remark_filter = fc5.text_input("REMARK",      key="remark_filter",  placeholder="Any remark…")
            status_filter = fc6.selectbox(
                "STATUS", key="status_filter",
                options=["All", "Not Processed", "Lot Generated"],
            )

            # Filter in PostgreSQL; only one page is transferred to the browser.
            base_where = "stock_status IN ('LIVE','LOT') AND (exported_at IS NULL OR exported_at='')"
            clauses = [base_where]
            params = []
            for value, column in [(report_filter, 'report_no'), (party_filter, 'party_name'),
                                  (shape_filter, 'shape'), (date_filter, 'buying_date'), (remark_filter, 'remark')]:
                if value:
                    clauses.append(f"POSITION(LOWER(?) IN LOWER(COALESCE({column},''))) > 0")
                    params.append(value)
            if status_filter != 'All':
                clauses.append('stock_status=?')
                params.append('LIVE' if status_filter == 'Not Processed' else 'LOT')
            where_sql = ' AND '.join(clauses)
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(cts),0), COALESCE(SUM(amount),0), "
                           "COALESCE(SUM(amount*COALESCE(bank_rate,0)),0) FROM buying_stock WHERE " + where_sql, params)
            total_stones, total_cts, total_amt, total_inr = cursor.fetchone()
            total_cts, total_amt, total_inr = [round(float(v),2) for v in (total_cts,total_amt,total_inr)]
            cursor.execute("SELECT COUNT(*) FILTER (WHERE stock_status='LIVE'), "
                           "COUNT(*) FILTER (WHERE stock_status='LOT') FROM buying_stock WHERE " + base_where)
            live_count_bs, lot_count_bs = cursor.fetchone()
            page_size = 200
            page_count = max(1, (total_stones + page_size - 1)//page_size)
            filter_signature = tuple(params) + (where_sql,)
            if st.session_state.get('stock_filter_signature') != filter_signature:
                st.session_state['stock_page'] = 1
                st.session_state['stock_filter_signature'] = filter_signature
            st.session_state['stock_page'] = min(st.session_state.get('stock_page',1), page_count)
            page = st.number_input('Page', min_value=1, max_value=page_count, step=1, key='stock_page')
            stock_select = "SELECT buyer_name,buying_date,party_name,report_no,lab,diamond_type,shape,cts,color,clarity,per_carat,amount,bank_rate,location,remark,inr_pc,inr_total,stock_status FROM buying_stock WHERE "
            fdf = read_frame(stock_select + where_sql + ' ORDER BY id DESC LIMIT ? OFFSET ?', conn,
                             params=params + [page_size,(page-1)*page_size])
            st.caption(f"Page {page} of {page_count} · {total_stones:,} matching stones · 200 per page. Totals and Excel include all matching stones. Column sorting applies to the current page.")

            st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
            km1, km2, km3, km4, km5, km6 = st.columns(6)
            km1.markdown(
                f'<div class="kpi-card" style="--accent:#171717;">'
                f'<span class="kpi-icon">💎</span>'
                f'<p class="kpi-label">TOTAL STONES</p>'
                f'<p class="kpi-value">{total_stones:,}</p>'
                f'<p class="kpi-sub">in buying stock</p>'
                f'</div>', unsafe_allow_html=True,
            )
            km2.markdown(
                f'<div class="kpi-card" style="--accent:#3b82f6;">'
                f'<span class="kpi-icon">📦</span>'
                f'<p class="kpi-label">TOTAL CARATS</p>'
                f'<p class="kpi-value">{total_cts:,}</p>'
                f'<p class="kpi-sub">total weight</p>'
                f'</div>', unsafe_allow_html=True,
            )
            km3.markdown(
                f'<div class="kpi-card" style="--accent:#22c55e;">'
                f'<span class="kpi-icon">💵</span>'
                f'<p class="kpi-label">TOTAL AMT USD</p>'
                f'<p class="kpi-value">${total_amt:,.0f}</p>'
                f'<p class="kpi-sub">buying value</p>'
                f'</div>', unsafe_allow_html=True,
            )
            km4.markdown(
                f'<div class="kpi-card" style="--accent:#a855f7;">'
                f'<span class="kpi-icon">🇮🇳</span>'
                f'<p class="kpi-label">TOTAL AMT INR</p>'
                f'<p class="kpi-value">₹{total_inr:,.0f}</p>'
                f'<p class="kpi-sub">converted value</p>'
                f'</div>', unsafe_allow_html=True,
            )
            km5.markdown(
                f'<div class="kpi-card" style="--accent:#8b5cf6;">'
                f'<span class="kpi-icon">🏷️</span>'
                f'<p class="kpi-label">LOT GENERATED</p>'
                f'<p class="kpi-value">{lot_count_bs:,}</p>'
                f'<p class="kpi-sub">Stones sent for lot</p>'
                f'</div>', unsafe_allow_html=True,
            )
            km6.markdown(
                f'<div class="kpi-card" style="--accent:#f59e0b;">'
                f'<span class="kpi-icon">⏳</span>'
                f'<p class="kpi-label">NOT PROCESSED</p>'
                f'<p class="kpi-value">{live_count_bs:,}</p>'
                f'<p class="kpi-sub">Stones pending lot</p>'
                f'</div>', unsafe_allow_html=True,
            )

            st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

            def format_stock(source):
                # Computed INR columns — use DB stored value if available, else calculate
                display_df = source.copy()
                display_df["status_label"] = display_df["stock_status"].map({"LIVE":"Not Processed", "LOT":"Lot Generated"}).fillna(display_df["stock_status"])
                pc  = pd.to_numeric(display_df["per_carat"], errors="coerce").fillna(0)
                amt = pd.to_numeric(display_df["amount"],    errors="coerce").fillna(0)
                br  = pd.to_numeric(display_df["bank_rate"], errors="coerce").fillna(0)
                db_inr_pc    = pd.to_numeric(display_df.get("inr_pc",    pd.Series()), errors="coerce")
                db_inr_total = pd.to_numeric(display_df.get("inr_total", pd.Series()), errors="coerce")
                display_df["INR P/C"]   = db_inr_pc.where(db_inr_pc.notna()   & (db_inr_pc   != 0), round(pc  * br, 2))
                display_df["INR TOTAL"] = db_inr_total.where(db_inr_total.notna() & (db_inr_total != 0), round(amt * br, 2))

                display_df = display_df.rename(columns={
                    "buyer_name":    "BUYER",
                    "buying_date":   "DATE",
                    "party_name":    "PARTY",
                    "report_no":     "REPORT NO",
                    "lab":           "LAB",
                    "diamond_type":  "TYPE",
                    "shape":         "SHAPE",
                    "cts":           "CTS",
                    "color":         "COLOR",
                    "clarity":       "CLARITY",
                    "per_carat":     "$P/CT",
                    "amount":        "AMT USD",
                    "bank_rate":     "BANK RATE",
                    "location":      "LOCATION",
                    "remark":        "REMARK",
                    "status_label":  "STATUS",
                })
                display_df.drop(["inr_pc", "inr_total", "stock_status"], axis=1, inplace=True, errors="ignore")

                # ── Exact column order as requested ───────────────────────────────
                _bs_col_order = [
                    "BUYER", "DATE", "PARTY", "REPORT NO", "LAB", "TYPE", "SHAPE",
                    "CTS", "COLOR", "CLARITY", "$P/CT", "AMT USD", "INR P/C",
                    "INR TOTAL", "BANK RATE", "LOCATION", "REMARK", "STATUS",
                ]
                display_df = display_df[[c for c in _bs_col_order if c in display_df.columns]]

                # ── DATE ko real date dtype banao taaki sorting text ki jagah ──────
                # chronological ho (column header pe click karke ascending/descending)
                if "DATE" in display_df.columns:
                    display_df["DATE"] = pd.to_datetime(
                        display_df["DATE"], format="%d-%m-%Y", errors="coerce"
                    )

                return display_df

            display_df = format_stock(fdf)

            # Build a full filtered export only when requested, not on every click.
            if st.button("Prepare Excel — all matching stones", key="prepare_stock_excel"):
                import io
                with st.spinner("Preparing Excel..."):
                    export_df = read_frame(stock_select + where_sql + ' ORDER BY id DESC', conn, params=params)
                    export_buffer = io.BytesIO()
                    format_stock(export_df).to_excel(export_buffer, index=False, engine="openpyxl")
                st.download_button("Download Excel", data=export_buffer.getvalue(),
                    file_name=f"Buying_Stock_{datetime.now().strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="buying_stock_excel_dl", on_click="ignore")

            st.dataframe(
                display_df,
                use_container_width=True,
                height=620,
                column_config={
                    "DATE": st.column_config.DateColumn("DATE", format="DD-MM-YYYY"),
                },
            )

        # ══════════════════════════════════════════════════════════════════════════
        # TAB 3 — LOT GENERATED
        # ══════════════════════════════════════════════════════════════════════════
    if tab3:
        st.markdown(_section_header("🏷", "Lot Generation"), unsafe_allow_html=True)

        lot_section = st.radio("Section", ["📂 Excel Upload", "📋 Input IGI No", "📊 Master Lot Data"], horizontal=True, key="lot_section")

        # ── shared helper ────────────────────────────────────────────────────────
        def normalize_cert(cert: str) -> str:
            """If user pastes a 9-digit number without LG prefix, auto-add LG."""
            c = cert.strip()
            if c.isdigit() and len(c) == 9:
                return "LG" + c
            return c

        def run_lot_generation(report_list, memo_dict, btn_key_suffix):
            cursor.execute("SELECT pg_advisory_xact_lock(728190402)")
            cursor.execute(
                "SELECT lot_no FROM buying_stock WHERE lot_no IS NOT NULL "
                "ORDER BY CASE WHEN lot_no ~ '^[0-9]+$' THEN lot_no::numeric ELSE 0 END DESC LIMIT 1"
            )
            last = cursor.fetchone()
            try:
                last_number = int(last[0]) if last else 917967
            except Exception:
                last_number = 917967

            generated = skipped = already = 0
            results = []
            for raw_report in report_list:
                report_no = normalize_cert(raw_report)

                # First check: does this certificate exist in buying stock at all?
                cursor.execute(
                    "SELECT report_no, lot_no, stock_status FROM buying_stock WHERE report_no=?",
                    (report_no,),
                )
                data = cursor.fetchone()

                if not data:
                    # Certificate not in buying file at all
                    skipped += 1
                    results.append({"REPORT NO": report_no, "STATUS": "❌ Buying not updated — Certificate not found", "LOT NO": ""})
                elif data[1]:
                    # Certificate exists but lot already generated
                    already += 1
                    results.append({"REPORT NO": report_no, "STATUS": "🚫 Lot already generated", "LOT NO": data[1]})
                elif data[2] != "LIVE":
                    # Certificate exists but not in LIVE status (RETURN etc.)
                    skipped += 1
                    results.append({"REPORT NO": report_no, "STATUS": f"❌ Not in LIVE status ({data[2]})", "LOT NO": ""})
                else:
                    # All good — generate lot
                    last_number += 1
                    lot_no   = str(last_number)
                    lot_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    memo     = memo_dict.get(report_no, memo_dict.get(raw_report, ""))
                    cursor.execute(
                        "UPDATE buying_stock SET lot_no=?, lot_date=?, stock_status='LOT', memo_no=? WHERE report_no=?",
                        (lot_no, lot_date, memo, report_no),
                    )
                    generated += 1
                    results.append({"REPORT NO": report_no, "STATUS": "✅ Generated", "LOT NO": lot_no, "MEMO NO": memo})

            conn.commit()

            # Store results in session_state so they survive rerun
            st.session_state["lot_gen_results"]   = results
            st.session_state["lot_gen_generated"] = generated
            st.session_state["lot_gen_already"]   = already
            st.session_state["lot_gen_skipped"]   = skipped
            st.session_state["lot_gen_tab"]       = btn_key_suffix
            st.rerun()

        def _show_lot_gen_results():
            """Display lot generation results stored in session_state (survives rerun)."""
            if "lot_gen_results" not in st.session_state:
                return
            generated = st.session_state["lot_gen_generated"]
            already   = st.session_state["lot_gen_already"]
            skipped   = st.session_state["lot_gen_skipped"]
            results   = st.session_state["lot_gen_results"]

            if generated:
                st.success(f"✅ {generated} lot(s) generated successfully")
            if already:
                st.markdown(
                    f'<div style="background:#fef2f2;border:1px solid #fecaca;border-left:4px solid #ef4444;'
                    f'border-radius:8px;padding:14px 18px;margin:8px 0;">'
                    f'<p style="color:#991b1b;font-size:14px;font-weight:800;margin:0 0 4px;">'
                    f'🚫 Lot Already Generated — {already} Certificate(s)</p>'
                    f'<p style="color:#b91c1c;font-size:12px;margin:0;">'
                    f'A lot has already been generated for these certificates. They have been skipped.</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if skipped:
                st.markdown(
                    f'<div style="background:#f5f5f5;border:1px solid #d4d4d4;border-left:4px solid #f59e0b;'
                    f'border-radius:8px;padding:14px 18px;margin:8px 0;">'
                    f'<p style="color:#92400e;font-size:14px;font-weight:800;margin:0 0 4px;">'
                    f'⚠️ Buying Not Updated — {skipped} Certificate(s)</p>'
                    f'<p style="color:#92400e;font-size:12px;margin:0;">'
                    f'These certificates were not found in the buying file. Please upload the buying file first.</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)

        def _render_today_lots(editor_key, btn_key, dl_key):
            """Render today's generated lots table with checkboxes for TXT export."""
            lot_today_df = read_frame(
                """
                SELECT * FROM buying_stock
                WHERE lot_no IS NOT NULL
                  AND stock_status != 'RETURN'
                  AND LEFT(lot_date, 10) = TO_CHAR(CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM-DD')
                ORDER BY CASE WHEN lot_no ~ '^[0-9]+$' THEN lot_no::numeric ELSE 0 END DESC
                """,
                conn,
            )

            st.subheader(f"🏷 Today's Generated Lots — {datetime.now().strftime('%d-%m-%Y')}")

            # ── Report No / Lot No filters ────────────────────────────────────
            flt1, flt2 = st.columns(2)
            report_flt_val = flt1.text_input("REPORT NO", key=f"{editor_key}_report_filter", placeholder="LG123…")
            lot_flt_val    = flt2.text_input("LOT NO",    key=f"{editor_key}_lot_filter",    placeholder="918123…")

            if report_flt_val:
                lot_today_df = lot_today_df[
                    lot_today_df["report_no"].astype(str).str.contains(report_flt_val, case=False, na=False)
                ]
            if lot_flt_val:
                lot_today_df = lot_today_df[
                    lot_today_df["lot_no"].astype(str).str.contains(lot_flt_val, case=False, na=False)
                ]

            if lot_today_df.empty:
                st.info(f"ℹ️ No lots generated today ({datetime.now().strftime('%d-%m-%Y')}) matching your filters.")
                return

            pc  = pd.to_numeric(lot_today_df["per_carat"], errors="coerce").fillna(0)
            amt = pd.to_numeric(lot_today_df["amount"],    errors="coerce").fillna(0)
            br  = pd.to_numeric(lot_today_df["bank_rate"], errors="coerce").fillna(0)

            if is_video:
                pc  = pc  * 0
                amt = amt * 0
                br  = br  * 0

            tbl = pd.DataFrame({
                "SELECT":             False,
                "CERTIFICATE":        lot_today_df["report_no"].values,
                "LOT NUMBER":         lot_today_df["lot_no"].values,
                "MEMO NO":            lot_today_df["memo_no"].values,
                "BUYER NAME":         lot_today_df["buyer_name"].values,
                "BUY DATE":           pd.to_datetime(lot_today_df["buying_date"], errors="coerce").dt.strftime("%d-%m-%Y").values,
                "PARTY NAME":         lot_today_df["party_name"].values,
                "LAB":                lot_today_df["lab"].values,
                "WT.":                lot_today_df["cts"].values,
                "SHAPE":              lot_today_df["shape"].values,
                "ORG.COST":           pc.values,
                "BANK RATE":          br.values,
                "TOTAL BUYING PRICE": amt.values,
                "INR P/C":            round(pc * br, 2).values,
                "INR TOTAL":          round(amt * br, 2).values,
                "REMARK":             lot_today_df["remark"].values,
            }).fillna("")

            st.markdown(
                '<p style="font-size:12px;color:#737373;margin-bottom:6px;">'
                '☑ Tick rows → Generate TXT</p>',
                unsafe_allow_html=True,
            )

            # ── SELECT ALL toggle ──────────────────────────────────────────────
            select_all_key = f"select_all_{editor_key}"
            select_all = st.checkbox("☑ Select All / Deselect All", key=select_all_key)
            tbl["SELECT"] = select_all

            edited = st.data_editor(
                tbl,
                column_config={
                    "SELECT": st.column_config.CheckboxColumn("✔", default=False, width="small"),
                },
                disabled=[c for c in tbl.columns if c != "SELECT"],
                use_container_width=True,
                hide_index=True,
                key=editor_key,
                height=520,
            )

            selected = edited[edited["SELECT"] == True]["CERTIFICATE"].tolist()

            # ── Excel download for today's lots (ALL rows included, with a
            #     SELECTED column reflecting each row's tick state: TRUE/FALSE) ──
            import io as _io
            _today_excel_buf = _io.BytesIO()
            _today_excel_export = edited.copy()
            _today_excel_export["SELECT"] = _today_excel_export["SELECT"].astype(bool)
            _today_excel_export = _today_excel_export.rename(columns={"SELECT": "SELECTED"})
            # Move SELECTED to the front so it's easy to spot
            _today_excel_export = _today_excel_export[
                ["SELECTED"] + [c for c in _today_excel_export.columns if c != "SELECTED"]
            ]
            _today_excel_export.to_excel(_today_excel_buf, index=False, engine="openpyxl")
            _today_excel_buf.seek(0)

            bc1, bc2, bc3 = st.columns([3, 1, 1])
            bc1.markdown(
                f'<div style="background:#fafafa;border:1px solid #e5e5e5;border-top:2px solid #171717;'
                f'border-radius:8px;padding:10px 16px;margin-top:6px;display:inline-block;">'
                f'<span style="font-size:12px;color:#737373;">SELECTED</span>'
                f'&nbsp;&nbsp;<span style="font-size:20px;font-weight:800;color:#171717;">{len(selected)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            bc3.download_button(
                label="⬇ Excel",
                data=_today_excel_buf,
                file_name=f"Today_Lots_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"today_excel_dl_{dl_key}",
                use_container_width=True,
            )
            if bc2.button("📥 Generate TXT", key=btn_key):
                if not selected:
                    st.warning("⚠️ Please select at least one row first.")
                else:
                    rows = lot_today_df[lot_today_df["report_no"].astype(str).isin(selected)].copy()
                    rows["per_carat"] = pd.to_numeric(rows["per_carat"], errors="coerce").fillna(0)
                    rows["bank_rate"] = pd.to_numeric(rows["bank_rate"], errors="coerce").fillna(0)
                    if is_video:
                        exp = pd.DataFrame({
                            "Lot#":         rows["lot_no"],
                            "Certificate#": rows["report_no"],
                            "Weight":       rows["cts"],
                            "Cost/Cts":     0,
                            "Lab":          rows["lab"],
                        }).fillna("")
                    else:
                        exp = pd.DataFrame({
                            "Certificate#": rows["report_no"],
                            "Lot#":         rows["lot_no"],
                            "Lab":          rows["lab"],
                            "Weight":       rows["cts"],
                            "Cost/Cts":     round(rows["per_carat"] * rows["bank_rate"], 2),
                        }).fillna("")
                    txt_content = exp.to_csv(sep="\t", index=False)
                    st.download_button(
                        label="⬇ Download TXT File",
                        data=txt_content,
                        file_name=f"Lot_File_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt",
                        mime="text/plain",
                        key=dl_key,
                    )
                    st.success(f"✅ {len(exp)} stones added to TXT file")
                    st.dataframe(exp, use_container_width=True)

            # ── Paste Certificate Numbers → TXT ───────────────────────────────────
            st.markdown("---")
            st.markdown(_label("📋  Paste Certificate Numbers → Generate TXT"), unsafe_allow_html=True)
            paste_key   = f"paste_cert_{editor_key}"
            paste_dl_key = f"paste_dl_{dl_key}"
            paste_btn_key = f"paste_btn_{btn_key}"

            paste_input = st.text_area(
                "Paste certificate numbers (one per line)",
                key=paste_key,
                placeholder="LG123456\nLG789012\n...",
                height=120,
                label_visibility="collapsed",
            )

            paste_list = [normalize_cert(x.strip()) for x in paste_input.splitlines() if x.strip()] if paste_input else []

            if paste_list:
                st.markdown(
                    f'<p style="font-size:12px;color:#171717;margin:4px 0 8px;">'
                    f'📋 {len(paste_list)} certificate(s) entered</p>',
                    unsafe_allow_html=True,
                )

            if st.button("📥 Generate TXT from Paste", key=paste_btn_key):
                if not paste_list:
                    st.warning("Paste at least one certificate number.")
                else:
                    # Fetch matching rows from today's lots OR any LOT status in DB
                    all_lots_df = read_frame(
                        "SELECT * FROM buying_stock WHERE lot_no IS NOT NULL AND stock_status != 'RETURN'",
                        conn,
                    )
                    matched = all_lots_df[all_lots_df["report_no"].astype(str).isin(paste_list)].copy()
                    not_found = [c for c in paste_list if c not in all_lots_df["report_no"].astype(str).values]

                    if matched.empty:
                        st.error("❌ None of the entered certificates have a lot generated. Please generate lots first.")
                    else:
                        matched["per_carat"] = pd.to_numeric(matched["per_carat"], errors="coerce").fillna(0)
                        matched["bank_rate"] = pd.to_numeric(matched["bank_rate"], errors="coerce").fillna(0)
                        if is_video:
                            exp = pd.DataFrame({
                                "Lot#":         matched["lot_no"],
                                "Certificate#": matched["report_no"],
                                "Weight":       matched["cts"],
                                "Cost/Cts":     0,
                                "Lab":          matched["lab"],
                            }).fillna("")
                        else:
                            exp = pd.DataFrame({
                                "Certificate#": matched["report_no"],
                                "Lot#":         matched["lot_no"],
                                "Lab":          matched["lab"],
                                "Weight":       matched["cts"],
                                "Cost/Cts":     round(matched["per_carat"] * matched["bank_rate"], 2),
                            }).fillna("")
                        txt_content = exp.to_csv(sep="\t", index=False)
                        st.download_button(
                            label="⬇ Download TXT File",
                            data=txt_content,
                            file_name=f"Lot_File_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt",
                            mime="text/plain",
                            key=paste_dl_key,
                        )
                        st.success(f"✅ {len(exp)} stone(s) added to TXT file")
                        st.dataframe(exp, use_container_width=True)

                    if not_found:
                        st.markdown(
                            f'<div style="background:#f5f5f5;border:1px solid #d4d4d4;border-left:4px solid #f59e0b;'
                            f'border-radius:8px;padding:12px 16px;margin-top:8px;">'
                            f'<p style="color:#92400e;font-size:13px;font-weight:700;margin:0 0 6px;">'
                            f'⚠️ {len(not_found)} Certificate(s) — No Lot Found</p>'
                            f'<p style="color:#92400e;font-size:12px;margin:0 0 6px;">'
                            f'These certificates do not have a lot generated:</p>'
                            f'<ul style="color:#92400e;font-size:12px;margin:0 0 0 16px;padding:0;line-height:1.8;">'
                            + "".join(f"<li>{c}</li>" for c in not_found) +
                            f'</ul></div>',
                            unsafe_allow_html=True,
                        )
        if lot_section == '📂 Excel Upload':
            st.markdown(_label("📂  Excel must have REPORT and MEMO NO columns", margin_bottom=12), unsafe_allow_html=True)

            lot_file = st.file_uploader(
                "Upload Excel (.xlsx)", type=["xlsx"], key="lot_upload"
            )

            xl_report_list: list[str] = []
            xl_memo_dict:   dict[str, str] = {}

            if lot_file:
                lot_df = read_uploaded_excel(lot_file)
                lot_df.columns = lot_df.columns.str.strip().str.upper()
                lot_df = lot_df.fillna("")
                st.dataframe(lot_df, use_container_width=True)

                if "REPORT" not in lot_df.columns or "MEMO NO" not in lot_df.columns:
                    st.error("❌ Excel must contain REPORT and MEMO NO columns")
                else:
                    for _, row in lot_df.iterrows():
                        r = normalize_cert(str(row["REPORT"]).strip())
                        xl_report_list.append(r)
                        xl_memo_dict[r] = str(row["MEMO NO"]).strip()

                    st.markdown(
                        f'<p style="font-size:12px;color:#171717;margin:8px 0;">'
                        f'📋 {len(xl_report_list)} certificate(s) ready</p>',
                        unsafe_allow_html=True,
                    )

            if st.button("🚀 Generate Lots (Excel)", key="gen_lots_excel_btn"):
                if not xl_report_list:
                    st.warning("Upload a valid Excel file first.")
                else:
                    run_lot_generation(xl_report_list, xl_memo_dict, "xl")

            # Show results after button click (survives rerun via session_state)
            if st.session_state.get("lot_gen_tab") == "xl":
                _show_lot_gen_results()

            # ── Today's Generated Lots table (Excel Upload tab) ──────────────────
            st.divider()
            _render_today_lots("lot_table_editor_xl", "generate_txt_btn_xl", "download_txt_lot_btn_xl")

        # ── SUB-TAB 2: Copy-Paste Text ───────────────────────────────────────────
        if lot_section == '📋 Input IGI No':
            st.markdown(_label("📋  Paste certificate numbers and one memo no for all", margin_bottom=12), unsafe_allow_html=True)

            cp_col1, cp_col2 = st.columns([3, 1])

            with cp_col1:
                cp_certs = st.text_area(
                    "CERTIFICATE NUMBERS (one per line)",
                    key="cp_certs_box",
                    placeholder="LG123456\nLG789012\nLG345678\n...",
                    height=200,
                )

            with cp_col2:
                cp_memo = st.text_input(
                    "MEMO NO",
                    key="cp_memo_input",
                    placeholder="e.g. AP2050",
                )
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

                # Live preview of count
                cp_list = [normalize_cert(x.strip()) for x in cp_certs.splitlines() if x.strip()] if cp_certs else []
                st.markdown(
                    f'<div style="background:#fafafa;border:1px solid #e5e5e5;border-top:2px solid #171717;'
                    f'border-radius:8px;padding:12px 16px;text-align:center;">'
                    f'<p style="font-size:12px;color:#737373;margin:0 0 4px;">CERTIFICATES</p>'
                    f'<p style="font-size:24px;font-weight:800;color:#171717;margin:0;">{len(cp_list)}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="background:#fafafa;border:1px solid #e5e5e5;border-top:2px solid #171717;'
                    f'border-radius:8px;padding:12px 16px;text-align:center;">'
                    f'<p style="font-size:12px;color:#737373;margin:0 0 4px;">MEMO NO</p>'
                    f'<p style="font-size:16px;font-weight:800;color:#171717;margin:0;">'
                    f'{cp_memo if cp_memo else "—"}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            if st.button("🚀 Generate Lots (Text)", key="gen_lots_text_btn"):
                if not cp_list:
                    st.warning("Paste at least one certificate number.")
                elif not cp_memo.strip():
                    st.warning("Enter a Memo No.")
                else:
                    # Same memo for all certs, each gets its own lot number
                    cp_memo_dict = {r: cp_memo.strip() for r in cp_list}
                    run_lot_generation(cp_list, cp_memo_dict, "cp")

            # Show results after button click (survives rerun via session_state)
            if st.session_state.get("lot_gen_tab") == "cp":
                _show_lot_gen_results()

            # ── Today's Generated Lots table (Input IGI No tab) ──────────────────
            st.divider()
            _render_today_lots("lot_table_editor_cp", "generate_txt_btn_cp", "download_txt_lot_btn_cp")

        # ── SUB-TAB 3: Master Lot Data (lazy loading) ─────────────────────────
        if lot_section == '📊 Master Lot Data':
            st.markdown(_label("📊  All lots generated before today", margin_bottom=12), unsafe_allow_html=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            master_where = """
                lot_no IS NOT NULL
                AND stock_status != 'RETURN'
                AND NULLIF(LEFT(lot_date, 10), '')::date < CAST(? AS date)
            """
            # Lightweight aggregate only: no master data rows are fetched on page load.
            totals = conn.cursor()
            try:
                totals.execute(
                    "SELECT COUNT(*), COALESCE(SUM(cts), 0), COALESCE(SUM(amount), 0) "
                    "FROM buying_stock WHERE " + master_where,
                    (today_str,),
                )
                master_count, master_cts, master_amount = totals.fetchone()
            finally:
                totals.close()

            mm1, mm2, mm3 = st.columns(3)
            mm1.metric("💎 Total Stones", f"{master_count:,}")
            mm2.metric("📦 Total Carats", f"{float(master_cts):,.2f}")
            if not is_video:
                mm3.metric("💰 Total AMT USD", f"{float(master_amount):,.2f}")

            if not master_count:
                st.info("ℹ️ No master lots generated before today.")
            else:
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                st.caption("No full data is loaded on opening this page. Excel data is fetched only when you click Prepare Excel.")
                pasted_certificates = st.text_area(
                    "Certificate numbers for TXT",
                    key="master_paste_certificates",
                    placeholder="LG841638639\\nLG841638699",
                    height=110,
                )
                selection = list(dict.fromkeys(
                    normalize_cert(x.strip()) for x in pasted_certificates.splitlines() if x.strip()
                ))
                txt_col, excel_col = st.columns([1, 1])

                if txt_col.button("📥 Generate TXT", key="master_generate_txt_btn", use_container_width=True):
                    st.session_state.pop("master_txt_content", None)
                    st.session_state.pop("master_txt_count", None)
                    if not selection:
                        st.warning("⚠️ Paste at least one certificate number.")
                    else:
                        matched = read_frame(
                            """
                            SELECT report_no, lot_no, lab, cts, per_carat, bank_rate
                            FROM buying_stock
                            WHERE """ + master_where + " AND report_no = ANY(?)",
                            conn,
                            params=(today_str, selection),
                        )
                        found = set(matched["report_no"].astype(str))
                        missing = [cert for cert in selection if cert not in found]
                        if missing:
                            st.warning(f"⚠️ {len(missing)} certificate(s) not found in master lots: " + ", ".join(missing[:15]))
                        if matched.empty:
                            st.error("No matching master lots found.")
                        else:
                            cost = pd.to_numeric(matched["per_carat"], errors="coerce").fillna(0)
                            bank = pd.to_numeric(matched["bank_rate"], errors="coerce").fillna(0)
                            if is_video:
                                export_df = pd.DataFrame({
                                    "Lot#": matched["lot_no"],
                                    "Certificate#": matched["report_no"],
                                    "Weight": matched["cts"],
                                    "Cost/Cts": 0,
                                    "Lab": matched["lab"],
                                }).fillna("")
                            else:
                                export_df = pd.DataFrame({
                                    "Certificate#": matched["report_no"],
                                    "Lot#": matched["lot_no"],
                                    "Lab": matched["lab"],
                                    "Weight": matched["cts"],
                                    "Cost/Cts": round(cost * bank, 2),
                                }).fillna("")
                            st.session_state["master_txt_content"] = export_df.to_csv(sep="\\t", index=False)
                            st.session_state["master_txt_count"] = len(export_df)

                if st.session_state.get("master_txt_content"):
                    st.success(f"✅ {st.session_state['master_txt_count']} stones ready for TXT download")
                    st.download_button(
                        "⬇ Download TXT File",
                        data=st.session_state["master_txt_content"],
                        file_name=f"Master_Lot_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt",
                        mime="text/plain",
                        key="master_download_txt_btn",
                    )

                if excel_col.button("📊 Prepare Full Master Excel", key="master_prepare_excel_btn", use_container_width=True):
                    # Full SELECT and Excel conversion run ONLY when this button is clicked.
                    st.session_state.pop("master_excel_bytes", None)
                    with st.spinner("Fetching master lots from Neon and preparing Excel..."):
                        master_df = read_frame(
                            """
                            SELECT report_no, lot_no, memo_no, buyer_name, buying_date,
                                   party_name, lab, cts, shape, color, clarity,
                                   per_carat, bank_rate, amount, lot_date, remark
                            FROM buying_stock
                            WHERE """ + master_where + """
                            ORDER BY CASE WHEN lot_no ~ '^[0-9]+$' THEN lot_no::numeric ELSE 0 END DESC
                            """,
                            conn,
                            params=(today_str,),
                        )
                        pc = pd.to_numeric(master_df["per_carat"], errors="coerce").fillna(0)
                        rate = pd.to_numeric(master_df["bank_rate"], errors="coerce").fillna(0)
                        amt = pd.to_numeric(master_df["amount"], errors="coerce").fillna(0)
                        if is_video:
                            pc = pc * 0
                            rate = rate * 0
                            amt = amt * 0
                        master_export = pd.DataFrame({
                            "CERTIFICATE": master_df["report_no"].values,
                            "LOT NUMBER": master_df["lot_no"].values,
                            "MEMO NO": master_df["memo_no"].values,
                            "BUYER NAME": master_df["buyer_name"].values,
                            "BUY DATE": pd.to_datetime(master_df["buying_date"], errors="coerce", dayfirst=True).dt.strftime("%d-%m-%Y").values,
                            "PARTY NAME": master_df["party_name"].values,
                            "LAB": master_df["lab"].values,
                            "WT.": master_df["cts"].values,
                            "SHAPE": master_df["shape"].values,
                            "COLOR": master_df["color"].values,
                            "CLARITY": master_df["clarity"].values,
                            "ORG.COST": pc.values,
                            "BANK RATE": rate.values,
                            "TOTAL BUYING PRICE": amt.values,
                            "INR P/C": round(pc * rate, 2).values,
                            "INR TOTAL": round(amt * rate, 2).values,
                            "LOT DATE": pd.to_datetime(master_df["lot_date"], errors="coerce").dt.strftime("%d-%m-%Y").values,
                            "REMARK": master_df["remark"].values,
                        }).fillna("")
                        import io
                        stream = io.BytesIO()
                        master_export.to_excel(stream, index=False, engine="openpyxl")
                        st.session_state["master_excel_bytes"] = stream.getvalue()
                        st.session_state["master_excel_row_count"] = len(master_export)

                if st.session_state.get("master_excel_bytes"):
                    st.success(f"✅ {st.session_state['master_excel_row_count']:,} master lots ready to download")
                    st.download_button(
                        "⬇ Download Full Master Excel",
                        data=st.session_state["master_excel_bytes"],
                        file_name=f"Master_Lot_{datetime.now().strftime('%d%m%Y')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="master_lot_download_btn",
                        use_container_width=True,
                    )


    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — RETURN STONES
    # ══════════════════════════════════════════════════════════════════════════
    if not is_video:
        if tab4:
            st.markdown(_section_header("🔴", "Return Stones"), unsafe_allow_html=True)

            def normalize_cert(cert: str) -> str:
                """If user pastes a 9-digit number without LG prefix, auto-add LG."""
                c = cert.strip()
                if c.isdigit() and len(c) == 9:
                    return "LG" + c
                return c

            return_section = st.radio("Section", ["🔴 Return", "🔄 Cancel Lot → Back to Buying Stock"], horizontal=True, key="return_section")

            # ── SUB-TAB 1: Normal Return ─────────────────────────────────────────
            if return_section == '🔴 Return':
                st.info("Paste REPORT numbers line by line")

                return_text = st.text_area("Paste REPORT Numbers", key="return_textbox")

                if st.button("🔴 Confirm Return", key="confirm_return_btn"):
                    if return_text.strip():
                        report_list_r = [x.strip() for x in return_text.splitlines() if x.strip()]
                        returned = not_found = 0
                        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        for report_no in report_list_r:
                            cursor.execute(
                                "SELECT report_no FROM buying_stock WHERE report_no=? AND stock_status != 'RETURN'",
                                (report_no,),
                            )
                            if cursor.fetchone():
                                cursor.execute(
                                    "UPDATE buying_stock SET stock_status='RETURN', return_date=? WHERE report_no=?",
                                    (return_date, report_no),
                                )
                                returned += 1
                            else:
                                not_found += 1

                        conn.commit()
                        st.success(f"✅ {returned} stones returned")
                        if not_found:
                            st.warning(f"⚠️ {not_found} stones not found or already returned")
                        st.rerun()

                st.divider()

                return_df = read_frame(
                    "SELECT * FROM buying_stock WHERE stock_status = 'RETURN' ORDER BY id DESC",
                    conn,
                )

                c1, c2 = st.columns(2)
                c1.metric("🔴 Total Returns", len(return_df))
                c2.metric(
                    "💰 Return Amount (USD)",
                    round(return_df["amount"].sum(), 2) if not return_df.empty else 0,
                )

                # ── Excel download for Return Stones table ───────────────────────
                if not return_df.empty:
                    import io as _ret_io
                    _ret_excel_buf = _ret_io.BytesIO()
                    return_df.to_excel(_ret_excel_buf, index=False, engine="openpyxl")
                    _ret_excel_buf.seek(0)

                    ret_dl1, ret_dl2 = st.columns([5, 1])
                    ret_dl2.download_button(
                        label="⬇ Excel",
                        data=_ret_excel_buf,
                        file_name=f"Return_Stones_{datetime.now().strftime('%d%m%Y')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="return_stones_excel_dl",
                        use_container_width=True,
                    )

                st.dataframe(return_df, use_container_width=True, height=620)

            # ── SUB-TAB 2: LOT CANCEL → BUYING STOCK (LIVE) ──────────────────────
            if return_section == '🔄 Cancel Lot → Back to Buying Stock':
                st.markdown(
                    '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-left:4px solid #22c55e;'
                    'border-radius:8px;padding:14px 18px;margin-bottom:20px;">'
                    '<p style="color:#166534;font-size:13px;font-weight:700;margin:0 0 4px;">🔄 Cancel Lot and Return to Buying Stock</p>'
                    '<p style="color:#166534;font-size:12px;margin:0;line-height:1.7;">'
                    'If a lot was generated by mistake for a certificate, or needs to be cancelled for any reason, '
                    'paste it below. The lot number will be cleared and the stone will go back to <b>LIVE Buying Stock</b>.</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                revert_text = st.text_area(
                    "Certificate Numbers (one per line)",
                    key="revert_lot_textbox",
                    placeholder="LG123456\nLG789012\n...",
                    height=160,
                )

                # Live preview of what will be reverted
                if revert_text.strip():
                    revert_list_preview = [normalize_cert(x.strip()) for x in revert_text.splitlines() if x.strip()]
                    if revert_list_preview:
                        preview_revert_df = read_frame(
                            f"""
                            SELECT report_no, lot_no, memo_no, party_name, shape, cts, per_carat, amount, stock_status
                            FROM buying_stock
                            WHERE report_no IN ({','.join(['?']*len(revert_list_preview))})
                            """,
                            conn,
                            params=revert_list_preview,
                        )

                        lot_found    = preview_revert_df[preview_revert_df["lot_no"].notna() & (preview_revert_df["lot_no"] != "")]
                        no_lot_found = [r for r in revert_list_preview if r not in preview_revert_df["report_no"].tolist()]
                        already_live = preview_revert_df[
                            (preview_revert_df["stock_status"] == "LIVE") &
                            (preview_revert_df["lot_no"].isna() | (preview_revert_df["lot_no"] == ""))
                        ]

                        if not lot_found.empty:
                            st.markdown(
                                f'<p style="font-size:12px;color:#166534;margin-bottom:6px;">'
                                f'✅ {len(lot_found)} certificate(s) will have their lot cancelled and return to LIVE:</p>',
                                unsafe_allow_html=True,
                            )
                            st.dataframe(
                                lot_found.rename(columns={
                                    "report_no": "CERTIFICATE", "lot_no": "LOT NO (CLEAR HOGA)",
                                    "memo_no": "MEMO NO", "party_name": "PARTY",
                                    "shape": "SHAPE", "cts": "CTS",
                                    "per_carat": "P/CT", "amount": "AMT USD", "stock_status": "STATUS"
                                }),
                                use_container_width=True,
                            )

                        if not already_live.empty:
                            st.markdown(
                                f'<div style="background:#fafafa;border:1px solid #d4d4d4;border-left:3px solid #f59e0b;'
                                f'border-radius:6px;padding:10px 14px;margin:6px 0;">'
                                f'<p style="color:#92400e;font-size:12px;margin:0;">'
                                f'⚠️ {len(already_live)} certificate(s) are already LIVE (no lot assigned): '
                                f'{", ".join(already_live["report_no"].tolist())}</p></div>',
                                unsafe_allow_html=True,
                            )

                        if no_lot_found:
                            st.markdown(
                                f'<div style="background:#fafafa;border:1px solid #d4d4d4;border-left:3px solid #ef4444;'
                                f'border-radius:6px;padding:10px 14px;margin:6px 0;">'
                                f'<p style="color:#991b1b;font-size:12px;margin:0;">'
                                f'❌ {len(no_lot_found)} certificate(s) not found in DB: '
                                f'{", ".join(no_lot_found)}</p></div>',
                                unsafe_allow_html=True,
                            )

                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

                if st.button("🔄 Confirm — Lot Cancel ", key="confirm_revert_lot_btn"):
                    if not revert_text.strip():
                        st.warning("⚠️ No certificate number pasted.")
                    else:
                        revert_list = [normalize_cert(x.strip()) for x in revert_text.splitlines() if x.strip()]
                        reverted = skipped_revert = not_found_revert = 0
                        revert_details = []

                        for report_no in revert_list:
                            cursor.execute(
                                "SELECT report_no, lot_no, stock_status FROM buying_stock WHERE report_no=?",
                                (report_no,),
                            )
                            row = cursor.fetchone()

                            if not row:
                                not_found_revert += 1
                                revert_details.append({"CERTIFICATE": report_no, "RESULT": "❌ Not found in DB", "LOT NO": ""})
                            elif not row[1]:
                                # No lot assigned
                                skipped_revert += 1
                                revert_details.append({"CERTIFICATE": report_no, "RESULT": f"⚠️ No lot was assigned (Status: {row[2]})", "LOT NO": ""})
                            else:
                                old_lot = row[1]
                                # Clear lot_no, lot_date, memo_no → set status back to LIVE
                                cursor.execute(
                                    """
                                    UPDATE buying_stock
                                    SET stock_status = 'LIVE',
                                        lot_no       = NULL,
                                        lot_date     = NULL,
                                        memo_no      = NULL,
                                        return_date  = NULL
                                    WHERE report_no = ?
                                    """,
                                    (report_no,),
                                )
                                reverted += 1
                                revert_details.append({"CERTIFICATE": report_no, "RESULT": "✅ Lot cancelled — back to LIVE", "LOT NO": old_lot})

                        conn.commit()

                        if reverted:
                            st.success(f"✅ {reverted} stone(s) had their lot cancelled — now back in Buying Stock (LIVE)")
                        if skipped_revert:
                            st.warning(f"⚠️ {skipped_revert} stone(s) skipped — no lot was assigned")
                        if not_found_revert:
                            st.error(f"❌ {not_found_revert} certificate(s) not found in DB")

                        if revert_details:
                            st.dataframe(pd.DataFrame(revert_details), use_container_width=True)

                        st.rerun()

        # ══════════════════════════════════════════════════════════════════════════
        # TAB 5 — ADMIN
        # ══════════════════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════════════════
    # TAB EXPORT STONES
    # ══════════════════════════════════════════════════════════════════════════
    if not is_video:
        if tab_export:
            st.markdown(_section_header("✈️", "Export Stones"), unsafe_allow_html=True)

            if "export_subpage" not in st.session_state:
                st.session_state["export_subpage"] = "mark"

            _esp1, _esp2 = st.columns(2)
            with _esp1:
                if st.button(
                    "✈️ Mark as Exported", key="export_subnav_mark", use_container_width=True,
                    type="primary" if st.session_state["export_subpage"] == "mark" else "secondary",
                ):
                    st.session_state["export_subpage"] = "mark"
                    st.rerun()
            with _esp2:
                if st.button(
                    "📊 Export Data", key="export_subnav_data", use_container_width=True,
                    type="primary" if st.session_state["export_subpage"] == "data" else "secondary",
                ):
                    st.session_state["export_subpage"] = "data"
                    st.rerun()

            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

            def normalize_cert_exp(cert: str) -> str:
                c = cert.strip()
                if c.isdigit() and len(c) == 9:
                    return "LG" + c
                return c

            # ── SUB-PAGE 1: Mark as Exported ──────────────────────────────────────
            if st.session_state["export_subpage"] == "mark":
                st.markdown(
                    _label("📋  Paste certificate numbers to mark as Exported (one per line)", margin_bottom=10),
                    unsafe_allow_html=True,
                )

                export_text = st.text_area(
                    "Certificate Numbers",
                    key="export_cert_box",
                    placeholder="LG123456\nLG789012\n...",
                    height=200,
                    label_visibility="collapsed",
                )

                export_list = [normalize_cert_exp(x) for x in export_text.splitlines() if x.strip()] if export_text else []

                if export_list:
                    st.markdown(
                        f'<p style="font-size:12px;color:#171717;margin:4px 0 10px;">'
                        f'📋 {len(export_list)} certificate(s) entered</p>',
                        unsafe_allow_html=True,
                    )

                    # Preview matching stones
                    placeholders = ",".join(["?"] * len(export_list))
                    preview_exp_df = read_frame(
                        f"""
                        SELECT report_no, buyer_name, party_name, shape, cts, color, clarity,
                               stock_status, lot_no, exported_at
                        FROM buying_stock
                        WHERE report_no IN ({placeholders})
                        """,
                        conn,
                        params=export_list,
                    )

                    not_found_exp  = [r for r in export_list if r not in preview_exp_df["report_no"].tolist()]
                    already_exp    = preview_exp_df[
                        preview_exp_df["exported_at"].notna() & (preview_exp_df["exported_at"] != "")
                    ]
                    to_export_df   = preview_exp_df[
                        preview_exp_df["exported_at"].isna() | (preview_exp_df["exported_at"] == "")
                    ]
                    invalid_status = to_export_df[~to_export_df["stock_status"].isin(["LIVE", "LOT"])]
                    valid_exp_df   = to_export_df[to_export_df["stock_status"].isin(["LIVE", "LOT"])]

                    if not valid_exp_df.empty:
                        st.markdown(
                            f'<p style="font-size:12px;color:#166534;font-weight:600;margin-bottom:6px;">'
                            f'✅ {len(valid_exp_df)} stone(s) ready to export:</p>',
                            unsafe_allow_html=True,
                        )
                        st.dataframe(
                            valid_exp_df[["report_no","buyer_name","party_name","shape","cts","color","clarity","stock_status","lot_no"]]
                            .rename(columns={"report_no":"CERTIFICATE","buyer_name":"BUYER","party_name":"PARTY",
                                             "shape":"SHAPE","cts":"CTS","color":"COLOR","clarity":"CLARITY",
                                             "stock_status":"STATUS","lot_no":"LOT NO"}),
                            use_container_width=True,
                        )

                    if not already_exp.empty:
                        st.markdown(
                            f'<div style="background:#f5f5f5;border:1px solid #d4d4d4;border-left:4px solid #f59e0b;'
                            f'border-radius:8px;padding:12px 16px;margin:8px 0;">'
                            f'<p style="color:#92400e;font-size:13px;font-weight:700;margin:0 0 4px;">'
                            f'⚠️ Already Exported — {len(already_exp)} Certificate(s)</p>'
                            f'<p style="color:#92400e;font-size:12px;margin:0 0 6px;">'
                            f'These certificates were already exported:</p>'
                            f'<ul style="color:#92400e;font-size:12px;margin:0 0 0 16px;padding:0;line-height:1.8;">'
                            + "".join(f"<li>{r}</li>" for r in already_exp["report_no"].tolist()) +
                            f'</ul></div>',
                            unsafe_allow_html=True,
                        )

                    if not invalid_status.empty:
                        st.markdown(
                            f'<div style="background:#fef2f2;border:1px solid #fecaca;border-left:4px solid #ef4444;'
                            f'border-radius:8px;padding:12px 16px;margin:8px 0;">'
                            f'<p style="color:#991b1b;font-size:13px;font-weight:700;margin:0 0 4px;">'
                            f'❌ Invalid Status — {len(invalid_status)} Certificate(s)</p>'
                            f'<p style="color:#b91c1c;font-size:12px;margin:0 0 6px;">'
                            f'These stones are not in LIVE or LOT status (possibly RETURN):</p>'
                            f'<ul style="color:#991b1b;font-size:12px;margin:0 0 0 16px;padding:0;line-height:1.8;">'
                            + "".join(f"<li>{r} ({s})</li>" for r, s in zip(invalid_status["report_no"], invalid_status["stock_status"])) +
                            f'</ul></div>',
                            unsafe_allow_html=True,
                        )

                    if not_found_exp:
                        st.markdown(
                            f'<div style="background:#f5f5f5;border:1px solid #d4d4d4;border-left:4px solid #ef4444;'
                            f'border-radius:8px;padding:12px 16px;margin:8px 0;">'
                            f'<p style="color:#991b1b;font-size:13px;font-weight:700;margin:0 0 4px;">'
                            f'❌ Not Found — {len(not_found_exp)} Certificate(s)</p>'
                            f'<p style="color:#b91c1c;font-size:12px;margin:0 0 6px;">'
                            f'These certificates were not found in the buying file:</p>'
                            f'<ul style="color:#991b1b;font-size:12px;margin:0 0 0 16px;padding:0;line-height:1.8;">'
                            + "".join(f"<li>{r}</li>" for r in not_found_exp) +
                            f'</ul></div>',
                            unsafe_allow_html=True,
                        )

                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

                # ── Export Details Form (shown when certificates are entered) ──
                if export_list:
                    st.markdown("---")
                    st.markdown(
                        _label("📋  Export Details — Fill before confirming", margin_bottom=10),
                        unsafe_allow_html=True,
                    )
                    ef1, ef2, ef3 = st.columns(3)
                    export_date_input    = ef1.date_input("Export Date",     key="exp_date_input",     value=datetime.now().date())
                    export_location_input = ef2.text_input("Export Location", key="exp_location_input")
                    export_part_input    = ef3.selectbox("Export Part",      key="exp_part_input",     options=["Part-A", "Part-B"])

                if st.button("✈️ Confirm Export", key="confirm_export_btn"):
                    if not export_list:
                        st.warning("⚠️ Paste at least one certificate number.")
                    elif not export_date_input:
                        st.warning("⚠️ Please select an Export Date.")
                    elif not export_location_input or not export_location_input.strip():
                        st.warning("⚠️ Please fill in the Export Location.")
                    elif not export_part_input:
                        st.warning("⚠️ Please select an Export Part.")
                    else:
                        export_ts        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        exp_date_str     = export_date_input.strftime("%d-%m-%Y")
                        exp_location_str = export_location_input
                        exp_part_str     = export_part_input
                        exported_count = skipped_exp = not_found_exp_btn = 0

                        for report_no in export_list:
                            cursor.execute(
                                "SELECT report_no, stock_status, exported_at FROM buying_stock WHERE report_no=?",
                                (report_no,),
                            )
                            row_data = cursor.fetchone()
                            if not row_data:
                                not_found_exp_btn += 1
                                continue
                            _, status, exp_at = row_data
                            if exp_at:
                                skipped_exp += 1
                                continue
                            if status not in ("LIVE", "LOT"):
                                skipped_exp += 1
                                continue
                            cursor.execute(
                                """UPDATE buying_stock
                                   SET exported_at=?, export_date=?, export_location=?, export_part=?
                                   WHERE report_no=?""",
                                (export_ts, exp_date_str, exp_location_str, exp_part_str, report_no),
                            )
                            exported_count += 1

                        conn.commit()

                        if exported_count:
                            st.success(
                                f"✈️ {exported_count} stone(s) exported  ·  "
                                f"Date: {exp_date_str}  ·  Location: {exp_location_str}  ·  Part: {exp_part_str}"
                            )
                        if skipped_exp:
                            st.warning(f"⚠️ {skipped_exp} stone(s) skipped (already exported or invalid status)")
                        if not_found_exp_btn:
                            st.error(f"❌ {not_found_exp_btn} certificate(s) not found in DB")
                        st.rerun()

            # ── SUB-PAGE 2: Export Data ────────────────────────────────────────────
            elif st.session_state["export_subpage"] == "data":
                st.markdown(_section_header("📊", "Export Data"), unsafe_allow_html=True)

                exp_data_df = read_frame(
                    """
                    SELECT b.buyer_name, b.buying_date, b.party_name, b.report_no, b.lab,
                           b.diamond_type, b.shape, b.cts, b.color, b.clarity,
                           b.per_carat, b.amount, b.bank_rate, b.location, b.remark,
                           b.stock_status, b.lot_no, b.inr_pc, b.inr_total,
                           b.exported_at, b.export_date, b.export_location, b.export_part
                    FROM buying_stock b
                    WHERE b.exported_at IS NOT NULL AND b.exported_at != ''
                    ORDER BY b.exported_at DESC
                    """,
                    conn,
                )

                if exp_data_df.empty:
                    st.info("ℹ️ No stones have been exported yet.")
                else:
                    # KPI Cards
                    e_stones = len(exp_data_df)
                    e_cts    = round(pd.to_numeric(exp_data_df["cts"],    errors="coerce").sum(), 2)
                    e_amt    = round(pd.to_numeric(exp_data_df["amount"], errors="coerce").sum(), 2)
                    e_br     = pd.to_numeric(exp_data_df["bank_rate"],    errors="coerce").fillna(0)
                    e_inr    = round((pd.to_numeric(exp_data_df["amount"], errors="coerce").fillna(0) * e_br).sum(), 2)

                    ek1, ek2, ek3, ek4 = st.columns(4)
                    ek1.markdown(
                        f'<div class="kpi-card" style="--accent:#171717;">'
                        f'<span class="kpi-icon">✈️</span>'
                        f'<p class="kpi-label">EXPORTED STONES</p>'
                        f'<p class="kpi-value">{e_stones:,}</p>'
                        f'<p class="kpi-sub">total exported</p></div>',
                        unsafe_allow_html=True,
                    )
                    ek2.markdown(
                        f'<div class="kpi-card" style="--accent:#3b82f6;">'
                        f'<span class="kpi-icon">⚖️</span>'
                        f'<p class="kpi-label">TOTAL CARATS</p>'
                        f'<p class="kpi-value">{e_cts:,}</p>'
                        f'<p class="kpi-sub">exported weight</p></div>',
                        unsafe_allow_html=True,
                    )
                    ek3.markdown(
                        f'<div class="kpi-card" style="--accent:#22c55e;">'
                        f'<span class="kpi-icon">💵</span>'
                        f'<p class="kpi-label">TOTAL AMT USD</p>'
                        f'<p class="kpi-value">${e_amt:,.0f}</p>'
                        f'<p class="kpi-sub">exported value</p></div>',
                        unsafe_allow_html=True,
                    )
                    ek4.markdown(
                        f'<div class="kpi-card" style="--accent:#a855f7;">'
                        f'<span class="kpi-icon">🇮🇳</span>'
                        f'<p class="kpi-label">TOTAL AMT INR</p>'
                        f'<p class="kpi-value">₹{e_inr:,.0f}</p>'
                        f'<p class="kpi-sub">converted value</p></div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

                    # Filters
                    st.markdown(_label("🔎  Filters", margin_bottom=6), unsafe_allow_html=True)
                    ef1, ef2, ef3 = st.columns(3)
                    ef_report = ef1.text_input("REPORT NO",  key="exp_report_filter", placeholder="LG123…")
                    ef_party  = ef2.text_input("PARTY",       key="exp_party_filter",  placeholder="Party name…")
                    ef_status = ef3.selectbox("STATUS", options=["All", "LIVE", "LOT"], key="exp_status_filter")

                    disp_exp = exp_data_df.copy()
                    if ef_report:
                        disp_exp = disp_exp[disp_exp["report_no"].astype(str).str.contains(ef_report, case=False, na=False)]
                    if ef_party:
                        disp_exp = disp_exp[disp_exp["party_name"].astype(str).str.contains(ef_party, case=False, na=False)]
                    if ef_status != "All":
                        disp_exp = disp_exp[disp_exp["stock_status"] == ef_status]

                    # INR columns
                    pc_e  = pd.to_numeric(disp_exp["per_carat"], errors="coerce").fillna(0)
                    amt_e = pd.to_numeric(disp_exp["amount"],    errors="coerce").fillna(0)
                    br_e  = pd.to_numeric(disp_exp["bank_rate"], errors="coerce").fillna(0)
                    db_inr_pc_e    = pd.to_numeric(disp_exp.get("inr_pc",    pd.Series(dtype=float)), errors="coerce")
                    db_inr_total_e = pd.to_numeric(disp_exp.get("inr_total", pd.Series(dtype=float)), errors="coerce")
                    disp_exp["INR P/C"]   = db_inr_pc_e.where(db_inr_pc_e.notna() & (db_inr_pc_e != 0), round(pc_e * br_e, 2))
                    disp_exp["INR TOTAL"] = db_inr_total_e.where(db_inr_total_e.notna() & (db_inr_total_e != 0), round(amt_e * br_e, 2))

                    disp_exp = disp_exp.rename(columns={
                        "buyer_name":        "BUYER",
                        "buying_date":       "DATE",
                        "party_name":        "PARTY",
                        "report_no":         "REPORT NO",
                        "lab":               "LAB",
                        "diamond_type":      "TYPE",
                        "shape":             "SHAPE",
                        "cts":               "CTS",
                        "color":             "COLOR",
                        "clarity":           "CLARITY",
                        "per_carat":         "$P/CT",
                        "amount":            "AMT USD",
                        "bank_rate":         "BANK RATE",
                        "location":          "LOCATION",
                        "remark":            "REMARK",
                        "stock_status":      "STATUS",
                        "lot_no":            "LOT NO",
                        "exported_at":       "EXPORTED AT",
                        "export_date":       "EXPORT DATE",
                        "export_location":   "EXPORT LOCATION",
                        "export_part":       "EXPORT PART",
                    })
                    disp_exp.drop(["inr_pc", "inr_total"], axis=1, inplace=True, errors="ignore")
                    st.dataframe(disp_exp, use_container_width=True, height=560)

                    # Excel download
                    import io as _exp_io
                    exp_buf = _exp_io.BytesIO()
                    disp_exp.to_excel(exp_buf, index=False, engine="openpyxl")
                    exp_buf.seek(0)
                    st.download_button(
                        label="⬇ Download Export Data (.xlsx)",
                        data=exp_buf,
                        file_name=f"Export_Data_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="export_data_dl_btn",
                    )

                    # Undo export section (admin only)
                    if is_admin:
                        st.markdown("---")
                        st.markdown(_label("↩️  Undo Export — paste certificates to move back to Buying Stock", margin_bottom=10), unsafe_allow_html=True)
                        undo_text = st.text_area(
                            "Certificates to Undo",
                            key="undo_export_box",
                            placeholder="LG123456\nLG789012\n...",
                            height=120,
                            label_visibility="collapsed",
                        )
                        if st.button("↩️ Undo Export", key="undo_export_btn"):
                            if not undo_text.strip():
                                st.warning("⚠️ Paste at least one certificate number.")
                            else:
                                undo_list = [normalize_cert_exp(x) for x in undo_text.splitlines() if x.strip()]
                                undone = undo_not_found = 0
                                for report_no in undo_list:
                                    cursor.execute(
                                        "SELECT report_no FROM buying_stock WHERE report_no=? AND exported_at IS NOT NULL AND exported_at != ''",
                                        (report_no,),
                                    )
                                    if cursor.fetchone():
                                        cursor.execute(
                                            "UPDATE buying_stock SET exported_at=NULL WHERE report_no=?",
                                            (report_no,),
                                        )
                                        undone += 1
                                    else:
                                        undo_not_found += 1
                                conn.commit()
                                if undone:
                                    st.success(f"↩️ {undone} stone(s) moved back to Buying Stock")
                                if undo_not_found:
                                    st.warning(f"⚠️ {undo_not_found} certificate(s) not found in export list")
                                st.rerun()

    if not is_video:
        if is_admin:
          if tab5:
            st.markdown(_section_header("⚙️", "Admin Panel"), unsafe_allow_html=True)

            admin_section = st.radio("Section", [
                "📥 Full Database Download",
                "🗑 Delete by Certificate",
                "✏️ Edit Row by Certificate",
                "👥 User Management",
                "🔀 Shape Mapping",
            ], horizontal=True, key="admin_section")

            # ── ADMIN SUB-TAB 1: FULL DB DOWNLOAD ─────────────────────────────────
            if admin_section == '📥 Full Database Download':
                st.markdown(_label("📥  Export entire database as Excel", margin_bottom=16), unsafe_allow_html=True)

                if st.button("📥 Generate Database Export", key="full_db_generate_btn", use_container_width=True):
                    full_df = read_frame("SELECT * FROM buying_stock ORDER BY id DESC", conn)
                    if full_df.empty:
                        st.warning("⚠️ No data found in database.")
                        st.session_state.pop("full_db_export_bytes", None)
                        st.session_state.pop("full_db_export_stats", None)
                    else:
                        import io
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            full_df.to_excel(writer, index=False, sheet_name="Stock")
                        buf.seek(0)
                        st.session_state["full_db_export_bytes"] = buf.getvalue()
                        st.session_state["full_db_export_stats"] = (
                            len(full_df),
                            round(pd.to_numeric(full_df["cts"], errors="coerce").sum(), 2),
                            round(pd.to_numeric(full_df["amount"], errors="coerce").sum(), 2),
                        )

                if "full_db_export_bytes" in st.session_state:
                    stones, carats, usd = st.session_state["full_db_export_stats"]
                    m1, m2, m3, _sp = st.columns([1, 1, 1, 3])
                    m1.metric("💎 Total Stones", stones)
                    m2.metric("📦 Total Carats", carats)
                    m3.metric("💰 Total USD",    usd)

                    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

                    st.download_button(
                        label="⬇ Download Full Database (.xlsx)",
                        data=st.session_state["full_db_export_bytes"],
                        file_name=f"LGD_Full_DB_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="full_db_download",
                    )

            # ── ADMIN SUB-TAB 2: DELETE BY CERTIFICATE ────────────────────────────
            if admin_section == '🗑 Delete by Certificate':
                st.markdown(_label("🗑  Paste certificate numbers to permanently delete", margin_bottom=16), unsafe_allow_html=True)

                del_text = st.text_area(
                    "Certificate Numbers (one per line)",
                    key="delete_cert_box",
                    placeholder="LG123456\nLG789012\n...",
                    height=160,
                )

                if del_text.strip():
                    del_list = [x.strip() for x in del_text.splitlines() if x.strip()]
                    preview_df = read_frame(
                        f"SELECT report_no, buyer_name, party_name, shape, cts, stock_status FROM buying_stock "
                        f"WHERE report_no IN ({','.join(['?']*len(del_list))})",
                        conn, params=del_list,
                    )
                    not_found_del = [r for r in del_list if r not in preview_df["report_no"].tolist()]

                    if not preview_df.empty:
                        st.markdown(
                            f'<p style="font-size:12px;color:#b91c1c;margin-bottom:6px;">'
                            f'⚠️ {len(preview_df)} stone(s) will be permanently deleted:</p>',
                            unsafe_allow_html=True,
                        )
                        st.dataframe(preview_df, use_container_width=True)

                    if not_found_del:
                        st.warning(f"Not found in DB: {', '.join(not_found_del)}")

                confirm_delete = st.button("🗑 Confirm Delete", key="confirm_delete_btn")
                if confirm_delete:
                    if not del_text.strip():
                        st.warning("Please enter certificate numbers first.")
                    else:
                        del_list = [x.strip() for x in del_text.splitlines() if x.strip()]
                        deleted = 0
                        for report_no in del_list:
                            cursor.execute("DELETE FROM buying_stock WHERE report_no=?", (report_no,))
                            deleted += cursor.rowcount
                        conn.commit()
                        st.success(f"✅ {deleted} stone(s) deleted permanently")
                        st.rerun()

            # ── ADMIN SUB-TAB 3: EDIT ROW BY CERTIFICATE ──────────────────────────
            if admin_section == '✏️ Edit Row by Certificate':
                st.markdown(
                    '<p style="font-size:12px;color:#737373;'
                    'margin-bottom:16px;">'
                    '✏️  Upload Excel with REPORT column + columns to update</p>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
                    'padding:14px 18px;margin-bottom:20px;">'
                    '<p style="color:#166534;font-size:12px;margin:0;font-family:DM Mono,monospace;line-height:2;">'
                    '📋 <b>Format:</b> Excel must have a <b>REPORT</b> column + any columns to update.<br>'
                    '⚡ If you change any of these: <b>CTS / PER CARAT / BANK RATE</b>, the following 3 fields will be automatically recalculated:<br>'
                    '&nbsp;&nbsp;• <b>AMT</b> = CTS × PER CARAT<br>'
                    '&nbsp;&nbsp;• <b>INR P/C</b> = PER CARAT × BANK RATE<br>'
                    '&nbsp;&nbsp;• <b>INR TOTAL</b> = AMT × BANK RATE<br>'
                    '<span style="color:#166534;">BUYER NAME | DATE | PARTY NAME | LAB | TYPE | SHAPE | CTS | COL | '
                    'CLA | PER CARAT | AMT | BANK RATE | LOCATION | REMARK</span>'
                    '</p></div>',
                    unsafe_allow_html=True,
                )

                edit_file = st.file_uploader(
                    "Upload Edit Excel (.xlsx)",
                    type=["xlsx"],
                    key="edit_upload",
                )

                COL_MAP = {
                    "BUYER NAME":    "buyer_name",
                    "DATE":          "buying_date",
                    "PARTY NAME":    "party_name",
                    "LAB":           "lab",
                    "TYPE":          "diamond_type",
                    "SHAPE":         "shape",
                    "CTS":           "cts",
                    "COL":           "color",
                    "CLA":           "clarity",
                    "PER CARAT":     "per_carat",
                    "AMT":           "amount",
                    "BANK RATE":     "bank_rate",
                    "LOCATION":      "location",
                    "REMARK":        "remark",
                }
                NUMERIC_COLS = {"CTS", "PER CARAT", "AMT", "BANK RATE"}

                if edit_file:
                    edit_df = read_uploaded_excel(edit_file)
                    edit_df.columns = edit_df.columns.str.strip().str.upper()
                    edit_df = edit_df.fillna("")

                    if "REPORT" not in edit_df.columns:
                        st.error("❌ REPORT column is required")
                    else:
                        updatable = [c for c in edit_df.columns if c in COL_MAP]
                        if not updatable:
                            st.error("❌ No updatable columns found.")
                        else:
                            # Show which columns will trigger recalculation
                            TRIGGER = {"CTS", "PER CARAT", "BANK RATE"}
                            triggered = [c for c in TRIGGER if c in updatable]
                            if triggered:
                                st.markdown(
                                    '<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:6px;'
                                    'padding:10px 14px;margin-bottom:12px;">'
                                    f'<p style="color:#92400e;font-size:12px;margin:0;line-height:1.9;">'
                                    f'⚡ <b>{", ".join(triggered)}</b> column(s) detected — the following 3 columns will be recalculated:<br>'
                                    '&nbsp;&nbsp;✦ <b>AMT</b> = CTS × PER CARAT<br>'
                                    '&nbsp;&nbsp;✦ <b>INR P/C</b> = PER CARAT × BANK RATE<br>'
                                    '&nbsp;&nbsp;✦ <b>INR TOTAL</b> = AMT × BANK RATE</p></div>',
                                    unsafe_allow_html=True,
                                )
                            st.markdown(
                                f'<p style="font-size:12px;color:#171717;margin-bottom:8px;">'
                                f'Columns to update: <b>{", ".join(updatable)}</b></p>',
                                unsafe_allow_html=True,
                            )
                            st.dataframe(edit_df, use_container_width=True)

                            if st.button("✏️ Apply Changes", key="apply_edit_btn"):
                                updated = not_found_e = 0
                                TRIGGER_COLS = {"CTS", "PER CARAT", "BANK RATE"}
                                needs_recalc = bool(TRIGGER_COLS & set(updatable))

                                for _, row in edit_df.iterrows():
                                    report_no = str(row["REPORT"]).strip()
                                    cursor.execute(
                                        "SELECT cts, per_carat, amount, bank_rate FROM buying_stock WHERE report_no=?",
                                        (report_no,),
                                    )
                                    existing = cursor.fetchone()
                                    if not existing:
                                        not_found_e += 1
                                        continue

                                    db_cts, db_pc, db_amt, db_br = (float(v or 0) for v in existing)

                                    # ── Pick final value: Excel cell if filled, else DB value ──
                                    def pick(col, db_val):
                                        if col in updatable and str(row[col]).strip() != "":
                                            try:    return float(row[col])
                                            except: return db_val
                                        return db_val

                                    new_cts = pick("CTS",       db_cts)
                                    new_pc  = pick("PER CARAT", db_pc)
                                    new_br  = pick("BANK RATE", db_br)

                                    # ── Recalculate all 3 derived columns ─────────────────────
                                    #   AMT       = CTS × PER CARAT
                                    #   INR P/C   = PER CARAT × BANK RATE
                                    #   INR TOTAL = AMT × BANK RATE
                                    new_amt      = round(new_cts * new_pc,       2)
                                    new_inr_pc   = round(new_pc  * new_br,       2)
                                    new_inr_total= round(new_amt  * new_br,      2)

                                    # ── Build SET clause: user columns first ──────────────────
                                    set_parts = []
                                    values    = []
                                    for c in updatable:
                                        db_col = COL_MAP[c]
                                        # Skip AMT — we will always force-set it below
                                        if db_col == "amount":
                                            continue
                                        if str(row[c]).strip() == "":
                                            continue
                                        set_parts.append(f"{db_col}=?")
                                        if c in NUMERIC_COLS and str(row[c]).strip() != "":
                                            values.append(float(row[c]))
                                        else:
                                            values.append(str(row[c]))

                                    # ── Always write the 3 recalculated columns to DB ─────────
                                    set_parts += ["amount=?", "inr_pc=?", "inr_total=?"]
                                    values    += [new_amt, new_inr_pc, new_inr_total]

                                    values.append(report_no)
                                    cursor.execute(
                                        f"UPDATE buying_stock SET {', '.join(set_parts)} WHERE report_no=?",
                                        values,
                                    )
                                    updated += 1

                                conn.commit()

                                recalc_note = " · AMT, INR P/C, INR TOTAL recalculated" if needs_recalc else ""
                                st.success(f"✅ {updated} stone(s) updated{recalc_note}")
                                if not_found_e:
                                    st.warning(f"⚠️ {not_found_e} certificate(s) not found in DB")
                                st.rerun()

            # ── ADMIN SUB-TAB 4: USER MANAGEMENT ──────────────────────────────────
            if admin_section == '👥 User Management':
                st.markdown(_label("👥  Manage users", margin_bottom=16), unsafe_allow_html=True)

                # Current users list
                users_df = read_frame("SELECT id, username, role FROM users ORDER BY id", conn)
                st.dataframe(users_df, use_container_width=True)

                st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
                st.markdown(_label("➕  Add New User", margin_bottom=10), unsafe_allow_html=True)

                u1, u2, u3, u4 = st.columns([2, 2, 1, 1])
                new_uname = u1.text_input("USERNAME",  key="new_uname",    placeholder="username")
                new_upass = u2.text_input("PASSWORD",  key="new_upass",    placeholder="password", type="password")
                new_role  = u3.selectbox("ROLE",       key="new_role",     options=["user", "admin", "video"])

                u4.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if u4.button("➕ Add User", key="add_user_btn"):
                    if not new_uname.strip() or len(new_upass.strip()) < 12:
                        st.warning("Username and a password of at least 12 characters are required.")
                    else:
                        try:
                            cursor.execute(
                                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                                (new_uname.strip(), hash_pw(new_upass.strip()), new_role),
                            )
                            conn.commit()
                            st.success(f"✅ User '{new_uname.strip()}' added as {new_role}")
                            st.rerun()
                        except Exception:
                            conn.rollback()
                            st.error(f"❌ Username '{new_uname.strip()}' already exists")

                st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
                st.markdown(_label("🗑  Delete / Reset Password", margin_bottom=10), unsafe_allow_html=True)

                d1, d2, d3, d4 = st.columns([2, 2, 1, 1])
                del_uname   = d1.text_input("USERNAME TO MANAGE", key="del_uname", placeholder="username")
                reset_upass = d2.text_input("NEW PASSWORD (for reset)", key="reset_pass", placeholder="leave blank to delete", type="password")

                d3.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if d3.button("🔑 Reset PW", key="reset_pw_btn"):
                    if not del_uname.strip() or len(reset_upass.strip()) < 12:
                        st.warning("Enter username and a new password of at least 12 characters.")
                    elif del_uname.strip() == st.session_state["username"]:
                        st.warning("To change your own password, sign out and use the 'Forgot / Reset Password' option on the login screen.")
                    else:
                        cursor.execute(
                            "UPDATE users SET password=? WHERE username=?",
                            (hash_pw(reset_upass.strip()), del_uname.strip()),
                        )
                        conn.commit()
                        if cursor.rowcount:
                            st.success(f"✅ Password reset for '{del_uname.strip()}'")
                        else:
                            st.error("User not found")
                        st.rerun()

                d4.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if d4.button("🗑 Delete User", key="del_user_btn"):
                    if not del_uname.strip():
                        st.warning("Enter a username to delete.")
                    elif del_uname.strip() == st.session_state["username"]:
                        st.error("❌ Cannot delete yourself.")
                    else:
                        cursor.execute("DELETE FROM users WHERE username=?", (del_uname.strip(),))
                        conn.commit()
                        if cursor.rowcount:
                            st.success(f"✅ User '{del_uname.strip()}' deleted")
                        else:
                            st.error("User not found")
                        st.rerun()

        # ── ADMIN SUB-TAB 5: SHAPE MAPPING ────────────────────────────────────
            if admin_section == '🔀 Shape Mapping':
                st.markdown(_label("🔀  Shape Alias Mapping — alias entered in Excel → saved as mapped value in DB", margin_bottom=16), unsafe_allow_html=True)

                # ── Current mappings table ─────────────────────────────────────
                maps_df = read_frame(
                    "SELECT id, alias, mapped_to FROM shape_mappings ORDER BY alias", conn
                )

                if maps_df.empty:
                    st.info("ℹ️ No mappings saved yet. Add one below.")
                else:
                    st.markdown(_label("📋  Existing Mappings", margin_bottom=6), unsafe_allow_html=True)
                    st.dataframe(
                        maps_df.rename(columns={"id": "ID", "alias": "ALIAS (Excel value)", "mapped_to": "MAPPED TO (DB value)"}),
                        use_container_width=True,
                        hide_index=True,
                    )

                st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

                # ── Add new mapping ────────────────────────────────────────────
                st.markdown(_label("➕  Add / Update Mapping", margin_bottom=10), unsafe_allow_html=True)
                mp1, mp2, mp3 = st.columns([2, 2, 1])
                new_alias  = mp1.text_input("ALIAS (e.g. RBC)", key="map_alias",    placeholder="Value in Excel…")
                new_mapped = mp2.text_input("MAPS TO (e.g. ROUND)", key="map_target", placeholder="Value to save in DB…")
                mp3.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                if mp3.button("💾 Save", key="save_mapping_btn"):
                    alias_val  = new_alias.strip().upper()
                    mapped_val = new_mapped.strip().upper()
                    if not alias_val or not mapped_val:
                        st.warning("Both Alias and Mapped To are required.")
                    else:
                        cursor.execute(
                            "INSERT INTO shape_mappings (alias, mapped_to) VALUES (?, ?) "
                            "ON CONFLICT(alias) DO UPDATE SET mapped_to=excluded.mapped_to",
                            (alias_val, mapped_val),
                        )
                        conn.commit()
                        st.success(f"✅ Mapping saved: **{alias_val}** → **{mapped_val}**")
                        st.rerun()

                st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

                # ── Delete mapping ─────────────────────────────────────────────
                if not maps_df.empty:
                    st.markdown(_label("🗑  Delete a Mapping", margin_bottom=10), unsafe_allow_html=True)
                    del1, del2 = st.columns([3, 1])
                    alias_to_del = del1.selectbox(
                        "Select alias to delete",
                        options=maps_df["alias"].tolist(),
                        key="del_alias_select",
                        label_visibility="collapsed",
                    )
                    del2.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                    if del2.button("🗑 Delete", key="del_mapping_btn"):
                        cursor.execute("DELETE FROM shape_mappings WHERE alias=?", (alias_to_del,))
                        conn.commit()
                        st.success(f"✅ Mapping '{alias_to_del}' deleted")
                        st.rerun()

        # ── CLOSE ─────────────────────────────────────────────────────────────────
        # Connection is released in the outer finally block.

finally:
    conn.close()
