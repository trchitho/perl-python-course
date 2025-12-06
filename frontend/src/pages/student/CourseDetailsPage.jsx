import React, { useState, useEffect, Fragment } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Divider,
  Grid,
  LinearProgress,
} from '@mui/material';
import {
  PlayCircle as PlayCircleIcon,
  CheckCircle as CheckCircleIcon,
  Lock as LockIcon,
  Book as BookIcon,
  School as SchoolIcon,
  AccessTime as AccessTimeIcon,
  Person as PersonIcon,
  Quiz as QuizIcon,
} from '@mui/icons-material';
import { getCourseDetail, listCourseQuizzes } from '../../../services/studentAPI';

const CourseDetailsPage = () => {
  const [searchParams] = useSearchParams();
  const courseId = searchParams.get('course_id');
  const navigate = useNavigate();

  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (courseId) {
      fetchCourseDetails();
    } else {
      setError('Không tìm thấy khóa học');
      setLoading(false);
    }
  }, [courseId]);

  const fetchCourseDetails = async () => {
    try {
      setLoading(true);
      const courseData = await getCourseDetail(courseId);
      setCourse(courseData);
      
      // Extract lessons from course data
      if (courseData.lessons) {
        setLessons(courseData.lessons || []);
      }
      
      // Fetch quizzes
      try {
        const quizzesData = await listCourseQuizzes(courseId);
        setQuizzes(quizzesData || []);
      } catch (err) {
        console.error('Error fetching quizzes:', err);
      }
    } catch (err) {
      setError(err.message || 'Không thể tải thông tin khóa học');
    } finally {
      setLoading(false);
    }
  };

  const handleLessonClick = (lessonId) => {
    navigate(`/student/lesson/${lessonId}`);
  };

  const handleQuizClick = (quizId) => {
    navigate(`/student/quiz/${quizId}`);
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (!course) {
    return (
      <Container maxWidth="lg">
        <Alert severity="info" sx={{ mt: 3 }}>
          Không tìm thấy khóa học
        </Alert>
      </Container>
    );
  }

  const completedLessons = lessons.filter(l => l.completed).length;
  const progress = lessons.length > 0 ? (completedLessons / lessons.length) * 100 : 0;

  return (
    <Container maxWidth="lg">
      {/* Course Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          variant="outlined"
          onClick={() => navigate('/student/courses')}
          sx={{ mb: 2 }}
        >
          ← Quay lại danh sách khóa học
        </Button>
        
        <Paper
          elevation={0}
          sx={{
            p: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: 3,
          }}
        >
          <Typography variant="h4" fontWeight={700} gutterBottom>
            {course.name || course.title}
          </Typography>
          {course.description && (
            <Typography variant="body1" sx={{ mb: 2, opacity: 0.95 }}>
              {course.description}
            </Typography>
          )}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2 }}>
            {course.category && (
              <Chip
                label={course.category}
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
              />
            )}
            {course.duration && (
              <Chip
                icon={<AccessTimeIcon />}
                label={course.duration}
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
              />
            )}
            {course.status && (
              <Chip
                label={course.status}
                sx={{
                  bgcolor: course.status === 'active' ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.2)',
                  color: 'white',
                }}
              />
            )}
          </Box>
        </Paper>
      </Box>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          {/* Progress Section */}
          {lessons.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" fontWeight={600}>
                    Tiến độ học tập
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {completedLessons} / {lessons.length} bài học
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    bgcolor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 5,
                      background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    },
                  }}
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {Math.round(progress)}% hoàn thành
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* Lessons Section */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
                Danh sách bài học
              </Typography>
              {lessons.length > 0 ? (
                <List>
                  {lessons.map((lesson, index) => (
                    <Fragment key={lesson.id}>
                      <ListItem disablePadding>
                        <ListItemButton onClick={() => handleLessonClick(lesson.id)}>
                          <ListItemIcon>
                            {lesson.completed ? (
                              <CheckCircleIcon color="success" />
                            ) : (
                              <PlayCircleIcon color="primary" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1" fontWeight={500}>
                                  Bài {index + 1}: {lesson.title}
                                </Typography>
                                {lesson.completed && (
                                  <Chip label="Đã hoàn thành" size="small" color="success" />
                                )}
                              </Box>
                            }
                            secondary={lesson.description}
                          />
                          <Button variant="outlined" size="small">
                            Học ngay
                          </Button>
                        </ListItemButton>
                      </ListItem>
                      {index < lessons.length - 1 && <Divider />}
                    </Fragment>
                  ))}
                </List>
              ) : (
                <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'background.default' }}>
                  <BookIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body1" color="text.secondary">
                    Chưa có bài học nào
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>

          {/* Quizzes Section */}
          {quizzes.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
                  Bài kiểm tra
                </Typography>
                <List>
                  {quizzes.map((quiz, index) => (
                    <Fragment key={quiz.id}>
                      <ListItem disablePadding>
                        <ListItemButton onClick={() => handleQuizClick(quiz.id)}>
                          <ListItemIcon>
                            <QuizIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Typography variant="subtitle1" fontWeight={500}>
                                {quiz.title || `Quiz ${index + 1}`}
                              </Typography>
                            }
                            secondary={quiz.description || `Bài kiểm tra số ${index + 1}`}
                          />
                          <Button variant="contained" size="small" color="primary">
                            Làm bài
                          </Button>
                        </ListItemButton>
                      </ListItem>
                      {index < quizzes.length - 1 && <Divider />}
                    </Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Thông tin khóa học
              </Typography>
              <Box sx={{ mt: 2 }}>
                {course.teacher_name && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <PersonIcon color="action" />
                    <Typography variant="body2">
                      <strong>Giảng viên:</strong> {course.teacher_name}
                    </Typography>
                  </Box>
                )}
                {course.duration && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <AccessTimeIcon color="action" />
                    <Typography variant="body2">
                      <strong>Thời lượng:</strong> {course.duration}
                    </Typography>
                  </Box>
                )}
                {course.category && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <SchoolIcon color="action" />
                    <Typography variant="body2">
                      <strong>Danh mục:</strong> {course.category}
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CourseDetailsPage;
