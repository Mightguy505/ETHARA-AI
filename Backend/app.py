from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date
import mysql.connector
from mysql.connector import Error
import os
from contextlib import contextmanager
import logging

# ------------------ APP SETUP ------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ethara-ai-s48k.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LOGGING ------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------ DATABASE CONFIG ------------------
# ⚠️ NO localhost defaults in production

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST"),
    "port": int(os.getenv("MYSQLPORT", 3306)),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE"),
}


missing_vars = [k for k, v in DB_CONFIG.items() if v is None]
if missing_vars:
    logging.error("Missing DB env vars: %s", missing_vars)

@contextmanager
def get_db_connection():
    conn = None
    try:
        logging.info(
            "Connecting to DB host=%s db=%s",
            DB_CONFIG["host"],
            DB_CONFIG["database"],
        )
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        logging.error("Database connection failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        if conn and conn.is_connected():
            conn.close()

# ------------------ MODELS ------------------

class Employee(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

    @field_validator("employee_id", "full_name", "department")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

class Attendance(BaseModel):
    employee_id: str
    attendance_date: date
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ["Present", "Absent"]:
            raise ValueError("Status must be Present or Absent")
        return v

# ------------------ ROUTES ------------------

@app.get("/")
def root():
    return {"message": "EtharaAI API running"}

@app.get("/api/health")
def health_check():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
    return {"status": "healthy", "db": "connected"}

# -------- EMPLOYEES --------

@app.post("/api/employees")
def create_employee(employee: Employee):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT employee_id FROM employees WHERE employee_id=%s",
            (employee.employee_id,),
        )
        if cursor.fetchone():
            raise HTTPException(400, "Employee ID already exists")

        cursor.execute(
            "SELECT email FROM employees WHERE email=%s",
            (employee.email,),
        )
        if cursor.fetchone():
            raise HTTPException(400, "Email already exists")

        cursor.execute(
            """
            INSERT INTO employees (employee_id, full_name, email, department)
            VALUES (%s, %s, %s, %s)
            """,
            (employee.employee_id, employee.full_name, employee.email, employee.department),
        )
        conn.commit()
        cursor.close()

    return {"message": "Employee created"}

@app.get("/api/employees")
def get_employees():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees ORDER BY created_at DESC")
        data = cursor.fetchall()
        cursor.close()
    return data

@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE employee_id=%s", (employee_id,))
        cursor.execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
        conn.commit()
        cursor.close()
    return {"message": "Employee deleted"}

# -------- ATTENDANCE --------

@app.post("/api/attendance")
def mark_attendance(attendance: Attendance):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO attendance (employee_id, attendance_date, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status=%s
            """,
            (
                attendance.employee_id,
                attendance.attendance_date,
                attendance.status,
                attendance.status,
            ),
        )
        conn.commit()
        cursor.close()

    return {"message": "Attendance marked"}

@app.get("/api/attendance")
def get_all_attendance():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.*, e.full_name, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            ORDER BY a.attendance_date DESC
            """
        )
        data = cursor.fetchall()
        cursor.close()
    return data

# -------- STATS --------

@app.get("/api/stats")
def get_stats():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total_employees = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM attendance WHERE attendance_date = CURDATE() AND status='Present'"
        )
        present_today = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM attendance")
        total_records = cursor.fetchone()["total"]

        cursor.close()

    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "total_records": total_records,
    }
