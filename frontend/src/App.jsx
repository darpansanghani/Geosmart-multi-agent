import React, { useState } from 'react';
import Map from './components/Map';
import ComplaintForm from './components/ComplaintForm';
import AgentExecutionTimeline from './components/AgentExecutionTimeline';
import ComplaintsList from './components/ComplaintsList';
import Dashboard from './components/Dashboard';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [latestResult, setLatestResult] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [currentView, setCurrentView] = useState('home'); // 'home' or 'dashboard'

  const handleLocationSelect = (lat, lng) => {
    if (lat === null || lng === null) {
      setSelectedLocation(null);
    } else {
      setSelectedLocation({ lat, lng });
    }
  };

  const handleComplaintSubmitted = (result) => {
    setLatestResult(result);
    // Add to complaints list
    setComplaints(prev => [result, ...prev]);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">G</div>
            <div>
              <span className="logo-text">GeoSmart</span>
              <span className="header-subtitle">Multi-Agent Grievance System</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
            <button
              className={currentView === 'home' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setCurrentView('home')}
              style={{ padding: 'var(--space-2) var(--space-4)' }}
            >
              📍 Submit Complaint
            </button>
            <button
              className={currentView === 'dashboard' ? 'btn btn-primary' : 'btn btn-secondary'}
              onClick={() => setCurrentView('dashboard')}
              style={{ padding: 'var(--space-2) var(--space-4)' }}
            >
              📊 Dashboard
            </button>
            {currentView === 'home' && (
              <span style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>
                🤖 6 Agents Active
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      {currentView === 'home' ? (
        <main className="main-content">
          {/* Map Section */}
          <div className="map-section">
            <Map 
              selectedLocation={selectedLocation} 
              complaints={complaints}
              onLocationSelect={handleLocationSelect}
            />
          </div>

          {/* Sidebar */}
          <aside className="sidebar">
            {/* Complaint Form */}
            <ComplaintForm 
              selectedLocation={selectedLocation}
              onComplaintSubmitted={handleComplaintSubmitted}
            />

            {/* Agent Execution Timeline */}
            {latestResult && latestResult.agent_execution_summary && (
              <AgentExecutionTimeline 
                executionData={latestResult.agent_execution_summary}
              />
            )}

            {/* Recent Complaints */}
            {complaints.length > 0 && (
              <ComplaintsList complaints={complaints.slice(0, 5)} />
            )}
          </aside>
        </main>
      ) : (
        <Dashboard />
      )}
    </div>
  );
}

export default App;
