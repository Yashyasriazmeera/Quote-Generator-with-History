import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app


class QuoteGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.db_path,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_quote_endpoint_fetches_and_stores_quote(self):
        with patch.object(self.app, "fetch_random_quote", return_value=("Stay curious", "Ada")):
            response = self.client.get("/api/quote")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["quote"], "Stay curious")
        self.assertEqual(payload["author"], "Ada")

        with self.app.app_context():
            row = self.app.get_db().execute(
                "SELECT quote, author FROM quote_history ORDER BY id DESC LIMIT 1"
            ).fetchone()
        self.assertEqual(row["quote"], "Stay curious")
        self.assertEqual(row["author"], "Ada")

    def test_history_endpoint_returns_recent_first(self):
        with self.app.app_context():
            db = self.app.get_db()
            db.execute("INSERT INTO quote_history (quote, author) VALUES (?, ?)", ("First", "A"))
            db.execute("INSERT INTO quote_history (quote, author) VALUES (?, ?)", ("Second", "B"))
            db.commit()

        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertEqual(payload[0]["quote"], "Second")
        self.assertEqual(payload[1]["quote"], "First")


if __name__ == "__main__":
    unittest.main()
