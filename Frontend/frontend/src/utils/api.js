import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://ethara-ai-s48k.vercel.app';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Employee APIs
export const getEmployees = () => api.get(`${API_URL}/api/employees`);
export const getEmployee = (id) => api.get(`${API_URL}/api/employees/${id}`);
export const createEmployee = (data) => api.post(`${API_URL}/api/employees`, data);
export const deleteEmployee = (id) => api.delete(`${API_URL}/api/employees/${id}`);

// Attendance APIs
export const getAllAttendance = () => api.get(`${API_URL}/api/attendance`);
export const getEmployeeAttendance = (employeeId, date = null) => {
    const url = date 
        ? `${API_URL}/api/attendance/${employeeId}?date=${date}`
        : `${API_URL}/api/attendance/${employeeId}`;
    return api.get(url);
};

export const markAttendance = (data) => api.post(`${API_URL}/api/attendance`, data);

// Stats API
export const getStats = () => api.get(`${API_URL}/api/stats`);

// Health check
export const healthCheck = () => api.get(`${API_URL}/api/health`);

export default api;