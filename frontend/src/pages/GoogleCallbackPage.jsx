import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Container, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';

const GoogleCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        setError('Đăng nhập Google bị hủy');
        setProcessing(false);
        return;
      }

      if (!code) {
        setError('Không nhận được mã xác thực từ Google');
        setProcessing(false);
        return;
      }

      try {
        // Send code to backend - include all params
        const params = new URLSearchParams(window.location.search);
        const response = await fetch(
          `http://localhost:5000/api/auth/google/callback?${params.toString()}`,
          {
            method: 'GET',
          }
        );

        const data = await response.json();
        console.log('Google OAuth Response:', data);

        if (!response.ok) {
          throw new Error(data.message || 'Đăng nhập thất bại');
        }

        if (!data.token) {
          throw new Error('Không nhận được token từ server');
        }

        // Save token and user info
        localStorage.setItem('token', data.token);
        localStorage.setItem('role', data.role);
        localStorage.setItem('fullname', data.fullname);
        localStorage.setItem('email', data.email);
        if (data.avatar_url) {
          localStorage.setItem('avatar_url', data.avatar_url);
        }

        console.log('Redirecting to dashboard...', data.role);

        // Small delay to ensure localStorage is saved
        setTimeout(() => {
          // Redirect based on role
          if (data.role === 'admin') {
            navigate('/admin/dashboard', { replace: true });
          } else if (data.role === 'teacher') {
            navigate('/teacher/dashboard', { replace: true });
          } else {
            navigate('/student/dashboard', { replace: true });
          }
        }, 100);
      } catch (err) {
        console.error('Google OAuth Error:', err);
        setError(err.message);
        setProcessing(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {processing ? (
            <>
              <CircularProgress size={60} sx={{ mb: 3 }} />
              <Typography variant="h5" gutterBottom>
                Đang xử lý đăng nhập...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vui lòng đợi trong giây lát
              </Typography>
            </>
          ) : (
            <>
              {error && (
                <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Typography variant="body1" sx={{ mt: 2 }}>
                <a href="/login">Quay lại trang đăng nhập</a>
              </Typography>
            </>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default GoogleCallbackPage;
