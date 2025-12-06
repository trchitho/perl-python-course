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
  Chip,
  Box,
  Alert,
  CircularProgress,
  TablePagination,
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';
import { listEnrollments, approveEnrollment } from '../../../services/adminAPI';

const EnrollmentsPage = () => {
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false,
  });

  useEffect(() => {
    loadEnrollments();
  }, [page, perPage]);

  const loadEnrollments = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await listEnrollments(page, perPage);
      setEnrollments(data.enrollments || data);
      if (data.pagination) {
        setPagination(data.pagination);
      }
    } catch (err) {
      setError('Không thể tải danh sách enrollments: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      setError('');
      await approveEnrollment(id);
      loadEnrollments();
    } catch (err) {
      setError('Không thể approve enrollment: ' + err.message);
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm('Bạn có chắc muốn reject enrollment này?')) return;
    
    try {
      setError('');
      // Call reject API
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/admin/enrollments/${id}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject enrollment');
      }
      
      loadEnrollments();
    } catch (err) {
      setError('Không thể reject enrollment: ' + err.message);
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

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Quản Lý Enrollments
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Student</TableCell>
              <TableCell>Course</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Payment</TableCell>
              <TableCell>Enrolled Date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {enrollments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                    Không có enrollments
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              enrollments.map((enrollment) => (
                <TableRow key={enrollment.id}>
                  <TableCell>{enrollment.id}</TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">{enrollment.student_name || 'N/A'}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {enrollment.email || ''}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{enrollment.course_name || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip
                      label={enrollment.status}
                      color={getStatusColor(enrollment.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={enrollment.payment_status || 'pending'}
                      color={enrollment.payment_status === 'paid' ? 'success' : 'warning'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {enrollment.enrolled_date ? new Date(enrollment.enrolled_date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      {enrollment.status === 'pending' && (
                        <>
                          <Button
                            size="small"
                            variant="contained"
                            color="success"
                            startIcon={<ApproveIcon />}
                            onClick={() => handleApprove(enrollment.id)}
                          >
                            Approve
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            color="error"
                            startIcon={<RejectIcon />}
                            onClick={() => handleReject(enrollment.id)}
                          >
                            Reject
                          </Button>
                        </>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={pagination.total}
          page={page - 1}
          onPageChange={(event, newPage) => setPage(newPage + 1)}
          rowsPerPage={perPage}
          onRowsPerPageChange={(event) => {
            setPerPage(parseInt(event.target.value, 10));
            setPage(1);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
          labelRowsPerPage="Số dòng mỗi trang:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} của ${count}`}
        />
      </TableContainer>
    </Container>
  );
};

export default EnrollmentsPage;
