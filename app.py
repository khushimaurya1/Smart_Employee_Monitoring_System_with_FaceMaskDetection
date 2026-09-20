from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from database import Database

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
db = Database()


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/employees")
def employees():
    employees_list = db.get_all_employees()
    return render_template("employees.html", employees=employees_list)


@app.route("/add_employee")
def add_employee():
    return render_template("add_employee.html")


@app.route("/save_employee", methods=["POST"])
def save_employee():
    employee_id = request.form.get("employee_id", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()

    if not employee_id or not name or not email:
        return redirect(url_for("add_employee"))

    db.add_employee(
        employee_id=employee_id,
        name=name,
        email=email,
        department=department,
        designation=designation,
    )

    return redirect(url_for("employees"))


@app.route("/attendance")
def attendance():
    attendance_list = db.get_attendance()
    return render_template("attendance.html", attendance=attendance_list)


@app.route("/violations")
def violations():
    violation_list = db.get_violations()
    return render_template("violations.html", violations=violation_list)


@app.route("/email_logs")
def email_logs():
    logs = db.get_email_logs()
    return render_template("email_logs.html", email_logs=logs)


@app.route("/camera")
def camera():
    return render_template("camera.html", running=False)


@app.route("/start_monitoring", methods=["POST"])
def start_monitoring():
    script_path = BASE_DIR / "main.py"
    if script_path.exists():
        subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            creationflags=0,
        )
    return redirect(url_for("camera"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
