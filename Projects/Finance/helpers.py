import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, flash, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={"Accept": "*/*", "User-Agent": "python-requests"},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        price = round(float(quotes[-1]["Adj Close"]), 2)
        return {"price": price, "symbol": symbol}
    except (KeyError, IndexError, requests.RequestException, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def calc_budget(db):
    cash = db.execute("SELECT cash FROM users WHERE id = (?)", session["user_id"])
    return float(cash[0]["cash"])


def calc_total(db, budget):
    result = db.execute(
        "SELECT COUNT(*) FROM stocks WHERE user_id = (?)", session["user_id"]
    )
    # Checking if there at least one position in `stocks`
    if result[0]["COUNT(*)"] > 0:
        total = db.execute(
            "SELECT ROUND(SUM(shares * price), 2) AS total FROM stocks WHERE user_id = ?",
            session["user_id"],
        )
        return round(float(total[0]["total"]) + budget, 2)
    else:
        return budget


def record_history(db, user_id, symbol, shares, price, type):
    db.execute(
        "INSERT INTO history (user_id, symbol, shares, price, timestamp, transaction_type) VALUES (?,?,?,?,datetime('now'),?)",
        user_id,
        symbol,
        shares,
        price,
        type,
    )


def calc_rows(db):
    return db.execute(
        "SELECT symbol, SUM(shares) AS total_shares, ROUND(SUM(shares * price), 2) AS shares_value, price FROM stocks WHERE user_id = ? GROUP BY symbol",
        session["user_id"],
    )


def user_nm(db):
    un = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    return un[0]["username"]
