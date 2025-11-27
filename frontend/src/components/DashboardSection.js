import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';

const SectionContainer = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  display: flex;
  flex-direction: column;
  /* Ensure proper scrolling behavior */
  overflow: visible;
`;

const DashboardHeader = styled.h3`
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.lg};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  /* Removed sticky positioning - header should persist in normal flow */
`;

const MetadataSections = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  overflow-x: auto;
  padding-bottom: ${props => props.theme.spacing.sm};
  /* Removed sticky positioning - cards should persist in normal flow */
  margin-bottom: ${props => props.theme.spacing.lg};
  
  &::-webkit-scrollbar {
    height: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.gray[100]};
    border-radius: ${props => props.theme.borderRadius.md};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.gray[400]};
    border-radius: ${props => props.theme.borderRadius.md};
    
    &:hover {
      background: ${props => props.theme.colors.gray[500]};
    }
  }
`;

const MetadataCard = styled.div`
  min-width: 200px;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.selected ? props.theme.colors.primary + '10' : props.theme.colors.gray[50]};
  cursor: ${props => props.clickable ? 'pointer' : 'default'};
  transition: all 0.2s ease;
  
  &:hover {
    ${props => props.clickable ? `
      border-color: ${props.theme.colors.primary};
      background: ${props.theme.colors.primary + '15'};
      transform: translateY(-2px);
      box-shadow: ${props.theme.shadows.md};
    ` : ''}
  }
`;

const MetadataTitle = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.gray[900]};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.sm};
  text-transform: capitalize;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: ${props => props.theme.colors.gray[200]};
  border-radius: ${props => props.theme.borderRadius.full};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.status === 'completed') return props.theme.colors.success;
    if (props.status === 'processing') return props.theme.colors.primary;
    return props.theme.colors.gray[300];
  }};
  transition: width 0.3s;
  width: ${props => props.progress}%;
`;

const StatusText = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => {
    if (props.status === 'completed') return props.theme.colors.success;
    if (props.status === 'processing') return props.theme.colors.primary;
    return props.theme.colors.gray[600];
  }};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const CurrentPhaseDisplay = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.primary + '10'};
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 3px solid ${props => props.theme.colors.primary};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  /* Removed sticky positioning - should persist in normal flow */
`;

const DownloadButtons = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  justify-content: center;
  margin-top: ${props => props.theme.spacing.sm};
`;

const DownloadButton = styled.button`
  background: transparent;
  border: 1.5px solid ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.xs};
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  
  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primary};
    color: white;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// SVG Icons as React components (outline style)
const DownloadIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7 10 12 15 17 10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const FileIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);

