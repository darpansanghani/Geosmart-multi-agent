import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
    department: ''
  });
  const [stats, setStats] = useState(null);

  // Fetch complaints and stats
  useEffect(() => {
    fetchComplaints();
    fetchStats();
  }, [filters]);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.status) params.append('status', filters.status);
      if (filters.department) params.append('department', filters.department);
      params.append('limit', '50');

      const response = await axios.get(`/api/complaints?${params}`);
      if (response.data.success) {
        setComplaints(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching complaints:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const getSeverityBadgeClass = (severity) => {
    const map = {
      'High': 'badge-high',
      'Medium': 'badge-medium',
      'Low': 'badge-low'
    };
    return map[severity] || 'badge-pending';
  };

  const getStatusBadgeClass = (status) => {
    const map = {
      'resolved': 'badge-success',
      'in-progress': 'badge-medium',
      'pending': 'badge-pending'
    };
    return map[status] || 'badge-pending';
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-8)' }}>
        <h1 style={{ marginBottom: 'var(--space-2)' }}>Complaints Dashboard</h1>
        <p style={{ color: 'var(--text-tertiary)', fontSize: '0.875rem' }}>
          Monitor and manage all civic complaints
        </p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-6)'
        }}>
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-1)' }}>
              Total Complaints
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--primary-400)' }}>
              {stats.overview.total_complaints}
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-1)' }}>
              Pending
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--warning-400)' }}>
              {stats.overview.pending}
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-1)' }}>
              In Progress
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent-400)' }}>
              {stats.overview.in_progress}
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-1)' }}>
              Resolved
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--accent-500)' }}>
              {stats.overview.resolved}
            </div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: 'var(--space-1)' }}>
              High Severity
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--error-400)' }}>
              {stats.overview.high_severity}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <h3 className="card-title" style={{ marginBottom: 'var(--space-4)' }}>Filters</h3>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-4)'
        }}>
          {/* Severity Filter */}
          <div>
            <label className="form-label">Severity</label>
            <select
              className="form-input"
              value={filters.severity}
              onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            >
              <option value="">All Severities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="form-label">Status</label>
            <select
              className="form-input"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          {/* Department Filter */}
          <div>
            <label className="form-label">Department</label>
            <select
              className="form-input"
              value={filters.department}
              onChange={(e) => setFilters({ ...filters, department: e.target.value })}
            >
              <option value="">All Departments</option>
              <option value="Sanitation">GHMC Sanitation</option>
              <option value="Roads">GHMC Roads</option>
              <option value="Electrical">GHMC Electrical</option>
              <option value="Water">GHMC Water Works</option>
              <option value="Engineering">GHMC Engineering</option>
            </select>
          </div>

          {/* Clear Filters */}
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className="btn btn-secondary"
              onClick={() => setFilters({ severity: '', status: '', department: '' })}
              style={{ width: '100%' }}
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Complaints Table */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: 'var(--space-4)' }}>
          All Complaints ({complaints.length})
        </h3>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-tertiary)' }}>
            <div className="loading-spinner" style={{ margin: '0 auto var(--space-4)' }}></div>
            Loading complaints...
          </div>
        ) : complaints.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--text-tertiary)' }}>
            No complaints found matching the filters
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '0.875rem'
            }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>ID</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Complaint</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Category</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Severity</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Status</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Department</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Zone</th>
                  <th style={{ padding: 'var(--space-3)', textAlign: 'left', color: 'var(--text-tertiary)', fontWeight: '500' }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {complaints.map((complaint) => (
                  <tr 
                    key={complaint.id}
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      transition: 'background var(--transition-fast)',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-tertiary)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: 'var(--space-3)', color: 'var(--text-tertiary)' }}>
                      #{complaint.id}
                    </td>
                    <td style={{ padding: 'var(--space-3)', maxWidth: '300px' }}>
                      <div style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        color: 'var(--text-primary)'
                      }}>
                        {complaint.text}
                      </div>
                    </td>
                    <td style={{ padding: 'var(--space-3)' }}>
                      {complaint.category || '-'}
                    </td>
                    <td style={{ padding: 'var(--space-3)' }}>
                      {complaint.severity && (
                        <span className={`badge ${getSeverityBadgeClass(complaint.severity)}`}>
                          {complaint.severity}
                        </span>
                      )}
                    </td>
                    <td style={{ padding: 'var(--space-3)' }}>
                      <span className={`badge ${getStatusBadgeClass(complaint.status)}`}>
                        {complaint.status}
                      </span>
                    </td>
                    <td style={{ padding: 'var(--space-3)', fontSize: '0.8125rem' }}>
                      {complaint.department ? complaint.department.replace('GHMC ', '') : '-'}
                    </td>
                    <td style={{ padding: 'var(--space-3)', fontSize: '0.8125rem', color: 'var(--text-tertiary)' }}>
                      {complaint.zone_name || '-'}
                    </td>
                    <td style={{ padding: 'var(--space-3)', fontSize: '0.8125rem', color: 'var(--text-tertiary)' }}>
                      {formatDate(complaint.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
