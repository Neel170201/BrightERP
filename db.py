"""PostgreSQL access. One connection per Streamlit run, never shared across users."""
import hashlib
import hmac
import secrets
import pandas as pd
import psycopg


def hash_pw(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
    return f'pbkdf2_sha256$600000${salt}${digest}'


def verify_pw(password, stored):
    if not stored:
        return False
    if stored.startswith('pbkdf2_sha256$'):
        try:
            _, rounds, salt, digest = stored.split('$')
            actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(rounds)).hex()
            return hmac.compare_digest(actual, digest)
        except (ValueError, TypeError):
            return False
    # Preserve old accounts during migration; app upgrades the hash after login.
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def bind_sql(query):
    """Translate existing qmark bindings outside SQL quoted literals/identifiers."""
    result = []
    quote = None
    i = 0
    while i < len(query):
        c = query[i]
        if quote:
            result.append('%%' if c == '%' else c)
            if c == quote:
                if i + 1 < len(query) and query[i + 1] == quote:
                    result.append(quote)
                    i += 1
                else:
                    quote = None
        elif c in ("'", '"'):
            quote = c
            result.append(c)
        elif c == '?':
            result.append('%s')
        else:
            result.append('%%' if c == '%' else c)
        i += 1
    return ''.join(result)


class Cursor:
    def __init__(self, raw):
        self.raw = raw

    def execute(self, query, params=None):
        if params is None:
            self.raw.execute(query)
        else:
            self.raw.execute(bind_sql(query), tuple(params))
        return self

    def __getattr__(self, name):
        return getattr(self.raw, name)


class Connection:
    def __init__(self, raw):
        self.raw = raw

    def cursor(self):
        return Cursor(self.raw.cursor())

    def __getattr__(self, name):
        return getattr(self.raw, name)


def connect(url):
    return Connection(psycopg.connect(url, sslmode='require', connect_timeout=20, prepare_threshold=None))


def read_frame(query, conn, params=None):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        return pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])
    finally:
        cursor.close()


def initialize(url, admin_username='admin', admin_password='', seed_admin=True):
    conn = connect(url)
    try:
        initialize_schema(conn)
        cur = conn.cursor()
        cur.execute('CREATE INDEX IF NOT EXISTS idx_stock_status ON buying_stock (stock_status)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_stock_lot ON buying_stock (lot_no)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_stock_export ON buying_stock (exported_at)')
        # Serialize only bootstrap so concurrent worker starts cannot create conflicting admins.
        cur.execute('SELECT pg_advisory_xact_lock(728190401)')
        cur.execute('SELECT COUNT(*) FROM users')
        if seed_admin and cur.fetchone()[0] == 0:
            if len(admin_password) < 12:
                raise ValueError('BOOTSTRAP_ADMIN_PASSWORD must have at least 12 characters')
            cur.execute('INSERT INTO users (username,password,role) VALUES (?,?,?)',
                        (admin_username, hash_pw(admin_password), 'admin'))
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_schema(conn):
    cursor = conn.cursor()
    # Stock table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buying_stock (
        id           BIGSERIAL PRIMARY KEY,
        buyer_name   TEXT,
        buying_date  TEXT,
        party_name   TEXT,
        report_no    TEXT UNIQUE,
        diamond_type TEXT,
        shape        TEXT,
        cts          DOUBLE PRECISION,
        color        TEXT,
        clarity      TEXT,
        per_carat    DOUBLE PRECISION,
        amount       DOUBLE PRECISION,
        inr_pc       DOUBLE PRECISION,
        inr_total    DOUBLE PRECISION,
        bank_rate    DOUBLE PRECISION,
        location     TEXT,
        remark       TEXT,
        stock_status TEXT,
        lot_no       TEXT,
        lot_date     TEXT,
        return_date  TEXT,
        upload_time  TEXT,
        memo_no      TEXT,
        lab          TEXT
    )
    """)

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       BIGSERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role     TEXT DEFAULT 'user'
    )
    """)
    conn.commit()

    for col_def in ("memo_no TEXT", "lab TEXT", "inr_pc DOUBLE PRECISION", "inr_total DOUBLE PRECISION", "exported_at TEXT", "export_date TEXT", "export_location TEXT", "export_part TEXT"):
        cursor.execute(f"ALTER TABLE buying_stock ADD COLUMN IF NOT EXISTS {col_def}")
    conn.commit()

    # Shape Mappings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shape_mappings (
        id        BIGSERIAL PRIMARY KEY,
        alias     TEXT UNIQUE,
        mapped_to TEXT
    )
    """)
    conn.commit()