const MetadataCardContent = ({ title, fileType, dashboardId, progress, status, currentStep, useExisting = false, isSelected = false, onClick = null }) => {
  const [fileAvailable, setFileAvailable] = useState(false);
  const [checkingFile, setCheckingFile] = useState(false);

  // Check file availability independently of overall progress
  useEffect(() => {
    let isCurrent = true;
    let pollInterval = null;
    
    // If using existing metadata, immediately check for files and show as available
    if (useExisting) {
      const checkFileExists = async () => {
        if (!isCurrent) return;
        try {
          const files = await dashboardAPI.getDashboardFiles(dashboardId);
          const hasFile = files.files?.some(f => f.type === fileType);
          if (isCurrent) {
            setFileAvailable(hasFile);
            setCheckingFile(false);
          }
        } catch (error) {
          if (isCurrent) {
            setFileAvailable(false);
            setCheckingFile(false);
          }
        }
      };
      
      checkFileExists();
      return () => {
        isCurrent = false;
      };
    }
    
    // If doing fresh extract (useExisting=false)
    // Don't check for files until processing actually starts
    // This prevents showing old files as "completed" when fresh extraction hasn't started yet
    if (!useExisting && status === 'pending') {
      // Fresh extract not started yet - don't show old files as available
      setFileAvailable(false);
      setCheckingFile(false);
      return;
    }
    
    // For fresh extract that's processing or completed
    const checkFileExists = async () => {
      if (!isCurrent) return;
      
      setCheckingFile(true);
      try {
        const files = await dashboardAPI.getDashboardFiles(dashboardId);
        const hasFile = files.files?.some(f => f.type === fileType);
        if (isCurrent) {
          setFileAvailable(hasFile);
          setCheckingFile(false);
        }
      } catch (error) {
        // File doesn't exist yet, that's okay
        if (isCurrent) {
          setFileAvailable(false);
          setCheckingFile(false);
        }
      }
    };
    
    // Initial check for fresh extract that's already processing
    if (status === 'processing' || status === 'completed') {
      checkFileExists();
    }
    
    // Poll every 3 seconds during processing
    if (status === 'processing') {
      pollInterval = setInterval(() => {
        checkFileExists();
      }, 3000);
    }
    
    return () => {
      isCurrent = false;
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [dashboardId, fileType, status, useExisting]);

  // Determine display status based on file availability and useExisting flag
  const getDisplayStatus = () => {
    // If using existing metadata, show as "Using Existing"
    if (useExisting) {
      return fileAvailable ? 'Using Existing' : 'Available';
    }
    
    // For fresh extracts
    if (checkingFile) return 'Checking...';
    if (fileAvailable) return 'Completed';
    if (status === 'processing') return currentStep || 'Processing...';
    if (status === 'pending') return 'Waiting...';
    if (status === 'error') return 'Error';
    return 'Pending';
  };

  const handleDownload = async (format) => {
    try {
      let blob;
      let filename;
      
      if (format === 'json' && fileType === 'json') {
        blob = await dashboardAPI.downloadDashboardFile(dashboardId, 'json');
        filename = `${dashboardId}_json.json`;
      } else if (format === 'csv') {
        blob = await dashboardAPI.downloadDashboardFile(dashboardId, fileType);
        const extension = fileType === 'filter_conditions' ? 'txt' : 'csv';
        filename = `${dashboardId}_${fileType}.${extension}`;
      } else {
        return;
      }
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error(`Error downloading ${fileType}:`, error);
      alert(`Failed to download ${fileType}. Please try again.`);
    }
  };

  // Determine completion and progress based on useExisting flag
  let isCompleted, progressPercent;
  
  if (useExisting) {
    // Using existing metadata - always show as completed if file exists
    isCompleted = fileAvailable;
    progressPercent = fileAvailable ? 100 : 0;
  } else {
    // Fresh extract - show actual progress based on file availability
    isCompleted = fileAvailable;
    progressPercent = isCompleted ? 100 : (status === 'processing' ? 50 : 0);
  }
  
  // Make card clickable even if not completed - will show appropriate state in viewer
  const isClickable = onClick !== null;
  const displayStatus = getDisplayStatus();

  return (
    <MetadataCard 
      selected={isSelected}
      clickable={isClickable}
      onClick={() => {
        if (onClick) {
          // Toggle: if already selected, deselect (close viewer), otherwise select
          onClick(isSelected ? null : fileType);
        }
      }}
    >
      <MetadataTitle>{title}</MetadataTitle>
      <ProgressBar>
        <ProgressFill progress={progressPercent} status={isCompleted ? 'completed' : status} />
      </ProgressBar>
      <StatusText status={isCompleted ? 'completed' : status}>
        {displayStatus}
      </StatusText>
      {isCompleted && (
        <DownloadButtons>
          {fileType !== 'filter_conditions' && (
            <>
              <DownloadButton onClick={() => handleDownload('csv')} title="Download CSV">
                <FileIcon size={14} />
                CSV
              </DownloadButton>
              {fileType === 'json' && (
                <DownloadButton onClick={() => handleDownload('json')} title="Download JSON">
                  <FileIcon size={14} />
                  JSON
                </DownloadButton>
              )}
            </>
          )}
          {fileType === 'filter_conditions' && (
            <DownloadButton onClick={() => handleDownload('csv')} title="Download TXT">
              <DownloadIcon size={14} />
              TXT
            </DownloadButton>
          )}
        </DownloadButtons>
      )}
    </MetadataCard>
  );
};

// Styled components for file content viewer
const FileContentViewer = styled.div`
  width: 100%;
  max-width: 100%;
  border-top: 2px solid ${props => props.theme.colors.gray[200]};
  padding-top: ${props => props.theme.spacing.lg};
  margin-top: ${props => props.theme.spacing.lg};
  /* Positioned directly below metadata cards in normal document flow */
  position: relative;
  z-index: 1;
`;

const ViewerHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  padding-bottom: ${props => props.theme.spacing.sm};
  border-bottom: 1px solid ${props => props.theme.colors.gray[200]};
  /* Removed sticky positioning - header should be in normal flow */
`;

const ViewerTitle = styled.h4`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
`;

const ContentContainer = styled.div`
  width: 100%;
  max-width: 100%;
  max-height: 600px;
  overflow-y: auto;
  overflow-x: auto;
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.gray[50]};
  /* Ensure scrolling happens only within this container */
  position: relative;
  
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.gray[100]};
    border-radius: ${props => props.theme.borderRadius.md};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.gray[400]};
    border-radius: ${props => props.theme.borderRadius.md};
    
    &:hover {
      background: ${props => props.theme.colors.gray[500]};
    }
  }
  
  /* Ensure table is visible and scrollable */
  table {
    display: table;
    width: 100%;
  }
