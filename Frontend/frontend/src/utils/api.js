import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Employee APIs
export const getEmployees = () => api.get('/api/employees');
export const getEmployee = (id) => api.get(`/api/employees/${id}`);
export const createEmployee = (data) => api.post('/api/employees', data);
export const deleteEmployee = (id) => api.delete(`/api/employees/${id}`);

// Attendance APIs
export const getAllAttendance = () => api.get('/api/attendance');
export const getEmployeeAttendance = (employeeId, date = null) => {
    const url = date 
        ? `/api/attendance/${employeeId}?date=${date}`
        : `/api/attendance/${employeeId}`;
    return api.get(url);
};

export const markAttendance = (data) => api.post('/api/attendance', data);

// Stats API
export const getStats = () => api.get('/api/stats');

// Health check
export const healthCheck = () => api.get('/api/health');

export default api;