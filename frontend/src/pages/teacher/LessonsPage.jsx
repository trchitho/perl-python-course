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
  ToggleButton,
  ToggleButtonGroup,
  Link,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  CloudUpload as UploadIcon,
  YouTube as YouTubeIcon,
  VideoLibrary as VideoIcon,
} from '@mui/icons-material';

const LessonsPage = () => {
  const [lessons, setLessons] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingLesson, setEditingLesson] = useState(null);
  const [videoType, setVideoType] = useState('youtube'); // 'youtube' or 'upload'
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    video_url: '',
    content: '',
    order_index: '',
  });

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadLessons();
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
      setLoading(true);
      setError('');
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
      setError('Không thể tải lessons: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (lesson = null) => {
    if (lesson) {
      setEditingLesson(lesson);
      setFormData({
        title: lesson.title,
        description: lesson.description || '',
        video_url: lesson.video_url || '',
        content: lesson.content || '',
        order_index: lesson.order_index || '',
      });
      // Detect video type
      if (lesson.video_url) {
        if (lesson.video_url.includes('youtube.com') || lesson.video_url.includes('youtu.be')) {
          setVideoType('youtube');
        } else {
          setVideoType('upload');
        }
      }
    } else {
      setEditingLesson(null);
      setFormData({
        title: '',
        description: '',
        video_url: '',
        content: '',
        order_index: lessons.length + 1,
      });
      setVideoType('youtube');
    }
    setUploadFile(null);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingLesson(null);
    setUploadFile(null);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate video file
      const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'];
      if (!validTypes.includes(file.type)) {
        setError('Chỉ chấp nhận file video (MP4, AVI, MOV, WMV, WebM)');
        return;
      }
      // Check file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        setError('File quá lớn. Tối đa 100MB');
        return;
      }
      setUploadFile(file);
      setError('');
    }
  };

  const handleSubmit = async () => {
    try {
      setError('');
      setSuccess('');
      setUploading(true);
      const token = localStorage.getItem('token');
      
      let videoUrl = formData.video_url;

      // If uploading video file
      if (videoType === 'upload' && uploadFile) {
        // Upload file first
        const uploadFormData = new FormData();
        uploadFormData.append('file', uploadFile);
        uploadFormData.append('subfolder', 'videos');
        uploadFormData.append('compress', 'false');

        const uploadResponse = await fetch('http://localhost:5000/api/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: uploadFormData,
        });

        if (!uploadResponse.ok) throw new Error('Failed to upload video');

        const uploadResult = await uploadResponse.json();
        // Use URL from Cloudinary or local storage
        if (uploadResult.storage === 'cloudinary') {
          videoUrl = uploadResult.secure_url || uploadResult.url;
        } else {
          videoUrl = uploadResult.url || `/uploads/${uploadResult.path}`;
        }
      }

      // Save lesson
      const lessonData = {
        title: formData.title,
        description: formData.description,
        video_url: videoUrl,
        content: formData.content,
        order_index: formData.order_index,
      };

      const url = editingLesson
        ? `http://localhost:5000/api/teacher/lessons/${editingLesson.id}`
        : `http://localhost:5000/api/teacher/courses/${selectedCourse}/lessons`;
      
      const method = editingLesson ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(lessonData),
      });
      
      if (!response.ok) throw new Error('Failed to save lesson');
      
      setSuccess(editingLesson ? 'Lesson đã được cập nhật!' : 'Lesson đã được tạo!');
      handleCloseDialog();
      loadLessons();
    } catch (err) {
      setError('Lỗi: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa lesson này?')) return;
    
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/teacher/lessons/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete lesson');
      
      setSuccess('Lesson đã được xóa!');
      loadLessons();
    } catch (err) {
      setError('Không thể xóa lesson: ' + err.message);
    }
  };

  const getVideoType = (url) => {
    if (!url) return null;
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return 'YouTube';
    }
    return 'Uploaded Video';
  };

  if (courses.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No courses yet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Please create a course first before adding lessons.
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Lessons
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
            Create Lesson
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
      ) : lessons.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No lessons yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create your first lesson for this course!
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Lesson
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Video</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {lessons.map((lesson) => (
                <TableRow key={lesson.id}>
                  <TableCell>
                    <Chip label={lesson.order_index || '-'} size="small" />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {lesson.title}
                      </Typography>
                      {lesson.description && (
                        <Typography variant="caption" color="text.secondary">
                          {lesson.description.substring(0, 60)}...
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {lesson.video_url ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {lesson.video_url.includes('youtube') ? (
                          <YouTubeIcon color="error" fontSize="small" />
                        ) : (
                          <VideoIcon color="primary" fontSize="small" />
                        )}
                        <Typography variant="caption">
                          {getVideoType(lesson.video_url)}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="caption" color="text.secondary">
                        No video
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(lesson)}
                      title="Edit"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(lesson.id)}
                      color="error"
                      title="Delete"
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
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingLesson ? 'Edit Lesson' : 'Create New Lesson'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Lesson Title"
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
            rows={2}
          />

          {/* Video Type Selector */}
          <Box sx={{ mt: 3, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Video Source
            </Typography>
            <ToggleButtonGroup
              value={videoType}
              exclusive
              onChange={(e, newType) => {
                if (newType) {
                  setVideoType(newType);
                  setUploadFile(null);
                  setFormData({ ...formData, video_url: '' });
                }
              }}
              fullWidth
            >
              <ToggleButton value="youtube">
                <YouTubeIcon sx={{ mr: 1 }} />
                YouTube Link
              </ToggleButton>
              <ToggleButton value="upload">
                <UploadIcon sx={{ mr: 1 }} />
                Upload Video
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* YouTube Link Input */}
          {videoType === 'youtube' && (
            <TextField
              fullWidth
              label="YouTube URL"
              value={formData.video_url}
              onChange={(e) => setFormData({ ...formData, video_url: e.target.value })}
              margin="normal"
              placeholder="https://www.youtube.com/watch?v=..."
              helperText="Paste YouTube video URL"
            />
          )}

          {/* Video Upload */}
          {videoType === 'upload' && (
            <Box sx={{ mt: 2 }}>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="video-file-input"
              />
              <label htmlFor="video-file-input">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<UploadIcon />}
                  fullWidth
                >
                  Select Video File
                </Button>
              </label>
              {uploadFile && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Selected: {uploadFile.name} ({(uploadFile.size / (1024 * 1024)).toFixed(2)} MB)
                </Alert>
              )}
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                Supported: MP4, AVI, MOV, WMV, WebM (Max 100MB)
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            label="Content / Notes"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            margin="normal"
            multiline
            rows={4}
            placeholder="Additional lesson content, notes, or instructions..."
          />

          <TextField
            fullWidth
            label="Order Index"
            type="number"
            value={formData.order_index}
            onChange={(e) => setFormData({ ...formData, order_index: e.target.value })}
            margin="normal"
            helperText="Lesson order in the course"
          />

          {uploading && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <CircularProgress size={24} />
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                {videoType === 'upload' ? 'Uploading video...' : 'Saving...'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.title || uploading || (videoType === 'upload' && !uploadFile && !editingLesson)}
          >
            {editingLesson ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LessonsPage;