`;

const CSVTable = styled.table`
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: ${props => props.theme.typography.fontSize.sm};
  table-layout: auto;
`;

const CSVTableHeader = styled.thead`
  background: ${props => props.theme.colors.primary};
  color: white;
  position: sticky;
  top: 0;
  z-index: 10;
  /* Sticky within ContentContainer, not page */
`;

const CSVTableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  text-align: left;
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  font-size: ${props => props.theme.typography.fontSize.xs};
  word-wrap: break-word;
  white-space: normal;
`;

const CSVTableRow = styled.tr`
  border-bottom: 1px solid ${props => props.theme.colors.gray[200]};
  
  &:hover {
    background: ${props => props.theme.colors.gray[50]};
  }
`;

const CSVTableCell = styled.td`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.gray[700]};
  word-break: break-word;
  white-space: normal;
  overflow-wrap: break-word;
  max-width: 400px;
  min-width: 100px;
  vertical-align: top;
`;

const TextContent = styled.pre`
  padding: ${props => props.theme.spacing.md};
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: ${props => props.theme.typography.fontFamily.mono};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.gray[800]};
  line-height: 1.6;
`;

const LoadingText = styled.div`
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: ${props => props.theme.colors.gray[600]};
`;

const ErrorText = styled.div`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.error}15;
  color: ${props => props.theme.colors.error};
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.error};
`;

const MetadataFileViewer = ({ dashboardId, fileType, title }) => {
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!dashboardId || !fileType) {
      setFileContent(null);
      return;
    }

    const fetchFileContent = async () => {
      try {
        setLoading(true);
        setError(null);
        const content = await dashboardAPI.getMetadataFileContent(dashboardId, fileType);
        setFileContent(content);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to load file content');
        console.error('Error fetching file content:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFileContent();
  }, [dashboardId, fileType]);

  if (!fileType) {
    return null;
  }

  if (loading) {
    return (
      <FileContentViewer>
        <ViewerHeader>
          <ViewerTitle>Select a metadata section to view content</ViewerTitle>
        </ViewerHeader>
        <ContentContainer>
          <LoadingText>Loading {title}...</LoadingText>
        </ContentContainer>
      </FileContentViewer>
    );
  }

  if (error) {
    // Check if error is "File not found" - this means extraction hasn't completed yet
    const isFileNotFound = error.includes('not found') || error.includes('Not Found');
    return (
      <FileContentViewer>
        <ViewerHeader>
          <ViewerTitle>{title}</ViewerTitle>
        </ViewerHeader>
        <ContentContainer>
          {isFileNotFound ? (
            <LoadingText style={{ color: '#6B7280' }}>
              ⏳ This file hasn't been generated yet. Please wait for extraction to complete for this dashboard.
            </LoadingText>
          ) : (
            <ErrorText>{error}</ErrorText>
          )}
        </ContentContainer>
      </FileContentViewer>
    );
  }

  if (!fileContent) {
    return (
      <FileContentViewer>
        <ViewerHeader>
          <ViewerTitle>Select a metadata section to view content</ViewerTitle>
        </ViewerHeader>
        <ContentContainer>
          <LoadingText>Click on any completed metadata section above to view its content</LoadingText>
        </ContentContainer>
      </FileContentViewer>
    );
  }

  return (
    <FileContentViewer>
      <ViewerHeader>
        <ViewerTitle>{title} ({fileContent.filename})</ViewerTitle>
        {fileContent.type === 'csv' && (
          <span style={{ fontSize: '0.875rem', color: '#6B7280' }}>
            {fileContent.total_rows} rows
          </span>
        )}
      </ViewerHeader>
      <ContentContainer>
        {fileContent.type === 'csv' ? (
          fileContent.columns && fileContent.columns.length > 0 ? (
            <CSVTable>
              <CSVTableHeader>
                <tr>
                  {fileContent.columns.map((column) => (
                    <CSVTableHeaderCell key={column}>{column}</CSVTableHeaderCell>
                  ))}
                </tr>
              </CSVTableHeader>
              <tbody>
                {fileContent.data && fileContent.data.length > 0 ? (
                  // Limit to 20 rows max as per requirements
                  fileContent.data.slice(0, 20).map((row, index) => (
                    <CSVTableRow key={index}>
                      {fileContent.columns.map((column) => {
                        const cellValue = row[column] !== null && row[column] !== undefined ? String(row[column]) : '';
                        return (
                          <CSVTableCell key={column} title={cellValue}>
                            {cellValue}
                          </CSVTableCell>
                        );
                      })}
                    </CSVTableRow>
                  ))
                ) : (
                  <CSVTableRow>
                    <CSVTableCell colSpan={fileContent.columns.length} style={{ textAlign: 'center', padding: '2rem', color: '#6B7280' }}>
                      No data available
                    </CSVTableCell>
                  </CSVTableRow>
                )}
                {fileContent.data && fileContent.data.length > 20 && (
                  <CSVTableRow>
                    <CSVTableCell colSpan={fileContent.columns.length} style={{ textAlign: 'center', padding: '1rem', color: '#6B7280', fontStyle: 'italic' }}>
                      Showing first 20 of {fileContent.total_rows} rows. Scroll to see more.
                    </CSVTableCell>
                  </CSVTableRow>
                )}
              </tbody>
            </CSVTable>
          ) : (
            <LoadingText>No columns found in file</LoadingText>
          )
        ) : (
          <TextContent>{fileContent.content}</TextContent>
        )}
      </ContentContainer>
    </FileContentViewer>
  );
};

