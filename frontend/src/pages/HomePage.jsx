import React from 'react';
import { Box, Typography, Button, Container, Grid, Card, CardContent, CardActions } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import {
  School as SchoolIcon,
  AutoAwesome as AutoAwesomeIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';

const HomePage = () => {
  const navigate = useNavigate();
  const features = [
    {
      icon: <SchoolIcon sx={{ fontSize: 48 }} />,
      title: 'Interactive Courses',
      description: 'Engage with comprehensive courses designed by expert instructors',
      color: '#6366f1',
    },
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 48 }} />,
      title: 'AI-Powered Learning',
      description: 'Get personalized assistance with our intelligent chatbot',
      color: '#ec4899',
    },
    {
      icon: <PeopleIcon sx={{ fontSize: 48 }} />,
      title: 'Expert Teachers',
      description: 'Learn from experienced educators passionate about teaching',
      color: '#10b981',
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
      title: 'Track Progress',
      description: 'Monitor your learning journey with detailed analytics',
      color: '#f59e0b',
    },
  ];

  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const fullname = localStorage.getItem('fullname') || 'User';

  const handleLogout = () => {
    // Xóa tất cả thông tin từ localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('fullname');
    localStorage.removeItem('email');
    // Sử dụng replace thay vì navigate để không thể back lại
    navigate('/login', { replace: true });
    // Reload page để đảm bảo state được reset hoàn toàn
    window.location.reload();
  };

  const getDashboardPath = () => {
    if (role === 'admin') return '/admin/dashboard';
    if (role === 'teacher') return '/teacher/dashboard';
    return '/student/dashboard';
  };
  
  return (
    <Box sx={{ pb: !token ? 4 : 0 }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          borderRadius: 3,
          mb: 6,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
            opacity: 0.3,
          },
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
            <Typography
              variant="h2"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 800,
                mb: 2,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
              }}
            >
              {token ? `Welcome back, ${fullname}! 👋` : 'Welcome to E-Learning Platform'}
            </Typography>
            <Typography
              variant="h5"
              sx={{
                mb: 4,
                opacity: 0.95,
                maxWidth: '700px',
                mx: 'auto',
                fontSize: { xs: '1.1rem', md: '1.5rem' },
              }}
            >
              {token 
                ? 'Continue your learning journey and explore new courses'
                : 'Your journey to mastering new skills starts here. Learn at your own pace with expert guidance.'
              }
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              {token ? (
                <>
                  <Button
                    variant="contained"
                    size="large"
                    component={Link}
                    to={getDashboardPath()}
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      '&:hover': {
                        bgcolor: 'rgba(255, 255, 255, 0.9)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 20px rgba(0,0,0,0.2)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    Go to Dashboard
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleLogout}
                    startIcon={<LogoutIcon />}
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      '&:hover': {
                        borderColor: 'white',
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        transform: 'translateY(-2px)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="contained"
                    size="large"
                    component={Link}
                    to="/login"
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      '&:hover': {
                        bgcolor: 'rgba(255, 255, 255, 0.9)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 20px rgba(0,0,0,0.2)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    Get Started
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    component={Link}
                    to="/login"
                    sx={{
                      borderColor: 'white',
                      color: 'white',
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      '&:hover': {
                        borderColor: 'white',
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        transform: 'translateY(-2px)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    Learn More
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg">
        <Typography
          variant="h4"
          component="h2"
          textAlign="center"
          gutterBottom
          sx={{ mb: 1, fontWeight: 700 }}
        >
          Why Choose Us?
        </Typography>
        <Typography
          variant="body1"
          color="text.secondary"
          textAlign="center"
          sx={{ mb: 6 }}
        >
          Discover what makes our platform the best choice for your learning journey
        </Typography>

        <Grid container spacing={4} sx={{ mb: 8 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  textAlign: 'center',
                  p: 3,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: `0 12px 24px ${feature.color}33`,
                  },
                }}
              >
                <Box
                  sx={{
                    color: feature.color,
                    mb: 2,
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  {feature.icon}
                </Box>
                <CardContent sx={{ flexGrow: 1, px: 0 }}>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* CTA Section - Only show when not logged in */}
        {!token && (
          <Box
            sx={{
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              borderRadius: 3,
              p: 6,
              textAlign: 'center',
              color: 'white',
              mb: 4,
            }}
          >
            <Typography variant="h4" gutterBottom fontWeight={700}>
              Ready to Start Learning?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.95 }}>
              Join thousands of students already learning with us
            </Typography>
            <Button
              variant="contained"
              size="large"
              component={Link}
              to="/login"
              sx={{
                bgcolor: 'white',
                color: 'secondary.main',
                px: 5,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 20px rgba(0,0,0,0.2)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              Sign Up Now
            </Button>
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default HomePage;
