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

const ButtonGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  align-items: center;
`;

const DownloadButton = styled.button`
  background: ${props => props.theme.colors.accent};
  color: white;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  cursor: pointer;
  border: none;

  &:hover {
    background: ${props => props.theme.colors.accentDark};
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.sm};
  }
`;

const TableContainer = styled.div`
  overflow-x: auto;
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.gray[200]};
  margin-top: ${props => props.theme.spacing.md};
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: white;
`;

const TableHeader = styled.thead`
  background: ${props => props.theme.colors.primary};
  color: white;
`;

const TableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.md};
  text-align: left;
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  font-size: ${props => props.theme.typography.fontSize.sm};
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableBody = styled.tbody``;

const TableRow = styled.tr`
  border-bottom: 1px solid ${props => props.theme.colors.gray[200]};
  transition: background-color 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.gray[50]};
  }

  &:last-child {
    border-bottom: none;
  }
`;

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.gray[700]};
  word-break: break-word;
`;

const InfoBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.gray[100]};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.gray[700]};
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

const TablesColumnsViewer = ({ dashboardId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!dashboardId) return;

      try {
        setLoading(true);
        setError(null);
        const result = await dashboardAPI.getDashboardTablesColumns(dashboardId);
        setData(result);
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to load tables and columns data';
        setError(errorMessage);
        console.error('Error fetching tables and columns:', err);
        console.error('Error response:', err.response);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [dashboardId]);

  const handleDownload = async () => {
    try {
      const blob = await dashboardAPI.downloadTablesColumns(dashboardId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard_${dashboardId}_tables_columns.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading tables-columns CSV:', err);
      alert('Failed to download tables-columns CSV file');
    }
  };

  if (!dashboardId) {
    return null;
  }

  if (loading) {
    return (
      <Container>
        <Title>Tables and Columns</Title>
        <LoadingMessage>Loading tables and columns data...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Title>Tables and Columns</Title>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  if (!data || !data.data || data.data.length === 0) {
    return (
      <Container>
        <Title>Tables and Columns</Title>
        <LoadingMessage>No tables and columns data available. Please extract a dashboard first.</LoadingMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Tables and Columns</Title>
        <ButtonGroup>
          <DownloadButton onClick={handleDownload}>
            ↓ Download CSV
          </DownloadButton>
        </ButtonGroup>
      </Header>
      
      <InfoBar>
        <span>Total Rows: {data.total_rows}</span>
        <span>Unique Tables: {new Set(data.data.map(row => row.table_name)).size}</span>
        <span>Unique Columns: {new Set(data.data.map(row => row.column_name).filter(c => c)).size}</span>
      </InfoBar>

      <TableContainer>
        <Table>
          <TableHeader>
            <tr>
              <TableHeaderCell>Table Name</TableHeaderCell>
              <TableHeaderCell>Column Name</TableHeaderCell>
              <TableHeaderCell>Data Type</TableHeaderCell>
              <TableHeaderCell>Column Labels (Chart IDs)</TableHeaderCell>
            </tr>
          </TableHeader>
          <TableBody>
            {data.data.map((row, index) => {
              let chartLabels = {};
              try {
                chartLabels = JSON.parse(row.column_label__chart_json || '{}');
              } catch (e) {
                chartLabels = {};
              }
              
              const chartLabelsText = Object.entries(chartLabels)
                .map(([chartId, label]) => `Chart ${chartId}: ${label}`)
                .join(', ');
              
              return (
                <TableRow key={index}>
                  <TableCell>{row.table_name || ''}</TableCell>
                  <TableCell>{row.column_name || ''}</TableCell>
                  <TableCell>{row.data_type || 'N/A'}</TableCell>
                  <TableCell title={row.column_label__chart_json}>
                    {chartLabelsText || row.column_label__chart_json || ''}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default TablesColumnsViewer;


