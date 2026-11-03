import os
import tempfile
import unittest

os.environ["INVOICE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

import app as invoice_app  # noqa: E402


class InvoiceSearchTests(unittest.TestCase):
    def setUp(self):
        invoice_app.init_db()
        import sqlite3
        with sqlite3.connect(invoice_app.DB_PATH) as conn:
            conn.execute("DELETE FROM invoices")
            conn.execute("DELETE FROM api_keys")
            conn.execute("INSERT INTO api_keys (owner, key) VALUES ('acme', 'test-key')")
            conn.executemany(
                "INSERT INTO invoices (customer, number, status, total_cents, issued_on) VALUES (?,?,?,?,?)",
                [("Acme Ltd", "INV-1", "paid", 12000, "2026-01-02"),
                 ("Globex", "INV-2", "sent", 4500, "2026-02-01")],
            )
        self.client = invoice_app.app.test_client()
        self.headers = {"X-Api-Key": "test-key"}

    def test_requires_key(self):
        self.assertEqual(self.client.get("/invoices").status_code, 401)

    def test_search_by_customer(self):
        res = self.client.get("/invoices?customer=acme", headers=self.headers)
        self.assertEqual([i["number"] for i in res.get_json()["invoices"]], ["INV-1"])

    def test_filter_by_status(self):
        res = self.client.get("/invoices?customer=&status=sent", headers=self.headers)
        self.assertEqual([i["number"] for i in res.get_json()["invoices"]], ["INV-2"])

    def test_customer_filter_is_not_injectable(self):
        payload = "' OR 1=1 --"
        res = self.client.get("/invoices", query_string={"customer": payload}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["invoices"], [])

    def test_quote_in_customer_name_is_matched_literally(self):
        import sqlite3
        with sqlite3.connect(invoice_app.DB_PATH) as conn:
            conn.execute(
                "INSERT INTO invoices (customer, number, status, total_cents, issued_on) VALUES (?,?,?,?,?)",
                ("O'Brien & Sons", "INV-3", "paid", 900, "2026-03-01"),
            )
        res = self.client.get("/invoices", query_string={"customer": "O'Brien"}, headers=self.headers)
        self.assertEqual([i["number"] for i in res.get_json()["invoices"]], ["INV-3"])


if __name__ == "__main__":
    unittest.main()
