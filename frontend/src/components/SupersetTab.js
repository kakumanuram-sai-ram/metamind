import React, { useState, useEffect, useCallback } from 'react';
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

// Vertical Selection Styles
const VerticalSection = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SelectLabel = styled.label`
  display: block;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.gray[700]};
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

// Dashboard Dropdown Styles
const DashboardDropdownContainer = styled.div`
  position: relative;
  flex: 1;
`;

const DashboardDropdownButton = styled.button`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  background: white;
  cursor: pointer;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray[100]};
    cursor: not-allowed;
  }
`;

const DropdownArrow = styled.span`
  transition: transform 0.2s;
  transform: ${props => props.isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
`;

const DashboardDropdownList = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  box-shadow: ${props => props.theme.shadows.lg};
  z-index: 100;
  margin-top: 4px;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.gray[100]};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.gray[400]};
    border-radius: 4px;
  }
`;

const DashboardDropdownItem = styled.div`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  cursor: pointer;
  border-bottom: 1px solid ${props => props.theme.colors.gray[100]};
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: ${props => props.theme.colors.gray[50]};
  }
  
  ${props => props.selected && `
    background: ${props.theme.colors.primary}10;
  `}
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: ${props => props.theme.colors.primary};
`;

const DashboardItemInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const DashboardTitle = styled.span`
  display: block;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.gray[900]};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const DashboardLink = styled.a`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
`;

const SelectedCount = styled.span`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.gray[500]};
  margin-left: ${props => props.theme.spacing.sm};
`;

const LoadingText = styled.div`
  padding: ${props => props.theme.spacing.md};
  text-align: center;
  color: ${props => props.theme.colors.gray[500]};
`;

const NoResultsText = styled.div`
  padding: ${props => props.theme.spacing.md};
  text-align: center;
  color: ${props => props.theme.colors.gray[500]};
`;

const Divider = styled.div`
  height: 1px;
  background: ${props => props.theme.colors.gray[200]};
  margin: ${props => props.theme.spacing.md} 0;
`;

const OrText = styled.span`
  display: block;
  text-align: center;
  color: ${props => props.theme.colors.gray[500]};
  font-size: ${props => props.theme.typography.fontSize.sm};
  margin: ${props => props.theme.spacing.sm} 0;
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


