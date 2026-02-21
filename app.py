from flask import Flask, render_template, request, redirect, url_for
import calendar
import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = "reminders.json"

def load_reminders():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_reminders(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    year = int(request.args.get("year", datetime.date.today().year))
    month = int(request.args.get("month", datetime.date.today().month))

    cal = calendar.monthcalendar(year, month)
    reminders = load_reminders()

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
    date = request.form["date"]
    text = request.form["text"]

    reminders = load_reminders()
    reminders.setdefault(date, []).append(text)
    save_reminders(reminders)

    y, m, _ = date.split("-")
    return redirect(url_for("index", year=y, month=m))

@app.route("/delete", methods=["POST"])
def delete_reminder():
    date = request.form["date"]
    index = int(request.form["index"])

    reminders = load_reminders()
    reminders[date].pop(index)

    if not reminders[date]:
        del reminders[date]

    save_reminders(reminders)

    y, m, _ = date.split("-")
    return redirect(url_for("index", year=y, month=m))

if __name__ == "__main__":
    app.run(debug=True)