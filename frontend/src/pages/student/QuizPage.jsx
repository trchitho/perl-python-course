import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Button,
  Box,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Timer as TimerIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { getQuiz, submitQuiz } from '../../../services/studentAPI';

const QuizPage = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState(null);

  useEffect(() => {
    if (quizId) {
      loadQuiz();
      // Load saved answers from localStorage
      const saved = localStorage.getItem(`quiz_${quizId}_answers`);
      if (saved) {
        try {
          const savedAnswers = JSON.parse(saved);
          setAnswers(savedAnswers);
          console.log('Restored answers from autosave');
        } catch (e) {
          console.error('Failed to restore answers:', e);
        }
      }
    }
  }, [quizId]);

  // Autosave answers every 10 seconds
  useEffect(() => {
    if (!quizId || Object.keys(answers).length === 0) return;

    const autosaveTimer = setInterval(() => {
      localStorage.setItem(`quiz_${quizId}_answers`, JSON.stringify(answers));
      console.log('Autosaved answers');
    }, 10000); // Save every 10 seconds

    return () => clearInterval(autosaveTimer);
  }, [quizId, answers]);

  // Save on answer change (debounced by the interval above)
  useEffect(() => {
    if (quizId && Object.keys(answers).length > 0) {
      localStorage.setItem(`quiz_${quizId}_answers`, JSON.stringify(answers));
    }
  }, [answers, quizId]);

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  const loadQuiz = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getQuiz(quizId);
      setQuiz(data);
      if (data.time_limit) {
        setTimeLeft(data.time_limit * 60); // Convert minutes to seconds
      }
    } catch (err) {
      setError('Không thể tải quiz: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({
      ...answers,
      [questionId]: answer,
    });
  };

  const handleSubmit = async () => {
    if (submitting) return;

    try {
      setSubmitting(true);
      setError('');
      const result = await submitQuiz(quizId, answers);
      
      // Clear autosaved data after successful submission
      localStorage.removeItem(`quiz_${quizId}_answers`);
      
      navigate('/student/quiz-history', {
        state: { message: `Quiz submitted! Score: ${result.score}%` }
      });
    } catch (err) {
      setError('Không thể submit quiz: ' + err.message);
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const answeredCount = Object.keys(answers).length;
  const totalQuestions = quiz?.questions?.length || 0;
  const progress = totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0;

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          {quiz?.title || 'Quiz'}
        </Typography>
        {timeLeft !== null && (
          <Chip
            icon={<TimerIcon />}
            label={formatTime(timeLeft)}
            color={timeLeft < 60 ? 'error' : 'primary'}
            sx={{ fontSize: '1.1rem', py: 2 }}
          />
        )}
      </Box>

      {quiz?.description && (
        <Typography variant="body1" color="text.secondary" paragraph>
          {quiz.description}
        </Typography>
      )}

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Progress: {answeredCount} / {totalQuestions} questions answered
          </Typography>
          <Chip 
            label="Auto-saving" 
            size="small" 
            color="success" 
            variant="outlined"
            sx={{ fontSize: '0.75rem' }}
          />
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {quiz?.questions?.map((question, index) => (
        <Paper key={question.id} sx={{ p: 3, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Question {index + 1}
          </Typography>
          <Typography variant="body1" paragraph>
            {question.question_text}
          </Typography>

          <FormControl component="fieldset">
            <RadioGroup
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            >
              {question.option_a && (
                <FormControlLabel value="A" control={<Radio />} label={`A. ${question.option_a}`} />
              )}
              {question.option_b && (
                <FormControlLabel value="B" control={<Radio />} label={`B. ${question.option_b}`} />
              )}
              {question.option_c && (
                <FormControlLabel value="C" control={<Radio />} label={`C. ${question.option_c}`} />
              )}
              {question.option_d && (
                <FormControlLabel value="D" control={<Radio />} label={`D. ${question.option_d}`} />
              )}
            </RadioGroup>
          </FormControl>
        </Paper>
      ))}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="outlined"
          onClick={() => navigate(-1)}
          disabled={submitting}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          startIcon={<SendIcon />}
          onClick={handleSubmit}
          disabled={submitting || answeredCount === 0}
        >
          {submitting ? 'Submitting...' : 'Submit Quiz'}
        </Button>
      </Box>
    </Container>
  );
};

export default QuizPage;
