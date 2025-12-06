import React, { useState, useEffect } from 'react';
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
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  Chat as ChatIcon,
  School as SchoolIcon,
  Book as BookIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Quiz as QuizIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { getStudentStats } from '../../../services/studentAPI';

const studentPages = [
  {
    title: 'Courses',
    path: '/student/courses',
    description: 'Browse and enroll in available courses',
    icon: <SchoolIcon sx={{ fontSize: 40 }} />,
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    title: 'My Courses',
    path: '/student/courses',
    description: 'View your enrolled courses and lessons',
    icon: <BookIcon sx={{ fontSize: 40 }} />,
    color: '#10b981',
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
  },
  {
    title: 'Quiz History',
    path: '/student/quiz-history',
    description: 'Review your past quiz results',
    icon: <HistoryIcon sx={{ fontSize: 40 }} />,
    color: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
  },
  {
    title: 'Progress',
    path: '/student/progress',
    description: 'Track your learning progress',
    icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
    color: '#ec4899',
    gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
  },
  {
    title: 'Chatbot',
    path: '/student/chatbot',
    description: 'Get help from AI assistant',
    icon: <ChatIcon sx={{ fontSize: 40 }} />,
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
  },
  {
    title: 'Profile',
    path: '/student/profile',
    description: 'View and edit your profile',
    icon: <PersonIcon sx={{ fontSize: 40 }} />,
    color: '#64748b',
    gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
  },
];

const DashboardPage = () => {
  const [stats, setStats] = useState([
    { label: 'Courses Enrolled', value: '...', color: '#6366f1' },
    { label: 'Lessons Completed', value: '...', color: '#10b981' },
    { label: 'Quizzes Taken', value: '...', color: '#f59e0b' },
    { label: 'Average Score', value: '...', color: '#ec4899' },
  ]);
  const [progressValues, setProgressValues] = useState({ completion: 0, performance: 0 });
  const [loading, setLoading] = useState(true);
  const fullname = localStorage.getItem('fullname') || 'Student';

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getStudentStats();
      
      setStats([
        { label: 'Courses Enrolled', value: data.courses, color: '#6366f1' },
        { label: 'Lessons Completed', value: data.lessons, color: '#10b981' },
        { label: 'Quizzes Taken', value: data.quizzes, color: '#f59e0b' },
        { label: 'Average Score', value: data.avgScore, color: '#ec4899' },
      ]);
      
      // Calculate average progress
      if (data.progressData && data.progressData.length > 0) {
        const avgProgress = data.progressData.reduce((sum, p) => 
          sum + (p.progress_percent || 0), 0) / data.progressData.length;
        setProgressValues({
          completion: Math.round(avgProgress),
          performance: parseInt(data.avgScore) || 0
        });
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl">
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome back, {fullname}! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Continue your learning journey and achieve your goals
        </Typography>
      </Box>

      {/* Stats Cards */}
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

      {/* Quick Actions */}
      <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {studentPages.map((page) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={page.title}>
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
                    color: page.color,
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

      {/* Progress Overview */}
      <Paper
        elevation={0}
        sx={{
          p: 4,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="h5" fontWeight={600} gutterBottom>
          Your Progress
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" fontWeight={500}>
                Course Completion
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {progressValues.completion}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progressValues.completion}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: '#e2e8f0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
                },
              }}
            />
          </Box>
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" fontWeight={500}>
                Overall Performance
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {progressValues.performance}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progressValues.performance}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: '#e2e8f0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                },
              }}
            />
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default DashboardPage;
