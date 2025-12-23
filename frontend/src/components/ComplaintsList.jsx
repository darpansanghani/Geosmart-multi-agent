import React from 'react';

const ComplaintsList = ({ complaints }) => {
  if (!complaints || complaints.length === 0) {
    return null;
  }

  const getSeverityBadgeClass = (severity) => {
    const map = {
      'High': 'badge-high',
      'Medium': 'badge-medium',
      'Low': 'badge-low'
    };
    return map[severity] || 'badge-pending';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Recent Complaints</h3>
        <p className="card-description">
          Latest {complaints.length} submissions
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        {complaints.map((complaint) => (
          <div
            key={complaint.id}
            style={{
              padding: 'var(--space-3)',
              background: 'var(--bg-tertiary)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              transition: 'all var(--transition-base)',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-hover)';
              e.currentTarget.style.background = 'var(--bg-secondary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.background = 'var(--bg-tertiary)';
            }}
          >
            {/* Header with Category and Time */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'start',
              marginBottom: 'var(--space-2)'
            }}>
              <span style={{
                fontSize: '0.875rem',
                fontWeight: '600',
                color: 'var(--text-primary)'
              }}>
                {complaint.category || 'Uncategorized'}
              </span>
              <span style={{
                fontSize: '0.75rem',
                color: 'var(--text-tertiary)'
              }}>
                {formatTime(complaint.created_at)}
              </span>
            </div>

            {/* Complaint Text Preview */}
            <p style={{
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              margin: '0 0 var(--space-2) 0',
              lineHeight: '1.4',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {complaint.text}
            </p>

            {/* Badges */}
            <div style={{
              display: 'flex',
              gap: 'var(--space-2)',
              flexWrap: 'wrap'
            }}>
              {complaint.severity && (
                <span className={`badge ${getSeverityBadgeClass(complaint.severity)}`}>
                  {complaint.severity}
                </span>
              )}
              {complaint.department && (
                <span className="badge" style={{
                  background: 'rgba(14, 165, 233, 0.15)',
                  color: 'var(--primary-400)',
                  border: '1px solid rgba(14, 165, 233, 0.3)'
                }}>
                  {complaint.department.replace('GHMC ', '')}
                </span>
              )}
              {complaint.zone_name && (
                <span className="badge" style={{
                  background: 'rgba(156, 163, 175, 0.15)',
                  color: 'var(--text-tertiary)',
                  border: '1px solid rgba(156, 163, 175, 0.3)'
                }}>
                  {complaint.zone_name}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComplaintsList;
