import React from 'react';
import styled from 'styled-components';

const TabsContainer = styled.div`
  background: white;
  border-bottom: 2px solid ${props => props.theme.colors.gray[200]};
  margin-bottom: 0;
  position: sticky;
  top: 120px; /* Header height + padding */
  z-index: 99;
  flex-shrink: 0;
`;

const TabsList = styled.div`
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${props => props.theme.spacing.xl};
  gap: ${props => props.theme.spacing.md};
`;

const Tab = styled.button`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background: transparent;
  border: none;
  border-bottom: 3px solid ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.gray[600]};
  font-size: ${props => props.theme.typography.fontSize.base};
  font-weight: ${props => props.active ? props.theme.typography.fontWeight.semibold : props.theme.typography.fontWeight.normal};
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  top: 2px;

  &:hover {
    color: ${props => props.theme.colors.primary};
    border-bottom-color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.gray[300]};
  }
`;

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'superset', label: 'Superset' },
    { id: 'googledocs', label: 'Google Docs' },
    { id: 'confluence', label: 'Confluence/Wiki' },
  ];

  return (
    <TabsContainer>
      <TabsList>
        {tabs.map(tab => (
          <Tab
            key={tab.id}
            active={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </Tab>
        ))}
      </TabsList>
    </TabsContainer>
  );
};

export default TabNavigation;

