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

// Removed unused styled component - using inline styles instead

const TableContainer = styled.div`
  overflow-x: auto;
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.gray[200]};
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
  max-width: 400px;
`;

const SQLCell = styled(TableCell)`
  font-family: ${props => props.theme.typography.fontFamily.mono};
  font-size: ${props => props.theme.typography.fontSize.xs};
  background: ${props => props.theme.colors.gray[50]};
  max-width: 500px;
  white-space: pre-wrap;
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

const CSVViewer = ({ dashboardId }) => {
  const [csvData, setCsvData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCSV = async () => {
      if (!dashboardId) return;

      try {
        setLoading(true);
        setError(null);
        const data = await dashboardAPI.getDashboardCSV(dashboardId);
        setCsvData(data);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load CSV data');
        console.error('Error fetching CSV:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCSV();
  }, [dashboardId]);

  const handleDownload = async () => {
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
    return (
      <Container>
        <Title>CSV Data</Title>
        <LoadingMessage>Select a dashboard to view CSV data</LoadingMessage>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container>
        <Title>CSV Data</Title>
        <LoadingMessage>Loading CSV data...</LoadingMessage>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Title>CSV Data</Title>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  if (!csvData || !csvData.data || csvData.data.length === 0) {
    return (
      <Container>
        <Title>CSV Data</Title>
        <LoadingMessage>No CSV data available</LoadingMessage>
      </Container>
    );
  }

  // Debug: Log when component renders
  console.log('CSVViewer rendering with dashboardId:', dashboardId, 'csvData:', !!csvData);

  return (
    <Container>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title>CSV Data</Title>
        <button 
          onClick={handleDownload} 
          title="Download CSV file"
          style={{ 
            background: '#00BAF2', 
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
          📥 Download CSV
        </button>
      </Header>
      
      <InfoBar>
        <span>Total Rows: {csvData.total_rows}</span>
        <span>Columns: {csvData.columns.length}</span>
      </InfoBar>

      <TableContainer>
        <Table>
          <TableHeader>
            <tr>
              {csvData.columns.map((column) => (
                <TableHeaderCell key={column}>{column}</TableHeaderCell>
              ))}
            </tr>
          </TableHeader>
          <TableBody>
            {csvData.data.map((row, index) => (
              <TableRow key={index}>
                {csvData.columns.map((column) => (
                  column === 'sql_query' ? (
                    <SQLCell key={column}>{row[column] || ''}</SQLCell>
                  ) : (
                    <TableCell key={column}>{row[column] || ''}</TableCell>
                  )
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default CSVViewer;

