import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Importing all necessary methods, including "new ones"
from helpers import (
    apology,
    login_required,
    lookup,
    usd,
    calc_budget,
    calc_total,
    calc_rows,
    record_history,
    user_nm,
)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Creating `shares` table if it doesn't exist
db.execute(
    """
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price NUMERIC NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""
)

# Creating `history` table if it doesn't exist
db.execute(
    """
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price NUMERIC NOT NULL,
        transaction_type TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""
)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Calculating total budget
    budget = calc_budget(db)
    # Calculating total value of user assets
    total_value = calc_total(db, budget)
    rows = calc_rows(db)

    if rows:
        return render_template(
            "index.html",
            rows=rows,
            budget=usd(budget),
            total_value=usd(total_value),
        )
    elif budget:
        return render_template(
            "index.html",
            budget=usd(budget),
            total_value=usd(budget),
        )
    else:
        return apology("unable to read user data", 403)

    """ RENDERING FROM DICT EXAMPLE
    return render_template("index.html,
        contacts = [{"name" : "Brin", "house" : "Winthrop"},
                    {"name" : "David", "house" : "Mather"}]) """


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Importing `symbol` value; ensuring it's upper case
        symbol = request.form.get("symbol").upper()
        # Receiving a dict with 'name', 'symbol', and 'price'
        quoted = lookup(symbol)
        if not quoted:
            return apology("invalid symbol", 400)
        # Importing amount of `shares` to buy
        try:
            shares = int(request.form.get("shares"))
            if shares < 0:
                return apology("invalid amount", 400)
        except ValueError:
            return apology("invalid amount", 400)
        # Importing `price` of the share
        price = round(float(quoted["price"]), 2)
        # Calculating price of the purchase
        total = round(float(price * shares), 2)
        flash(f"Price:{price}  Total:{total} ——")
        budget = calc_budget(db)

        # Ensuring that user has enough funds for purchase
        if total > budget:
            return apology("budget too low for this purhase", 400)
        else:
            # Adjusting user post-purhase budget
            db.execute(
                "UPDATE users SET cash = cash - (?) WHERE id = (?)",
                total,
                session["user_id"],
            )
            # Inserting newly purchased stocks
            db.execute(
                "INSERT INTO stocks (user_id, symbol, shares, price) VALUES (?,?,?,?)",
                session["user_id"],
                symbol,
                shares,
                price,
            )
            # Registering transaction in users transaction history
            record_history(db, session["user_id"], symbol, shares, price, "Purchase")

        budget = calc_budget(db)
        rows = calc_rows(db)

        # Displaying transaction details
        if shares > 0:
            flash(f"Purchased {shares} shares of {quoted['symbol']} for ${total}")
        return redirect("/")
    else:
        budget = calc_budget(db)
        rows = calc_rows(db)
        return render_template(
            "buy.html",
            budget=usd(budget),
            rows=rows,
        )


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    budget = calc_budget(db)
    total_value = calc_total(db, budget)

    # Fetch transaction history only for the logged-in user
    rows = db.execute(
        "SELECT timestamp, transaction_type, symbol, shares, price, ROUND(shares * price, 2) AS total FROM history WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"],
    )
    if rows:
        return render_template(
            "history.html",
            rows=rows,
            budget=usd(budget),
            total_value=usd(total_value),
        )
    elif budget:
        return render_template(
            "history.html",
            budget=budget,
            total_value=budget,
        )
    else:
        return apology("unable to read user data", 403)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_nm"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        quoted = lookup(symbol)
        if not quoted:
            return apology("invalid symbol", 400)

        return render_template("quote.html", quoted=quoted)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Retrieving and checking user input
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password doesn't match confirmation", 400)

        username = request.form.get("username")
        password = request.form.get("password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Apologizing if username is already taken
        if len(rows) == 1:
            return apology("this username is already taken", 400)

        # Generating hashed password
        hashed_password = generate_password_hash(
            password, method="pbkdf2", salt_length=16
        )

        # Inserting new user to the database (table `users`)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hashed_password,
        )
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Now that the user is successfully registered, set the session user_id
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page after successful registration
        return redirect("/")
    else:
        return render_template("register.html", session=session)


