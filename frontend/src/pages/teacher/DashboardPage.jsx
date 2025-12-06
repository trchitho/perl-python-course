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
  Announcement as AnnouncementIcon,
  School as SchoolIcon,
  BarChart as BarChartIcon,
  Book as BookIcon,
  Quiz as QuizIcon,
  People as PeopleIcon,
} from '@mui/icons-material';

const teacherPages = [
  {
    title: 'Courses',
    path: '/teacher/courses',
    description: 'Manage and create your courses',
    icon: <SchoolIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    title: 'Lessons',
    path: '/teacher/lessons',
    description: 'Create and organize course lessons',
    icon: <BookIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
  },
  {
    title: 'Quizzes',
    path: '/teacher/quizzes',
    description: 'Create and manage quizzes',
    icon: <QuizIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
  },
  {
    title: 'Subscribers',
    path: '/teacher/subscribers',
    description: 'View and manage your students',
    icon: <PeopleIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
  },
  {
    title: 'Announcements',
    path: '/teacher/announcements',
    description: 'Post announcements to your students',
    icon: <AnnouncementIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
  },
  {
    title: 'Grades',
    path: '/teacher/grades',
    description: 'View and manage student grades',
    icon: <BarChartIcon sx={{ fontSize: 40 }} />,
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
  },
];

const DashboardPage = () => {
  const fullname = localStorage.getItem('fullname') || 'Teacher';
  const [stats, setStats] = React.useState([
    { label: 'Total Courses', value: '0', color: '#6366f1' },
    { label: 'Active Students', value: '0', color: '#10b981' },
    { label: 'Total Lessons', value: '0', color: '#f59e0b' },
    { label: 'Avg. Score', value: '0', color: '#ec4899' },
  ]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/teacher/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats([
          { label: 'Total Courses', value: data.courses.toString(), color: '#6366f1' },
          { label: 'Active Students', value: data.students.toString(), color: '#10b981' },
          { label: 'Total Lessons', value: data.lessons.toString(), color: '#f59e0b' },
          { label: 'Avg. Score', value: data.avg_score.toFixed(1), color: '#ec4899' },
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome, {fullname}! 👨‍🏫
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your courses and engage with your students
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
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <Typography variant="body2" color="text.secondary">Loading...</Typography>
                </Box>
              ) : (
                <>
                  <Typography variant="h3" fontWeight={700} sx={{ color: stat.color, mb: 1 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" fontWeight={500}>
                    {stat.label}
                  </Typography>
                </>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3}>
        {teacherPages.map((page) => (
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
