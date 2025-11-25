import React from 'react';
import styled from 'styled-components';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContainer = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: ${props => props.theme.shadows.xl};
`;

const ModalHeader = styled.h2`
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
`;

const ModalDescription = styled.p`
  color: ${props => props.theme.colors.gray[600]};
  margin-bottom: ${props => props.theme.spacing.xl};
  line-height: 1.6;
`;

const DashboardList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const DashboardItem = styled.div`
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.gray[50]};
`;

const DashboardId = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.gray[900]};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.base};
`;

const ExistingBadge = styled.span`
  display: inline-block;
  margin-left: ${props => props.theme.spacing.sm};
  padding: 2px 8px;
  background: ${props => props.theme.colors.success + '20'};
  color: ${props => props.theme.colors.success};
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: ${props => props.theme.typography.fontSize.xs};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ChoiceButtons = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
`;

const ChoiceButton = styled.button`
  flex: 1;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.selected ? props.theme.colors.primary : 'white'};
  color: ${props => props.selected ? 'white' : props.theme.colors.gray[700]};
  font-weight: ${props => props.selected ? props.theme.typography.fontWeight.semibold : props.theme.typography.fontWeight.normal};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.selected ? props.theme.colors.primary : props.theme.colors.primary + '10'};
    color: ${props => props.selected ? 'white' : props.theme.colors.primary};
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  justify-content: flex-end;
  margin-top: ${props => props.theme.spacing.xl};
`;

const Button = styled.button.attrs(props => ({
  // Remove primary from DOM attributes
  primary: undefined
}))`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all 0.2s;

  ${props => props.primary ? `
    background: ${props.theme.colors.primary};
    color: white;
    border: none;

    &:hover:not(:disabled) {
      background: ${props.theme.colors.primaryDark};
    }

    &:disabled {
      background: ${props.theme.colors.gray[400]};
      cursor: not-allowed;
    }
  ` : `
    background: white;
    color: ${props.theme.colors.gray[700]};
    border: 1px solid ${props.theme.colors.gray[300]};

    &:hover {
      background: ${props.theme.colors.gray[50]};
    }
  `}
`;

const MetadataChoiceModal = ({ isOpen, dashboardIds, existingMetadata, onConfirm, onCancel }) => {
  const [choices, setChoices] = React.useState({});

  React.useEffect(() => {
    if (isOpen && dashboardIds) {
      // Initialize choices - default to 'create_fresh' for all
      const initialChoices = {};
      dashboardIds.forEach(id => {
        initialChoices[id] = existingMetadata[id] ? 'use_existing' : 'create_fresh';
      });
      setChoices(initialChoices);
    }
  }, [isOpen, dashboardIds, existingMetadata]);

  const handleChoice = (dashboardId, choice) => {
    setChoices(prev => ({
      ...prev,
      [dashboardId]: choice
    }));
  };

  const handleConfirm = () => {
    onConfirm(choices);
  };

  if (!isOpen) return null;

  return (
    <ModalOverlay onClick={onCancel}>
      <ModalContainer onClick={(e) => e.stopPropagation()}>
        <ModalHeader>Use Existing Metadata or Create Fresh?</ModalHeader>
        <ModalDescription>
          For each dashboard, choose whether to use existing metadata (if available) or create fresh metadata.
          This choice will determine how the merging process works.
        </ModalDescription>
        
        <DashboardList>
          {dashboardIds.map(dashboardId => (
            <DashboardItem key={dashboardId}>
              <DashboardId>
                Dashboard ID: {dashboardId}
                {existingMetadata[dashboardId] && (
                  <ExistingBadge>Existing Metadata Available</ExistingBadge>
                )}
              </DashboardId>
              <ChoiceButtons>
                <ChoiceButton
                  selected={choices[dashboardId] === 'use_existing'}
                  onClick={() => handleChoice(dashboardId, 'use_existing')}
                  disabled={!existingMetadata[dashboardId]}
                >
                  {existingMetadata[dashboardId] ? '✓ Use Existing' : 'No Existing Metadata'}
                </ChoiceButton>
                <ChoiceButton
                  selected={choices[dashboardId] === 'create_fresh'}
                  onClick={() => handleChoice(dashboardId, 'create_fresh')}
                >
                  Create Fresh
                </ChoiceButton>
              </ChoiceButtons>
            </DashboardItem>
          ))}
        </DashboardList>

        <ActionButtons>
          <Button onClick={onCancel}>Cancel</Button>
          <Button primary onClick={handleConfirm}>
            Proceed with Extraction
          </Button>
        </ActionButtons>
      </ModalContainer>
    </ModalOverlay>
  );
};

export default MetadataChoiceModal;