@app.route("/change_pass", methods=["GET", "POST"])
def change_pass():
    """Change Password"""
    if request.method == "POST":
        # Retrieving and checking user input
        if not request.form.get("old_pass"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password doesn't match confirmation", 400)

        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure old password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("old_pass")
        ):
            return apology("invalid old password", 403)

        # Generating hashed password
        hashed_password = generate_password_hash(
            password, method="pbkdf2", salt_length=16
        )

        # Updating password
        db.execute(
            "UPDATE users SET hash = (?) WHERE id = (?)",
            hashed_password,
            session["user_id"],
        )

        # Redirect user to home page after successful change
        flash("Password updated")
        return redirect("/")
    else:
        return render_template("change_pass.html", session=session)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        # Receiving a dict with 'symbol' and 'price'
        quoted = lookup(symbol)
        if not quoted:
            return apology("something went wrong", 400)
        want_sell = sold = int(request.form.get("shares"))

        price = float(quoted["price"])
        total = round(price * want_sell, 2)

        # Ensuring that user wan to sell more than 0 shares
        if want_sell != 0:
            # Calculation total amount of shares of indicated symbol
            db_sellable = db.execute(
                "SELECT SUM(shares) AS sell FROM stocks WHERE user_id = (?) AND symbol = (?)",
                session["user_id"],
                symbol,
            )
            # Total amount of certain shares
            sellable = db_sellable[0]["sell"]
            # Ensuring that user has enough shares to sell
            if sellable > want_sell:
                # Adding cash for sold shares
                db.execute(
                    "UPDATE users SET cash = cash + (?) WHERE id = (?)",
                    total,
                    session["user_id"],
                )
                # Looping through rows until user will sell required quantity of shares
                while True:
                    db_selling = db.execute(
                        "SELECT shares, id FROM stocks WHERE user_id = (?) AND symbol = (?)",
                        session["user_id"],
                        symbol,
                    )
                    # Establishing how much shares is in evaluated row
                    pos_shares = db_selling[0]["shares"]
                    if want_sell > pos_shares or want_sell == pos_shares:
                        # Adjusting amount of shares that still has to be sold
                        want_sell -= pos_shares
                        # Deleting the row if id doesn't exceed the amoun of shares user want to sell
                        db.execute(
                            "DELETE FROM stocks WHERE user_id = (?) AND symbol = (?) AND id = (?)",
                            session["user_id"],
                            symbol,
                            db_selling[0]["id"],
                        )
                    elif want_sell < pos_shares:
                        # Adjusting amount of the shares in the row and declaring there is no more shres user want to sell
                        pos_shares -= want_sell
                        want_sell = 0
                        db.execute(
                            "UPDATE stocks SET shares = (?) WHERE user_id = (?) AND symbol = (?) AND id = (?)",
                            pos_shares,
                            session["user_id"],
                            symbol,
                            db_selling[0]["id"],
                        )
                    # Breaking the loop if all required shares were sold
                    if want_sell == 0:
                        break
            else:
                return apology("you don't have enough shares", 400)

            # Recording history of transactions
            record_history(db, session["user_id"], symbol, sold, price, "Sale")
            # Displaying transaction details
            flash(f"Sold {sold} shares of {quoted['symbol']} for ${total}")

        return redirect("/")
    else:
        budget = calc_budget(db)
        total_value = calc_total(db, budget)
        stocks_rows = calc_rows(db)
        return render_template(
            "sell.html",
            budget=usd(budget),
            total_value=usd(total_value),
            rows=stocks_rows,
        )


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Buy shares of stock"""
    if request.method == "POST":
        budget = calc_budget(db)
        add_cash = request.form.get("cash")
        db.execute(
            "UPDATE users SET cash = cash + (?) WHERE id = (?)",
            add_cash,
            session["user_id"],
        )
        budget = calc_budget(db)
        return redirect("/")
    else:
        budget = calc_budget(db)
        return render_template("add_cash.html", budget=usd(budget))
