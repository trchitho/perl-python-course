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
  Box,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

const GradesPage = () => {
  const [courses, setCourses] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedQuiz, setSelectedQuiz] = useState('all');
  const [selectedStudent, setSelectedStudent] = useState('all');
  const [results, setResults] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadQuizzes();
      loadResults();
    }
  }, [selectedCourse]);

  useEffect(() => {
    if (selectedCourse) {
      loadResults();
    }
  }, [selectedQuiz, selectedStudent]);

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
      
      // Auto-select first course
      if (data.length > 0 && !selectedCourse) {
        setSelectedCourse(data[0].id);
      }
    } catch (err) {
      setError('Không thể tải danh sách courses: ' + err.message);
    }
  };

  const loadQuizzes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/courses/${selectedCourse}/quizzes`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load quizzes');
      }
      
      const data = await response.json();
      setQuizzes(data);
    } catch (err) {
      setError('Không thể tải danh sách quizzes: ' + err.message);
    }
  };

  const loadResults = async () => {
    if (!selectedCourse) return;
    
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/courses/${selectedCourse}/scores`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load results');
      }
      
      const data = await response.json();
      setResults(data.results || []);
      setSummary(data.summary || null);
      
      // Extract unique students
      const uniqueStudents = [...new Map(
        data.results.map(r => [r.user_id, { id: r.user_id, name: r.user_name }])
      ).values()];
      setStudents(uniqueStudents);
    } catch (err) {
      setError('Không thể tải kết quả: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = results.filter(result => {
    if (selectedQuiz !== 'all' && result.quiz_id !== parseInt(selectedQuiz)) {
      return false;
    }
    if (selectedStudent !== 'all' && result.user_id !== parseInt(selectedStudent)) {
      return false;
    }
    return true;
  });

  const calculateStats = () => {
    if (filteredResults.length === 0) {
      return {
        totalAttempts: 0,
        averageScore: 0,
        highestScore: 0,
        lowestScore: 0,
        passRate: 0,
      };
    }

    const scores = filteredResults.map(r => r.score);
    const passThreshold = 70;
    const passedCount = scores.filter(s => s >= passThreshold).length;

    return {
      totalAttempts: filteredResults.length,
      averageScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2),
      highestScore: Math.max(...scores),
      lowestScore: Math.min(...scores),
      passRate: ((passedCount / scores.length) * 100).toFixed(1),
    };
  };

  const stats = calculateStats();

  const exportToCSV = () => {
    if (filteredResults.length === 0) {
      alert('Không có dữ liệu để export');
      return;
    }

    // Create CSV content
    const headers = ['Student Name', 'Quiz Title', 'Lesson', 'Score', 'Submitted At'];
    const rows = filteredResults.map(result => [
      result.user_name,
      result.quiz_title,
      result.lesson_title || 'N/A',
      result.score,
      result.submitted_at ? new Date(result.submitted_at).toLocaleString('vi-VN') : 'N/A',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    const courseName = courses.find(c => c.id === selectedCourse)?.name || 'course';
    const fileName = `grades_${courseName}_${new Date().toISOString().split('T')[0]}.csv`;
    
    link.setAttribute('href', url);
    link.setAttribute('download', fileName);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 70) return 'info';
    if (score >= 50) return 'warning';
    return 'error';
  };

  const getScoreIcon = (score) => {
    if (score >= 70) return <TrendingUpIcon fontSize="small" />;
    return <TrendingDownIcon fontSize="small" />;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Grades & Reports
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadResults}
            disabled={!selectedCourse}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={exportToCSV}
            disabled={filteredResults.length === 0}
          >
            Export CSV
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
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
            <Grid item xs={12} sm={6} md={2.4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    Total Attempts
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalAttempts}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    Average Score
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.averageScore}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    Highest Score
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.highestScore}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    Lowest Score
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {stats.lowestScore}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" variant="body2" gutterBottom>
                    Pass Rate
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {stats.passRate}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Filters */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Filter by Quiz</InputLabel>
                  <Select
                    value={selectedQuiz}
                    onChange={(e) => setSelectedQuiz(e.target.value)}
                    label="Filter by Quiz"
                  >
                    <MenuItem value="all">All Quizzes</MenuItem>
                    {quizzes.map((quiz) => (
                      <MenuItem key={quiz.id} value={quiz.id}>
                        {quiz.title}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Filter by Student</InputLabel>
                  <Select
                    value={selectedStudent}
                    onChange={(e) => setSelectedStudent(e.target.value)}
                    label="Filter by Student"
                  >
                    <MenuItem value="all">All Students</MenuItem>
                    {students.map((student) => (
                      <MenuItem key={student.id} value={student.id}>
                        {student.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>

          {/* Results Table */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : filteredResults.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <AssessmentIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Chưa có kết quả quiz nào
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Students chưa submit quiz hoặc không có quiz nào trong course này
              </Typography>
            </Paper>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Quiz</TableCell>
                    <TableCell>Lesson</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Submitted At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredResults.map((result, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {result.user_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {result.quiz_title}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {result.lesson_title || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getScoreIcon(result.score)}
                          <Chip
                            label={`${result.score}%`}
                            color={getScoreColor(result.score)}
                            size="small"
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.score >= 70 ? 'Passed' : 'Failed'}
                          color={result.score >= 70 ? 'success' : 'error'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {result.submitted_at 
                            ? new Date(result.submitted_at).toLocaleString('vi-VN')
                            : 'N/A'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Summary Info */}
          {summary && filteredResults.length > 0 && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Course Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography color="text.secondary" variant="body2">
                    Unique Students:
                  </Typography>
                  <Typography variant="h6">
                    {summary.students || students.length}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography color="text.secondary" variant="body2">
                    Total Quizzes:
                  </Typography>
                  <Typography variant="h6">
                    {summary.quizzes || quizzes.length}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography color="text.secondary" variant="body2">
                    Total Attempts:
                  </Typography>
                  <Typography variant="h6">
                    {summary.attempts || filteredResults.length}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography color="text.secondary" variant="body2">
                    Course Average:
                  </Typography>
                  <Typography variant="h6">
                    {summary.average_score || stats.averageScore}%
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}
        </>
      )}
    </Container>
  );
};

export default GradesPage;
