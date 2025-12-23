import React from 'react';

const AgentExecutionTimeline = ({ executionData }) => {
  if (!executionData || !executionData.agents_executed) {
    return null;
  }

  const { total_agents, execution_time_ms, agents_executed } = executionData;

  const getAgentIcon = (agentName) => {
    const icons = {
      'UnderstandingAgent': '🧠',
      'GISIntelligenceAgent': '🗺️',
      'ClassificationAgent': '🏷️',
      'RoutingAgent': '🎯',
      'ActionPlanningAgent': '📋'
    };
    return icons[agentName] || '🤖';
  };

  const getStatusColor = (status) => {
    return status === 'success' ? 'var(--accent-400)' : 'var(--error-400)';
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">🤖 Multi-Agent Execution</h3>
        <p className="card-description">
          {total_agents} agents • {execution_time_ms}ms total
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        {agents_executed.map((agent, index) => (
          <div
            key={index}
            style={{
              position: 'relative',
              paddingLeft: 'var(--space-8)'
            }}
          >
            {/* Timeline Line */}
            {index < agents_executed.length - 1 && (
              <div style={{
                position: 'absolute',
                left: '11px',
                top: '24px',
                bottom: '-16px',
                width: '2px',
                background: 'var(--border-color)'
              }} />
            )}

            {/* Agent Icon */}
            <div style={{
              position: 'absolute',
              left: '0',
              top: '0',
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: agent.status === 'success' 
                ? 'rgba(52, 211, 153, 0.2)' 
                : 'rgba(239, 68, 68, 0.2)',
              border: `2px solid ${getStatusColor(agent.status)}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px'
            }}>
              {getAgentIcon(agent.name)}
            </div>

            {/* Agent Details */}
            <div style={{
              background: 'var(--bg-tertiary)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-3)',
              border: '1px solid var(--border-color)'
            }}>
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
                  {agent.name.replace('Agent', '')}
                </span>
                <span style={{
                  fontSize: '0.75rem',
                  color: getStatusColor(agent.status),
                  fontWeight: '500'
                }}>
                  {agent.execution_time_ms}ms
                </span>
              </div>

              {agent.key_findings && (
                <p style={{
                  fontSize: '0.75rem',
                  color: 'var(--text-tertiary)',
                  margin: 0,
                  lineHeight: '1.4'
                }}>
                  {agent.key_findings}
                </p>
              )}

              {agent.error && (
                <p style={{
                  fontSize: '0.75rem',
                  color: 'var(--error-400)',
                  margin: '0.5rem 0 0 0'
                }}>
                  Error: {agent.error}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div style={{
        marginTop: 'var(--space-4)',
        padding: 'var(--space-3)',
        background: 'rgba(14, 165, 233, 0.1)',
        border: '1px solid rgba(14, 165, 233, 0.3)',
        borderRadius: 'var(--radius-md)',
        fontSize: '0.75rem',
        color: 'var(--primary-400)',
        textAlign: 'center'
      }}>
        ✓ Multi-agent processing complete
      </div>
    </div>
  );
};

export default AgentExecutionTimeline;
