import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import {
  PlayCircleOutline as PlayIcon,
  CheckCircle as CheckIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import { getCourseDetail } from '../../../services/studentAPI';

const LessonsPage = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (courseId) {
      loadCourse();
    }
  }, [courseId]);

  const loadCourse = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getCourseDetail(courseId);
      setCourse(data);
      setLessons(data.lessons || []);
    } catch (err) {
      setError('Không thể tải lessons: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLessonClick = (lessonId) => {
    navigate(`/student/lesson/${lessonId}`);
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/student/courses')}
        sx={{ mb: 2 }}
      >
        Back to Courses
      </Button>

      <Typography variant="h4" gutterBottom>
        {course?.name || 'Course Lessons'}
      </Typography>

      {course?.description && (
        <Typography variant="body1" color="text.secondary" paragraph>
          {course.description}
        </Typography>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mt: 3 }}>
        <List>
          {lessons.length === 0 ? (
            <ListItem>
              <ListItemText primary="No lessons available yet" />
            </ListItem>
          ) : (
            lessons.map((lesson, index) => (
              <ListItemButton
                key={lesson.id}
                onClick={() => handleLessonClick(lesson.id)}
                sx={{
                  borderBottom: index < lessons.length - 1 ? '1px solid #e0e0e0' : 'none',
                }}
              >
                <ListItemIcon>
                  {lesson.completed ? (
                    <CheckIcon color="success" />
                  ) : (
                    <PlayIcon color="primary" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body1">
                        Lesson {index + 1}: {lesson.title}
                      </Typography>
                      {lesson.completed && (
                        <Chip label="Completed" size="small" color="success" />
                      )}
                    </Box>
                  }
                  secondary={lesson.description}
                />
              </ListItemButton>
            ))
          )}
        </List>
      </Paper>
    </Container>
  );
};

export default LessonsPage;
