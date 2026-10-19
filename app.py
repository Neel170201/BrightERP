import streamlit as st
import pandas as pd
from db import connect, initialize, read_frame, hash_pw, verify_pw, fingerprint
import os
import base64
import io
from PIL import Image
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
PAGE_ICON_B64 = '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'
BRAND_MARK_HTML = f'<div class="brand-mark"><img src="{COMPANY_LOGO_URI}" alt="Bright Trading logo"></div>'

# ── PAGE CONFIG (must be first st call) ───────────────────────────────────
st.set_page_config(page_title="Bright • Diamond ERP", page_icon=Image.open(io.BytesIO(base64.b64decode(PAGE_ICON_B64))), layout="wide", initial_sidebar_state="collapsed")

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

/* ── Smooth navigation: zero artificial wait, 240ms visual entrance ── */
@keyframes bt-page-enter {
  from {opacity:.72;transform:translateY(7px)}
  to {opacity:1;transform:translateY(0)}
}
/* A unique animation-name per route forces a fresh transition on Streamlit reruns.
   The former one-time .block-container animation did not restart when changing pages. */
.bt-route-marker {display:none!important;}
@keyframes bt-route-home {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-upload {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-stock {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-lot {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-return {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-export {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
@keyframes bt-route-admin {from{opacity:.32;transform:translate3d(0,16px,0)}to{opacity:1;transform:translate3d(0,0,0)}}
.block-container:has(.bt-route-marker[data-route="home"]) {animation:bt-route-home .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="upload"]) {animation:bt-route-upload .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="stock"]) {animation:bt-route-stock .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="lot"]) {animation:bt-route-lot .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="return"]) {animation:bt-route-return .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="export"]) {animation:bt-route-export .38s cubic-bezier(.19,1,.22,1) both;}
.block-container:has(.bt-route-marker[data-route="admin"]) {animation:bt-route-admin .38s cubic-bezier(.19,1,.22,1) both;}

/* Highlight actionable module navigation without changing Streamlit routing. */
[class*="st-key-workspace_card_"] {transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease!important;}
[class*="st-key-workspace_card_"]:hover {border-color:#cf9b5b!important;box-shadow:0 10px 28px rgba(16,40,66,.10)!important;transform:translateY(-2px);}
[class*="st-key-nav_card_"] button {transition:color .18s ease,transform .18s ease!important;}
[class*="st-key-nav_card_"] button:hover {color:#bb8748!important;transform:translateX(3px);}
/* Clear, brand-colored focus/active feedback on page navigation. */
[class*="st-key-back_home_btn"] button:hover {border-color:#c99558!important;color:#94632d!important;}
@media(prefers-reduced-motion:reduce) {
  .block-container {animation:none!important;}
  [class*="st-key-workspace_card_"]:hover,[class*="st-key-nav_card_"] button:hover {transform:none!important;}
}
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
        login_hero_uri = "data:image/webp;base64,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"
        login_css = """
<style>
/* Login styles are scoped so the signed-in ERP keeps its existing theme. */
[data-testid="stAppViewContainer"]:has(.bt-login-shell)::before{display:none!important}
.block-container:has(.bt-login-shell){max-width:1260px!important;padding:clamp(12px,3.5vh,38px) 18px 30px!important;width:100%!important}
.block-container:has(.bt-login-shell) > div{max-width:none!important}
[data-testid="stHorizontalBlock"]:has(.bt-login-visual):has(.bt-login-panel){gap:0!important;align-items:stretch!important;overflow:hidden;border-radius:30px;background:#fff;box-shadow:0 22px 68px rgba(17,39,65,.13);border:1px solid #e2e8f0;min-height:730px}
[data-testid="stHorizontalBlock"]:has(.bt-login-visual):has(.bt-login-panel)>[data-testid="stColumn"]{min-width:0!important;align-self:stretch!important}
[data-testid="stColumn"]:has(.bt-login-visual){background:#06182c;padding:0!important}
[data-testid="stColumn"]:has(.bt-login-panel){background:#fff;padding:48px clamp(28px,3.4vw,54px) 28px!important}
[data-testid="stColumn"]:has(.bt-login-visual)>[data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.bt-login-visual)>div,
[data-testid="stColumn"]:has(.bt-login-visual)>div>[data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.bt-login-visual)>div>div{height:100%!important;min-height:730px}
[data-testid="stColumn"]:has(.bt-login-visual) [data-testid="stMarkdown"],
[data-testid="stColumn"]:has(.bt-login-visual) [data-testid="stMarkdownContainer"]{height:100%!important}
.bt-login-shell,.bt-login-panel{display:none}
.bt-login-visual{height:100%;min-height:730px;box-sizing:border-box;background:#07192c url('__LOGIN_HERO_URI__') center center/cover no-repeat;padding:50px 44px 30px;color:#fff;position:relative}
.bt-login-visual:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(1,8,18,.2) 0%,rgba(1,8,18,.06) 42%,rgba(1,8,18,.15) 100%);pointer-events:none}
.bt-login-visual>*{position:relative;z-index:1}
.bt-logo-chip{width:84px;height:84px;display:flex;align-items:center;justify-content:center;border:1px solid #bf874e;border-radius:22px;background:rgba(3,15,26,.75);box-shadow:0 10px 28px #0003}
.bt-logo-chip img{height:74%;width:74%;object-fit:contain}
.bt-brand-name{font-size:13px;font-weight:800;letter-spacing:.18em;color:#e5a763;margin-top:18px;line-height:1.5}
.bt-brand-tagline{font-size:10px;font-weight:600;letter-spacing:.22em;color:#e2e2e5;margin-top:12px;line-height:1.7}
.bt-hero-rule{background:#d8a268;height:2px;width:62px;margin-top:22px}
.bt-hero-copy{margin-top:42px;max-width:355px}
.bt-hero-copy h1{font-size:29px;line-height:1.13;letter-spacing:-.025em;color:#fff;font-weight:750;margin:0!important;padding:0!important;text-shadow:0 2px 12px #001a}
.bt-hero-copy h1 em{font-style:normal;color:#efb26d}
.bt-hero-copy p{font-size:14px;margin:12px 0 0;color:#e5e7eb;line-height:1.5;text-shadow:0 1px 8px #001a}
.bt-login-panel-head{padding:0 0 24px!important;margin:0!important}
.bt-login-eyebrow{font-size:12px;font-weight:800;letter-spacing:.21em;color:#c7894a;margin-bottom:16px}
.bt-login-rule{background:#d6a16f;height:2px;width:62px;margin:0 0 30px}
.bt-login-title{font-size:clamp(31px,3vw,39px);font-weight:800;line-height:1.15;letter-spacing:-.035em;color:#102746;margin:0!important;padding:0!important}
.bt-login-subtitle{font-size:15px;color:#71839d;margin:12px 0 0!important;line-height:1.5}
/* Cancel Streamlit's form panel, which produced the visible nested rectangle. */
.block-container:has(.bt-login-shell) [data-testid="stForm"],
.block-container:has(.bt-login-shell) .stForm,
.block-container:has(.bt-login-shell) form{border:0!important;outline:0!important;box-shadow:none!important;border-radius:0!important;background:transparent!important;padding:0!important;margin:0!important}
.block-container:has(.bt-login-shell) [data-testid="stForm"] [data-testid="stVerticalBlock"]{gap:14px!important}
.block-container:has(.bt-login-shell) [data-testid="stWidgetLabel"] p{font-size:13px!important;font-weight:750!important;color:#102746!important;margin:0!important}
.block-container:has(.bt-login-shell) [data-baseweb="input"]{min-height:49px!important;background:#f5f7fa!important;border:1px solid #d9e1eb!important;border-radius:11px!important;box-shadow:none!important}
.block-container:has(.bt-login-shell) [data-baseweb="input"]:focus-within{border-color:#c9935b!important;box-shadow:0 0 0 3px #c9935b22!important}
.block-container:has(.bt-login-shell) [data-baseweb="input"] input{font-size:14px!important;background:transparent!important;color:#122a45!important}
.block-container:has(.bt-login-shell) [data-testid="stFormSubmitButton"]{padding-top:14px!important}
.block-container:has(.bt-login-shell) [data-testid="stFormSubmitButton"] button{height:53px!important;min-height:53px!important;border:0!important;border-radius:12px!important;background:linear-gradient(110deg,#123d86,#092961)!important;color:white!important;font-size:15px!important;font-weight:750!important;box-shadow:0 9px 18px #102e6227!important;transition:transform .18s ease,box-shadow .18s ease!important}
.block-container:has(.bt-login-shell) [data-testid="stFormSubmitButton"] button:hover{background:linear-gradient(110deg,#1850a7,#0b3473)!important;transform:translateY(-2px)!important;box-shadow:0 13px 22px #102e6238!important}
.bt-login-help{margin:30px 0 18px!important;text-align:center;font-size:13px;color:#70819b;line-height:1.65}
.bt-login-help strong{font-size:15px;color:#172e4e;display:block;font-weight:750}
.block-container:has(.bt-login-shell) [data-testid="stExpander"]{border:1px solid #dce3ed!important;border-radius:12px!important;box-shadow:none!important;background:white!important;overflow:hidden}
.block-container:has(.bt-login-shell) [data-testid="stExpander"] summary{padding:10px 12px!important}
.bt-login-footer{font-size:12px;letter-spacing:.045em;color:#9cabc0;text-align:center;margin:26px 0 0}
@media(max-width:900px){
 [data-testid="stHorizontalBlock"]:has(.bt-login-visual):has(.bt-login-panel){min-height:640px}
 [data-testid="stColumn"]:has(.bt-login-visual)>div{min-height:640px}
 .bt-login-visual{min-height:640px;padding:30px 25px}
 .bt-hero-copy{margin-top:26px}
 .bt-hero-copy h1{font-size:26px}
 [data-testid="stColumn"]:has(.bt-login-panel){padding:35px 26px!important}
}
@media(max-width:650px){
 .block-container:has(.bt-login-shell){padding:12px!important}
 [data-testid="stHorizontalBlock"]:has(.bt-login-visual):has(.bt-login-panel){display:flex!important;flex-direction:column!important;border-radius:20px;min-height:unset!important}
 [data-testid="stHorizontalBlock"]:has(.bt-login-visual):has(.bt-login-panel)>[data-testid="stColumn"]{width:100%!important;flex:none!important}
 [data-testid="stColumn"]:has(.bt-login-visual)>div{min-height:280px!important}
 .bt-login-visual{min-height:280px!important;padding:23px 26px!important;background-position:center 60%}
 .bt-logo-chip{width:55px;height:55px;border-radius:13px}
 .bt-brand-name{font-size:11px;margin-top:8px}
 .bt-brand-tagline,.bt-hero-rule,.bt-hero-copy{display:none}
 [data-testid="stColumn"]:has(.bt-login-panel){padding:27px 26px 30px!important}
 .bt-login-rule{margin-bottom:18px}
 .bt-login-panel-head{padding-bottom:18px!important}
}
@media(prefers-reduced-motion:reduce){.block-container:has(.bt-login-shell) *{transition:none!important;animation:none!important}}
</style>
"""
        st.markdown(login_css.replace("__LOGIN_HERO_URI__", login_hero_uri), unsafe_allow_html=True)

        st.markdown('<div class="bt-login-shell"></div>', unsafe_allow_html=True)
        visual_panel, form_panel = st.columns([1.12, 1.0], gap="small")
        with visual_panel:
            # A single HTML line avoids Markdown treating closing tags as code blocks.
            visual_html = (
                '<div class="bt-login-visual">'
                '<div class="bt-logo-chip"><img src="' + COMPANY_LOGO_URI + '" alt="Bright Trading logo"></div>'
                '<div class="bt-brand-name">BRIGHT TRADING INDIA LLP</div>'
                '<div class="bt-brand-tagline">PRECISION TODAY - BRIGHTER TOMORROW</div>'
                '<div class="bt-hero-rule"></div>'
                '<div class="bt-hero-copy"><h1>Precision in every <em>operation.</em></h1>'
                '<p>Your diamond workspace, connected.</p></div>'
                '</div>'
            )
            st.markdown(visual_html, unsafe_allow_html=True)
        with form_panel:
            st.markdown(
                '<div class="bt-login-panel"></div>'
                '<div class="bt-login-panel-head">'
                '<div class="bt-login-eyebrow">BRIGHT TRADING INDIA LLP</div>'
                '<div class="bt-login-rule"></div>'
                '<h2 class="bt-login-title">Welcome back</h2>'
                '<p class="bt-login-subtitle">Sign in to your workspace</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            with st.form("bright_login", clear_on_submit=False):
                username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                password = st.text_input("Password", key="login_pass", placeholder="Enter your password", type="password")
                submitted = st.form_submit_button("Sign in  →", type="primary", use_container_width=True)
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
            st.markdown('<div class="bt-login-help"><strong>Trouble signing in?</strong>Contact your administrator</div>', unsafe_allow_html=True)
            with st.expander("Change password"):
                fp_uname = st.text_input("USERNAME", key="fp_uname", placeholder="Your username")
                fp_old_pass = st.text_input("CURRENT PASSWORD", key="fp_old_pass", placeholder="Enter current password", type="password")
                fp_new_pass = st.text_input("NEW PASSWORD", key="fp_new_pass", placeholder="Enter new password", type="password")
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

    # Route marker is updated on every navigation rerun, restarting CSS entrance.
    # No sleeps, blocking code, or changes to database operations.
    st.markdown(
        f'<span class="bt-route-marker" data-route="{escape(st.session_state["page"])}" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )

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
        with st.popover(f"{st.session_state['username']} ▾", use_container_width=True):
            st.caption(f"Role: {st.session_state['role']}")
            if st.button("Sign out", key="logout_btn", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["username"] = ""
                st.session_state["role"] = ""
                st.query_params.clear()
                st.rerun()

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

    # ── BACK-TO-HOME BAR (shown on every page except Home) ────────────────────
    if st.session_state["page"] != "home":
        if st.button("← Back to Home", key="back_home_btn"):
            st.session_state["page"] = "home"
            st.rerun()
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    # Home dashboard; module visibility follows the existing role permissions.
    if st.session_state["page"] == "home":
        st.markdown("""
<style>
[data-testid="stAppViewContainer"]:has(.home-dashboard)::before {display:none;}
.home-dashboard {display:none;}
.hero {background:linear-gradient(115deg,#102842,#183b54);padding:20px 26px;border-radius:14px;margin-bottom:22px;}
.hero:after {display:none;}
.hero h1 {font-size:32px;font-weight:650;}
.home-date {color:#d5dce4;font-size:12px;margin-top:10px;}
.home-diamond {position:absolute;right:12%;top:16px;width:110px;height:90px;color:#c89570;opacity:.9;}
.home-summary {display:flex;align-items:center;gap:10px;background:white;border:1px solid #dce5ed;border-radius:10px;padding:14px 12px;min-height:88px;box-sizing:border-box;}
.home-summary-icon {display:flex;align-items:center;justify-content:center;width:32px;height:32px;flex-shrink:0;border-radius:50%;font-size:18px;color:#087f8c;background:#e7f4f5;}
.home-summary.copper .home-summary-icon {color:#ad642d;background:#fbf0e7;}
.home-summary-label {font-size:12px;color:#52647b;margin-bottom:6px;}
.home-summary-value {font-size:clamp(16px,1.45vw,22px);font-weight:700;color:#102842;letter-spacing:-.03em;overflow-wrap:anywhere;}
.home-summary-note {font-size:11px;color:#8793a4;margin-top:4px;}
[class*="st-key-workspace_card_"] {background-color:#ffffff!important;background-image:none!important;border:1px solid #dce5ed!important;border-radius:12px!important;box-shadow:none!important;}
[class*="st-key-workspace_card_"]:hover {background-color:#ffffff!important;background-image:none!important;border-color:#cf9b5b!important;box-shadow:0 10px 28px rgba(16,40,66,.10)!important;}
.home-section {font-size:23px;font-weight:700;color:#102842;margin:18px 0 10px;}
.module-card {min-height:56px;padding:2px 2px 0 54px;position:relative;}
.module-icon {position:absolute;left:4px;top:2px;width:36px;height:36px;font-size:18px;border-radius:50%;box-shadow:none;border:0;}
.module-icon:before,.module-card:after {display:none;}
.module-title {font-size:15px;margin-bottom:4px;}
.module-copy {font-size:12px;line-height:1.4;}
[data-testid="stVerticalBlockBorderWrapper"]:has(.module-card),[data-testid="stVerticalBlock"][style*="border"]:has(.module-card) {background:#ffffff!important;border:1px solid #dce5ed!important;border-radius:12px;box-shadow:none;}
[data-testid="stVerticalBlock"]:has(.module-card) .stButton button {color:#087f8c;background:transparent;border:0;box-shadow:none;text-align:left;justify-content:flex-start;min-height:28px;padding-left:56px;}
@media(min-width:761px) and (max-width:1100px) {
[data-testid="stHorizontalBlock"]:has(.home-summary) {flex-wrap:wrap;}
[data-testid="stHorizontalBlock"]:has(.home-summary)>[data-testid="stColumn"] {width:calc(33.333% - 12px)!important;flex:1 1 calc(33.333% - 12px)!important;min-width:0;}
}
@media(max-width:760px) {
[data-testid="stHorizontalBlock"]:has(.home-summary) {flex-wrap:wrap;}
[data-testid="stHorizontalBlock"]:has(.home-summary)>[data-testid="stColumn"] {width:calc(50% - 8px)!important;flex:1 1 calc(50% - 8px)!important;min-width:0;}
.home-summary {padding:12px 10px;gap:8px;}
.home-summary-icon {width:28px;height:28px;font-size:16px;}
.home-summary-note {font-size:10px;}
.home-diamond {display:none;} .hero h1 {font-size:26px;} .home-summary-value {font-size:22px;}}

.premium-hero {
  position:relative; isolation:isolate; background:linear-gradient(105deg,#08203a 0%,#062345 55%,#0b3466 100%)!important;
  min-height:225px; padding:35px 40px!important; border-radius:25px!important;
  overflow:hidden; box-shadow:0 13px 32px rgba(11,43,80,.18); display:flex; align-items:center;
  border:1px solid rgba(212,156,82,.40);
}
.premium-hero:before { content:""; position:absolute; right:0; top:0; bottom:0; width:49%;
  background:linear-gradient(90deg,#062345 0%,rgba(6,35,69,0) 24%),url("data:image/webp;base64,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") center right/cover no-repeat;
  z-index:-1; pointer-events:none; }
.premium-hero:after {display:none!important;}
.premium-hero-content {display:flex;align-items:center; gap:26px; position:relative; z-index:2; max-width:72%;}
.premium-hero-logo {width:112px;height:112px;display:flex;align-items:center;justify-content:center; flex-shrink:0;
  border:2px solid #e3a85c; border-radius:24px; background:#091d34; box-shadow:0 8px 28px #0004;}
.premium-hero-logo img {width:84px;height:84px;object-fit:contain;}
.premium-hero-copy {border-left:1px solid #d5a15c; padding-left:27px;}
.premium-hero-title {font-size:clamp(21px,2.2vw,31px);font-weight:800;letter-spacing:.035em;color:#fff;line-height:1.25;white-space:nowrap;}
.premium-hero h1 {font-size:19px!important;font-weight:600!important;color:#efd0a7!important;margin:11px 0 5px!important;}
.premium-hero p {font-size:16px;color:#e5a961!important;}
.premium-hero .home-date {font-size:13px!important;color:#f1f5fc!important;margin-top:13px!important;}
@media(max-width:920px) {.premium-hero {padding:25px!important;min-height:180px;} .premium-hero-content {max-width:100%;gap:15px;} .premium-hero-logo {width:74px;height:74px;border-radius:17px;} .premium-hero-logo img {width:55px;height:55px;} .premium-hero-title {white-space:normal;font-size:19px;} .premium-hero-copy {padding-left:15px;} .premium-hero:before {opacity:.4;width:65%;}}
@media(max-width:520px) {.premium-hero {padding:21px 16px!important;} .premium-hero-logo {width:54px;height:54px;} .premium-hero-logo img {width:41px;height:41px;} .premium-hero-title {font-size:15px;} .premium-hero h1 {font-size:15px!important;} .premium-hero p {font-size:12px;} .premium-hero-content {gap:10px;} .premium-hero-copy {padding-left:10px;}}
</style><div class="home-dashboard"></div>
""", unsafe_allow_html=True)
        st.markdown(
            '<div class="hero premium-hero">'
            '<div class="premium-hero-content">'
            '<div class="premium-hero-logo">'
            f'<img src="{COMPANY_LOGO_URI}" alt="Bright Trading India LLP logo"></div>'
            '<div class="premium-hero-copy">'
            '<div class="premium-hero-title">BRIGHT TRADING INDIA LLP</div>'
            f'<h1>Welcome back, {escape(str(st.session_state["username"]))}</h1>'
            '<p>Diamond operations at a glance.</p>'
            f'<div class="home-date">▦ &nbsp; {datetime.now().strftime("%d %B %Y")}</div>'
            '</div></div></div>',
            unsafe_allow_html=True,
        )
        if not is_video:
            # Same inventory scope and valuation as the former Buying Stock cards.
            cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(cts),0), COALESCE(SUM(amount),0), "
                "COALESCE(SUM(amount*COALESCE(bank_rate,0)),0), "
                "COUNT(*) FILTER (WHERE stock_status='LOT'), "
                "COUNT(*) FILTER (WHERE stock_status='LIVE') "
                "FROM buying_stock WHERE stock_status IN ('LIVE','LOT') "
                "AND (exported_at IS NULL OR exported_at='')"
            )
            stones, carats, usd, inr, lot_stones, pending = cursor.fetchone()
            summaries = [
                ("Total stones", f"{stones:,}", "In buying stock", "◇"),
                ("Total carats", f"{float(carats):,.2f} ct", "Total weight", "◈"),
                ("Total value · USD", f"${float(usd):,.0f}", "Buying value", "$"),
                ("Total value · INR", f"₹{float(inr):,.0f}", "Converted value", "₹"),
                ("Lot generated", f"{lot_stones:,}", "Stones assigned to lots", "▱"),
                ("Not processed", f"{pending:,}", "Stones pending lot", "◷"),
            ]
            for start in range(0, len(summaries), 6):
                for index, (column, item) in enumerate(zip(st.columns(6), summaries[start:start+6])):
                    label, value, note, icon = item
                    column.markdown(
                        f'<div class="home-summary {"copper" if (start+index)%2 == 0 else ""}">'
                        f'<span class="home-summary-icon">{icon}</span><div>'
                        f'<div class="home-summary-label">{label}</div>'
                        f'<div class="home-summary-value">{value}</div>'
                        f'<div class="home-summary-note">{note}</div></div></div>',
                        unsafe_allow_html=True,
                    )
        st.markdown('<div class="home-section">Your workspace</div>', unsafe_allow_html=True)
        details = {
            "upload": ("Buying Upload", "Import buying files and review incoming stones.", "↥"),
            "stock": ("Buying Stock", "Search inventory and review stone details.", "⌕"),
            "lot": ("Lots", "Create lots and track processing.", "◇"),
            "return": ("Returns", "Manage returned stones and records.", "↺"),
            "export": ("Exports", "Prepare shipments and review exports.", "➜"),
            "admin": ("Admin", "Manage users and shape mappings.", "♙"),
        }
        for start in range(0, len(_nav), 3):
            for column, (key, _, _) in zip(st.columns(3), _nav[start:start+3]):
                title, description, icon = details[key]
                copper = key in ("upload", "lot", "export")
                bg, color = ("#fbf0e7", "#ad642d") if copper else ("#e7f4f5", "#087f8c")
                with column:
                    with st.container(border=True, key=f"workspace_card_{key}"):
                        st.markdown(
                            f'<div class="module-card" style="--icon-bg:{bg};--icon-color:{color};">'
                            f'<div class="module-icon"><span class="glyph">{icon}</span></div>'
                            f'<p class="module-title">{title}</p><p class="module-copy">{description}</p></div>',
                            unsafe_allow_html=True,
                        )
                        if st.button("Open →", key=f"nav_card_{key}", use_container_width=True):
                            st.session_state["page"] = key
                            st.rerun()
        if not is_video:
            st.markdown('<div class="home-section">Recent activity</div>', unsafe_allow_html=True)
            # Derived from current records, rather than a separate historical audit log.
            activity = read_frame(
                "SELECT activity, details, event_time, status FROM ("
                "SELECT 'Buying upload' AS activity, CAST(COUNT(*) AS TEXT) || ' stones' AS details, "
                "upload_time AS event_time, 'Recorded' AS status FROM buying_stock "
                "WHERE COALESCE(upload_time,'')<>'' GROUP BY upload_time "
                "UNION ALL SELECT 'Lot created', COALESCE(lot_no,'') || ' · ' || CAST(COUNT(*) AS TEXT) || ' stones', "
                "lot_date, 'Recorded' FROM buying_stock WHERE COALESCE(lot_date,'')<>'' "
                "AND COALESCE(lot_no,'')<>'' GROUP BY lot_no,lot_date "
                "UNION ALL SELECT 'Return recorded', CAST(COUNT(*) AS TEXT) || ' stones', "
                "return_date, 'Recorded' FROM buying_stock WHERE COALESCE(return_date,'')<>'' GROUP BY return_date "
                "UNION ALL SELECT 'Export recorded', CAST(COUNT(*) AS TEXT) || ' stones', "
                "exported_at, 'Recorded' FROM buying_stock WHERE COALESCE(exported_at,'')<>'' GROUP BY exported_at"
                ") recent ORDER BY event_time DESC LIMIT 6", conn,
            )
            if activity.empty:
                st.info("No recent activity yet. Upload a buying file to get started.")
            else:
                activity.columns = ["Activity", "Details", "Time · IST", "Status"]
                st.dataframe(activity, hide_index=True, use_container_width=True)
                st.caption("Recent activity is based on current stock records.")
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
            with st.container(key="buying_stock_page"):
                st.markdown("""
    <style>
    .st-key-buying_stock_page [data-testid="stForm"] {background:#ffffff!important;background-image:none!important;border:1px solid #dce5ed!important;border-radius:12px!important;padding:18px!important;}
    .st-key-buying_stock_page .stock-title h2 {font-size:28px!important;line-height:1.3!important;font-weight:700!important;color:#102842!important;margin:0!important;padding:0!important;}
    .st-key-buying_stock_page .stock-title span {font-size:14px!important;line-height:1.5!important;color:#748398!important;}
    .st-key-buying_stock_page [data-baseweb="input"],
    .st-key-buying_stock_page [data-baseweb="input"] input,
    .st-key-buying_stock_page [data-baseweb="select"]>div,
    .st-key-buying_stock_page [data-baseweb="select"] input {background-color:#ffffff!important;color:#18324b!important;}
    .st-key-buying_stock_page [data-baseweb="input"],
    .st-key-buying_stock_page [data-baseweb="select"]>div {border:1px solid #dce5ed!important;border-radius:8px!important;}
    .st-key-buying_stock_page [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],
    .st-key-buying_stock_page [data-testid="stFormSubmitButton"] button[kind="primary"] {background:#087f8c!important;border-color:#087f8c!important;color:white!important;}
    .st-key-buying_stock_page [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] p {color:white!important;}
    .st-key-stock_toolbar,.st-key-stock_pagination {background:#ffffff!important;background-image:none!important;border:1px solid #dce5ed!important;border-radius:10px!important;padding:12px 14px!important;}
    .st-key-buying_stock_page .stock-count {font-size:17px!important;}
    .st-key-buying_stock_page .stock-count small {font-size:12px!important;}
    .st-key-buying_stock_page .stock-table-wrap {background:#ffffff!important;}
    .st-key-buying_stock_page .stock-table {font-size:13px!important;background:#ffffff!important;}
    .st-key-buying_stock_page .stock-table th {font-size:13px!important;background:#f4f7fa!important;}
    .st-key-buying_stock_page .stock-table td {font-size:13px!important;background:#ffffff!important;}
    .st-key-buying_stock_page .stock-table tr:nth-child(even) td {background:#f7f9fb!important;}

    [data-testid="stAppViewContainer"]:has(.stock-page-marker)::before {display:none;}
    .stock-title {display:flex;align-items:center;gap:24px;margin:0 0 18px;}
    .stock-title h2 {font-size:28px;margin:0;color:#102842;}
    .stock-title span {font-size:14px;color:#7b889b;}
    .st-key-stock_filters {background:#fff!important;border:1px solid #dce5ed!important;border-radius:12px;padding:18px;}
    .stock-count {font-size:17px;font-weight:700;color:#102842;padding-top:9px;}
    .stock-count small {font-size:12px;font-weight:400;color:#7b889b;margin-left:12px;}
    .stock-table-wrap {overflow:auto;border:1px solid #dce5ed;border-radius:10px;background:#fff;max-height:570px;}
    .stock-table {width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap;color:#18324b;}
    .stock-table th {position:sticky;top:0;background:#f4f7fa;padding:13px 14px;text-align:left;font-weight:650;border-bottom:1px solid #dce5ed;z-index:1;}
    .stock-table td {padding:10px 14px;border-bottom:1px solid #edf0f4;}
    .stock-table tr:nth-child(even) td {background:#f7f9fb;}
    .stock-table tr:hover td {background:#edf7f8;}
    .stock-table .num {text-align:right;}
    .stock-pill {display:inline-block;padding:4px 9px;border-radius:7px;font-size:12px;font-weight:600;}
    .stock-pill.pending {background:#fff0dd;color:#9b530e;}
    .stock-pill.lot {background:#dff1f2;color:#087083;}
    @media(max-width:760px) {.stock-title {display:block;} .stock-title span {display:block;margin-top:6px;}}
    </style><div class="stock-page-marker"></div>
    <div class="stock-title"><h2>Buying Stock</h2><span>Search and review your diamond inventory.</span></div>
    """, unsafe_allow_html=True)
                base_where = "stock_status IN ('LIVE','LOT') AND (exported_at IS NULL OR exported_at='')"
                cursor.execute("SELECT DISTINCT party_name FROM buying_stock WHERE " + base_where + " AND COALESCE(party_name,'')<>'' ORDER BY party_name")
                parties = [r[0] for r in cursor.fetchall()]
                cursor.execute("SELECT DISTINCT shape FROM buying_stock WHERE " + base_where + " AND COALESCE(shape,'')<>'' ORDER BY shape")
                shapes = [r[0] for r in cursor.fetchall()]
                def clear_stock_filters():
                    for key, value in {"bs_report":"", "bs_party":None, "bs_shape":None, "bs_status":"All statuses", "bs_date":None, "bs_remark":""}.items():
                        st.session_state[key] = value
                    st.session_state["bs_applied"] = {}
                    st.session_state["stock_page"] = 1
                with st.form("stock_filters"):
                    f1, f2, f3, f4 = st.columns(4)
                    report = f1.text_input("Report No", key="bs_report", placeholder="Search report number")
                    party = f2.selectbox("Party", parties, index=None, placeholder="All parties", key="bs_party")
                    shape = f3.selectbox("Shape", shapes, index=None, placeholder="All shapes", key="bs_shape")
                    status = f4.selectbox("Status", ["All statuses", "Not processed", "Lot generated"], key="bs_status")
                    with st.expander("More filters"):
                        d1, d2 = st.columns(2)
                        day = d1.date_input("Buying date", value=None, key="bs_date", format="DD-MM-YYYY")
                        remark = d2.text_input("Remark", key="bs_remark", placeholder="Search remark")
                    _, apply_col, clear_col = st.columns([6, 1.5, 1.5])
                    applied = apply_col.form_submit_button("Apply filters", type="primary", use_container_width=True)
                    clear_col.form_submit_button("Clear filters", on_click=clear_stock_filters, use_container_width=True)
                if applied:
                    st.session_state["bs_applied"] = {"report":report.strip(), "party":party, "shape":shape, "status":status, "date":day.strftime("%d-%m-%Y") if day else "", "remark":remark.strip()}
                    st.session_state["stock_page"] = 1
                filters = st.session_state.get("bs_applied", {})
                clauses, params = [base_where], []
                for key, column in [("report","report_no"),("date","buying_date"),("remark","remark")]:
                    if filters.get(key):
                        clauses.append(f"POSITION(LOWER(?) IN LOWER(COALESCE({column},''))) > 0")
                        params.append(filters[key])
                for key, column in [("party","party_name"),("shape","shape")]:
                    if filters.get(key):
                        clauses.append(column + "=?")
                        params.append(filters[key])
                if filters.get("status") in ("Not processed", "Lot generated"):
                    clauses.append("stock_status=?")
                    params.append("LIVE" if filters["status"] == "Not processed" else "LOT")
                where_sql = " AND ".join(clauses)
                cursor.execute("SELECT COUNT(*) FROM buying_stock WHERE " + where_sql, params)
                total_stones = cursor.fetchone()[0]
                default_cols = ["REPORT NO","PARTY","SHAPE","CTS","COLOR","CLARITY","$P/CT","AMT USD","STATUS"]
                all_cols = default_cols + ["BUYER","DATE","LAB","TYPE","INR P/C","INR TOTAL","BANK RATE","LOCATION","REMARK"]
                sort_options = {"Newest first":"id DESC", "Oldest first":"id ASC", "Carats: high to low":"cts DESC NULLS LAST, id DESC", "Carats: low to high":"cts ASC NULLS LAST, id DESC", "Amount: high to low":"amount DESC NULLS LAST, id DESC", "Amount: low to high":"amount ASC NULLS LAST, id DESC"}
                with st.container(key="stock_toolbar"):
                    count_col, cols_col, sort_col, export_col = st.columns([4,1.2,2,1.4])
                    with cols_col:
                        with st.popover("Columns", use_container_width=True):
                            selected_cols = st.multiselect("Visible columns", all_cols, default=default_cols, key="bs_columns")
                    sort_label = sort_col.selectbox("Sort", list(sort_options), key="bs_sort", label_visibility="collapsed")
                    export_clicked = export_col.button("Export Excel", key="prepare_stock_excel", use_container_width=True)
                page_size = st.session_state.get("bs_page_size", 200)
                signature = tuple(params) + (where_sql, sort_label, page_size)
                if st.session_state.get("stock_filter_signature") != signature:
                    st.session_state["stock_page"] = 1
                    st.session_state["stock_filter_signature"] = signature
                page_count = max(1, (total_stones + page_size - 1)//page_size)
                page = min(max(1,st.session_state.get("stock_page",1)),page_count)
                st.session_state["stock_page"] = page
                first = (page-1)*page_size+1 if total_stones else 0
                last = min(page*page_size,total_stones)
                count_col.markdown(f'<div class="stock-count">{total_stones:,} matching stones <small>Showing {first:,}–{last:,}</small></div>', unsafe_allow_html=True)
                stock_select = "SELECT buyer_name,buying_date,party_name,report_no,lab,diamond_type,shape,cts,color,clarity,per_carat,amount,bank_rate,location,remark,inr_pc,inr_total,stock_status FROM buying_stock WHERE "
                order_sql = " ORDER BY " + sort_options[sort_label]
                fdf = read_frame(stock_select + where_sql + order_sql + " LIMIT ? OFFSET ?", conn, params=params+[page_size,(page-1)*page_size])
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
                if export_clicked:
                    import io
                    with st.spinner("Preparing all matching stones..."):
                        export_df = read_frame(stock_select + where_sql + order_sql, conn, params=params)
                        export_buffer = io.BytesIO()
                        format_stock(export_df).to_excel(export_buffer, index=False, engine="openpyxl")
                    st.download_button("Download Excel", data=export_buffer.getvalue(), file_name=f"Buying_Stock_{datetime.now().strftime('%d%m%Y')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="buying_stock_excel_dl", on_click="ignore")
                labels = {"REPORT NO":"Report No", "PARTY":"Party", "SHAPE":"Shape", "CTS":"Carats", "COLOR":"Color", "CLARITY":"Clarity", "$P/CT":"USD/ct", "AMT USD":"Amount USD", "STATUS":"Status", "BUYER":"Buyer", "DATE":"Date", "LAB":"Lab", "TYPE":"Type", "INR P/C":"INR/ct", "INR TOTAL":"Amount INR", "BANK RATE":"Bank rate", "LOCATION":"Location", "REMARK":"Remark"}
                numeric_cols = {"CTS","$P/CT","AMT USD","INR P/C","INR TOTAL","BANK RATE"}
                if not selected_cols:
                    st.info("Select at least one column from Columns.")
                elif display_df.empty:
                    st.info("No stones match your filters. Try clearing the filters.")
                else:
                    headings = ''.join(f'<th class="{"num" if col in numeric_cols else ""}">{labels[col]}</th>' for col in selected_cols)
                    rows = []
                    for record in display_df[selected_cols].itertuples(index=False, name=None):
                        cells = []
                        for col, value in zip(selected_cols,record):
                            if pd.isna(value):
                                text = ""
                            elif col in numeric_cols:
                                text = f"{float(value):,.2f}"
                            elif col == "DATE":
                                text = value.strftime("%d-%m-%Y")
                            else:
                                text = str(value)
                            text = escape(text)
                            if col == "STATUS":
                                style = "pending" if value == "Not Processed" else "lot"
                                text = f'<span class="stock-pill {style}">{text}</span>'
                            cells.append(f'<td class="{"num" if col in numeric_cols else ""}">{text}</td>')
                        rows.append('<tr>'+''.join(cells)+'</tr>')
                    st.markdown('<div class="stock-table-wrap"><table class="stock-table"><thead><tr>'+headings+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>', unsafe_allow_html=True)
                def change_stock_page(delta):
                    st.session_state["stock_page"] = max(1,min(page_count,st.session_state["stock_page"]+delta))
                with st.container(key="stock_pagination"):
                    size_col, page_col, prev_col, next_col = st.columns([2,5,1.5,1.5])
                    size_col.selectbox("Rows per page", [50,100,200], index=2, key="bs_page_size")
                    page_col.markdown(f'<div style="text-align:center;padding-top:28px;color:#52647b;">Page {page} of {page_count}</div>', unsafe_allow_html=True)
                    prev_col.button("← Previous", disabled=page<=1, on_click=change_stock_page, args=(-1,), use_container_width=True)
                    next_col.button("Next →", disabled=page>=page_count, on_click=change_stock_page, args=(1,), use_container_width=True)
                st.caption("Sort applies to all matching stones. Excel includes all matching stones and all columns.")

        # ══════════════════════════════════════════════════════════════════════════
        # TAB 3 — LOT GENERATED
        # ══════════════════════════════════════════════════════════════════════════
    if tab3:
        with st.container(key="lots_page"):
            st.markdown("""
<style>
.master-summary {background:#fff;border:1px solid #dce5ed;border-radius:10px;padding:16px 18px;}
.master-label {font-size:12px;color:#64748b;margin-bottom:6px;}
.master-value {font-size:25px;font-weight:700;line-height:1.3;color:#102842;}
.master-note {font-size:11px;color:#8793a4;margin-top:5px;}
.st-key-master_txt_panel,.st-key-master_excel_panel {background:#fff!important;border:1px solid #dce5ed!important;border-radius:12px!important;padding:20px!important;}
.st-key-master_txt_panel h3,.st-key-master_excel_panel h3 {font-size:20px!important;margin-top:0!important;}
.master-export-note {padding:16px;margin:16px 0;background:#eef7f8;border-radius:8px;color:#52647b;font-size:13px;line-height:1.7;}
.master-export-note strong {color:#102842;}

.st-key-lots_section_tabs {border-bottom:1px solid #dce5ed!important;margin-bottom:4px;}
.st-key-lots_section_tabs .stButton button {background:transparent!important;border:0!important;border-bottom:3px solid transparent!important;border-radius:0!important;box-shadow:none!important;color:#64748b!important;min-height:44px!important;padding:8px 12px!important;transform:none!important;}
.st-key-lots_section_tabs .stButton button p {font-size:14px!important;font-weight:600!important;color:inherit!important;white-space:nowrap;}
.st-key-lots_section_tabs .stButton button[kind="primary"] {background:transparent!important;border-bottom:3px solid #087f8c!important;color:#087f8c!important;box-shadow:none!important;}
.st-key-lots_section_tabs .stButton button[kind="primary"] p {color:#087f8c!important;}
.st-key-lots_page [data-testid="stTextInput"] [data-baseweb="base-input"],
.st-key-lots_page [data-testid="stTextInput"] [data-baseweb="input"],
.st-key-lots_page [data-testid="stTextInput"] input {background-color:#ffffff!important;}
.st-key-lots_input_panel {padding:20px!important;}
.st-key-lots_input_panel h3 {font-size:22px!important;margin-bottom:4px!important;}
.st-key-lots_input_panel .stButton button {margin-top:4px;}
.lots-count-note {background:#eef7f8;border:1px solid #d9ecee;border-radius:8px;padding:12px 14px;font-size:13px;color:#52647b;}
.lots-count-note strong {font-size:19px;color:#087f8c;margin-right:6px;}

[data-testid="stAppViewContainer"]:has(.st-key-lots_page)::before {display:none!important;}
.st-key-lots_page .lots-title h2 {font-size:28px!important;line-height:1.3!important;font-weight:700;color:#102842;margin:0 0 6px;padding:0;}
.lots-title p {font-size:14px!important;color:#748398;margin:0 0 18px;}
.st-key-lots_page [data-testid="stRadio"]>label {display:none;}
.st-key-lots_page [data-testid="stRadio"] [role="radiogroup"] {gap:12px;border-bottom:1px solid #dce5ed;padding-bottom:0;}
.st-key-lots_page [data-testid="stRadio"] [role="radiogroup"] label {padding:10px 14px;margin:0;border-bottom:3px solid transparent;}
.st-key-lots_page [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {border-bottom-color:#087f8c;background:#eaf6f6;}
.st-key-lots_page [data-testid="stRadio"] [role="radiogroup"] label>div:first-child {display:none;}
.st-key-lots_upload_panel,.st-key-lots_input_panel,[class*="st-key-lots_today_"] {background:#ffffff!important;background-image:none!important;border:1px solid #dce5ed!important;border-radius:12px!important;padding:20px!important;}
.st-key-lots_page [data-testid="stFileUploaderDropzone"] {background:#eff9fa!important;border:1px dashed #44a6b0!important;border-radius:10px!important;padding:28px!important;}
.st-key-lots_page [data-baseweb="input"],.st-key-lots_page [data-baseweb="input"] input,.st-key-lots_page [data-baseweb="select"]>div,.st-key-lots_page textarea {background:#ffffff!important;color:#18324b!important;}
.st-key-lots_page [data-baseweb="input"],.st-key-lots_page textarea {border:1px solid #dce5ed!important;border-radius:8px!important;}
.st-key-lots_page h3 {font-size:22px!important;color:#102842!important;}
.st-key-lots_page [data-testid="stDataFrame"],.st-key-lots_page [data-testid="stDataEditor"] {background:#ffffff!important;border:1px solid #dce5ed!important;border-radius:10px!important;}
@media(max-width:760px) {.st-key-lots_upload_panel,.st-key-lots_input_panel,[class*="st-key-lots_today_"] {padding:14px!important;}}

.st-key-master_txt_panel,.st-key-master_excel_panel {min-height:310px!important;padding:22px!important;box-sizing:border-box;}
.st-key-master_txt_panel [data-testid="stVerticalBlock"],.st-key-master_excel_panel [data-testid="stVerticalBlock"] {gap:10px;}
.st-key-master_txt_panel h3,.st-key-master_excel_panel h3 {margin:0!important;padding:0!important;font-size:20px!important;}
.st-key-master_txt_panel .stButton button,.st-key-master_excel_panel .stButton button {min-width:160px;min-height:40px;box-shadow:none!important;border-radius:8px!important;margin-top:6px;}
.master-summary {padding:14px 18px!important;}
.master-export-note {height:137px!important;box-sizing:border-box;margin:5px 0 0!important;display:block;background:#f5f9fa!important;border:1px solid #e0ecee;line-height:1.7;}
.master-file-icon {display:block;width:44px;margin-bottom:8px;border:1px solid #a5cdd0;border-radius:5px;padding:3px 6px;font-size:10px;font-weight:700;color:#087f8c;background:#fff;}
@media(max-width:760px) {.st-key-master_txt_panel,.st-key-master_excel_panel {min-height:0!important;}}
</style>
<div class="lots-title"><h2>Lot Generation</h2><p>Create lots and review generated records.</p></div>

""", unsafe_allow_html=True)

            lot_options = [("📂 Excel Upload", "Excel Upload"), ("📋 Input IGI No", "Input IGI No"), ("📊 Master Lot Data", "Master Lot Data")]
            if st.session_state.get("lot_section") not in [value for value, _ in lot_options]:
                st.session_state["lot_section"] = lot_options[0][0]
            with st.container(key="lots_section_tabs"):
                tab_columns = st.columns([1.3, 1.4, 1.6, 5.7])
                for column, (value, label) in zip(tab_columns, lot_options):
                    if column.button(label, key=f"lots_nav_{label}", type="primary" if st.session_state["lot_section"] == value else "secondary", use_container_width=True):
                        st.session_state["lot_section"] = value
                        st.rerun()
            lot_section = st.session_state["lot_section"]

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
                with st.container(key=f"lots_today_{editor_key}"):
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
                with st.container(key="lots_upload_panel"):
                    st.subheader("Generate lots from Excel")
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

                    if st.button("🚀 Generate Lots (Excel)", key="gen_lots_excel_btn", type="primary"):
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
                with st.container(key="lots_input_panel"):
                    st.subheader("Generate lots from certificate numbers")
                    st.markdown(_label("📋  Paste certificate numbers and one memo no for all", margin_bottom=12), unsafe_allow_html=True)

                    cp_col1, cp_col2 = st.columns([2.5, 1])

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
                        cp_list = [normalize_cert(x.strip()) for x in cp_certs.splitlines() if x.strip()] if cp_certs else []
                        st.caption("This memo number applies to all entered certificates.")
                        st.markdown(
                            f'<div class="lots-count-note"><strong>{len(cp_list)}</strong> certificates entered</div>',
                            unsafe_allow_html=True,
                        )

                    if st.button("🚀 Generate Lots (Text)", key="gen_lots_text_btn", type="primary"):
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
                _render_today_lots("lot_table_editor_cp", "generate_txt_btn_cp", "download_txt_lot_btn_cp")

            # ── SUB-TAB 3: Master Lot Data (lazy loading) ─────────────────────────
            if lot_section == '📊 Master Lot Data':
                st.subheader("Master Lot Data")
                st.caption("Review totals and download records for lots generated before today.")
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

                master_metrics = [("Total stones", f"{master_count:,}", "Historical lot records"), ("Total carats", f"{float(master_cts):,.2f} ct", "Total weight")]
                if not is_video:
                    master_metrics.append(("Total value · USD", f"${float(master_amount):,.2f}", "Buying value"))
                for column, (label, value, note) in zip(st.columns(len(master_metrics)), master_metrics):
                    column.markdown(f'<div class="master-summary"><div class="master-label">{label}</div><div class="master-value">{value}</div><div class="master-note">{note}</div></div>', unsafe_allow_html=True)

                st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

                if not master_count:
                    st.info("ℹ️ No master lots generated before today.")
                else:
                    txt_panel, excel_panel = st.columns(2, gap="medium")
                    with txt_panel:
                        with st.container(key="master_txt_panel"):
                            st.subheader("Certificate TXT")
                            st.caption("Paste one certificate number per line to prepare your TXT file.")
                            pasted_certificates = st.text_area(
                                "Certificate numbers for TXT",
                                key="master_paste_certificates",
                                placeholder="LG841638639\nLG841638699",
                                height=110,
                            )
                            selection = list(dict.fromkeys(
                                normalize_cert(x.strip()) for x in pasted_certificates.splitlines() if x.strip()
                            ))

                            if st.button("Generate TXT", key="master_generate_txt_btn", type="primary", use_container_width=False):
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

                    with excel_panel:
                        with st.container(key="master_excel_panel"):
                            st.subheader("Full Master Excel")
                            st.caption("Download all master lot records in the existing Excel format.")
                            st.markdown(f'<div class="master-export-note"><span class="master-file-icon">XLSX</span><strong>{master_count:,} master records</strong><br>Ready to prepare your full Excel download.</div>', unsafe_allow_html=True)
                            if st.button("Prepare Excel", key="master_prepare_excel_btn", type="primary", use_container_width=False):
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
            with st.container(key="returns_page"):
                st.markdown('<style>[data-testid="stAppViewContainer"]:has(.st-key-returns_page)::before{display:none!important;} .st-key-return_input_panel,.st-key-return_records_panel,.st-key-return_cancel_panel{background:#fff!important;border:1px solid #dce5ed!important;border-radius:12px!important;padding:20px!important;} .st-key-returns_page [data-baseweb="input"],.st-key-returns_page [data-baseweb="base-input"],.st-key-returns_page input,.st-key-returns_page textarea{background:#fff!important;} .st-key-return_section_tabs{border-bottom:1px solid #dce5ed;margin-bottom:10px;} .st-key-return_section_tabs .stButton button{background:transparent!important;border:0!important;border-bottom:3px solid transparent!important;border-radius:0!important;box-shadow:none!important;color:#64748b!important;transform:none!important;} .st-key-return_section_tabs .stButton button[kind="primary"]{border-bottom-color:#087f8c!important;color:#087f8c!important;} .st-key-return_section_tabs .stButton button p{color:inherit!important;font-size:14px!important;font-weight:600!important;} .st-key-returns_page [data-testid="stMetric"]{padding:14px 18px!important;box-shadow:none!important;} .st-key-returns_page [data-testid="stMetricValue"]{font-size:25px!important;} </style>', unsafe_allow_html=True)
                st.subheader("Return Stones")
                st.caption("Return stones and manage lot cancellations.")

                def normalize_cert(cert: str) -> str:
                    """If user pastes a 9-digit number without LG prefix, auto-add LG."""
                    c = cert.strip()
                    if c.isdigit() and len(c) == 9:
                        return "LG" + c
                    return c

                return_options = [("🔴 Return", "Return Stones"), ("🔄 Cancel Lot → Back to Buying Stock", "Cancel Lot → Buying Stock")]
                if st.session_state.get("return_section") not in [value for value, _ in return_options]:
                    st.session_state["return_section"] = return_options[0][0]
                with st.container(key="return_section_tabs"):
                    nav_columns = st.columns([1.4, 2.4, 6.2])
                    for column, (value, label) in zip(nav_columns, return_options):
                        if column.button(label, key=f"return_nav_{label}", type="primary" if st.session_state["return_section"] == value else "secondary", use_container_width=True):
                            st.session_state["return_section"] = value
                            st.rerun()
                return_section = st.session_state["return_section"]

                # ── SUB-TAB 1: Normal Return ─────────────────────────────────────────
                if return_section == '🔴 Return':
                    with st.container(key="return_input_panel"):
                        st.subheader("Return certificates")
                        st.caption("Paste one report number per line, then confirm the return.")

                        return_text = st.text_area("Paste REPORT Numbers", key="return_textbox")

                        if st.button("🔴 Confirm Return", key="confirm_return_btn", type="primary"):
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


                    return_df = read_frame(
                        "SELECT * FROM buying_stock WHERE stock_status = 'RETURN' ORDER BY NULLIF(return_date,'') DESC NULLS LAST, id DESC",
                        conn,
                    )

                    with st.container(key="return_records_panel"):
                        st.subheader("Returned stones")
                        st.caption("Latest returned stones appear first.")
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
                    with st.container(key="return_cancel_panel"):
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

                        if st.button("🔄 Confirm — Lot Cancel ", key="confirm_revert_lot_btn", type="primary"):
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
            st.markdown('<style>[data-testid="stAppViewContainer"]:has(.st-key-export_mark_panel)::before{display:none!important;}.st-key-export_mark_panel,.st-key-export_download_panel{background:#fff!important;border:1px solid #dce5ed!important;border-radius:12px!important;padding:22px!important;}.st-key-export_mark_panel [data-baseweb="input"],.st-key-export_download_panel [data-baseweb="input"],.st-key-export_mark_panel input,.st-key-export_download_panel input,.st-key-export_download_panel [data-baseweb="select"]>div{background:#fff!important;}.export-file-note{padding:16px;background:#eaf6f7;border-radius:8px;color:#087083;font-size:13px;margin:10px 0;}</style>', unsafe_allow_html=True)
            st.subheader("Export Stones")
            st.caption("Mark stones as exported and download your export records.")
            def normalize_cert_exp(cert: str) -> str:
                c = cert.strip()
                if c.isdigit() and len(c) == 9:
                    return "LG" + c
                return c

            mark_panel, download_panel = st.columns([1.5, 1], gap="medium")
            with mark_panel:
                with st.container(key="export_mark_panel"):
                    st.subheader("Mark as exported")
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

                    if st.button("✈️ Confirm Export", key="confirm_export_btn", type="primary"):
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

            with download_panel:
                with st.container(key="export_download_panel"):
                    st.subheader("Download export data")
                    st.caption("Download exported stone records as an Excel file.")
                    st.markdown('<div class="export-file-note">Excel file · All exported records</div>', unsafe_allow_html=True)
                    def build_export_excel(database_url=url):
                        download_conn = connect(database_url)
                        try:
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
                                download_conn,
                            )

                            disp_exp = exp_data_df.copy()
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

                            # Excel download
                            import io as _exp_io
                            exp_buf = _exp_io.BytesIO()
                            disp_exp.to_excel(exp_buf, index=False, engine="openpyxl")
                            exp_buf.seek(0)
                            return exp_buf.getvalue()
                        finally:
                            download_conn.close()
                    st.download_button(
                        "Download Excel", data=build_export_excel,
                        file_name=f"Export_Data_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="export_data_dl_btn", type="primary", use_container_width=True,
                        on_click="ignore",
                    )
                    st.caption("Excel is generated only when you click Download Excel.")
            if is_admin:
                with st.expander("Undo export"):
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
