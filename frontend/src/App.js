import React, { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { paytmTheme } from './styles/theme';
import styled from 'styled-components';
import TabNavigation from './components/TabNavigation';
import BusinessVertical from './components/BusinessVertical';
import SupersetTab from './components/SupersetTab';
import GoogleDocsTab from './components/GoogleDocsTab';
import ConfluenceTab from './components/ConfluenceTab';
import GlobalStyles from './styles/GlobalStyles';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, ${props => props.theme.colors.gray[50]} 0%, ${props => props.theme.colors.gray[100]} 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Header = styled.header`
  background: ${props => props.theme.colors.accentLight};
  color: white;
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.lg};
  margin-bottom: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  flex-shrink: 0;
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.h1`
  font-size: ${props => props.theme.typography.fontSize['3xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin: 0;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const MetaText = styled.span`
  color: ${props => props.theme.colors.primary};
`;

const MindText = styled.span`
  color: ${props => props.theme.colors.accent};
`;

const Subtitle = styled.p`
  margin: ${props => props.theme.spacing.xs} 0 0 0;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.gray[600]};
  font-weight: ${props => props.theme.typography.fontWeight.normal};
`;

const MainContent = styled.main`
  flex: 1;
  overflow-y: auto;
  padding-bottom: ${props => props.theme.spacing.xl};
`;


function App() {
  const [activeTab, setActiveTab] = useState('superset');
  const [selectedVertical, setSelectedVertical] = useState(null);
  const [selectedSubVertical, setSelectedSubVertical] = useState(null);
  
  // Preserve SupersetTab state across tab switches
  const [supersetState, setSupersetState] = useState({
    dashboardIds: '',
    activeDashboardIds: [],
    progress: null,
    statusMessage: null,
  });


  const renderTabContent = () => {
    switch (activeTab) {
      case 'superset':
        return (
          <SupersetTab 
            preservedState={supersetState}
            onStateChange={setSupersetState}
          />
        );
      case 'googledocs':
        return <GoogleDocsTab />;
      case 'confluence':
        return <ConfluenceTab />;
      default:
        return (
          <SupersetTab 
            preservedState={supersetState}
            onStateChange={setSupersetState}
          />
        );
    }
  };

  return (
    <ThemeProvider theme={paytmTheme}>
      <GlobalStyles />
      <AppContainer>
        <Header>
          <HeaderContent>
            <div>
              <Logo>
                <MetaText>Meta</MetaText><MindText>Mind</MindText>
              </Logo>
              <Subtitle>Intelligence Embedded in Every Query. Insight Extracted Automatically</Subtitle>
            </div>
          </HeaderContent>
        </Header>

        <BusinessVertical
          selectedVertical={selectedVertical}
          selectedSubVertical={selectedSubVertical}
          onVerticalChange={setSelectedVertical}
          onSubVerticalChange={setSelectedSubVertical}
        />

        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        <MainContent>
          {renderTabContent()}
        </MainContent>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;

