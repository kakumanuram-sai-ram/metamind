import React, { useState } from 'react';
import styled from 'styled-components';
import { dashboardAPI } from '../services/api';

const Container = styled.div`
  background: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.primary};
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const Label = styled.label`
  color: ${props => props.theme.colors.gray[700]};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const Input = styled.input`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.gray[300]};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: ${props => props.theme.typography.fontSize.base};
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const Button = styled.button`
  background: ${props => props.theme.colors.accent};
  color: white;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  font-size: ${props => props.theme.typography.fontSize.base};
  transition: all 0.2s ease;
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};

  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.accentDark};
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const Message = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-top: ${props => props.theme.spacing.md};
  ${props => {
    if (props.type === 'success') {
      return `
        background: ${props.theme.colors.success}15;
        color: ${props.theme.colors.success};
        border: 1px solid ${props.theme.colors.success};
      `;
    } else if (props.type === 'error') {
      return `
        background: ${props.theme.colors.error}15;
        color: ${props.theme.colors.error};
        border: 1px solid ${props.theme.colors.error};
      `;
    }
    return '';
  }}
`;

const DashboardExtractor = ({ onExtractSuccess }) => {
  const [dashboardUrl, setDashboardUrl] = useState('');
  const [dashboardId, setDashboardId] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);

    try {
      const result = await dashboardAPI.extractDashboard(
        dashboardUrl,
        dashboardId ? parseInt(dashboardId) : null
      );

      setMessage({
        type: 'success',
        text: `Dashboard "${result.dashboard_title}" extracted successfully! Found ${result.total_charts} charts.`,
      });

      setDashboardUrl('');
      setDashboardId('');

      // Notify parent component with dashboard data
      if (onExtractSuccess) {
        setTimeout(() => {
          onExtractSuccess({
            dashboard_id: result.dashboard_id,
            dashboard_title: result.dashboard_title,
            total_charts: result.total_charts
          });
        }, 500);
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || error.message || 'Failed to extract dashboard',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Title>Extract Dashboard</Title>
      <Form onSubmit={handleSubmit}>
        <InputGroup>
          <Label htmlFor="dashboard-url">Dashboard URL</Label>
          <Input
            id="dashboard-url"
            type="url"
            value={dashboardUrl}
            onChange={(e) => setDashboardUrl(e.target.value)}
            placeholder="https://cdp-dataview.platform.mypaytm.com/superset/dashboard/729/"
            required
          />
        </InputGroup>
        
        <InputGroup>
          <Label htmlFor="dashboard-id">Dashboard ID (Optional)</Label>
          <Input
            id="dashboard-id"
            type="number"
            value={dashboardId}
            onChange={(e) => setDashboardId(e.target.value)}
            placeholder="729"
          />
        </InputGroup>

        <Button type="submit" disabled={loading}>
          {loading ? 'Extracting...' : '→ Extract Dashboard'}
        </Button>

        {message && (
          <Message type={message.type}>{message.text}</Message>
        )}
      </Form>
    </Container>
  );
};

export default DashboardExtractor;

