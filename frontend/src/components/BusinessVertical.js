import React, { useState, useMemo } from 'react';
import styled from 'styled-components';

const VerticalContainer = styled.div`
  background: white;
  border-bottom: 2px solid ${props => props.theme.colors.gray[200]};
  padding: ${props => props.theme.spacing.lg} ${props => props.theme.spacing.xl};
  position: sticky;
  top: 120px; /* Header height */
  z-index: 98;
  flex-shrink: 0;
`;

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const SectionTitle = styled.h3`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  margin-bottom: ${props => props.theme.spacing.md};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary + '20'};
  }
`;

const VerticalsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
  max-height: 120px;
  overflow-y: auto;
  padding-bottom: ${props => props.theme.spacing.xs};
  
  &::-webkit-scrollbar {
    width: 6px;
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

const VerticalButton = styled.button`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.selected ? '#E0F2FE' : 'white'};
  color: ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[700]};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.selected ? props.theme.typography.fontWeight.semibold : props.theme.typography.fontWeight.normal};
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.selected ? '#E0F2FE' : props.theme.colors.gray[50]};
  }
`;

const SubVerticalsContainer = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding-top: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.gray[200]};
`;

const SubVerticalsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
`;

const SubVerticalButton = styled.button`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.selected ? '#E0F2FE' : 'white'};
  color: ${props => props.selected ? props.theme.colors.primary : props.theme.colors.gray[700]};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.selected ? props.theme.typography.fontWeight.semibold : props.theme.typography.fontWeight.normal};
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  
  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.selected ? '#E0F2FE' : props.theme.colors.gray[50]};
  }
`;

const BusinessVertical = ({ selectedVertical, selectedSubVertical, onVerticalChange, onSubVerticalChange }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const verticals = [
    { id: 'upi', name: 'UPI', subVerticals: ['UPI Growth', 'User Growth'] },
    { id: 'merchant', name: 'Merchant', subVerticals: ['QR / SB', 'EDC', 'All Offline Merchant'] },
    { id: 'lending', name: 'Lending', subVerticals: ['MCA', 'PL'] },
    { id: 'travel', name: 'Travel', subVerticals: ['Flights', 'Trains', 'Bus'] },
    { id: 'recharges', name: 'Recharges & Utilities', subVerticals: ['Electricity', 'Broadband', 'Mobile'] },
  ];

  const filteredVerticals = useMemo(() => {
    if (!searchTerm.trim()) {
      return verticals;
    }
    const term = searchTerm.toLowerCase();
    return verticals.filter(v => 
      v.name.toLowerCase().includes(term) ||
      v.subVerticals.some(sv => sv.toLowerCase().includes(term))
    );
  }, [searchTerm]);

  const top5Verticals = filteredVerticals.slice(0, 5);
  const restVerticals = filteredVerticals.slice(5);

  const selectedVerticalData = verticals.find(v => v.id === selectedVertical);

  return (
    <VerticalContainer>
      <Container>
        <SectionTitle>Business Vertical</SectionTitle>
        <SearchInput
          type="text"
          placeholder="Search verticals..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <VerticalsList>
          {top5Verticals.map(vertical => (
            <VerticalButton
              key={vertical.id}
              selected={selectedVertical === vertical.id}
              onClick={() => onVerticalChange(vertical.id)}
            >
              {vertical.name}
            </VerticalButton>
          ))}
          {restVerticals.length > 0 && (
            <>
              {restVerticals.map(vertical => (
                <VerticalButton
                  key={vertical.id}
                  selected={selectedVertical === vertical.id}
                  onClick={() => onVerticalChange(vertical.id)}
                >
                  {vertical.name}
                </VerticalButton>
              ))}
            </>
          )}
        </VerticalsList>

        {selectedVerticalData && (
          <SubVerticalsContainer>
            <SectionTitle style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              Sub-Verticals for {selectedVerticalData.name}
            </SectionTitle>
            <SubVerticalsList>
              {selectedVerticalData.subVerticals.map(subVertical => (
                <SubVerticalButton
                  key={subVertical}
                  selected={selectedSubVertical === subVertical}
                  onClick={() => onSubVerticalChange(subVertical)}
                >
                  {subVertical}
                </SubVerticalButton>
              ))}
            </SubVerticalsList>
          </SubVerticalsContainer>
        )}
      </Container>
    </VerticalContainer>
  );
};

export default BusinessVertical;

