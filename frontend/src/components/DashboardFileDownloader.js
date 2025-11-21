/**
 * Dashboard File Downloader Component
 * 
 * Allows downloading all metadata files for a specific dashboard
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
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Input = styled.input`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  
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

const FilesList = styled.div`
  margin-top: ${props => props.theme.spacing.lg};
`;

const FileItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[200]};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.div`
  font-weight: 600;
  color: ${props => props.theme.colors.gray[900]};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const FileMeta = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.gray[600]};
`;

const DownloadButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: ${props => props.theme.colors.primaryDark};
  }
`;

const DownloadAllButton = styled(Button)`
  background: ${props => props.theme.colors.accent};
  margin-top: ${props => props.theme.spacing.md};
  
  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.accentDark};
  }
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

const DashboardFileDownloader = () => {
  const [dashboardId, setDashboardId] = useState('');
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState(null);
  const [message, setMessage] = useState(null);

  const handleLoadFiles = async (e) => {
    e?.preventDefault();
    if (!dashboardId) return;

    setLoading(true);
    setMessage(null);
    setFiles(null);

    try {
      const filesData = await dashboardAPI.getDashboardFiles(parseInt(dashboardId));
      setFiles(filesData);
      setMessage({
        type: 'success',
        text: `Found ${filesData.total_files} metadata files for dashboard ${dashboardId}`,
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || 'Failed to load files',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadFile = async (fileType, filename) => {
    try {
      const blob = await dashboardAPI.downloadDashboardFile(parseInt(dashboardId), fileType);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert(`Failed to download ${filename}: ${error.message}`);
    }
  };

  const handleDownloadAll = async () => {
    try {
      const blob = await dashboardAPI.downloadAllDashboardFiles(parseInt(dashboardId));
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard_${dashboardId}_metadata.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert(`Failed to download ZIP: ${error.message}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <Container>
      <Title>Download Dashboard Metadata Files</Title>
      
      {message && (
        <Message type={message.type}>{message.text}</Message>
      )}

      <Form onSubmit={handleLoadFiles}>
        <Input
          type="number"
          value={dashboardId}
          onChange={(e) => setDashboardId(e.target.value)}
          placeholder="Enter Dashboard ID (e.g., 842)"
          disabled={loading}
        />
        <Button type="submit" disabled={loading || !dashboardId}>
          {loading ? 'Loading...' : 'Load Files'}
        </Button>
      </Form>

      {files && files.files && files.files.length > 0 && (
        <FilesList>
          <h3>Available Files ({files.total_files})</h3>
          {files.files.map((file, index) => (
            <FileItem key={index}>
              <FileInfo>
                <FileName>{file.filename}</FileName>
                <FileMeta>
                  Type: {file.type} | Format: {file.format} | Size: {formatFileSize(file.size)}
                </FileMeta>
              </FileInfo>
              <DownloadButton
                onClick={() => handleDownloadFile(file.type, file.filename)}
              >
                Download
              </DownloadButton>
            </FileItem>
          ))}
          
          <DownloadAllButton onClick={handleDownloadAll}>
            Download All as ZIP
          </DownloadAllButton>
        </FilesList>
      )}
    </Container>
  );
};

export default DashboardFileDownloader;

