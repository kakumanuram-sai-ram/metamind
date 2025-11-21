import React, { useState } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';
import TablesColumnsViewer from './TablesColumnsViewer';

const Container = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  margin-bottom: ${props => props.theme.spacing.xl};
  text-align: center;
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
`;

const DownloadButton = styled.button`
  background: ${props => props.color || props.theme.colors.accent};
  color: white;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  cursor: pointer;
  border: none;
  min-width: 200px;
  justify-content: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
    opacity: 0.9;
  }

  &:active {
    transform: translateY(0);
  }
`;

const DashboardInfo = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.gray[50]};
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.gray[200]};
`;

const DashboardTitle = styled.h3`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const DashboardMeta = styled.div`
  color: ${props => props.theme.colors.gray[600]};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const ViewButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  cursor: pointer;
  border: none;
  min-width: 200px;
  justify-content: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
    opacity: 0.9;
  }

  &:active {
    transform: translateY(0);
  }
`;

const DownloadButtons = ({ dashboardId, dashboardTitle, totalCharts }) => {
  const [showTablesColumns, setShowTablesColumns] = useState(false);
  const handleDownloadJSON = async () => {
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

  const handleDownloadCSV = async () => {
    try {
      const blob = await dashboardAPI.downloadCSV(dashboardId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard_${dashboardId}_metadata.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading CSV:', err);
      alert('Failed to download CSV file');
    }
  };

  if (!dashboardId) {
    return null;
  }

  return (
    <Container>
      {dashboardTitle && (
        <DashboardInfo>
          <DashboardTitle>{dashboardTitle}</DashboardTitle>
          <DashboardMeta>
            Dashboard ID: {dashboardId} {totalCharts && `• ${totalCharts} Charts`}
          </DashboardMeta>
        </DashboardInfo>
      )}
      <Title>Download Dashboard Data</Title>
      <ButtonContainer>
        <DownloadButton
          onClick={handleDownloadJSON}
          color="#00BAF2"
          title="Download JSON file with complete dashboard metadata"
        >
          {'{ }'} Download JSON
        </DownloadButton>
        <DownloadButton
          onClick={handleDownloadCSV}
          color="#00BAF2"
          title="Download CSV file with chart metadata and SQL queries"
        >
          📄 Download CSV
        </DownloadButton>
        <ViewButton
          onClick={() => setShowTablesColumns(!showTablesColumns)}
          title="View tables and columns used in dashboard charts"
        >
          {showTablesColumns ? '▲ Hide' : '▼ View'} Tables & Columns
        </ViewButton>
      </ButtonContainer>
      
      {showTablesColumns && (
        <TablesColumnsViewer dashboardId={dashboardId} />
      )}
    </Container>
  );
};

export default DownloadButtons;

