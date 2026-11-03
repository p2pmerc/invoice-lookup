"""Small invoice search API backed by SQLite."""
import os
import sqlite3

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("INVOICE_DB", "invoices.db")

app = Flask(__name__)


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
            conn.executescript(f.read())


@app.before_request
def require_key():
    if request.path == "/health":
        return None
    key = request.headers.get("X-Api-Key", "")
    row = db().execute("SELECT owner FROM api_keys WHERE key = ?", (key,)).fetchone()
    if row is None:
        return jsonify(error="missing or unknown API key"), 401
    return None


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.get("/invoices")
def search_invoices():
    """Search by customer name, optionally filtered by status. Newest first."""
    customer = request.args.get("customer", "")
    status = request.args.get("status")
    limit = min(int(request.args.get("limit", 50)), 200)

    query = "SELECT id, customer, number, status, total_cents, issued_on FROM invoices WHERE customer LIKE ?"
    params = [f"%{customer}%"]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY issued_on DESC LIMIT ?"
    params.append(limit)

    rows = db().execute(query, params).fetchall()
    return jsonify(invoices=[dict(r) for r in rows])


@app.get("/invoices/<number>")
def get_invoice(number):
    row = db().execute("SELECT * FROM invoices WHERE number = ?", (number,)).fetchone()
    if row is None:
        return jsonify(error="not found"), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    init_db()
    app.run(port=int(os.environ.get("PORT", 5000)))
