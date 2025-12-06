import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  CheckCircle as CheckIcon,
  NavigateNext as NextIcon,
  NavigateBefore as PrevIcon,
  Download as DownloadIcon,
  PlayCircleOutline as VideoIcon,
} from '@mui/icons-material';
import { getLessonDetail, listLessonQuizzes } from '../../../services/studentAPI';

// Helper function to convert YouTube URL to embed format
const getYouTubeEmbedUrl = (url) => {
  if (!url) return null;
  
  // Already in embed format
  if (url.includes('/embed/')) {
    return url;
  }
  
  // Convert watch?v= to embed/
  // https://www.youtube.com/watch?v=VIDEO_ID -> https://www.youtube.com/embed/VIDEO_ID
  const watchMatch = url.match(/[?&]v=([^&]+)/);
  if (watchMatch) {
    return `https://www.youtube.com/embed/${watchMatch[1]}`;
  }
  
  // Convert youtu.be short links
  // https://youtu.be/VIDEO_ID -> https://www.youtube.com/embed/VIDEO_ID
  const shortMatch = url.match(/youtu\.be\/([^?]+)/);
  if (shortMatch) {
    return `https://www.youtube.com/embed/${shortMatch[1]}`;
  }
  
  // Return original URL if not YouTube or already valid
  return url;
};

const LessonDetailPage = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [videoLoadTime, setVideoLoadTime] = useState(null);

  useEffect(() => {
    // Track component render time
    const renderStart = Date.now();
    
    if (lessonId) {
      loadLesson();
      loadQuizzes();
    }
  }, [lessonId]);

  const loadLesson = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getLessonDetail(lessonId);
      setLesson(data);
    } catch (err) {
      setError('Không thể tải bài học: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadQuizzes = async () => {
    try {
      console.log('Loading quizzes for lesson:', lessonId);
      const data = await listLessonQuizzes(lessonId);
      console.log('Quizzes loaded:', data);
      setQuizzes(data || []);
    } catch (err) {
      console.error('Không thể tải quizzes:', err);
      setQuizzes([]);
    }
  };

  const handleBack = () => {
    if (lesson?.course_id) {
      navigate(`/student/course-details?course_id=${lesson.course_id}`);
    } else {
      navigate('/student/courses');
    }
  };

  // Get embed URL for video
  const videoEmbedUrl = lesson?.video_url ? getYouTubeEmbedUrl(lesson.video_url) : null;

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<BackIcon />} onClick={handleBack} sx={{ mt: 2 }}>
          Quay lại
        </Button>
      </Container>
    );
  }

  if (!lesson) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">Không tìm thấy bài học</Alert>
        <Button startIcon={<BackIcon />} onClick={handleBack} sx={{ mt: 2 }}>
          Quay lại
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Button
        startIcon={<BackIcon />}
        onClick={handleBack}
        sx={{ mb: 3 }}
      >
        Quay lại khóa học
      </Button>

      <Paper sx={{ p: 4 }}>
        {/* Lesson Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h4" fontWeight={700}>
              {lesson.title}
            </Typography>
            {lesson.completed && (
              <Chip
                icon={<CheckIcon />}
                label="Đã hoàn thành"
                color="success"
                size="small"
              />
            )}
          </Box>
          {lesson.course_title && (
            <Typography variant="subtitle1" color="text.secondary">
              Khóa học: {lesson.course_title}
            </Typography>
          )}
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Video Section */}
        {videoEmbedUrl && (
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <VideoIcon color="primary" />
              <Typography variant="h6" fontWeight={600}>
                Video bài học
              </Typography>
            </Box>
            <Paper elevation={2} sx={{ overflow: 'hidden', borderRadius: 2 }}>
              <Box
                component="iframe"
                src={videoEmbedUrl}
                sx={{
                  width: '100%',
                  height: '500px',
                  border: 'none',
                }}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </Paper>
          </Box>
        )}

        {/* File Attachment */}
        {lesson.file_url && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              📎 Tài liệu đính kèm
            </Typography>
            <Button
              variant="outlined"
              href={lesson.file_url}
              target="_blank"
              startIcon={<DownloadIcon />}
              sx={{ mt: 1 }}
            >
              Tải xuống tài liệu
            </Button>
          </Box>
        )}

        {/* Lesson Content */}
        <Box sx={{ mb: 4 }}>
          {lesson.description && (
            <Typography variant="body1" sx={{ mb: 3, fontSize: '1.1rem', lineHeight: 1.8 }}>
              {lesson.description}
            </Typography>
          )}

          {lesson.content && (
            <Box
              sx={{
                '& h1, & h2, & h3': { mt: 3, mb: 2, fontWeight: 600 },
                '& p': { mb: 2, lineHeight: 1.7 },
                '& ul, & ol': { mb: 2, pl: 3 },
                '& li': { mb: 1 },
                '& code': {
                  bgcolor: '#f5f5f5',
                  p: 0.5,
                  borderRadius: 1,
                  fontFamily: 'monospace',
                },
                '& pre': {
                  bgcolor: '#f5f5f5',
                  p: 2,
                  borderRadius: 2,
                  overflow: 'auto',
                },
              }}
              dangerouslySetInnerHTML={{ __html: lesson.content }}
            />
          )}

          {!lesson.content && !lesson.description && !lesson.video_url && (
            <Alert severity="info">
              Nội dung bài học đang được cập nhật
            </Alert>
          )}
        </Box>

        {/* Quizzes Section */}
        {quizzes.length > 0 && (
          <>
            <Divider sx={{ mb: 3 }} />
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
                📝 Bài kiểm tra
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Hoàn thành các bài kiểm tra để củng cố kiến thức
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {quizzes.map((quiz, index) => (
                  <Paper
                    key={quiz.id}
                    elevation={1}
                    sx={{
                      p: 3,
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                          {quiz.title}
                        </Typography>
                        {quiz.description && (
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {quiz.description}
                          </Typography>
                        )}
                        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                          {quiz.total_questions && (
                            <Chip
                              label={`${quiz.total_questions} câu hỏi`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                          {quiz.time_limit && (
                            <Chip
                              label={`${quiz.time_limit} phút`}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          )}
                        </Box>
                      </Box>
                      <Button
                        variant="contained"
                        onClick={() => navigate(`/student/quiz/${quiz.id}`)}
                        sx={{
                          ml: 2,
                          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                          },
                        }}
                      >
                        Làm bài
                      </Button>
                    </Box>
                  </Paper>
                ))}
              </Box>
            </Box>
          </>
        )}

        {/* Navigation Buttons */}
        <Divider sx={{ mb: 3 }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            startIcon={<PrevIcon />}
            onClick={() => {
              // Navigate to previous lesson if available
              if (lesson.prev_lesson_id) {
                navigate(`/student/lesson/${lesson.prev_lesson_id}`);
              }
            }}
            disabled={!lesson.prev_lesson_id}
          >
            Bài trước
          </Button>
          <Button
            variant="contained"
            endIcon={<NextIcon />}
            onClick={() => {
              // Navigate to next lesson if available
              if (lesson.next_lesson_id) {
                navigate(`/student/lesson/${lesson.next_lesson_id}`);
              } else {
                handleBack();
              }
            }}
          >
            {lesson.next_lesson_id ? 'Bài tiếp theo' : 'Hoàn thành'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default LessonDetailPage;