const DashboardSection = ({ dashboardId, progress, useExisting = false }) => {
  const [selectedFileType, setSelectedFileType] = useState(null);
  
  const metadataTypes = [
    { key: 'table_metadata', title: 'Table Metadata', fileType: 'table_metadata', phase: 'Phase 4: Table Metadata' },
    { key: 'columns_metadata', title: 'Column Metadata', fileType: 'columns_metadata', phase: 'Phase 5: Column Metadata' },
    { key: 'joining_conditions', title: 'Joining Conditions', fileType: 'joining_conditions', phase: 'Phase 6: Joining Conditions' },
    { key: 'filter_conditions', title: 'Filter Conditions', fileType: 'filter_conditions', phase: 'Phase 7: Filter Conditions' },
    { key: 'definitions', title: 'Definitions', fileType: 'definitions', phase: 'Phase 8: Term Definitions' },
  ];

  // Map phase names to metadata types
  const phaseToMetadataMap = {
    'Phase 1: Dashboard Extraction': null,
    'Phase 2: Tables & Columns': null,
    'Phase 3: Schema Enrichment': null,
    'Phase 4: Table Metadata': 'table_metadata',
    'Phase 5: Column Metadata': 'columns_metadata',
    'Phase 6: Joining Conditions': 'joining_conditions',
    'Phase 7: Filter Conditions': 'filter_conditions',
    'Phase 8: Term Definitions': 'definitions',
    'Phase 9: Quality Judging': null,
    'Initializing': null,
    'Completed': null,
  };

  const getStatus = (fileType, phase) => {
    // If using existing metadata, mark as completed immediately
    if (useExisting) {
      return { status: 'completed', step: 'Using Existing' };
    }
    
    if (!progress) return { status: 'pending', step: 'Waiting...' };
    
    // Check if dashboard is actually being processed (status should be processing or completed)
    if (progress.status !== 'processing' && progress.status !== 'completed') {
      return { status: 'pending', step: 'Waiting...' };
    }
    
    const completedFiles = progress.completed_files || [];
    const fileName = `${dashboardId}_${fileType}.${fileType === 'filter_conditions' ? 'txt' : 'csv'}`;
    const isCompleted = completedFiles.includes(fileName);
    
    if (isCompleted) {
      return { status: 'completed', step: 'Completed' };
    }
    
    // Check if current phase matches this metadata type
    const currentPhase = progress.current_phase || '';
    const currentFile = progress.current_file || '';
    
    // If current file matches, it's actively processing
    if (currentFile === fileName) {
      return { status: 'processing', step: getStepFromPhase(currentPhase) };
    }
    
    // If current phase matches this metadata type, it's processing
    if (phaseToMetadataMap[currentPhase] === fileType) {
      return { status: 'processing', step: getStepFromPhase(currentPhase) };
    }
    
    // If dashboard is processing, show status based on phase comparison
    if (progress.status === 'processing' && currentPhase) {
      // Check if we're past this phase
      const phaseOrder = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Phase 5', 'Phase 6', 'Phase 7', 'Phase 8'];
      const currentPhaseIndex = phaseOrder.findIndex(p => currentPhase.includes(p));
      const thisPhaseIndex = phaseOrder.findIndex(p => phase.includes(p));
      
      if (currentPhaseIndex > thisPhaseIndex) {
        // We've moved past this phase, but file not completed - might be error or skipped
        return { status: 'pending', step: 'Skipped or error' };
      }
      
      if (currentPhaseIndex < thisPhaseIndex) {
        // Still waiting for this phase
        return { status: 'pending', step: 'Waiting...' };
      }
      
      // We're at this phase - show processing
      return { status: 'processing', step: 'Processing...' };
    }
    
    return { status: 'pending', step: 'Waiting to start' };
  };

  const getStepFromPhase = (phase) => {
    if (!phase) return 'Initializing';
    if (phase.includes('Phase 1')) return 'Extraction';
    if (phase.includes('Phase 2')) return 'Tables & Columns';
    if (phase.includes('Phase 3')) return 'Schema Enrichment';
    if (phase.includes('Phase 4')) return 'Table Metadata';
    if (phase.includes('Phase 5')) return 'Column Metadata';
    if (phase.includes('Phase 6')) return 'Joining Conditions';
    if (phase.includes('Phase 7')) return 'Filter Conditions';
    if (phase.includes('Phase 8')) return 'Term Definitions';
    if (phase.includes('Phase 9')) return 'Quality Judging';
    if (phase === 'Completed') return 'Completed';
    return phase;
  };

  const getProgress = (fileType, phase) => {
    // If using existing metadata, always return 100%
    if (useExisting) return 100;
    
    const statusInfo = getStatus(fileType, phase);
    if (statusInfo.status === 'completed') return 100;
    if (statusInfo.status === 'processing') return 50;
    return 0;
  };

  // If using existing, all files should show as completed
  React.useEffect(() => {
    if (useExisting) {
      // Files are already available, no need to check
    }
  }, [useExisting]);

  // Get current phase for display (only show once below header)
  const currentPhase = progress?.current_phase || null;
  const getPhaseDisplayName = (phase) => {
    if (!phase) return null;
    if (phase.includes('Phase 1')) return 'Dashboard Extraction';
    if (phase.includes('Phase 2')) return 'Tables & Columns';
    if (phase.includes('Phase 3')) return 'Schema Enrichment';
    if (phase.includes('Phase 4')) return 'Table Metadata';
    if (phase.includes('Phase 5')) return 'Column Metadata';
    if (phase.includes('Phase 6')) return 'Joining Conditions';
    if (phase.includes('Phase 7')) return 'Filter Conditions';
    if (phase.includes('Phase 8')) return 'Term Definitions';
    if (phase.includes('Phase 9')) return 'Quality Judging';
    if (phase === 'Completed') return 'Completed';
    return phase;
  };

  return (
    <SectionContainer>
      <DashboardHeader>
        Dashboard ID: {dashboardId}
        {useExisting && (
          <span style={{ 
            marginLeft: '1rem', 
            fontSize: '0.875rem', 
            color: '#10B981', 
            fontWeight: 'normal' 
          }}>
            (Using Existing Metadata)
          </span>
        )}
      </DashboardHeader>
      {currentPhase && progress?.status === 'processing' && !useExisting && (
        <CurrentPhaseDisplay>
          Current Phase: {getPhaseDisplayName(currentPhase)}
        </CurrentPhaseDisplay>
      )}
      <MetadataSections>
        {metadataTypes.map(({ key, title, fileType, phase }) => {
          const statusInfo = getStatus(fileType, phase);
          // Make sections clickable even if not completed (will show loading/error state)
          return (
            <MetadataCardContent
              key={key}
              title={title}
              fileType={fileType}
              dashboardId={dashboardId}
              progress={getProgress(fileType, phase)}
              status={statusInfo.status}
              currentStep={statusInfo.step}
              useExisting={useExisting}
              isSelected={selectedFileType === fileType}
              onClick={setSelectedFileType}
            />
          );
        })}
      </MetadataSections>
      
      {/* Table viewer directly below metadata cards - in normal document flow */}
      <MetadataFileViewer
        dashboardId={dashboardId}
        fileType={selectedFileType}
        title={metadataTypes.find(m => m.fileType === selectedFileType)?.title || 'Metadata Content'}
      />
    </SectionContainer>
  );
};

export default DashboardSection;

