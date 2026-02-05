# EtharaAI - Employee Management System

A simple Employee Management System with attendance tracking. Built with FastAPI (backend) and React (frontend).

## What You Need Before Running

- Python 3.8+
- Node.js & npm
- MySQL Server installed and running
- Git

## Setup Instructions

### 1. Database Setup

First, create the database and tables:

```bash
mysql -u root -p < Backend/schemas.sql
```

When prompted, enter your MySQL password.

### 2. Backend Setup

Navigate to the Backend folder:

```bash
cd Backend
```

Create a virtual environment (Windows):

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**Important:** Update the `.env` file with your MySQL credentials:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ems_lite
```

Run the backend server:

```bash
python app.py
```

The API will start at `http://localhost:8000`

### 3. Frontend Setup

In a new terminal, navigate to the Frontend folder:

```bash
cd Frontend/frontend
```

Install dependencies:

```bash
npm install
```

**Important:** The `.env` file should have:

```
VITE_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal)

## Features

- **Employee Management**: Add, view, and delete employees
- **Attendance Tracking**: Mark and track employee attendance
- **Dashboard**: Real-time stats showing total employees, present today, and total attendance records
- **Employee List**: View all employees with their details
- **Attendance Records**: View attendance history

## Troubleshooting

**Dashboard not showing counts?**
- Make sure MySQL server is running
- Check that the database `ems_lite` is created
- Verify database credentials in `.env`
- Check browser console for API errors

**Frontend can't connect to backend?**
- Make sure backend is running on port 8000
- Check `VITE_API_URL` in Frontend `.env` file
- Clear browser cache and refresh

**Port conflicts?**
- Backend runs on port 8000 (can change in `app.py`)
- Frontend runs on port 5173 (Vite will suggest another if in use)

## Useful Commands

Build frontend for production:
```bash
npm run build
```

Check code style:
```bash
npm run lint
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/employees` - Get all employees
- `POST /api/employees` - Add new employee
- `GET /api/employees/{id}` - Get employee details
- `DELETE /api/employees/{id}` - Delete employee
- `GET /api/attendance` - Get all attendance records
- `POST /api/attendance` - Mark attendance
- `GET /api/stats` - Get dashboard statss
