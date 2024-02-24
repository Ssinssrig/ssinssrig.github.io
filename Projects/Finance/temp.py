@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_nm_profile = user_nm(db)
    budget = calc_budget(db)
    total_value = calc_total(db, budget)

    # Fetch transaction history only for the logged-in user
    rows = db.execute(
        "SELECT timestamp, transaction_type, symbol, shares, price, shares * price AS total FROM history WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )

    if rows:
        return render_template(
            "history.html",
            user_nm_profile=user_nm_profile,
            rows=rows,
            budget=budget,
            total_value=total_value,
        )
    elif budget:
        return render_template(
            "history.html",
            user_nm_profile=user_nm_profile,
            budget=budget,
            total_value=budget,
        )
    else:
        return apology("unable to read user data", 403)
