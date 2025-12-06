import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  LinearProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  Grid,
  Divider,
} from '@mui/material';
import {
  Timer as TimerIcon,
  CheckCircle as CheckIcon,
  School as SchoolIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { apiGet, apiPost } from '../../../services/apiConfig';

const PlacementTestPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('intro'); // intro, test, result
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes

  useEffect(() => {
    if (step === 'test' && timeLeft > 0) {
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
    }
  }, [step, timeLeft]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiGet('/placement-test/questions');
      setQuestions(data.questions);
      setStep('test');
    } catch (err) {
      setError('Không thể tải câu hỏi: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({
      ...answers,
      [questionId]: answer
    });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      
      const data = await apiPost('/placement-test/submit', { answers });
      setResult(data);
      setStep('result');
    } catch (err) {
      setError('Không thể nộp bài: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'Beginner': 'success',
      'Intermediate': 'warning',
      'Advanced': 'error'
    };
    return colors[difficulty] || 'default';
  };

  // Intro Screen
  if (step === 'intro') {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <SchoolIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Placement Test
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Đánh giá trình độ IT của bạn
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Thông tin bài test:
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      Số câu hỏi
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      30 câu
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      Thời gian
                    </Typography>
                    <Typography variant="h5" fontWeight={600}>
                      30 phút
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" paragraph>
              <strong>Cấu trúc bài test:</strong>
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip label="10 câu Beginner (1 điểm)" color="success" />
              <Chip label="10 câu Intermediate (2 điểm)" color="warning" />
              <Chip label="10 câu Advanced (3 điểm)" color="error" />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Tổng điểm tối đa: 60 điểm
            </Typography>
          </Box>

          <Alert severity="info" sx={{ mb: 3 }}>
            Bài test này sẽ giúp chúng tôi đánh giá trình độ IT của bạn và đề xuất lộ trình học phù hợp.
          </Alert>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={loadQuestions}
            disabled={loading}
          >
            {loading ? 'Đang tải...' : 'Bắt đầu làm bài'}
          </Button>
        </Paper>
      </Container>
    );
  }

  // Test Screen
  if (step === 'test' && questions.length > 0) {
    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    const answeredCount = Object.keys(answers).length;

    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box>
              <Typography variant="h6">
                Câu {currentQuestion + 1}/{questions.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Đã trả lời: {answeredCount}/{questions.length}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TimerIcon color={timeLeft < 300 ? 'error' : 'action'} />
              <Typography 
                variant="h6" 
                color={timeLeft < 300 ? 'error' : 'inherit'}
              >
                {formatTime(timeLeft)}
              </Typography>
            </Box>
          </Box>

          {/* Progress */}
          <LinearProgress variant="determinate" value={progress} sx={{ mb: 3 }} />

          {/* Question */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={question.difficulty} 
                color={getDifficultyColor(question.difficulty)} 
                size="small" 
              />
              <Chip label={question.category} size="small" variant="outlined" />
              <Chip label={`${question.points} điểm`} size="small" />
            </Box>

            <Typography variant="h6" sx={{ mb: 3 }}>
              {question.question}
            </Typography>

            <FormControl component="fieldset" fullWidth>
              <RadioGroup
                value={answers[question.id] || ''}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              >
                {Object.entries(question.options).map(([key, value]) => (
                  <Paper
                    key={key}
                    variant="outlined"
                    sx={{
                      p: 2,
                      mb: 1,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' },
                      bgcolor: answers[question.id] === key ? 'action.selected' : 'transparent'
                    }}
                    onClick={() => handleAnswerChange(question.id, key)}
                  >
                    <FormControlLabel
                      value={key}
                      control={<Radio />}
                      label={`${key}. ${value}`}
                      sx={{ width: '100%', m: 0 }}
                    />
                  </Paper>
                ))}
              </RadioGroup>
            </FormControl>
          </Box>

          {/* Navigation */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
            >
              Câu trước
            </Button>

            <Box sx={{ display: 'flex', gap: 1 }}>
              {currentQuestion < questions.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleNext}
                >
                  Câu tiếp
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="success"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? 'Đang nộp bài...' : 'Nộp bài'}
                </Button>
              )}
            </Box>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Paper>
      </Container>
    );
  }

  // Result Screen
  if (step === 'result' && result) {
    const recommendation = result.recommendation;

    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <CheckIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Hoàn thành!
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Kết quả placement test của bạn
            </Typography>
          </Box>

          {/* Score */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h2" fontWeight={700} color="primary">
              {result.score}/{result.max_score}
            </Typography>
            <Typography variant="h6" color="text.secondary">
              {result.percentage}% - {result.correct_answers}/{result.total_questions} câu đúng
            </Typography>
          </Box>

          {/* Level */}
          <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingIcon sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h5" fontWeight={600}>
                    {recommendation.title}
                  </Typography>
                  <Typography variant="body2">
                    {recommendation.description}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Khóa học đề xuất:
            </Typography>
            <Grid container spacing={1}>
              {recommendation.suggested_courses.map((course, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Chip 
                    label={course} 
                    color="primary" 
                    variant="outlined"
                    sx={{ width: '100%' }}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" paragraph>
              <strong>Lộ trình học:</strong> {recommendation.learning_path}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Thời gian ước tính:</strong> {recommendation.estimated_time}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              fullWidth
              onClick={() => navigate('/student/courses')}
            >
              Xem khóa học
            </Button>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate('/student/dashboard')}
            >
              Về Dashboard
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center' }}>
        <Typography>Đang tải...</Typography>
      </Box>
    </Container>
  );
};

export default PlacementTestPage;
