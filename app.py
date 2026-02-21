from flask import Flask, render_template, request, redirect, url_for, session
import calendar
import datetime
import sqlite3
import os
from models import init_db, get_db

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# Initialize DB tables
init_db()

def get_current_user():
    return session.get("user_id")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        c = db.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            return "Username already exists. Go back and try another."
        db.close()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        c = db.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        db.close()

        if user:
            session["user_id"] = user[0]
            return redirect(url_for("index"))
        else:
            return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not get_current_user():
        return redirect(url_for("login"))

    year = int(request.args.get("year", datetime.date.today().year))
    month = int(request.args.get("month", datetime.date.today().month))
    cal = calendar.monthcalendar(year, month)

    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, date, text FROM reminders WHERE user_id=?", (get_current_user(),))
    rows = c.fetchall()
    db.close()

    reminders = {}
    for r_id, date, text in rows:
        reminders.setdefault(date, []).append({"id": r_id, "text": text})

    return render_template(
        "index.html",
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        cal=cal,
        reminders=reminders
    )

@app.route("/add", methods=["POST"])
def add_reminder():
    if not get_current_user():
        return redirect(url_for("login"))

    date = request.form["date"]
    text = request.form["text"]

    db = get_db()
    c = db.cursor()
    c.execute(
        "INSERT INTO reminders (user_id, date, text) VALUES (?, ?, ?)",
        (get_current_user(), date, text)
    )
    db.commit()
    db.close()

    y, m, _ = date.split("-")
    return redirect(url_for("index", year=y, month=m))

@app.route("/delete", methods=["POST"])
def delete_reminder():
    if not get_current_user():
        return redirect(url_for("login"))

    reminder_id = request.form["id"]

    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (reminder_id, get_current_user()))
    db.commit()
    db.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)