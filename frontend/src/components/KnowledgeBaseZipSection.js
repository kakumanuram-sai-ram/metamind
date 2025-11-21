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

const DownloadButton = styled.button`
  background: ${props => props.theme.colors.success};
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
  gap: ${props => props.theme.spacing.sm};
  
  &:hover:not(:disabled) {
    background: #059669;
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:disabled {
    background: ${props => props.theme.colors.gray[400]};
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const DownloadIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7 10 12 15 17 10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const KnowledgeBaseZipSection = ({ progress, dashboardIds = [] }) => {
  const [zipAvailable, setZipAvailable] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [allFilesReady, setAllFilesReady] = useState(false);

  // Check if all individual metadata files are ready for all dashboards
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
    // Check when KB build is completed AND all individual files are ready
    if (progress?.kb_build_status?.status === 'completed') {
      checkAllFilesReady().then((ready) => {
        if (ready) {
          checkZipAvailability();
        }
      });
      
      // Also check periodically
      const interval = setInterval(() => {
        checkAllFilesReady().then((ready) => {
          if (ready) {
            checkZipAvailability();
          }
        });
      }, 5000);
      
      return () => clearInterval(interval);
    } else {
      setZipAvailable(false);
      setAllFilesReady(false);
    }
  }, [progress, checkAllFilesReady, checkZipAvailability]);

  const getStatus = () => {
    if (!progress) return { status: 'pending', step: 'Waiting for extraction', progress: 0 };
    
    const kbStatus = progress.kb_build_status?.status || 'pending';
    const mergeStatus = progress.merge_status?.status || 'pending';
    const overallStatus = progress.status || 'idle';

    if (kbStatus === 'completed' && zipAvailable && allFilesReady) {
      return { status: 'completed', step: 'Ready for download', progress: 100 };
    }
    
    if (kbStatus === 'completed' && !allFilesReady) {
      return { status: 'processing', step: 'Waiting for all dashboard files to be ready', progress: 90 };
    }
    
    if (kbStatus === 'processing') {
      const currentStep = progress.kb_build_status?.current_step || 'Building knowledge base';
      return { status: 'processing', step: currentStep, progress: 75 };
    }
    
    if (mergeStatus === 'processing' || overallStatus === 'merging') {
      const currentStep = progress.merge_status?.current_step || 'Merging metadata';
      return { status: 'merging', step: currentStep, progress: 50 };
    }
    
    if (overallStatus === 'extracting') {
      return { status: 'pending', step: 'Waiting for extraction to complete', progress: 25 };
    }
    
    return { status: 'pending', step: 'Waiting to start', progress: 0 };
  };

  const handleDownload = async () => {
    setDownloading(true);
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
    } catch (error) {
      console.error('Error downloading knowledge base ZIP:', error);
      alert('Failed to download knowledge base ZIP. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  const statusInfo = getStatus();
  const isHighlighted = statusInfo.status === 'processing' || statusInfo.status === 'merging' || statusInfo.status === 'completed';

  return (
    <SectionContainer highlight={isHighlighted}>
      <SectionHeader>
        <SectionTitle>Knowledge Base ZIP</SectionTitle>
        <StatusBadge status={statusInfo.status}>
          {statusInfo.status === 'completed' ? 'Ready' : 
           statusInfo.status === 'processing' ? 'Building' :
           statusInfo.status === 'merging' ? 'Merging' : 'Pending'}
        </StatusBadge>
      </SectionHeader>
      
      <SectionDescription>
        Consolidated knowledge base containing all merged metadata files. This ZIP file is created after all dashboards are extracted and merged.
      </SectionDescription>
      
      <ProgressBar>
        <ProgressFill progress={statusInfo.progress} status={statusInfo.status} />
      </ProgressBar>
      
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginTop: '1rem'
      }}>
        <div style={{ 
          fontSize: '0.875rem', 
          color: statusInfo.status === 'completed' ? '#10B981' : '#6B7280' 
        }}>
          {statusInfo.step}
        </div>
        
        {statusInfo.status === 'completed' && zipAvailable && allFilesReady && (
          <DownloadButton onClick={handleDownload} disabled={downloading}>
            <DownloadIcon size={18} />
            {downloading ? 'Downloading...' : 'Download ZIP'}
          </DownloadButton>
        )}
      </div>
    </SectionContainer>
  );
};

export default KnowledgeBaseZipSection;

