/**
 * Multi-Dashboard Processor Component
 * 
 * Allows processing multiple dashboards with progress tracking
 */
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';

const Container = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.lg};
  font-size: 1.5rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const Input = styled.input`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const TextArea = styled.textarea`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  min-height: 100px;
  font-family: monospace;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const InputRow = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  align-items: stretch;
`;

const DashboardIdInput = styled.input`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  height: auto;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const Button = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primaryDark};
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray[400]};
    cursor: not-allowed;
  }
`;

const ProgressContainer = styled.div`
  margin-top: ${props => props.theme.spacing.xl};
  padding: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.gray[50]};
  border-radius: ${props => props.theme.borderRadius.md};
`;

const ProgressTitle = styled.h3`
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 20px;
  background: ${props => props.theme.colors.gray[200]};
  border-radius: ${props => props.theme.borderRadius.md};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => props.theme.colors.primary};
  transition: width 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
`;

const StatusText = styled.div`
  color: ${props => props.theme.colors.gray[700]};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const DashboardStatus = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background: white;
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 4px solid ${props => {
    if (props.status === 'completed') return props.theme.colors.success;
    if (props.status === 'error') return props.theme.colors.error;
    if (props.status === 'processing') return props.theme.colors.primary;
    return props.theme.colors.gray[300];
  }};
`;

const DashboardStatusTitle = styled.div`
  font-weight: 600;
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.gray[900]};
`;

const DashboardStatusDetail = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.gray[600]};
`;

const Message = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
  background: ${props => {
    if (props.type === 'success') return props.theme.colors.success + '15';
    if (props.type === 'error') return props.theme.colors.error + '15';
    return props.theme.colors.gray[100];
  }};
  color: ${props => {
    if (props.type === 'success') return props.theme.colors.success;
    if (props.type === 'error') return props.theme.colors.error;
    return props.theme.colors.gray[700];
  }};
  border: 1px solid ${props => {
    if (props.type === 'success') return props.theme.colors.success;
    if (props.type === 'error') return props.theme.colors.error;
    return props.theme.colors.gray[300];
  }};
`;

const MultiDashboardProcessor = () => {
  const [dashboardIds, setDashboardIds] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [progress, setProgress] = useState(null);
  const [progressInterval, setProgressInterval] = useState(null);

  useEffect(() => {
    // Cleanup interval on unmount
    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [progressInterval]);

  const fetchProgress = async () => {
    try {
      const progressData = await dashboardAPI.getProgress();
      setProgress(progressData);
      
      // Stop polling if completed
      if (progressData.status === 'completed' || progressData.status === 'idle') {
        if (progressInterval) {
          clearInterval(progressInterval);
          setProgressInterval(null);
        }
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);

    try {
      // Parse dashboard IDs
      const ids = dashboardIds
        .split(/[,\s]+/)
        .map(id => parseInt(id.trim()))
        .filter(id => !isNaN(id) && id > 0);

      if (ids.length === 0) {
        throw new Error('Please enter at least one valid dashboard ID');
      }

      // Start processing
      await dashboardAPI.processMultipleDashboards(ids, true, true, true);

      setMessage({
        type: 'success',
        text: `Processing started for ${ids.length} dashboards. Check progress below.`,
      });

      // Start polling for progress
      fetchProgress();
      const interval = setInterval(fetchProgress, 2000); // Poll every 2 seconds
      setProgressInterval(interval);

    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || 'Failed to start processing',
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = () => {
    if (!progress || !progress.dashboards) return 0;
    
    const total = progress.total_dashboards || 0;
    const completed = progress.completed_dashboards || 0;
    
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  return (
    <Container>
      <Title>Process Multiple Dashboards</Title>
      
      {message && (
        <Message type={message.type}>{message.text}</Message>
      )}

      <Form onSubmit={handleSubmit}>
        <label>
          Dashboard IDs (comma or space separated):
        </label>
        <InputRow>
          <DashboardIdInput
            type="text"
            value={dashboardIds}
            onChange={(e) => setDashboardIds(e.target.value)}
            placeholder="585, 729, 476, 842, 511, 588, 964, 915, 567, 583, 657, 195, 249"
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !dashboardIds.trim()}>
            {loading ? 'Starting...' : 'Start Processing'}
          </Button>
        </InputRow>
      </Form>

      {progress && progress.status !== 'idle' && (
        <ProgressContainer>
          <ProgressTitle>Processing Progress</ProgressTitle>
          
          <StatusText>
            Status: <strong>{progress.status}</strong> | 
            Operation: <strong>{progress.current_operation || 'N/A'}</strong>
          </StatusText>
          
          {progress.status === 'extracting' && (
            <>
              <ProgressBar>
                <ProgressFill style={{ width: `${calculateProgress()}%` }}>
                  {calculateProgress()}%
                </ProgressFill>
              </ProgressBar>
              <StatusText>
                Completed: {progress.completed_dashboards || 0} / {progress.total_dashboards || 0} dashboards
                {progress.failed_dashboards > 0 && ` | Failed: ${progress.failed_dashboards}`}
              </StatusText>
            </>
          )}

          {progress.dashboards && Object.keys(progress.dashboards).length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              {Object.values(progress.dashboards).map((dashboard) => (
                <DashboardStatus key={dashboard.dashboard_id} status={dashboard.status}>
                  <DashboardStatusTitle>
                    Dashboard {dashboard.dashboard_id} - {dashboard.status}
                  </DashboardStatusTitle>
                  {dashboard.current_phase && (
                    <DashboardStatusDetail>
                      Phase: {dashboard.current_phase}
                    </DashboardStatusDetail>
                  )}
                  {dashboard.current_file && (
                    <DashboardStatusDetail style={{ fontWeight: 'bold', color: '#1e40af' }}>
                      📄 Working on: {dashboard.current_file}
                    </DashboardStatusDetail>
                  )}
                  {dashboard.completed_files_count > 0 && (
                    <DashboardStatusDetail>
                      Files: {dashboard.completed_files_count} / {dashboard.total_files}
                    </DashboardStatusDetail>
                  )}
                  {dashboard.error && (
                    <DashboardStatusDetail style={{ color: '#dc2626' }}>
                      Error: {dashboard.error}
                    </DashboardStatusDetail>
                  )}
                </DashboardStatus>
              ))}
            </div>
          )}

          {progress.merge_status && progress.merge_status.status !== 'pending' && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'white', borderRadius: '8px' }}>
              <strong>Merge Status:</strong> {progress.merge_status.status}
              {progress.merge_status.current_step && (
                <div>Current Step: {progress.merge_status.current_step}</div>
              )}
            </div>
          )}

          {progress.kb_build_status && progress.kb_build_status.status !== 'pending' && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'white', borderRadius: '8px' }}>
              <strong>Knowledge Base Build Status:</strong> {progress.kb_build_status.status}
              {progress.kb_build_status.current_step && (
                <div>Current Step: {progress.kb_build_status.current_step}</div>
              )}
            </div>
          )}
        </ProgressContainer>
      )}
    </Container>
  );
};

export default MultiDashboardProcessor;

