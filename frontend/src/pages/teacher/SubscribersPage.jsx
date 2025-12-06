import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Box,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

const SubscribersPage = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [subscribers, setSubscribers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentProgress, setStudentProgress] = useState(null);
  const [progressDialogOpen, setProgressDialogOpen] = useState(false);
  const [progressLoading, setProgressLoading] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadSubscribers();
    }
  }, [selectedCourse]);

  const loadCourses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/teacher/courses', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load courses');
      }
      
      const data = await response.json();
      setCourses(data);
      
      // Auto-select first course if available
      if (data.length > 0 && !selectedCourse) {
        setSelectedCourse(data[0].id);
      }
    } catch (err) {
      setError('Không thể tải danh sách courses: ' + err.message);
    }
  };

  const loadSubscribers = async () => {
    if (!selectedCourse) return;
    
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/courses/${selectedCourse}/subscribers`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load subscribers');
      }
      
      const data = await response.json();
      setSubscribers(data);
    } catch (err) {
      setError('Không thể tải danh sách subscribers: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (enrollmentId) => {
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/subscribers/${enrollmentId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve enrollment');
      }
      
      setSuccess('Enrollment đã được approve!');
      loadSubscribers();
    } catch (err) {
      setError('Không thể approve enrollment: ' + err.message);
    }
  };

  const handleReject = async (enrollmentId) => {
    if (!window.confirm('Bạn có chắc muốn reject enrollment này?')) return;
    
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      
      const response = await fetch(`http://localhost:5000/api/teacher/subscribers/${enrollmentId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject enrollment');
      }
      
      setSuccess('Enrollment đã được reject!');
      loadSubscribers();
    } catch (err) {
      setError('Không thể reject enrollment: ' + err.message);
    }
  };

  const handleRemove = async (enrollmentId) => {
    if (!window.confirm('Bạn có chắc muốn xóa student này khỏi course? Hành động này không thể hoàn tác.')) return;
    
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/subscribers/${enrollmentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to remove subscriber');
      }
      
      setSuccess('Student đã được xóa khỏi course!');
      loadSubscribers();
    } catch (err) {
      setError('Không thể xóa subscriber: ' + err.message);
    }
  };

  const handleViewProgress = async (student) => {
    setSelectedStudent(student);
    setProgressDialogOpen(true);
    setProgressLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      
      // Load progress data
      const progressResponse = await fetch(
        `http://localhost:5000/api/teacher/courses/${selectedCourse}/progress/${student.user_id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      // Load quiz results
      const scoresResponse = await fetch(
        `http://localhost:5000/api/teacher/courses/${selectedCourse}/scores`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      let progressData = null;
      let quizResults = [];
      
      if (progressResponse.ok) {
        progressData = await progressResponse.json();
      }
      
      if (scoresResponse.ok) {
        const scoresData = await scoresResponse.json();
        // Filter results for this student
        quizResults = scoresData.results?.filter(r => r.user_id === student.user_id) || [];
      }
      
      setStudentProgress({
        progress: progressData,
        quizResults: quizResults,
      });
    } catch (err) {
      setError('Không thể tải progress data: ' + err.message);
    } finally {
      setProgressLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const filteredSubscribers = subscribers.filter(sub => {
    // Status filter
    if (statusFilter !== 'all' && sub.status !== statusFilter) {
      return false;
    }
    
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        sub.fullname?.toLowerCase().includes(query) ||
        sub.email?.toLowerCase().includes(query)
      );
    }
    
    return true;
  });

  const stats = {
    total: subscribers.length,
    pending: subscribers.filter(s => s.status === 'pending').length,
    approved: subscribers.filter(s => s.status === 'approved').length,
    rejected: subscribers.filter(s => s.status === 'rejected').length,
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Quản Lý Subscribers
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadSubscribers}
          disabled={!selectedCourse}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* Course Selection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth>
          <InputLabel>Chọn Course</InputLabel>
          <Select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            label="Chọn Course"
          >
            {courses.map((course) => (
              <MenuItem key={course.id} value={course.id}>
                {course.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      {selectedCourse && (
        <>
          {/* Statistics Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Tổng Số
                  </Typography>
                  <Typography variant="h4">
                    {stats.total}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Pending
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {stats.pending}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Approved
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.approved}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Rejected
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {stats.rejected}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Filters */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Tìm kiếm theo tên hoặc email"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Nhập tên hoặc email..."
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Lọc theo Status</InputLabel>
                  <Select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    label="Lọc theo Status"
                  >
                    <MenuItem value="all">Tất cả</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="rejected">Rejected</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {/* Subscribers Table */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : filteredSubscribers.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                {searchQuery || statusFilter !== 'all' 
                  ? 'Không tìm thấy kết quả phù hợp'
                  : 'Chưa có student nào enroll vào course này'}
              </Typography>
            </Paper>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Tên Student</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredSubscribers.map((subscriber) => (
                    <TableRow key={subscriber.id}>
                      <TableCell>{subscriber.id}</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {subscriber.fullname || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {subscriber.email || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={subscriber.status}
                          color={getStatusColor(subscriber.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                          {subscriber.status === 'pending' && (
                            <>
                              <Button
                                size="small"
                                variant="contained"
                                color="success"
                                startIcon={<ApproveIcon />}
                                onClick={() => handleApprove(subscriber.id)}
                              >
                                Approve
                              </Button>
                              <Button
                                size="small"
                                variant="outlined"
                                color="error"
                                startIcon={<RejectIcon />}
                                onClick={() => handleReject(subscriber.id)}
                              >
                                Reject
                              </Button>
                            </>
                          )}
                          {subscriber.status === 'approved' && (
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewProgress(subscriber)}
                              title="Xem Progress"
                            >
                              <ViewIcon />
                            </IconButton>
                          )}
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRemove(subscriber.id)}
                            title="Xóa khỏi course"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}

      {/* Progress Dialog */}
      <Dialog
        open={progressDialogOpen}
        onClose={() => setProgressDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Chi Tiết Progress - {selectedStudent?.fullname}
        </DialogTitle>
        <DialogContent>
          {progressLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              {/* Progress Info */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Tiến Độ Học Tập
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography color="text.secondary">
                        Lessons Completed:
                      </Typography>
                      <Typography variant="h6">
                        {studentProgress?.progress?.lessons_completed || 0} / {studentProgress?.progress?.total_lessons || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography color="text.secondary">
                        Progress:
                      </Typography>
                      <Typography variant="h6">
                        {studentProgress?.progress?.progress_percent || 0}%
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Quiz Results */}
              <Typography variant="h6" gutterBottom>
                Kết Quả Quiz
              </Typography>
              {studentProgress?.quizResults?.length > 0 ? (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Quiz</TableCell>
                        <TableCell>Lesson</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Submitted At</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {studentProgress.quizResults.map((result, index) => (
                        <TableRow key={index}>
                          <TableCell>{result.quiz_title}</TableCell>
                          <TableCell>{result.lesson_title || 'N/A'}</TableCell>
                          <TableCell>
                            <Chip
                              label={`${result.score}%`}
                              color={result.score >= 70 ? 'success' : result.score >= 50 ? 'warning' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {result.submitted_at ? new Date(result.submitted_at).toLocaleString('vi-VN') : 'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    Student chưa hoàn thành quiz nào
                  </Typography>
                </Paper>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProgressDialogOpen(false)}>
            Đóng
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SubscribersPage;
