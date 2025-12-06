import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { getProgress } from '../../../services/studentAPI';

const ProgressPage = () => {
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getProgress();
      setProgress(data);
    } catch (err) {
      setError('Không thể tải progress: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateOverallProgress = () => {
    if (progress.length === 0) return 0;
    const total = progress.reduce((sum, p) => sum + (p.progress_percent || 0), 0);
    return Math.round(total / progress.length);
  };

  const totalLessonsCompleted = progress.reduce((sum, p) => sum + (p.lessons_completed || 0), 0);
  const totalLessons = progress.reduce((sum, p) => sum + (p.total_lessons || 0), 0);

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        My Progress
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Overall Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SchoolIcon sx={{ mr: 1, color: '#6366f1' }} />
                <Typography variant="h6">Courses</Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {progress.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enrolled
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckIcon sx={{ mr: 1, color: '#10b981' }} />
                <Typography variant="h6">Lessons</Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {totalLessonsCompleted}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed of {totalLessons}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon sx={{ mr: 1, color: '#f59e0b' }} />
                <Typography variant="h6">Overall</Typography>
              </Box>
              <Typography variant="h3" sx={{ color: '#f59e0b' }}>
                {calculateOverallProgress()}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average Progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Course Progress */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Course Progress
      </Typography>

      {progress.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            You haven't enrolled in any courses yet.
          </Typography>
        </Paper>
      ) : (
        progress.map((item) => (
          <Paper key={item.course_id} sx={{ p: 3, mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {item.course_title || 'Course'}
              </Typography>
              <Typography variant="h5" color="primary" fontWeight="bold">
                {item.progress_percent || 0}%
              </Typography>
            </Box>

            <LinearProgress
              variant="determinate"
              value={item.progress_percent || 0}
              sx={{
                height: 12,
                borderRadius: 6,
                mb: 2,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 6,
                  background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
                },
              }}
            />

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary">
                Lessons: {item.lessons_completed || 0} / {item.total_lessons || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Quizzes: {item.completed_quizzes || 0}
              </Typography>
            </Box>
          </Paper>
        ))
      )}
    </Container>
  );
};

export default ProgressPage;
