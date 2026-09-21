import os
import sqlite3
from datetime import datetime
from pathlib import Path
from employee_data import EMPLOYEES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = (
    "/tmp/employee.db"
    if os.environ.get("VERCEL")
    else os.path.join(BASE_DIR, "database", "employee.db")
)
DB_PATH = os.environ.get(
    "DATABASE_PATH",
    DEFAULT_DB_PATH,
)


class Database:

    def __init__(self):

        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

        self.attendance_marked = set()
        self.attendance_date = datetime.now().strftime("%Y-%m-%d")


    # =====================================================
    # CREATE TABLES
    # =====================================================

    def create_tables(self):

        # -------------------------
        # Employee Table
        # -------------------------

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                employee_id TEXT UNIQUE,

                name TEXT,

                email TEXT UNIQUE,

                department TEXT,

                designation TEXT

            )
        """)


        # -------------------------
        # Attendance Table
        # -------------------------

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT,

                date TEXT,

                time TEXT

            )
        """)


        # -------------------------
        # Violation Table
        # -------------------------

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT,

                violation_time TEXT,

                warning_count INTEGER

            )
        """)


        # -------------------------
        # Email Log Table
        # -------------------------

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_logs(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT,

                receiver TEXT,

                send_time TEXT

            )
        """)


        self.connection.commit()
        self.seed_employees()

    def seed_employees(self):

        for name, employee in EMPLOYEES.items():

            self.cursor.execute("""
                INSERT INTO employees(
                    employee_id,
                    name,
                    email,
                    department,
                    designation
                )
                VALUES(?,?,?,?,?)
                ON CONFLICT(employee_id) DO UPDATE SET
                    name = excluded.name,
                    email = excluded.email,
                    department = excluded.department,
                    designation = excluded.designation
            """, (
                employee["employee_id"],
                name,
                employee["email"],
                employee["department"],
                employee["designation"]
            ))

        self.connection.commit()

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    def _generate_employee_id(self):

        self.cursor.execute("""
            SELECT employee_id
            FROM employees
            WHERE employee_id LIKE 'EMP%'
            ORDER BY CAST(SUBSTR(employee_id, 4) AS INTEGER) DESC
            LIMIT 1
        """)

        row = self.cursor.fetchone()

        if row is None:
            return "EMP001"

        try:
            last_number = int(str(row[0])[3:])
        except (TypeError, ValueError):
            last_number = 0

        return f"EMP{last_number + 1:03d}"

    def add_employee(
        self,
        employee_id,
        name=None,
        email=None,
        department=None,
        designation=None
    ):

        if email is None and department is None and designation is None:
            legacy_name, legacy_email = employee_id, name
            employee_id = None
            name = legacy_name
            email = legacy_email

        if name is None:
            name = ""

        if email is None:
            email = ""

        if department is None:
            department = "General"

        if designation is None:
            designation = "Employee"

        if employee_id is None:
            employee_id = self._generate_employee_id()

        existing = self.cursor.execute("""
            SELECT employee_id
            FROM employees
            WHERE lower(trim(name)) = lower(trim(?))
               OR lower(trim(email)) = lower(trim(?))
            LIMIT 1
        """, (name, email)).fetchone()

        if existing is not None:
            employee_id = existing[0]

        self.cursor.execute("""
            INSERT INTO employees(

                employee_id,
                name,
                email,
                department,
                designation

            )

            VALUES(?,?,?,?,?)
            ON CONFLICT(employee_id) DO UPDATE SET
                name = excluded.name,
                email = excluded.email,
                department = excluded.department,
                designation = excluded.designation
        """, (

            employee_id,
            name,
            email,
            department,
            designation

        ))

        self.connection.commit()

        return employee_id


    # =====================================================
    # GET EMPLOYEE BY NAME
    # =====================================================

    def get_employee(self, name):

        self.cursor.execute("""
            SELECT

                employee_id,
                name,
                email,
                department,
                designation

            FROM employees

            WHERE lower(trim(name)) = lower(trim(?))
               OR lower(trim(name)) LIKE lower(trim(?)) || ' %'

            ORDER BY CASE
                WHEN lower(trim(name)) = lower(trim(?)) THEN 0
                ELSE 1
            END, id DESC

            LIMIT 1

        """, (name, name, name))


        row = self.cursor.fetchone()


        if row is None:

            return None


        return {

            "employee_id": row[0],

            "name": row[1],

            "email": row[2],

            "department": row[3],

            "designation": row[4]

        }


    # =====================================================
    # GET ALL EMPLOYEES
    # =====================================================

    def get_all_employees(self):

        self.cursor.execute("""
            SELECT

                employee_id,
                name,
                email,
                department,
                designation

            FROM employees

            ORDER BY id DESC

        """)

        return self.cursor.fetchall()


    # =====================================================
    # ATTENDANCE
    # =====================================================

    def mark_attendance(self, name):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        if today != self.attendance_date:
            self.attendance_marked.clear()
            self.attendance_date = today

        if name in self.attendance_marked:
            return False

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )


        self.cursor.execute("""
            INSERT INTO attendance(

                name,
                date,
                time

            )

            VALUES(?,?,?)

        """, (

            name,
            today,
            current_time

        ))


        self.connection.commit()


        self.attendance_marked.add(name)


        print(
            f"✅ Attendance Marked : {name}"
        )

        return True


    # =====================================================
    # ADD VIOLATION
    # =====================================================

    def add_violation(
        self,
        name,
        warning
    ):

        current_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        self.cursor.execute("""
            INSERT INTO violations(

                name,
                violation_time,
                warning_count

            )

            VALUES(?,?,?)

        """, (

            name,
            current_time,
            warning

        ))


        self.connection.commit()


    # =====================================================
    # LOG EMAIL
    # =====================================================

    def log_email(
        self,
        name,
        receiver
    ):

        current_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        self.cursor.execute("""
            INSERT INTO email_logs(

                name,
                receiver,
                send_time

            )

            VALUES(?,?,?)

        """, (

            name,
            receiver,
            current_time

        ))


        self.connection.commit()

    def get_attendance(self):

        self.cursor.execute("""
            SELECT name, date, time
            FROM attendance
            ORDER BY date DESC, time DESC
        """)

        return self.cursor.fetchall()

    def get_violations(self):

        self.cursor.execute("""
            SELECT name, violation_time, warning_count
            FROM violations
            ORDER BY violation_time DESC
        """)

        return self.cursor.fetchall()

    def get_email_logs(self):

        self.cursor.execute("""
            SELECT name, receiver, send_time
            FROM email_logs
            ORDER BY send_time DESC
        """)

        return self.cursor.fetchall()


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    def close(self):

        self.connection.close()