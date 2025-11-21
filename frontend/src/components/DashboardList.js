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
  margin-bottom: ${props => props.theme.spacing.lg};
  padding-bottom: ${props => props.theme.spacing.md};
  border-bottom: 2px solid ${props => props.theme.colors.gray[200]};
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const RefreshButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primaryLight};
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const DashboardCard = styled.div`
  background: ${props => props.theme.colors.gray[50]};
  border: 2px solid ${props => props.theme.colors.gray[200]};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.md};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    box-shadow: ${props => props.theme.shadows.md};
    transform: translateY(-2px);
  }
`;

const DashboardTitle = styled.h3`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const DashboardId = styled.div`
  color: ${props => props.theme.colors.gray[600]};
  font-size: ${props => props.theme.typography.fontSize.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const DashboardUrl = styled.a`
  color: ${props => props.theme.colors.accent};
  font-size: ${props => props.theme.typography.fontSize.sm};
  word-break: break-all;
  display: block;
  margin-top: ${props => props.theme.spacing.sm};

  &:hover {
    color: ${props => props.theme.colors.accentDark};
    text-decoration: underline;
  }
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

const DashboardList = ({ onSelectDashboard }) => {
  const [dashboards, setDashboards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboards = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardAPI.getDashboards();
      setDashboards(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboards');
      console.error('Error fetching dashboards:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboards();
  }, []);

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading dashboards...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Available Dashboards</Title>
        <RefreshButton onClick={fetchDashboards}>Refresh</RefreshButton>
      </Header>
      
      {dashboards.length === 0 ? (
        <LoadingMessage>No dashboards found. Extract a dashboard to get started.</LoadingMessage>
      ) : (
        <DashboardGrid>
          {dashboards.map((dashboard) => (
            <DashboardCard
              key={dashboard.dashboard_id}
              onClick={() => onSelectDashboard(dashboard.dashboard_id)}
            >
              <DashboardTitle>{dashboard.dashboard_title}</DashboardTitle>
              <DashboardId>ID: {dashboard.dashboard_id}</DashboardId>
              {dashboard.dashboard_url && (
                <DashboardUrl
                  href={dashboard.dashboard_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                >
                  {dashboard.dashboard_url}
                </DashboardUrl>
              )}
            </DashboardCard>
          ))}
        </DashboardGrid>
      )}
    </Container>
  );
};

export default DashboardList;

