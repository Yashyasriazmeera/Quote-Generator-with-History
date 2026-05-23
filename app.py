from flask import Flask, render_template, jsonify
import requests
import sqlite3
import os
import random
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "quotes.db")
def init_db():
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT,
            author TEXT
        )
    """)

    conn.commit()
    conn.close()

# Save Quote
def save_quote(quote, author):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    # Always insert the quote, even if it's a duplicate
    cursor.execute(
        "INSERT INTO quotes (quote, author) VALUES (?, ?)",
        (quote, author)
    )
    conn.commit()
    conn.close()

# Fetch History
def get_history(limit=10):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT quote, author FROM quotes ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    history = cursor.fetchall()
    conn.close()
    return history

def fetch_random_quote():
    import traceback
    import random
    url = "https://dummyjson.com/quotes/random"
    fallback_quotes = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill"),
        ("What you get by achieving your goals is not as important as what you become by achieving your goals.", "Zig Ziglar"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
        ("The best way to get started is to quit talking and begin doing.", "Walt Disney"),
        ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
        ("Keep your face always toward the sunshine—and shadows will fall behind you.", "Walt Whitman"),
        ("Opportunities don't happen. You create them.", "Chris Grosser"),
        ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
        ("Everything you’ve ever wanted is on the other side of fear.", "George Addair"),
        ("Hardships often prepare ordinary people for an extraordinary destiny.", "C.S. Lewis"),
        ("Dream bigger. Do bigger.", "Unknown"),
        ("Don’t let yesterday take up too much of today.", "Will Rogers"),
        ("If you are not willing to risk the usual, you will have to settle for the ordinary.", "Jim Rohn"),
        ("Great things never come from comfort zones.", "Unknown"),
        ("Push yourself, because no one else is going to do it for you.", "Unknown"),
        ("Success doesn’t just find you. You have to go out and get it.", "Unknown"),
        ("The harder you work for something, the greater you’ll feel when you achieve it.", "Unknown"),
        ("Dream it. Wish it. Do it.", "Unknown")
    ]
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("quote", "No quote found."), data.get("author", "Unknown")
    except Exception as e:
        print("Error fetching quote:", e)
        traceback.print_exc()
        # Fallback to a random local quote
        return random.choice(fallback_quotes)

# Home Route
@app.route("/")
def index():
    quote, author = fetch_random_quote()
    save_quote(quote, author)
    history = get_history(limit=20)
    return render_template(
        "index.html",
        quote=quote,
        author=author,
        history=history
    )

# AJAX endpoint for new quote
@app.route("/quote", methods=["GET"])
def get_quote():
    quote, author = fetch_random_quote()
    save_quote(quote, author)
    history = get_history(limit=20)
    return jsonify({
        "quote": quote,
        "author": author,
        "history": history
    })

# Run App
if __name__ == "__main__":
    init_db()
    app.run(debug=True)