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
from dotenv import load_dotenv

# Load environment variables from .env file - THIS IS CRITICAL!
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:3000",  
        "https://your-frontend.vercel.app","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ems_lite')  # Changed default to match your schema
}

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@contextmanager
def get_db_connection():
    connection = None
    try:
        logging.debug("Attempting to connect to the database with config: %s", {**DB_CONFIG, 'password': '***'})
        connection = mysql.connector.connect(**DB_CONFIG)
        logging.debug("Database connection established successfully.")
        yield connection
    except Error as e:
        logging.error("Database connection failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    finally:
        if connection and connection.is_connected():
            logging.debug("Closing database connection.")
            connection.close()
            

class Employee(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID cannot be empty') 
        return v.strip() 
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full name cannot be empty') 
        return v.strip() 
    
    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        if not v or not v.strip():
            raise ValueError('Department cannot be empty') 
        return v.strip() 
    
class Attendance(BaseModel):
    employee_id: str
    attendance_date: date
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['Present', 'Absent']:
            raise ValueError('Status must be either Present or Absent')
        return v        
    
# -------------- API Endpoints ----------------
@app.get('/')
def root():
    return {"message": "Welcome to EtharaAI Employee Management System"}
 
@app.get("/api/health")
def health_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1") 
            cursor.fetchone()
            cursor.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}  
    
    
#-------------- Employee Endpoints ----------------
#  POST REQUEST - To Create Employee
@app.post("/api/employees")  
def create_employee(employee: Employee):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (employee.employee_id,))
            if cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=400, detail="Employee ID already exists")
            
            cursor.execute("SELECT email FROM employees WHERE email = %s", (employee.email,))
            if cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=400, detail="Email already exists")
            
            query = """INSERT INTO employees (employee_id, full_name, email, department) VALUES (%s, %s, %s, %s)"""
            
            cursor.execute(query, (employee.employee_id, employee.full_name, employee.email, employee.department))
            conn.commit()
            cursor.close()
            
        return {"message": "Employee created successfully", "employee_id": employee.employee_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# GET REQUEST - To Get Employees
@app.get("/api/employees")
def get_employees():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM employees ORDER BY created_at DESC")
            employees = cursor.fetchall()
            cursor.close()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
                 
@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))    
            employee = cursor.fetchone()
            cursor.close()
            
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return employee
    except HTTPException:
        raise   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# DELETE REQUEST - To Delete Employee
@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (employee_id,))   
            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=404, detail="Employee not found")  
            
            cursor.execute("DELETE FROM attendance WHERE employee_id = %s", (employee_id,))   
            
            cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
            conn.commit()
            cursor.close()
        return {"message": "Employee deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
#-------------- ATTENDANCE Endpoints ----------------
# POST REQUEST - To Mark Attendance
@app.post("/api/attendance")
def mark_attendance(attendance: Attendance):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (attendance.employee_id,))
            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=404, detail="Employee not found")
            
            cursor.execute("SELECT id FROM attendance WHERE employee_id = %s AND attendance_date = %s", (attendance.employee_id, attendance.attendance_date))
            
            existing = cursor.fetchone()
            
            if existing:
                query = """UPDATE attendance SET status = %s WHERE employee_id = %s AND attendance_date = %s"""
                cursor.execute(query, (attendance.status, attendance.employee_id, attendance.attendance_date))
            else:
                query = """INSERT INTO attendance (employee_id, attendance_date, status) VALUES (%s, %s, %s)"""
                cursor.execute(query, (attendance.employee_id, attendance.attendance_date, attendance.status))
            conn.commit()
            cursor.close()
        return {"message": "Attendance marked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/attendance/{employee_id}")
def get_attendance(employee_id: str, date: Optional[str] = None):
    try: 
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (employee_id,))
            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=404, detail="Employee not found")
            
            if date:
                query = """SELECT * FROM attendance WHERE employee_id = %s AND attendance_date = %s ORDER BY attendance_date DESC"""
                cursor.execute(query, (employee_id, date))
            else:
                query = """SELECT * FROM attendance WHERE employee_id = %s ORDER BY attendance_date DESC"""
                cursor.execute(query, (employee_id,)) 
            records = cursor.fetchall()       
            cursor.close()
        return records
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/attendance")
def get_all_attendance():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT a.*, e.full_name, e.department FROM attendance a JOIN employees e ON a.employee_id = e.employee_id ORDER BY a.attendance_date DESC, e.full_name"""
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/stats")
def get_stats():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            logging.debug("Fetching total employees count.")
            cursor.execute("SELECT COUNT(*) as total FROM employees")
            total_employees = cursor.fetchone()
            logging.debug("Total employees: %s", total_employees)

            logging.debug("Fetching present employees count for today.")
            cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE attendance_date = CURDATE() AND status = 'Present'")
            present_today = cursor.fetchone()
            logging.debug("Present today: %s", present_today)

            logging.debug("Fetching total attendance records count.")
            cursor.execute("SELECT COUNT(*) as total FROM attendance")
            total_records = cursor.fetchone()
            logging.debug("Total attendance records: %s", total_records)

            cursor.close()
        return {
            "total_employees": total_employees['total'] if total_employees else 0,
            "present_today": present_today['total'] if present_today else 0,
            "total_records": total_records['total'] if total_records else 0
        }
    except Exception as e:
        logging.error("Error in /api/stats: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)