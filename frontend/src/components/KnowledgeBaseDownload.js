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
    // Don't check if no dashboards or no progress
    if (!dashboardIds || dashboardIds.length === 0 || !progress) {
      setZipAvailable(false);
      setAllFilesReady(false);
      return;
    }
    
    const overallStatus = progress?.status || 'idle';
    const kbStatus = progress?.kb_build_status?.status || 'pending';
    const mergeStatus = progress?.merge_status?.status || 'pending';
    
    // If everything is idle, don't check
    if (overallStatus === 'idle') {
      setZipAvailable(false);
      setAllFilesReady(false);
      return;
    }
    
    // Check periodically if KB is processing or completed
    const shouldCheck = kbStatus === 'processing' || 
                       kbStatus === 'completed' || 
                       mergeStatus === 'processing' ||
                       mergeStatus === 'completed' ||
                       overallStatus === 'completed';
    
    if (!shouldCheck) {
      return;
    }
    
    // Check files and ZIP availability
    const performChecks = async () => {
      // Always check ZIP if KB is complete or completed overall
      if (kbStatus === 'completed' || overallStatus === 'completed') {
        await checkZipAvailability();
      }
      
      // Check dashboard files
      const filesReady = await checkAllFilesReady();
      
      // If files ready and KB complete, check ZIP
      if (filesReady && (kbStatus === 'completed' || overallStatus === 'completed')) {
        await checkZipAvailability();
      }
    };
    
    // Initial check
    performChecks();
    
    // Poll every 5 seconds while processing or completed
    const interval = setInterval(performChecks, 5000);
    
    return () => clearInterval(interval);
  }, [progress, dashboardIds, checkAllFilesReady, checkZipAvailability]);

  // Calculate granular progress based on current step
  const calculateProgress = (step, type = 'merge') => {
    // Merge steps: preparing → table_metadata → columns_metadata → joining_conditions → definitions → filter_conditions → conflicts_report
    const mergeSteps = ['preparing', 'table_metadata', 'columns_metadata', 'joining_conditions', 'definitions', 'filter_conditions', 'conflicts_report'];
    
    // KB build steps: tables → columns → joins → definitions → filter_conditions
    const kbSteps = ['tables', 'columns', 'joins', 'definitions', 'filter_conditions'];
    
    if (type === 'merge') {
      const stepIndex = mergeSteps.indexOf(step);
      if (stepIndex === -1) return 45; // Default to start of merge range
      
      // Merge range: 45% → 65% (20% total, 7 steps = ~2.86% per step)
      const startPercent = 45;
      const rangePercent = 20;
      const progressPercent = startPercent + ((stepIndex + 1) / mergeSteps.length) * rangePercent;
      return Math.floor(progressPercent);
    } else {
      const stepIndex = kbSteps.indexOf(step);
      if (stepIndex === -1) return 65; // Default to start of KB range
      
      // KB range: 65% → 100% (35% total, 5 steps = 7% per step)
      const startPercent = 65;
      const rangePercent = 35;
      const progressPercent = startPercent + ((stepIndex + 1) / kbSteps.length) * rangePercent;
      return Math.floor(progressPercent);
    }
  };

  // Helper function to convert technical step names to user-friendly messages
  const formatStepMessage = (step, type = 'merge') => {
    if (!step) return type === 'merge' ? 'Merging metadata' : 'Building knowledge base';
    
    // Merge steps with user-friendly messages
    const mergeSteps = {
      'preparing': '📋 Preparing metadata for merge (1/7)',
      'table_metadata': '🗂️  Merging table metadata (2/7)',
      'columns_metadata': '📊 Merging column metadata (3/7)',
      'joining_conditions': '🔗 Merging joining conditions (4/7)',
      'definitions': '📖 Merging term definitions (5/7)',
      'filter_conditions': '🔍 Merging filter conditions (6/7)',
      'conflicts_report': '⚠️  Generating conflicts report (7/7)'
    };
    
    // KB build steps with user-friendly messages
    const kbSteps = {
      'tables': '🗂️  Converting table metadata (1/5)',
      'columns': '📊 Converting column metadata (2/5)',
      'joins': '🔗 Converting joining conditions (3/5)',
      'definitions': '📖 Converting term definitions (4/5)',
      'filter_conditions': '🔍 Converting filter conditions (5/5)'
    };
    
    if (type === 'merge') {
      return mergeSteps[step] || `Merging: ${step}`;
    } else {
      return kbSteps[step] || `Building: ${step}`;
    }
  };

  const getStatus = () => {
    if (!progress || !dashboardIds || dashboardIds.length === 0) {
      return { status: 'pending', step: 'Waiting for extraction', progress: 0 };
    }
    
    const kbStatus = progress.kb_build_status?.status || 'pending';
    const mergeStatus = progress.merge_status?.status || 'pending';
    const overallStatus = progress.status || 'idle';

    // Count how many dashboards are completed
    const completedDashboards = Object.values(progress.dashboards || {}).filter(
      d => d.status === 'completed'
    );
    const completedCount = completedDashboards.length;
    const totalDashboards = Object.keys(progress.dashboards || {}).length;
    
    // Check if all required dashboards in our selection are completed
    const allDashboardsCompleted = dashboardIds.every(id => {
      const dashProgress = progress.dashboards?.[id.toString()];
      return dashProgress?.status === 'completed';
    });

    // PRIORITY 1: Overall Status Complete (simplest check - backend says done)
    if (overallStatus === 'completed' && kbStatus === 'completed' && mergeStatus === 'completed') {
      // Backend says everything is done, show as ready
      return { status: 'completed', step: '✅ Ready for download', progress: 100 };
    }
    
    // PRIORITY 2: KB Complete with verification
    if (kbStatus === 'completed' && zipAvailable) {
      return { status: 'completed', step: '✅ Ready for download', progress: 100 };
    }
    
    // PRIORITY 3: KB Build In Progress (GRANULAR PROGRESS)
    if (kbStatus === 'processing') {
      const currentStep = progress.kb_build_status?.current_step;
      const formattedStep = formatStepMessage(currentStep, 'kb');
      const progressPercent = calculateProgress(currentStep, 'kb');
      return { status: 'processing', step: formattedStep, progress: progressPercent };
    }
    
    // PRIORITY 4: KB Complete but ZIP check pending
    if (kbStatus === 'completed' && !zipAvailable) {
      return { status: 'processing', step: '⏳ Verifying knowledge base files...', progress: 98 };
    }
    
    // PRIORITY 5: Merge Complete, Waiting for KB
    if (mergeStatus === 'completed' && kbStatus === 'pending') {
      if (overallStatus === 'building_kb') {
        return { status: 'processing', step: '🔄 Starting knowledge base build...', progress: 65 };
      } else {
        return { status: 'processing', step: '✅ Merge complete, preparing knowledge base', progress: 65 };
      }
    }
    
    // PRIORITY 6: Merge In Progress (GRANULAR PROGRESS)
    if (mergeStatus === 'processing' || overallStatus === 'merging') {
      const currentStep = progress.merge_status?.current_step;
      const formattedStep = formatStepMessage(currentStep, 'merge');
      const progressPercent = calculateProgress(currentStep, 'merge');
      return { status: 'merging', step: formattedStep, progress: progressPercent };
    }
    
    // PRIORITY 7: Extraction Complete, Waiting for Merge
    if (allDashboardsCompleted && mergeStatus === 'pending') {
      return { status: 'pending', step: '✅ All dashboards extracted, starting merge...', progress: 45 };
    }
    
    // PRIORITY 8: Extraction In Progress (GRANULAR PROGRESS)
    if (overallStatus === 'extracting' || totalDashboards > 0) {
      if (completedCount === 0) {
        return { status: 'pending', step: '⏳ Extraction starting...', progress: 5 };
      } else if (completedCount < totalDashboards) {
        // Calculate granular extraction progress: 5% → 40% range
        const extractionProgress = 5 + Math.floor((completedCount / totalDashboards) * 35);
        return { 
          status: 'pending', 
          step: `⏳ Extracting dashboards (${completedCount}/${totalDashboards} completed)`, 
          progress: extractionProgress
        };
      } else {
        // All extracted but merge hasn't started
        return { status: 'pending', step: '✅ Extraction complete, preparing merge...', progress: 40 };
      }
    }
    
    // PRIORITY 9: Idle/Waiting
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

