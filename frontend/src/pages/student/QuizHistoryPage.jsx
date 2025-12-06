import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
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
  Chip,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  CheckCircle as PassIcon,
  Cancel as FailIcon,
} from '@mui/icons-material';
import { getQuizHistory } from '../../../services/studentAPI';

const QuizHistoryPage = () => {
  const location = useLocation();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
    }
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getQuizHistory();
      setHistory(data);
    } catch (err) {
      setError('Không thể tải quiz history: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreIcon = (score) => {
    return score >= 60 ? <PassIcon /> : <FailIcon />;
  };

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
        Quiz History
      </Typography>

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage('')}>
          {successMessage}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {history.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            You haven't taken any quizzes yet.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Quiz</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Lesson</TableCell>
                <TableCell align="center">Score</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="center">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.quiz_title || 'N/A'}</TableCell>
                  <TableCell>{item.course_title || 'N/A'}</TableCell>
                  <TableCell>{item.lesson_title || '-'}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${item.score}%`}
                      color={getScoreColor(item.score)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {item.submitted_at
                      ? new Date(item.submitted_at).toLocaleDateString()
                      : 'N/A'}
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      {getScoreIcon(item.score)}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {history.length > 0 && (
        <Box sx={{ mt: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            Summary
          </Typography>
          <Typography variant="body2">
            Total Quizzes: {history.length}
          </Typography>
          <Typography variant="body2">
            Average Score:{' '}
            {history.length > 0
              ? (
                  history.reduce((sum, item) => sum + (item.score || 0), 0) /
                  history.length
                ).toFixed(1)
              : 0}
            %
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default QuizHistoryPage;
