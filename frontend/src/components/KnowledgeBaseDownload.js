import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';

const SectionContainer = styled.div`
  background: ${props => {
    if (props.highlight) {
      return props.theme.colors.info + '15';
    }
    return 'white';
  }};
  border: ${props => {
    if (props.highlight) {
      return `2px solid ${props.theme.colors.info}`;
    }
    return `1px solid ${props.theme.colors.gray[300]}`;
  }};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.highlight ? props.theme.shadows.lg : props.theme.shadows.md};
  margin-top: ${props => props.theme.spacing.xl};
  transition: all 0.3s ease;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const SectionTitle = styled.h3`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin: 0;
`;

const StatusBadge = styled.div`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  background: ${props => {
    if (props.status === 'completed') return props.theme.colors.success;
    if (props.status === 'processing') return props.theme.colors.info;
    if (props.status === 'merging') return props.theme.colors.warning;
    return props.theme.colors.gray[300];
  }};
  color: white;
`;

const SectionDescription = styled.p`
  color: ${props => props.theme.colors.gray[600]};
  margin-bottom: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.base};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 12px;
  background: ${props => props.theme.colors.gray[200]};
  border-radius: ${props => props.theme.borderRadius.full};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.status === 'completed') return props.theme.colors.success;
    if (props.status === 'processing') return props.theme.colors.info;
    return props.theme.colors.primary;
  }};
  transition: width 0.3s;
  width: ${props => props.progress}%;
`;

const ActionButtonsContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  flex: 1;
  min-width: 200px;
  background: ${props => {
    if (props.variant === 'n8n') return props.theme.colors.info;
    if (props.variant === 'prism') return props.theme.colors.warning;
    return props.theme.colors.success;
  }};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${props => props.theme.spacing.sm};
  
  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray[400]};
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const StatusMessage = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
  background: ${props => {
    if (props.type === 'success') return props.theme.colors.success + '20';
    if (props.type === 'error') return props.theme.colors.error + '20';
    return props.theme.colors.info + '20';
  }};
  color: ${props => {
    if (props.type === 'success') return props.theme.colors.success;
    if (props.type === 'error') return props.theme.colors.error;
    return props.theme.colors.info;
  }};
`;

const DownloadIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7 10 12 15 17 10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const KnowledgeBaseDownload = ({ progress, dashboardIds = [] }) => {
  const [zipAvailable, setZipAvailable] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [allFilesReady, setAllFilesReady] = useState(false);
  const [actionStatus, setActionStatus] = useState(null); // { type: 'success'|'error', message: string }

  // Check if all 5 required metadata files are ready for all dashboards
  const checkAllFilesReady = useCallback(async () => {
    if (!dashboardIds || dashboardIds.length === 0) {
      setAllFilesReady(false);
      return false;
    }

    try {
      const requiredFileTypes = ['table_metadata', 'columns_metadata', 'definitions', 'joining_conditions', 'filter_conditions'];
      let allReady = true;

      for (const dashboardId of dashboardIds) {
        try {
          const filesData = await dashboardAPI.getDashboardFiles(dashboardId);
          const availableTypes = filesData.files?.map(f => f.type) || [];
          
          // Check if all required file types are available
          const hasAllFiles = requiredFileTypes.every(type => availableTypes.includes(type));
          
          if (!hasAllFiles) {
            allReady = false;
            break;
          }
        } catch (error) {
          allReady = false;
          break;
        }
      }

      setAllFilesReady(allReady);
      return allReady;
    } catch (error) {
      setAllFilesReady(false);
      return false;
    }
  }, [dashboardIds]);

  // Check if ZIP file is available
  const checkZipAvailability = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/knowledge-base/download`, {
        method: 'HEAD',
      });
      setZipAvailable(response.ok);
    } catch (error) {
      setZipAvailable(false);
    }
  }, []);

  useEffect(() => {
    // Only check if extraction is in progress or completed
    // Don't check if status is idle or if there are no dashboards
    if (!dashboardIds || dashboardIds.length === 0) {
      setZipAvailable(false);
      setAllFilesReady(false);
      return;
    }
    
    const overallStatus = progress?.status || 'idle';
    
    // Check if ALL dashboard IDs are in progress (strict matching)
    const progressDashboardIds = Object.keys(progress?.dashboards || {}).map(id => parseInt(id));
    const allDashboardsMatch = dashboardIds.length > 0 && 
                               dashboardIds.every(id => progressDashboardIds.includes(id));
    
    // If status is idle or progress doesn't match ALL our dashboards, don't check
    if (overallStatus === 'idle' || !allDashboardsMatch) {
      setZipAvailable(false);
      setAllFilesReady(false);
      return;
    }
    
    // Only check files when there's an active extraction that's progressing or completed
    // Check periodically if all files are ready (every 10 seconds to reduce load)
    const interval = setInterval(() => {
      checkAllFilesReady().then((ready) => {
        if (ready) {
          checkZipAvailability();
        }
      });
    }, 10000); // Reduced from 5 to 10 seconds
    
    // Initial check
    checkAllFilesReady().then((ready) => {
      if (ready) {
        checkZipAvailability();
      }
    });
    
    return () => clearInterval(interval);
  }, [progress, dashboardIds, checkAllFilesReady, checkZipAvailability]);

  const getStatus = () => {
    if (!progress || !dashboardIds || dashboardIds.length === 0) {
      return { status: 'pending', step: 'Waiting for extraction', progress: 0 };
    }
    
    // Check if ALL dashboard IDs are in progress (strict matching)
    const progressDashboardIds = Object.keys(progress.dashboards || {}).map(id => parseInt(id));
    const allDashboardsMatch = dashboardIds.length > 0 && 
                               dashboardIds.every(id => progressDashboardIds.includes(id));
    
    // If no matching dashboards, show pending
    if (!allDashboardsMatch) {
      return { status: 'pending', step: 'Waiting to start', progress: 0 };
    }
    
    const kbStatus = progress.kb_build_status?.status || 'pending';
    const mergeStatus = progress.merge_status?.status || 'pending';
    const overallStatus = progress.status || 'idle';

    // Only mark as completed when all 5 files are ready AND KB is built AND ALL dashboards match
    if (kbStatus === 'completed' && zipAvailable && allFilesReady && allDashboardsMatch) {
      // Double-check that all dashboards are actually completed
      const allDashboardsCompleted = dashboardIds.every(id => {
        const dashProgress = progress.dashboards?.[id.toString()];
        return dashProgress?.status === 'completed';
      });
      
      if (allDashboardsCompleted) {
        return { status: 'completed', step: 'Ready for download', progress: 100 };
      }
    }
    
    if (kbStatus === 'completed' && !allFilesReady && allDashboardsMatch) {
      return { status: 'processing', step: 'Waiting for all metadata files to be ready', progress: 90 };
    }
    
    if (kbStatus === 'processing' && allDashboardsMatch) {
      const currentStep = progress.kb_build_status?.current_step || 'Building knowledge base';
      return { status: 'processing', step: currentStep, progress: 75 };
    }
    
    // Handle transition from merging completed to KB building
    // If merging is completed but KB build hasn't started yet, show as processing (preparing for KB build)
    if (mergeStatus === 'completed' && kbStatus === 'pending' && allDashboardsMatch) {
      // Check if overall status indicates we're moving to KB building
      if (overallStatus === 'building_kb') {
        // KB build is starting but status hasn't updated yet
        return { status: 'processing', step: 'Preparing to build knowledge base', progress: 60 };
      } else if (overallStatus === 'completed') {
        // Everything is done, but KB status might not be updated yet
        // Check if files are ready
        if (allFilesReady) {
          return { status: 'processing', step: 'Finalizing knowledge base', progress: 90 };
        } else {
          return { status: 'processing', step: 'Merging completed, preparing knowledge base', progress: 60 };
        }
      } else {
        // Merging completed, waiting for KB build to start
        return { status: 'processing', step: 'Merging completed, preparing knowledge base', progress: 60 };
      }
    }
    
    if ((mergeStatus === 'processing' || overallStatus === 'merging') && allDashboardsMatch) {
      const currentStep = progress.merge_status?.current_step || 'Merging metadata';
      return { status: 'merging', step: currentStep, progress: 50 };
    }
    
    if (overallStatus === 'extracting' && allDashboardsMatch) {
      return { status: 'pending', step: 'Waiting for extraction to complete', progress: 25 };
    }
    
    return { status: 'pending', step: 'Waiting to start', progress: 0 };
  };

  const handleDownloadForClaude = async () => {
    setDownloading(true);
    setActionStatus(null);
    try {
      const blob = await dashboardAPI.downloadKnowledgeBaseZip();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'knowledge_base.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setActionStatus({ type: 'success', message: 'Knowledge base ZIP downloaded successfully!' });
    } catch (error) {
      console.error('Error downloading knowledge base ZIP:', error);
      setActionStatus({ type: 'error', message: 'Failed to download knowledge base ZIP. Please try again.' });
    } finally {
      setDownloading(false);
    }
  };

  const handleConnectToN8N = async () => {
    setActionStatus(null);
    try {
      const response = await dashboardAPI.connectToN8N();
      if (response.success) {
        setActionStatus({ type: 'success', message: response.message || 'Successfully connected to N8N!' });
      } else {
        setActionStatus({ type: 'error', message: response.message || 'Failed to connect to N8N.' });
      }
    } catch (error) {
      console.error('Error connecting to N8N:', error);
      setActionStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || error.message || 'Failed to connect to N8N. Please try again.' 
      });
    }
  };

  const handleEnableOnPrism = async () => {
    setActionStatus(null);
    try {
      const response = await dashboardAPI.enableOnPrism();
      if (response.success) {
        setActionStatus({ type: 'success', message: response.message || 'Successfully enabled on Prism!' });
      } else {
        setActionStatus({ type: 'error', message: response.message || 'Failed to enable on Prism.' });
      }
    } catch (error) {
      console.error('Error enabling on Prism:', error);
      setActionStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || error.message || 'Failed to enable on Prism. Please try again.' 
      });
    }
  };

  const statusInfo = getStatus();
  const isHighlighted = statusInfo.status === 'processing' || statusInfo.status === 'merging' || statusInfo.status === 'completed';
  const isReady = statusInfo.status === 'completed' && zipAvailable && allFilesReady;

  return (
    <SectionContainer highlight={isHighlighted}>
      <SectionHeader>
        <SectionTitle>Knowledge Base Download</SectionTitle>
        <StatusBadge status={statusInfo.status}>
          {statusInfo.status === 'completed' ? 'Ready' : 
           statusInfo.status === 'processing' ? 'Building' :
           statusInfo.status === 'merging' ? 'Merging' : 'Pending'}
        </StatusBadge>
      </SectionHeader>
      
      <SectionDescription>
        Consolidated knowledge base containing all merged metadata files. Download is available only after all metadata files (table_metadata, columns_metadata, joining_conditions, filter_conditions, definitions) are extracted and merged.
      </SectionDescription>
      
      <ProgressBar>
        <ProgressFill progress={statusInfo.progress} status={statusInfo.status} />
      </ProgressBar>
      
      <div style={{ 
        fontSize: '0.875rem', 
        color: statusInfo.status === 'completed' ? '#10B981' : '#6B7280',
        marginTop: '1rem'
      }}>
        {statusInfo.step}
      </div>

      {isReady && (
        <ActionButtonsContainer>
          <ActionButton
            onClick={handleDownloadForClaude}
            disabled={downloading}
            variant="claude"
          >
            <DownloadIcon size={18} />
            {downloading ? 'Downloading...' : 'Download for Claude'}
          </ActionButton>
          
          <ActionButton
            onClick={handleConnectToN8N}
            disabled={false}
            variant="n8n"
          >
            Connect to N8N
          </ActionButton>
          
          <ActionButton
            onClick={handleEnableOnPrism}
            disabled={false}
            variant="prism"
          >
            Enable on Prism
          </ActionButton>
        </ActionButtonsContainer>
      )}

      {actionStatus && (
        <StatusMessage type={actionStatus.type}>
          {actionStatus.message}
        </StatusMessage>
      )}
    </SectionContainer>
  );
};

export default KnowledgeBaseDownload;

