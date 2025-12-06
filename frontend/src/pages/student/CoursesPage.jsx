import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Button,
  Box,
  Chip,
  Rating,
  TextField,
  InputAdornment,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  AccessTime as AccessTimeIcon,
  Star as StarIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { useNavigate, Link } from 'react-router-dom';
import { listAllCourses, enrollCourse } from '../../../services/courseAPI';

const CoursesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [enrolling, setEnrolling] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await listAllCourses();
      setCourses(data || []);
    } catch (err) {
      setError(err.message || 'Không thể tải danh sách khóa học');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId) => {
    try {
      setEnrolling({ ...enrolling, [courseId]: true });
      await enrollCourse(courseId);
      // Refresh courses list
      await fetchCourses();
    } catch (err) {
      alert(err.message || 'Đăng ký khóa học thất bại');
    } finally {
      setEnrolling({ ...enrolling, [courseId]: false });
    }
  };

  const handleViewDetails = (courseId) => {
    navigate(`/student/course-details?course_id=${courseId}`);
  };

  const filteredCourses = courses.filter((course) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      (course.name || course.title || '').toLowerCase().includes(query) ||
      (course.description || '').toLowerCase().includes(query) ||
      (course.category || '').toLowerCase().includes(query)
    );
  });

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl">
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Khám phá Khóa học
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Khám phá các khóa học đa dạng để nâng cao kỹ năng của bạn
        </Typography>

        {/* Search Bar */}
        <TextField
          fullWidth
          placeholder="Tìm kiếm khóa học..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{
            maxWidth: 600,
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              bgcolor: 'background.paper',
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* Courses Grid */}
      {filteredCourses.length > 0 ? (
        <Grid container spacing={3}>
          {filteredCourses.map((course) => (
            <Grid item xs={12} sm={6} md={4} key={course.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                  },
                }}
              >
                <CardMedia
                  component="div"
                  sx={{
                    height: 180,
                    background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                  }}
                >
                  <SchoolIcon sx={{ fontSize: 64, opacity: 0.8 }} />
                </CardMedia>
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    {course.category && (
                      <Chip
                        label={course.category}
                        size="small"
                        sx={{
                          bgcolor: 'primary.light',
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                    )}
                    {course.status && (
                      <Chip
                        label={course.status}
                        size="small"
                        variant="outlined"
                        sx={{ fontWeight: 500 }}
                        color={course.status === 'active' ? 'success' : 'default'}
                      />
                    )}
                  </Box>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    {course.name || course.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2, minHeight: 40 }}
                  >
                    {course.description || 'Không có mô tả'}
                  </Typography>
                  {course.duration && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                      <AccessTimeIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {course.duration}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                <CardActions sx={{ p: 3, pt: 0, gap: 1 }}>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => handleViewDetails(course.id)}
                    startIcon={<PlayArrowIcon />}
                    sx={{ flex: 1 }}
                  >
                    Xem chi tiết
                  </Button>
                  {!course.enrolled && (
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => handleEnroll(course.id)}
                      disabled={enrolling[course.id]}
                      sx={{
                        flex: 1,
                        py: 1.5,
                        fontWeight: 600,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 20px rgba(102, 126, 234, 0.4)',
                        },
                        transition: 'all 0.3s ease',
                      }}
                    >
                      {enrolling[course.id] ? 'Đang đăng ký...' : 'Đăng ký ngay'}
                    </Button>
                  )}
                  {course.enrolled && (
                    <Button
                      variant="contained"
                      fullWidth
                      component={Link}
                      to={`/student/course-details?course_id=${course.id}`}
                      sx={{
                        flex: 1,
                        py: 1.5,
                        fontWeight: 600,
                        bgcolor: 'success.main',
                        '&:hover': {
                          bgcolor: 'success.dark',
                        },
                      }}
                    >
                      Vào học
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper
          sx={{
            p: 6,
            textAlign: 'center',
            borderRadius: 3,
            bgcolor: 'background.paper',
          }}
        >
          <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Không tìm thấy khóa học
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Thử điều chỉnh từ khóa tìm kiếm của bạn
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default CoursesPage;
