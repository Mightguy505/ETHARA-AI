import React, {useState, useEffect} from 'react';
import {getStats, getEmployees, getAllAttendance} from '../utils/api';

const Dashboard = () => {
    const[stats, setStats] = useState(null);
    const[loading, setLoading] = useState(true);
    const[error, setError] = useState('');
    const[recentEmployees, setRecentEmployees] = useState([]);
    const[recentAttendance, setRecentAttendance] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
    try {
        setLoading(true);
        setError('');

        const results = await Promise.allSettled([
            getStats(),
            getEmployees(),
            getAllAttendance()
        ]);

        if (results[0].status === 'fulfilled') {
            setStats(results[0].value.data);
        }

        if (results[1].status === 'fulfilled') {
            setRecentEmployees(results[1].value.data.slice(0, 5));
        }

        if (results[2].status === 'fulfilled') {
            setRecentAttendance(results[2].value.data.slice(0, 10));
        }

        if (results.some(r => r.status === 'rejected')) {
            setError('Some dashboard data failed to load');
            console.error(results);
        }

    } finally {
        setLoading(false);
    }
};

    
    if(loading){
        return(
            <div className="loading">
                <div className="loading-spinner"></div>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    if(error){
        return <div className="error">{error}</div>;
    }


  return (
    <>
    <div className="container">
        <div className="page-header">
            <h2>Dashboard</h2>
            <p>Overview of your HR system</p>
        </div>

        <div className="stats-grid">
            <div className="stats-card">
                <h3>Total Employees</h3>
                <div className="stat-value">{stats?.total_employees || 0}</div>
            </div>
            <div className="stat-card" style={{borderLeftColor:'27ae60'}}>
                <h3>Present Today</h3>
                <div className="stat-value">{stats?.present_today || 0}</div>
            </div>
            <div className="stat-card" style={{borderLeftColor:'f39c12'}}>
                <h3>Total Records</h3>
                <div className="stat-value">{stats?.total_records || 0}</div>
        </div>
    </div>

<div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Recent Employees</h3>
        {recentEmployees.length === 0 ? (
          <div className="empty-state">
            <p>No employees added yet</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Department</th>
                </tr>
              </thead>
              <tbody>
                {recentEmployees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td>{emp.employee_id}</td>
                    <td>{emp.full_name}</td>
                    <td>{emp.email}</td>
                    <td>{emp.department}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Recent Attendance</h3>
        {recentAttendance.length === 0 ? (
          <div className="empty-state">
            <p>No attendance records yet</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Department</th>
                </tr>
              </thead>
              <tbody>
                {recentAttendance.map((record, idx) => (
                  <tr key={idx}>
                    <td>{record.full_name}</td>
                    <td>{new Date(record.attendance_date).toLocaleDateString()}</td>
                    <td>
                      <span className={`badge ${record.status === 'Present' ? 'badge-success' : 'badge-danger'}`}>
                        {record.status}
                      </span>
                    </td>
                    <td>{record.department}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
    </>
  );
}
export default Dashboard;