import React, { useState, useEffect } from 'react';
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
  Chip,
  Box,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';

const CoursesPage = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editDialog, setEditDialog] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [editData, setEditData] = useState({
    name: '',
    description: '',
    category: '',
    duration: '',
  });

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/admin/courses', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load courses');
      }
      
      const data = await response.json();
      setCourses(data);
    } catch (err) {
      setError('Không thể tải danh sách courses: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa course này? Tất cả lessons và enrollments liên quan sẽ bị ảnh hưởng.')) return;
    
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/admin/courses/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete course');
      }
      
      setSuccess('Course đã được xóa thành công!');
      loadCourses();
    } catch (err) {
      setError('Không thể xóa course: ' + err.message);
    }
  };

  const handleEdit = (course) => {
    setSelectedCourse(course);
    setEditData({
      name: course.name,
      description: course.description || '',
      category: course.category || '',
      duration: course.duration || '',
    });
    setEditDialog(true);
  };

  const handleSaveEdit = async () => {
    try {
      setError('');
      setSuccess('');
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/admin/courses/${selectedCourse.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update course');
      }
      
      setSuccess('Course đã được cập nhật!');
      setEditDialog(false);
      loadCourses();
    } catch (err) {
      setError('Không thể cập nhật course: ' + err.message);
    }
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Quản Lý Courses
        </Typography>
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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Course Name</TableCell>
              <TableCell>Teacher</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Students</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {courses.map((course) => (
              <TableRow key={course.id}>
                <TableCell>{course.id}</TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" fontWeight="medium">
                      {course.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {course.description ? course.description.substring(0, 50) + '...' : 'No description'}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{course.teacher_name || 'N/A'}</TableCell>
                <TableCell>{course.category || 'N/A'}</TableCell>
                <TableCell>{course.duration ? `${course.duration}h` : 'N/A'}</TableCell>
                <TableCell>
                  <Chip label={course.enrollment_count || 0} size="small" color="primary" />
                </TableCell>
                <TableCell>
                  {course.created_at ? new Date(course.created_at).toLocaleDateString() : 'N/A'}
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleEdit(course)}
                    title="Edit"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(course.id)}
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

      {/* Edit Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Course</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Course Name"
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            margin="normal"
            multiline
            rows={4}
          />
          <TextField
            fullWidth
            label="Category"
            value={editData.category}
            onChange={(e) => setEditData({ ...editData, category: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Duration (hours)"
            type="number"
            value={editData.duration}
            onChange={(e) => setEditData({ ...editData, duration: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CoursesPage;
