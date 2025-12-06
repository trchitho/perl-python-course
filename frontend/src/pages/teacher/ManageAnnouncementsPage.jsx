import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Campaign as CampaignIcon,
} from '@mui/icons-material';
import { apiGet, apiPost, apiPut, apiDelete } from '../../../services/apiConfig';

const ManageAnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAnnouncement, setEditingAnnouncement] = useState(null);
  
  const [formData, setFormData] = useState({
    course_id: '',
    title: '',
    content: '',
    priority: 'normal',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [announcementsData, coursesData] = await Promise.all([
        apiGet('/announcements'),
        apiGet('/admin/courses'),
      ]);
      setAnnouncements(announcementsData);
      setCourses(coursesData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (announcement = null) => {
    if (announcement) {
      setEditingAnnouncement(announcement);
      setFormData({
        course_id: announcement.course_id || '',
        title: announcement.title,
        content: announcement.content,
        priority: announcement.priority,
      });
    } else {
      setEditingAnnouncement(null);
      setFormData({
        course_id: '',
        title: '',
        content: '',
        priority: 'normal',
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingAnnouncement(null);
    setFormData({
      course_id: '',
      title: '',
      content: '',
      priority: 'normal',
    });
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        course_id: formData.course_id || null,
      };

      if (editingAnnouncement) {
        await apiPut(`/announcements/${editingAnnouncement.id}`, payload);
        setSuccess('Cập nhật thông báo thành công!');
      } else {
        await apiPost('/announcements', payload);
        setSuccess('Tạo thông báo thành công!');
      }

      handleCloseDialog();
      loadData();
    } catch (err) {
      console.error('Failed to save announcement:', err);
      setError('Không thể lưu thông báo');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa thông báo này?')) {
      return;
    }

    try {
      await apiDelete(`/announcements/${id}`);
      setSuccess('Xóa thông báo thành công!');
      loadData();
    } catch (err) {
      console.error('Failed to delete announcement:', err);
      setError('Không thể xóa thông báo');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'normal':
        return 'info';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CampaignIcon sx={{ fontSize: 40, mr: 2, color: '#6366f1' }} />
          <Typography variant="h4" fontWeight={700}>
            Quản Lý Thông Báo
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ bgcolor: '#6366f1', '&:hover': { bgcolor: '#5558dd' } }}
        >
          Tạo Thông Báo
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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#f5f5f5' }}>
              <TableCell><strong>Tiêu đề</strong></TableCell>
              <TableCell><strong>Khóa học</strong></TableCell>
              <TableCell><strong>Độ ưu tiên</strong></TableCell>
              <TableCell><strong>Ngày tạo</strong></TableCell>
              <TableCell align="center"><strong>Thao tác</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {announcements.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography color="text.secondary">Chưa có thông báo nào</Typography>
                </TableCell>
              </TableRow>
            ) : (
              announcements.map((announcement) => (
                <TableRow key={announcement.id} hover>
                  <TableCell>{announcement.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.course_name}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={announcement.priority.toUpperCase()}
                      size="small"
                      color={getPriorityColor(announcement.priority)}
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(announcement.created_at).toLocaleDateString('vi-VN')}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleOpenDialog(announcement)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(announcement.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAnnouncement ? 'Chỉnh Sửa Thông Báo' : 'Tạo Thông Báo Mới'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Khóa học</InputLabel>
              <Select
                value={formData.course_id}
                onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                label="Khóa học"
              >
                <MenuItem value="">Tất cả khóa học</MenuItem>
                {courses.map((course) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Tiêu đề"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />

            <TextField
              fullWidth
              label="Nội dung"
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              multiline
              rows={6}
              required
            />

            <FormControl fullWidth>
              <InputLabel>Độ ưu tiên</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                label="Độ ưu tiên"
              >
                <MenuItem value="low">Thấp</MenuItem>
                <MenuItem value="normal">Bình thường</MenuItem>
                <MenuItem value="high">Cao</MenuItem>
                <MenuItem value="urgent">Khẩn cấp</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Hủy</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.title || !formData.content}
          >
            {editingAnnouncement ? 'Cập nhật' : 'Tạo'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ManageAnnouncementsPage;
