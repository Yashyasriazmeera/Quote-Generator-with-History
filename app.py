import json
import os
import random
import sqlite3
from urllib.request import urlopen

from flask import Flask, g, jsonify, render_template

DEFAULT_API_URL = "https://api.quotable.io/random"
BACKUP_API_URL = "https://zenquotes.io/api/random"
LOCAL_FALLBACK_QUOTES = [
    ("Success is the sum of small efforts, repeated day in and day out.", "Robert Collier"),
    ("Action is the foundational key to all success.", "Pablo Picasso"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "quotes.db"),
        QUOTE_API_URLS=[DEFAULT_API_URL, BACKUP_API_URL],
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS quote_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()

    def parse_quote(payload):
        if isinstance(payload, dict):
            quote = payload.get("content") or payload.get("quote")
            author = payload.get("author")
            if quote and author:
                return quote.strip(), author.strip()

        if isinstance(payload, list) and payload:
            item = payload[0]
            quote = item.get("q") or item.get("content") or item.get("quote")
            author = item.get("a") or item.get("author")
            if quote and author:
                return quote.strip(), author.strip()

        raise ValueError("Unsupported quote payload")

    def fetch_random_quote():
        for api_url in app.config["QUOTE_API_URLS"]:
            try:
                with urlopen(api_url, timeout=5) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return parse_quote(data)
            except Exception:
                continue

        return random.choice(LOCAL_FALLBACK_QUOTES)

    app.fetch_random_quote = fetch_random_quote

    @app.teardown_appcontext
    def teardown_db(error):
        close_db(error)

    @app.route("/")
    def index():
        db = get_db()
        history = db.execute(
            """
            SELECT id, quote, author, created_at
            FROM quote_history
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()
        return render_template("index.html", history=history)

    @app.route("/api/quote")
    def get_quote():
        try:
            quote, author = app.fetch_random_quote()
        except Exception:  # pragma: no cover - defensive path
            app.logger.exception("Failed to fetch quote from providers")
            return jsonify({"error": "Failed to fetch quote right now. Please try again."}), 502

        db = get_db()
        cursor = db.execute(
            "INSERT INTO quote_history (quote, author) VALUES (?, ?)",
            (quote, author),
        )
        db.commit()

        return jsonify(
            {
                "id": cursor.lastrowid,
                "quote": quote,
                "author": author,
            }
        )

    @app.route("/api/history")
    def get_history():
        db = get_db()
        rows = db.execute(
            """
            SELECT id, quote, author, created_at
            FROM quote_history
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()
        return jsonify(
            [
                {
                    "id": row["id"],
                    "quote": row["quote"],
                    "author": row["author"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        )

    with app.app_context():
        init_db()

    app.get_db = get_db
    return app


app = create_app()


if __name__ == "__main__":
    app.run()
