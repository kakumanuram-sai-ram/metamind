import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';
import DashboardSection from './DashboardSection';
import KnowledgeBaseDownload from './KnowledgeBaseDownload';
import MetadataChoiceModal from './MetadataChoiceModal';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${props => props.theme.spacing.xl};
`;

const InputSection = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const InputLabel = styled.label`
  display: block;
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.gray[900]};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.base};
`;

const InputRow = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  align-items: center;
`;

const DashboardIdInput = styled.input`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const StartButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  
  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primaryDark};
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray[400]};
    cursor: not-allowed;
  }
`;

const DashboardsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xl};
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  padding-right: ${props => props.theme.spacing.sm};
  
  &::-webkit-scrollbar {
    width: 8px;
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

const StatusMessage = styled.div`
  background: ${props => {
    if (props.type === 'info') return props.theme.colors.info;
    if (props.type === 'success') return props.theme.colors.success;
    if (props.type === 'error') return props.theme.colors.error;
    return props.theme.colors.gray[200];
  }};
  color: white;
  border: 1px solid ${props => {
    if (props.type === 'info') return props.theme.colors.info;
    if (props.type === 'success') return props.theme.colors.success;
    if (props.type === 'error') return props.theme.colors.error;
    return props.theme.colors.gray[300];
  }};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  box-shadow: ${props => props.theme.shadows.sm};
`;


const SupersetTab = ({ preservedState, onStateChange }) => {
  // Use preserved state if available, otherwise initialize
  const [dashboardIds, setDashboardIds] = useState(preservedState?.dashboardIds || '');
  const [loading, setLoading] = useState(false);
  const [activeDashboardIds, setActiveDashboardIds] = useState(preservedState?.activeDashboardIds || []);
  const [progress, setProgress] = useState(preservedState?.progress || null);
  const [progressInterval, setProgressInterval] = useState(null);
  const [statusMessage, setStatusMessage] = useState(preservedState?.statusMessage || null);
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [pendingDashboardIds, setPendingDashboardIds] = useState([]);
  const [existingMetadata, setExistingMetadata] = useState({});
  const [metadataChoices, setMetadataChoices] = useState({}); // Store user's choices

  // Update parent state whenever key state changes
  React.useEffect(() => {
    if (onStateChange) {
      onStateChange({
        dashboardIds,
        activeDashboardIds,
        progress,
        statusMessage,
      });
    }
  }, [dashboardIds, activeDashboardIds, progress, statusMessage, onStateChange]);

  const fetchProgress = async () => {
    try {
      const progressData = await dashboardAPI.getProgress();
      setProgress(progressData);
      
      // Only show status messages if we have active dashboards being processed
      if (activeDashboardIds.length === 0) {
        setStatusMessage(null);
        return;
      }
      
      // Check if ALL active dashboards are in progress (strict matching)
      const progressDashboardIds = Object.keys(progressData.dashboards || {}).map(id => parseInt(id));
      const allDashboardsMatch = activeDashboardIds.length > 0 && 
                                 activeDashboardIds.every(id => progressDashboardIds.includes(id));
      
      // Only show status if ALL active dashboards are in progress
      if (!allDashboardsMatch && progressData.status !== 'idle') {
        // Progress is for different dashboards, don't show status
        setStatusMessage(null);
        return;
      }
      
      // Update status messages based on progress - only if all dashboards match
      if (!allDashboardsMatch) {
        setStatusMessage(null);
        return;
      }
      
      if (progressData.status === 'merging') {
        setStatusMessage({ type: 'info', text: 'Metadata merging is happening...' });
      } else if (progressData.status === 'building_kb') {
        setStatusMessage({ type: 'info', text: 'Validation is happening...' });
      } else if (progressData.status === 'completed' && allDashboardsMatch) {
        // Only show completed if ALL active dashboards are completed
        // Also verify that all dashboards actually have completed status
        const allCompleted = activeDashboardIds.every(id => {
          const dashProgress = progressData.dashboards?.[id.toString()];
          return dashProgress?.status === 'completed' || dashProgress?.status === 'processing';
        });
        
        if (allCompleted) {
          setStatusMessage({ type: 'success', text: 'All processing complete! Knowledge base ZIP file is available for download.' });
          if (progressInterval) {
            clearInterval(progressInterval);
            setProgressInterval(null);
          }
        } else {
          setStatusMessage({ type: 'info', text: 'Processing in progress...' });
        }
      } else if (progressData.status === 'extracting') {
        setStatusMessage({ type: 'info', text: 'Extraction in progress...' });
      } else if (progressData.status === 'idle') {
        setStatusMessage(null);
      } else {
        // Default: show processing
        setStatusMessage({ type: 'info', text: 'Processing in progress...' });
      }
      
      // Stop polling if completed or idle (only for our dashboards)
      if ((progressData.status === 'completed' && allDashboardsMatch) || progressData.status === 'idle') {
        if (progressInterval) {
          clearInterval(progressInterval);
          setProgressInterval(null);
        }
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };

  useEffect(() => {
    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [progressInterval]);

  // Restore progress polling if we have active dashboards when component mounts
  useEffect(() => {
    if (activeDashboardIds.length > 0 && !progressInterval) {
      // Restart polling if we have active dashboards
      // Poll every 3 seconds instead of 2 to reduce server load
      fetchProgress();
      const interval = setInterval(fetchProgress, 3000);
      setProgressInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const checkExistingMetadata = async (dashboardIds) => {
    const existing = {};
    for (const id of dashboardIds) {
      try {
        const exists = await dashboardAPI.checkDashboardMetadataExists(id);
        existing[id] = exists;
      } catch (error) {
        existing[id] = false;
      }
    }
    return existing;
  };

  const handleStartExtraction = async (e) => {
    e?.preventDefault();
    setStatusMessage(null);
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

      // Check for existing metadata
      const existing = await checkExistingMetadata(ids);
      setExistingMetadata(existing);
      
      // Check if any dashboard has existing metadata
      const hasExisting = Object.values(existing).some(v => v === true);
      
      if (hasExisting) {
        // Show modal to ask user about metadata choices
        setPendingDashboardIds(ids);
        setShowMetadataModal(true);
        setLoading(false);
        return;
      }

      // No existing metadata, proceed directly
      await proceedWithExtraction(ids, {});

    } catch (error) {
      setStatusMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || 'Failed to start processing',
      });
      setLoading(false);
    }
  };

  const handleMetadataChoiceConfirm = async (choices) => {
    setShowMetadataModal(false);
    setLoading(true);
    
    // Convert choices to format expected by API (dashboard_id -> use_existing boolean)
    const choicesDict = {};
    Object.keys(choices).forEach(dashboardId => {
      choicesDict[parseInt(dashboardId)] = choices[dashboardId] === 'use_existing';
    });
    
    // Store choices for use in DashboardSection
    setMetadataChoices(choicesDict);
    
    await proceedWithExtraction(pendingDashboardIds, choicesDict);
  };

  const proceedWithExtraction = async (ids, metadataChoices) => {
    try {
      // Clear any previous status messages and progress
      setStatusMessage(null);
      setProgress(null);
      
      // Set active dashboard IDs
      setActiveDashboardIds(ids);

      // Start processing with metadata choices
      await dashboardAPI.processMultipleDashboards(ids, true, true, true, metadataChoices);

      setStatusMessage({
        type: 'info',
        text: `Processing started for ${ids.length} dashboard(s).`,
      });

      // Start polling for progress
      fetchProgress();
      const interval = setInterval(fetchProgress, 2000); // Poll every 2 seconds
      setProgressInterval(interval);

    } catch (error) {
      setStatusMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || 'Failed to start processing',
      });
    } finally {
      setLoading(false);
    }
  };


  return (
    <Container>
      <InputSection>
        <InputLabel>Dashboard ID</InputLabel>
        <InputRow>
          <DashboardIdInput
            type="text"
            value={dashboardIds}
            onChange={(e) => setDashboardIds(e.target.value)}
            placeholder="Enter dashboard IDs (comma-separated, e.g., 585, 729, 842)"
            disabled={loading}
          />
          <StartButton 
            type="button" 
            onClick={handleStartExtraction}
            disabled={loading || !dashboardIds.trim()}
          >
            {loading ? 'Starting...' : 'Start Extraction'}
          </StartButton>
        </InputRow>
      </InputSection>

      {statusMessage && (
        <StatusMessage type={statusMessage.type}>
          {statusMessage.text}
        </StatusMessage>
      )}

      {activeDashboardIds.length > 0 && (
        <DashboardsContainer>
          {activeDashboardIds.map(dashboardId => (
            <DashboardSection
              key={dashboardId}
              dashboardId={dashboardId}
              progress={progress?.dashboards?.[dashboardId] || null}
              useExisting={metadataChoices[dashboardId] === true}
            />
          ))}
        </DashboardsContainer>
      )}

      {activeDashboardIds.length > 0 && (
        <KnowledgeBaseDownload 
          progress={progress} 
          dashboardIds={activeDashboardIds}
        />
      )}

      <MetadataChoiceModal
        isOpen={showMetadataModal}
        dashboardIds={pendingDashboardIds}
        existingMetadata={existingMetadata}
        onConfirm={handleMetadataChoiceConfirm}
        onCancel={() => {
          setShowMetadataModal(false);
          setLoading(false);
        }}
      />
    </Container>
  );
};

export default SupersetTab;

