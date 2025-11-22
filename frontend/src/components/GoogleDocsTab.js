import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: ${props => props.theme.colors.gray[600]};
`;

const GoogleDocsTab = () => {
  return (
    <Container>
      <h2>Google Docs Integration</h2>
      <p>This feature is coming soon...</p>
    </Container>
  );
};

export default GoogleDocsTab;



