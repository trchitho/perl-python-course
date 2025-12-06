import React from 'react';
import { Link } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Box,
  Container,
  Paper,
} from '@mui/material';
import {
  BarChart as BarChartIcon,
  School as SchoolIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { getAdminStats } from '../../../services/adminAPI';

const adminPages = [
  {
    title: 'Users',
    path: '/admin/users',
    description: 'Manage user accounts and permissions',
    icon: <PeopleIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    title: 'Enrollments',
    path: '/admin/enrollments',
    description: 'Manage course enrollments and registrations',
    icon: <SchoolIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
  },
  {
    title: 'C&C Dashboard',
    path: '/admin/cc-dashboard',
    description: 'View C&C metrics and analytics',
    icon: <BarChartIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
  },
  {
    title: 'Logs',
    path: '/admin/logs',
    description: 'View system logs and audit trails',
    icon: <HistoryIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
  },
  {
    title: 'Settings',
    path: '/admin/settings',
    description: 'Configure application settings',
    icon: <SettingsIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
  },
];

const DashboardPage = () => {
  const [stats, setStats] = React.useState([
    { label: 'Total Users', value: '...', color: '#6366f1' },
    { label: 'Active Courses', value: '...', color: '#10b981' },
    { label: 'Total Enrollments', value: '...', color: '#f59e0b' },
    { label: 'System Health', value: '...', color: '#ec4899' },
  ]);
  const [loading, setLoading] = React.useState(true);
  const fullname = localStorage.getItem('fullname') || 'Admin';

  React.useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getAdminStats();
      setStats([
        { label: 'Total Users', value: data.users || 0, color: '#6366f1' },
        { label: 'Active Courses', value: data.courses || 0, color: '#10b981' },
        { label: 'Total Enrollments', value: data.enrollments || 0, color: '#f59e0b' },
        { label: 'System Health', value: '99.9%', color: '#ec4899' },
      ]);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome, {fullname}! 👨‍💼
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage the platform and monitor system performance
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                borderRadius: 3,
                background: `linear-gradient(135deg, ${stat.color}15 0%, ${stat.color}05 100%)`,
                border: `1px solid ${stat.color}20`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 24px ${stat.color}30`,
                },
              }}
            >
              <Typography variant="h3" fontWeight={700} sx={{ color: stat.color, mb: 1 }}>
                {stat.value}
              </Typography>
              <Typography variant="body2" color="text.secondary" fontWeight={500}>
                {stat.label}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
        Admin Tools
      </Typography>
      <Grid container spacing={3}>
        {adminPages.map((page) => (
          <Grid item xs={12} sm={6} md={4} key={page.title}>
            <Card
              component={Link}
              to={page.path}
              sx={{
                height: '100%',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: page.gradient,
                },
                '&:hover': {
                  transform: 'translateY(-8px)',
                  '& .card-icon': {
                    transform: 'scale(1.1) rotate(5deg)',
                  },
                },
                transition: 'all 0.3s ease',
              }}
            >
              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                <Box
                  className="card-icon"
                  sx={{
                    background: page.gradient,
                    width: 64,
                    height: 64,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    mb: 2,
                    transition: 'transform 0.3s ease',
                  }}
                >
                  {page.icon}
                </Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  {page.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {page.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default DashboardPage;