const SupersetTab = ({ preservedState, onStateChange, selectedVertical, selectedSubVertical }) => {
  // Log component mount
  React.useEffect(() => {
    const mountTime = performance.now();
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [SUPERSET_TAB MOUNT] Component mounted`, {
      mountTime: `${mountTime.toFixed(2)}ms`,
      hasPreservedState: !!preservedState,
      activeDashboardIds: preservedState?.activeDashboardIds || [],
      timestamp: Date.now()
    });
    
    return () => {
      const unmountTime = performance.now();
      const unmountTimestamp = new Date().toISOString();
      console.log(`[${unmountTimestamp}] [SUPERSET_TAB UNMOUNT] Component unmounting`, {
        lifetime: `${(unmountTime - mountTime).toFixed(2)}ms`
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Use preserved state if available, otherwise initialize
  const [dashboardIds, setDashboardIds] = useState(preservedState?.dashboardIds || '');
  const [loading, setLoading] = useState(false);
  const [activeDashboardIds, setActiveDashboardIds] = useState(preservedState?.activeDashboardIds || []);
  const [progress, setProgress] = useState(preservedState?.progress || null);
  const [progressInterval, setProgressInterval] = useState(null);
  const [statusMessage, setStatusMessage] = useState(preservedState?.statusMessage || null);
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [pendingDashboardIds, setPendingDashboardIds] = useState([]);
  const [existingMetadata, setExistingMetadata] = useState(preservedState?.existingMetadata || {});
  const [metadataChoices, setMetadataChoices] = useState(preservedState?.metadataChoices || {}); // Store user's choices

  // Dashboard selection states
  const [availableDashboards, setAvailableDashboards] = useState([]);
  const [selectedDashboards, setSelectedDashboards] = useState(preservedState?.selectedDashboards || []);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [loadingDashboards, setLoadingDashboards] = useState(false);

  // Fetch dashboards when vertical/sub-vertical changes
  useEffect(() => {
    // Track if this effect is still current (for cleanup)
    let isCurrent = true;
    
    if (!selectedVertical) {
      setLoadingDashboards(false);
      setAvailableDashboards([]);
      setSelectedDashboards([]);
      return;
    }
    
    // Set loading immediately WITHOUT clearing results (to prevent flash of "No results")
    setLoadingDashboards(true);
    
    // Fetch dashboards
    const fetchDashboards = async () => {
      try {
        console.log(`Fetching dashboards for vertical=${selectedVertical}, subVertical=${selectedSubVertical}`);
        const response = await dashboardAPI.getDashboardsByVertical(selectedVertical, selectedSubVertical || null);
        console.log(`Received ${response.dashboards?.length || 0} dashboards, tags_searched=${JSON.stringify(response.tags_searched)}, isCurrent=${isCurrent}`);
        
        // Only update state if this is still the current request
        if (isCurrent) {
          if (response.success) {
            setAvailableDashboards(response.dashboards);
            setSelectedDashboards([]); // Clear selections when new results arrive
          } else {
            setAvailableDashboards([]);
            setSelectedDashboards([]);
          }
          setLoadingDashboards(false);
        }
      } catch (error) {
        console.error('Error fetching dashboards:', error);
        if (isCurrent) {
          setAvailableDashboards([]);
          setSelectedDashboards([]);
          setLoadingDashboards(false);
        }
      }
    };
    
    fetchDashboards();
    
    // Cleanup: mark this effect as stale when deps change or component unmounts
    return () => {
      isCurrent = false;
    };
  }, [selectedVertical, selectedSubVertical]);

  // Toggle dashboard selection
  const toggleDashboardSelection = (dashboard) => {
    setSelectedDashboards(prev => {
      const isSelected = prev.some(d => d.id === dashboard.id);
      if (isSelected) {
        return prev.filter(d => d.id !== dashboard.id);
      } else {
        return [...prev, dashboard];
      }
    });
  };

  // Update parent state whenever key state changes
  React.useEffect(() => {
    if (onStateChange) {
      onStateChange({
        dashboardIds,
        activeDashboardIds,
        progress,
        statusMessage,
        metadataChoices,
        existingMetadata,
        selectedDashboards,
      });
    }
  }, [dashboardIds, activeDashboardIds, progress, statusMessage, metadataChoices, existingMetadata, selectedDashboards, onStateChange]);

  const fetchProgress = async () => {
    const startTime = performance.now();
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [SUPERSET_TAB] fetchProgress called`);
    
    try {
      const progressData = await dashboardAPI.getProgress();
      const duration = (performance.now() - startTime).toFixed(2);
      console.log(`[${new Date().toISOString()}] [SUPERSET_TAB] fetchProgress completed`, {
        duration: `${duration}ms`,
        status: progressData?.status,
        dashboardsCount: Object.keys(progressData?.dashboards || {}).length
      });
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
      
      // Check KB build status for proper completion detection
      const kbBuildStatus = progressData.kb_build_status?.status;
      const mergeStatus = progressData.merge_status?.status;
      
      if (progressData.status === 'extracting') {
        // Show current extraction phase
        const extractingDashboard = activeDashboardIds.find(id => {
          const dashProgress = progressData.dashboards?.[id.toString()];
          return dashProgress?.status === 'processing';
        });
        if (extractingDashboard) {
          const dashProgress = progressData.dashboards?.[extractingDashboard.toString()];
          const phase = dashProgress?.current_phase || 'Extracting';
          setStatusMessage({ type: 'info', text: `${phase} for Dashboard ${extractingDashboard}...` });
        } else {
          setStatusMessage({ type: 'info', text: 'Extraction in progress...' });
        }
      } else if (progressData.status === 'merging') {
        const currentStep = progressData.merge_status?.current_step || 'merging';
        setStatusMessage({ type: 'info', text: `Metadata merging: ${currentStep}...` });
      } else if (progressData.status === 'building_kb') {
        const currentStep = progressData.kb_build_status?.current_step || 'building';
        setStatusMessage({ type: 'info', text: `Building knowledge base: ${currentStep}...` });
      } else if (progressData.status === 'completed' && kbBuildStatus === 'completed' && allDashboardsMatch) {
        // Only show completed if:
        // 1. Overall status is 'completed'
        // 2. KB build status is 'completed' (Phase 9 done)
        // 3. All active dashboards are in the progress tracker
        const allDashboardsCompleted = activeDashboardIds.every(id => {
          const dashProgress = progressData.dashboards?.[id.toString()];
          return dashProgress?.status === 'completed';
        });
        
        if (allDashboardsCompleted) {
          setStatusMessage({ type: 'success', text: 'All processing complete! Knowledge base ZIP file is available for download.' });
          if (progressInterval) {
            clearInterval(progressInterval);
            setProgressInterval(null);
          }
        } else {
          setStatusMessage({ type: 'info', text: 'Finalizing processing...' });
        }
      } else if (progressData.status === 'idle') {
        setStatusMessage(null);
      } else {
        // Default: show processing with current operation
        const currentOp = progressData.current_operation || 'processing';
        setStatusMessage({ type: 'info', text: `${currentOp.charAt(0).toUpperCase() + currentOp.slice(1)} in progress...` });
      }
      
      // Stop polling only when KB build is actually completed (Phase 9 done)
      if (progressData.status === 'completed' && kbBuildStatus === 'completed' && allDashboardsMatch) {
        if (progressInterval) {
          clearInterval(progressInterval);
          setProgressInterval(null);
        }
      } else if (progressData.status === 'idle') {
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
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [SUPERSET_TAB] useEffect mount check`, {
      activeDashboardIdsCount: activeDashboardIds.length,
      hasProgressInterval: !!progressInterval
    });
    
    if (activeDashboardIds.length > 0 && !progressInterval) {
      // Restart polling if we have active dashboards
      // Poll every 3 seconds instead of 2 to reduce server load
      // Use setTimeout to avoid blocking initial render
      const timeoutId = setTimeout(() => {
        const startPollTime = performance.now();
        console.log(`[${new Date().toISOString()}] [SUPERSET_TAB] Starting progress polling`);
        fetchProgress();
        const interval = setInterval(fetchProgress, 3000);
        setProgressInterval(interval);
        const setupDuration = (performance.now() - startPollTime).toFixed(2);
        console.log(`[${new Date().toISOString()}] [SUPERSET_TAB] Progress polling setup complete`, {
          setupDuration: `${setupDuration}ms`,
          interval: '3000ms'
        });
      }, 100); // Small delay to allow initial render
      
      return () => {
        clearTimeout(timeoutId);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  const checkExistingMetadata = async (dashboardIds) => {
    const startTime = performance.now();
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [SUPERSET_TAB] checkExistingMetadata called`, {
      dashboardIdsCount: dashboardIds.length,
      dashboardIds
    });
    
    const existing = {};
    for (const id of dashboardIds) {
      const checkStartTime = performance.now();
      try {
        const exists = await dashboardAPI.checkDashboardMetadataExists(id);
        const checkDuration = (performance.now() - checkStartTime).toFixed(2);
        console.log(`[${new Date().toISOString()}] [SUPERSET_TAB] Metadata check for dashboard ${id}`, {
          exists,
          duration: `${checkDuration}ms`
        });
        existing[id] = exists;
      } catch (error) {
        const checkDuration = (performance.now() - checkStartTime).toFixed(2);
        console.error(`[${new Date().toISOString()}] [SUPERSET_TAB] Metadata check error for dashboard ${id}`, {
          error: error.message,
          duration: `${checkDuration}ms`
        });
        existing[id] = false;
      }
    }
    
    const totalDuration = (performance.now() - startTime).toFixed(2);
    console.log(`[${new Date().toISOString()}] [SUPERSET_TAB] checkExistingMetadata completed`, {
      totalDuration: `${totalDuration}ms`,
      results: existing
    });
    
    return existing;
  };

  const handleStartExtraction = async (e) => {
    e?.preventDefault();
    setStatusMessage(null);
    setLoading(true);

    try {
      let ids = [];
      
      // First check if dashboards are selected from dropdown
      if (selectedDashboards.length > 0) {
        ids = selectedDashboards.map(d => d.id);
      } else {
        // Parse dashboard IDs from manual input
        ids = dashboardIds
          .split(/[,\s]+/)
          .map(id => parseInt(id.trim()))
          .filter(id => !isNaN(id) && id > 0);
      }

      if (ids.length === 0) {
        throw new Error('Please select dashboards from the dropdown or enter dashboard IDs manually');
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


  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isDropdownOpen && !event.target.closest('[data-dropdown-container]')) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isDropdownOpen]);

  return (
    <Container>
      <InputSection>
        {/* Dashboard Selection Section */}
        <VerticalSection>
          <InputLabel>Select Dashboards</InputLabel>
          
          {/* Dashboard Dropdown */}
          <DashboardDropdownContainer data-dropdown-container>
            <SelectLabel>Available Dashboards</SelectLabel>
            <DashboardDropdownButton
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              disabled={loading || !selectedVertical}
            >
              <span>
                {selectedDashboards.length > 0 
                  ? `${selectedDashboards.length} dashboard(s) selected`
                  : selectedVertical 
                    ? 'Click to select dashboards'
                    : 'Please select a Business Vertical above to see dashboards'}
              </span>
              <DropdownArrow isOpen={isDropdownOpen}>▼</DropdownArrow>
            </DashboardDropdownButton>
            
            {isDropdownOpen && (
              <DashboardDropdownList>
                {loadingDashboards ? (
                  <LoadingText>Loading dashboards...</LoadingText>
                ) : availableDashboards.length === 0 ? (
                  <NoResultsText>
                    {selectedVertical 
                      ? `No dashboards found matching tags for ${selectedVertical}${selectedSubVertical ? ` - ${selectedSubVertical}` : ''}`
                      : 'Please select a Business Vertical above to see dashboards'}
                  </NoResultsText>
                ) : (
                  availableDashboards.map(dashboard => (
                    <DashboardDropdownItem
                      key={dashboard.id}
                      selected={selectedDashboards.some(d => d.id === dashboard.id)}
                      onClick={() => toggleDashboardSelection(dashboard)}
                    >
                      <Checkbox
                        type="checkbox"
                        checked={selectedDashboards.some(d => d.id === dashboard.id)}
                        onChange={() => {}} // Handled by parent onClick
                        onClick={(e) => e.stopPropagation()}
                      />
                      <DashboardItemInfo>
                        <DashboardTitle>{dashboard.title}</DashboardTitle>
                        <DashboardLink
                          href={dashboard.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {dashboard.url}
                        </DashboardLink>
                      </DashboardItemInfo>
                    </DashboardDropdownItem>
                  ))
                )}
              </DashboardDropdownList>
            )}
          </DashboardDropdownContainer>
          
          {selectedDashboards.length > 0 && (
            <SelectedCount>
              Selected: {selectedDashboards.map(d => d.title).join(', ')}
            </SelectedCount>
          )}
        </VerticalSection>
        
        <Divider />
        <OrText>OR enter dashboard IDs manually</OrText>
        
        {/* Manual Dashboard ID Input */}
        <InputLabel>Dashboard ID</InputLabel>
        <InputRow>
          <DashboardIdInput
            type="text"
            value={dashboardIds}
            onChange={(e) => setDashboardIds(e.target.value)}
            placeholder="Enter dashboard IDs (comma-separated, e.g., 585, 729, 842)"
            disabled={loading || selectedDashboards.length > 0}
          />
          <StartButton 
            type="button" 
            onClick={handleStartExtraction}
            disabled={loading || (selectedDashboards.length === 0 && !dashboardIds.trim())}
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

