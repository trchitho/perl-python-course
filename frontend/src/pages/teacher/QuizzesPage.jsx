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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  QuestionAnswer as QuestionIcon,
} from '@mui/icons-material';

const QuizzesPage = () => {
  const [quizzes, setQuizzes] = useState([]);
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [openQuestionsDialog, setOpenQuestionsDialog] = useState(false);
  const [editingQuiz, setEditingQuiz] = useState(null);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    lesson_id: '',
    time_limit: '',
  });

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadLessons();
      loadQuizzes();
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
      
      if (!response.ok) throw new Error('Failed to load courses');
      
      const data = await response.json();
      setCourses(data);
      if (data.length > 0) {
        setSelectedCourse(data[0].id);
      }
    } catch (err) {
      setError('Không thể tải courses: ' + err.message);
    }
  };

  const loadLessons = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/courses/${selectedCourse}/lessons`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to load lessons');
      
      const data = await response.json();
      setLessons(data);
    } catch (err) {
      console.error('Failed to load lessons:', err);
    }
  };

  const loadQuizzes = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/courses/${selectedCourse}/quizzes`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to load quizzes');
      
      const data = await response.json();
      setQuizzes(data);
    } catch (err) {
      setError('Không thể tải quizzes: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (quiz = null) => {
    if (quiz) {
      setEditingQuiz(quiz);
      setFormData({
        title: quiz.title,
        description: quiz.description || '',
        lesson_id: quiz.lesson_id || '',
        time_limit: quiz.time_limit || '',
      });
    } else {
      setEditingQuiz(null);
      setFormData({
        title: '',
        description: '',
        lesson_id: '',
        time_limit: '30',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingQuiz(null);
  };

  const handleSubmit = async () => {
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      
      const url = editingQuiz
        ? `http://localhost:5000/api/teacher/quizzes/${editingQuiz.id}`
        : `http://localhost:5000/api/teacher/courses/${selectedCourse}/quizzes`;
      
      const method = editingQuiz ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) throw new Error('Failed to save quiz');
      
      setSuccess(editingQuiz ? 'Quiz đã được cập nhật!' : 'Quiz đã được tạo!');
      handleCloseDialog();
      loadQuizzes();
    } catch (err) {
      setError('Lỗi: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa quiz này? Tất cả questions và results sẽ bị xóa.')) return;
    
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/quizzes/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete quiz');
      
      setSuccess('Quiz đã được xóa!');
      loadQuizzes();
    } catch (err) {
      setError('Không thể xóa quiz: ' + err.message);
    }
  };

  const handleOpenImportDialog = (quiz) => {
    setSelectedQuiz(quiz);
    setUploadFile(null);
    setOpenImportDialog(true);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.docx') && !file.name.endsWith('.doc')) {
        setError('Chỉ chấp nhận file Word (.doc, .docx)');
        return;
      }
      setUploadFile(file);
      setError('');
    }
  };

  const handleOpenQuestionsDialog = async (quiz) => {
    setSelectedQuiz(quiz);
    setOpenQuestionsDialog(true);
    await loadQuestions(quiz.id);
  };

  const loadQuestions = async (quizId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/quizzes/${quizId}/questions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to load questions');
      
      const data = await response.json();
      setQuestions(data);
    } catch (err) {
      setError('Không thể tải questions: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const [questionForm, setQuestionForm] = useState({
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_option: 'A',
  });
  const [editingQuestion, setEditingQuestion] = useState(null);

  const handleAddQuestion = async () => {
    try {
      setError('');
      const token = localStorage.getItem('token');
      
      const response = await fetch(`http://localhost:5000/api/teacher/quizzes/${selectedQuiz.id}/questions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionForm),
      });
      
      if (!response.ok) throw new Error('Failed to add question');
      
      setSuccess('Câu hỏi đã được thêm!');
      setQuestionForm({
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: 'A',
      });
      loadQuestions(selectedQuiz.id);
      loadQuizzes(); // Reload to update question count
    } catch (err) {
      setError('Lỗi: ' + err.message);
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Bạn có chắc muốn xóa câu hỏi này?')) return;
    
    try {
      setError('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/questions/${questionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete question');
      
      setSuccess('Câu hỏi đã được xóa!');
      loadQuestions(selectedQuiz.id);
      loadQuizzes();
    } catch (err) {
      setError('Không thể xóa câu hỏi: ' + err.message);
    }
  };

  const handleImportQuestions = async () => {
    if (!uploadFile) {
      setError('Vui lòng chọn file Word');
      return;
    }

    try {
      setUploading(true);
      setError('');
      const token = localStorage.getItem('token');

      // Step 1: Upload file
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('subfolder', 'quizzes');
      formData.append('compress', 'false');

      const uploadResponse = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!uploadResponse.ok) throw new Error('Failed to upload file');

      const uploadResult = await uploadResponse.json();

      // Step 2: Import questions from uploaded file
      // Use URL if from Cloudinary, otherwise use path
      const filePath = uploadResult.storage === 'cloudinary' 
        ? (uploadResult.secure_url || uploadResult.url)
        : uploadResult.path;

      const importResponse = await fetch(`http://localhost:5000/api/teacher/quizzes/${selectedQuiz.id}/import`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_path: filePath,
        }),
      });

      if (!importResponse.ok) {
        const errorData = await importResponse.json();
        throw new Error(errorData.error || 'Failed to import questions');
      }

      const importResult = await importResponse.json();
      setSuccess(`Đã import ${importResult.count} câu hỏi thành công!`);
      setOpenImportDialog(false);
      loadQuizzes();
    } catch (err) {
      setError('Lỗi import: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  if (courses.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No courses yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Please create a course first before adding quizzes.
          </Typography>
        </Paper>
      </Container>
    );
  }

  // Removed lesson requirement - quizzes can be created without lessons

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Quizzes
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Select Course</InputLabel>
            <Select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              label="Select Course"
            >
              {courses.map((course) => (
                <MenuItem key={course.id} value={course.id}>
                  {course.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            disabled={!selectedCourse}
          >
            Create Quiz
          </Button>
        </Box>
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

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : quizzes.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No quizzes yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create your first quiz for this course!
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Quiz
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Quiz Title</TableCell>
                <TableCell>Lesson</TableCell>
                <TableCell>Questions</TableCell>
                <TableCell>Time Limit</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {quizzes.map((quiz) => (
                <TableRow key={quiz.id}>
                  <TableCell>{quiz.id}</TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {quiz.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {quiz.description ? quiz.description.substring(0, 50) + '...' : 'No description'}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {quiz.lesson_title || 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={quiz.total_questions || 0} size="small" color="primary" />
                  </TableCell>
                  <TableCell>{quiz.time_limit ? `${quiz.time_limit} min` : 'No limit'}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenQuestionsDialog(quiz)}
                      title="Manage Questions"
                      color="success"
                    >
                      <QuestionIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenImportDialog(quiz)}
                      title="Import from Word"
                      color="primary"
                    >
                      <UploadIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(quiz)}
                      title="Edit Quiz"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(quiz.id)}
                      color="error"
                      title="Delete Quiz"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingQuiz ? 'Edit Quiz' : 'Create New Quiz'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Quiz Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Lesson (Optional)</InputLabel>
            <Select
              value={formData.lesson_id}
              onChange={(e) => setFormData({ ...formData, lesson_id: e.target.value })}
              label="Lesson (Optional)"
            >
              <MenuItem value="">
                <em>No lesson (General quiz)</em>
              </MenuItem>
              {lessons.map((lesson) => (
                <MenuItem key={lesson.id} value={lesson.id}>
                  {lesson.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Time Limit (minutes)"
            type="number"
            value={formData.time_limit}
            onChange={(e) => setFormData({ ...formData, time_limit: e.target.value })}
            margin="normal"
            helperText="Leave empty for no time limit"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!formData.title}>
            {editingQuiz ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Questions Dialog */}
      <Dialog open={openImportDialog} onClose={() => setOpenImportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Import Questions from Word File
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload a Word document (.doc, .docx) with questions in the following format:
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, mt: 2, mb: 2, bgcolor: 'grey.50' }}>
              <Typography variant="caption" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
{`Question 1: What is Python?
A. A snake
B. A programming language
C. A framework
D. A database
Answer: B

Question 2: What is Flask?
A. A bottle
B. A web framework
C. A database
D. A language
Answer: B`}
              </Typography>
            </Paper>
            
            <input
              type="file"
              accept=".doc,.docx"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="word-file-input"
            />
            <label htmlFor="word-file-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
                fullWidth
                disabled={uploading}
              >
                Select Word File
              </Button>
            </label>

            {uploadFile && (
              <Box sx={{ mt: 2 }}>
                <Alert severity="info">
                  Selected: {uploadFile.name}
                </Alert>
              </Box>
            )}

            {uploading && (
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <CircularProgress size={24} />
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Uploading and importing...
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenImportDialog(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleImportQuestions} 
            variant="contained" 
            disabled={!uploadFile || uploading}
          >
            Import
          </Button>
        </DialogActions>
      </Dialog>

      {/* Manage Questions Dialog */}
      <Dialog 
        open={openQuestionsDialog} 
        onClose={() => setOpenQuestionsDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Manage Questions: {selectedQuiz?.title}
          <Chip label={`${questions.length} questions`} size="small" sx={{ ml: 2 }} />
        </DialogTitle>
        <DialogContent>
          <Tabs value={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tab label="Add Question" />
            <Tab label={`View All (${questions.length})`} disabled />
          </Tabs>

          {/* Add Question Form */}
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Question"
              value={questionForm.question_text}
              onChange={(e) => setQuestionForm({ ...questionForm, question_text: e.target.value })}
              margin="normal"
              multiline
              rows={2}
              required
            />
            
            <TextField
              fullWidth
              label="Option A"
              value={questionForm.option_a}
              onChange={(e) => setQuestionForm({ ...questionForm, option_a: e.target.value })}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Option B"
              value={questionForm.option_b}
              onChange={(e) => setQuestionForm({ ...questionForm, option_b: e.target.value })}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Option C"
              value={questionForm.option_c}
              onChange={(e) => setQuestionForm({ ...questionForm, option_c: e.target.value })}
              margin="normal"
              required
            />
            
            <TextField
              fullWidth
              label="Option D"
              value={questionForm.option_d}
              onChange={(e) => setQuestionForm({ ...questionForm, option_d: e.target.value })}
              margin="normal"
              required
            />
            
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Correct Answer</InputLabel>
              <Select
                value={questionForm.correct_option}
                onChange={(e) => setQuestionForm({ ...questionForm, correct_option: e.target.value })}
                label="Correct Answer"
              >
                <MenuItem value="A">A</MenuItem>
                <MenuItem value="B">B</MenuItem>
                <MenuItem value="C">C</MenuItem>
                <MenuItem value="D">D</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              onClick={handleAddQuestion}
              fullWidth
              sx={{ mt: 2 }}
              disabled={!questionForm.question_text || !questionForm.option_a || !questionForm.option_b || !questionForm.option_c || !questionForm.option_d}
            >
              Add Question
            </Button>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Questions List */}
          <Typography variant="h6" gutterBottom>
            Current Questions
          </Typography>
          
          {questions.length === 0 ? (
            <Alert severity="info">No questions yet. Add your first question above!</Alert>
          ) : (
            <List>
              {questions.map((q, index) => (
                <Paper key={q.id} sx={{ p: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2" fontWeight="bold">
                        Question {index + 1}:
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
                        {q.question_text}
                      </Typography>
                      
                      <Box sx={{ pl: 2 }}>
                        <Typography variant="body2" color={q.correct_option === 'A' ? 'success.main' : 'text.primary'}>
                          A. {q.option_a} {q.correct_option === 'A' && '✓'}
                        </Typography>
                        <Typography variant="body2" color={q.correct_option === 'B' ? 'success.main' : 'text.primary'}>
                          B. {q.option_b} {q.correct_option === 'B' && '✓'}
                        </Typography>
                        <Typography variant="body2" color={q.correct_option === 'C' ? 'success.main' : 'text.primary'}>
                          C. {q.option_c} {q.correct_option === 'C' && '✓'}
                        </Typography>
                        <Typography variant="body2" color={q.correct_option === 'D' ? 'success.main' : 'text.primary'}>
                          D. {q.option_d} {q.correct_option === 'D' && '✓'}
                        </Typography>
                      </Box>
                    </Box>
                    
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteQuestion(q.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Paper>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenQuestionsDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default QuizzesPage;
