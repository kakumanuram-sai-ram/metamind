import React, { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { paytmTheme } from './styles/theme';
import styled from 'styled-components';
import DashboardExtractor from './components/DashboardExtractor';
import DownloadButtons from './components/DownloadButtons';
import MultiDashboardProcessor from './components/MultiDashboardProcessor';
import DashboardFileDownloader from './components/DashboardFileDownloader';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, ${props => props.theme.colors.gray[50]} 0%, ${props => props.theme.colors.gray[100]} 100%);
`;

const Header = styled.header`
  background: ${props => props.theme.colors.accentLight};
  color: white;
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${props => props.theme.spacing.xl} ${props => props.theme.spacing.xl};
`;


function App() {
  const [extractedDashboard, setExtractedDashboard] = useState(null);

  const handleExtractSuccess = (dashboardData) => {
    setExtractedDashboard({
      dashboardId: dashboardData.dashboard_id,
      dashboardTitle: dashboardData.dashboard_title,
      totalCharts: dashboardData.total_charts
    });
  };

  return (
    <ThemeProvider theme={paytmTheme}>
      <AppContainer>
        <Header>
          <HeaderContent>
            <div>
              <Logo>
                <MetaText>Meta</MetaText><MindText>Mind</MindText>
              </Logo>
              <Subtitle>Extract and visualize dashboard metadata from Apache Superset</Subtitle>
            </div>
          </HeaderContent>
        </Header>

        <MainContent>
          <MultiDashboardProcessor />
          <DashboardFileDownloader />
          <DashboardExtractor onExtractSuccess={handleExtractSuccess} />
          
          {extractedDashboard && (
            <DownloadButtons
              dashboardId={extractedDashboard.dashboardId}
              dashboardTitle={extractedDashboard.dashboardTitle}
              totalCharts={extractedDashboard.totalCharts}
            />
          )}
        </MainContent>
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;

