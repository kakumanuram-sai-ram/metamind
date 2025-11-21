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

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  padding-bottom: ${props => props.theme.spacing.md};
  border-bottom: 2px solid ${props => props.theme.colors.gray[200]};
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

// Removed unused styled components - using inline styles instead

const JSONContainer = styled.div`
  background: ${props => props.theme.colors.gray[900]};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.md};
  overflow-x: auto;
  max-height: ${props => props.$expanded ? 'none' : '600px'};
  overflow-y: ${props => props.$expanded ? 'visible' : 'auto'};
`;

const JSONPre = styled.pre`
  color: ${props => props.theme.colors.gray[100]};
  font-family: ${props => props.theme.typography.fontFamily.mono};
  font-size: ${props => props.theme.typography.fontSize.sm};
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray[600]};
`;

const ErrorMessage = styled.div`
  background: ${props => props.theme.colors.error}15;
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.error};
`;

const JSONViewer = ({ dashboardId }) => {
  const [jsonData, setJsonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchJSON = async () => {
      if (!dashboardId) return;

      try {
        setLoading(true);
        setError(null);
        const data = await dashboardAPI.getDashboardJSON(dashboardId);
        setJsonData(data);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load JSON data');
        console.error('Error fetching JSON:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJSON();
  }, [dashboardId]);

  if (!dashboardId) {
    return (
      <Container>
        <Title>JSON Data</Title>
        <LoadingMessage>Select a dashboard to view JSON data</LoadingMessage>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container>
        <Title>JSON Data</Title>
        <LoadingMessage>Loading JSON data...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Title>JSON Data</Title>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  const handleDownload = async () => {
    try {
      const blob = await dashboardAPI.downloadJSON(dashboardId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard_${dashboardId}_info.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading JSON:', err);
      alert('Failed to download JSON file');
    }
  };

  // Debug: Log when component renders
  console.log('JSONViewer rendering with dashboardId:', dashboardId, 'jsonData:', !!jsonData);

  return (
    <Container>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title>JSON Data</Title>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button 
            onClick={handleDownload} 
            title="Download JSON file"
            style={{ 
              background: '#FF6F00', 
              color: 'white', 
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            📥 Download JSON
          </button>
          <button 
            onClick={() => setExpanded(!expanded)} 
            title="Expand/Collapse JSON view"
            style={{
              background: '#E5E7EB',
              color: '#374151',
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        </div>
      </Header>
      <JSONContainer $expanded={expanded}>
        <JSONPre>{JSON.stringify(jsonData, null, 2)}</JSONPre>
      </JSONContainer>
    </Container>
  );
};

export default JSONViewer;

