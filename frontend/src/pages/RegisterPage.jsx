import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link as MuiLink,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { PersonAdd as RegisterIcon } from '@mui/icons-material';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullname: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.fullname || !formData.email || !formData.password) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }

    if (formData.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fullname: formData.fullname,
          email: formData.email,
          password: formData.password,
          role: formData.role,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Đăng ký thất bại');
      }

      // Registration successful
      alert('Đăng ký thành công! Vui lòng đăng nhập.');
      navigate('/login');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <RegisterIcon sx={{ fontSize: 30, color: 'white' }} />
          </Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Đăng Ký
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Tạo tài khoản mới để bắt đầu học tập
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Họ và Tên"
            name="fullname"
            value={formData.fullname}
            onChange={handleChange}
            margin="normal"
            required
            autoFocus
          />

          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            margin="normal"
            required
          />

          <TextField
            fullWidth
            label="Mật khẩu"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            margin="normal"
            required
            helperText="Ít nhất 6 ký tự"
          />

          <TextField
            fullWidth
            label="Xác nhận mật khẩu"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            margin="normal"
            required
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Vai trò</InputLabel>
            <Select
              name="role"
              value={formData.role}
              onChange={handleChange}
              label="Vai trò"
            >
              <MenuItem value="student">Học viên (Student)</MenuItem>
              <MenuItem value="teacher">Giảng viên (Teacher)</MenuItem>
            </Select>
          </FormControl>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            sx={{
              mt: 3,
              mb: 2,
              py: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
              },
            }}
          >
            {loading ? 'Đang đăng ký...' : 'Đăng Ký'}
          </Button>

          <Box sx={{ position: 'relative', my: 3 }}>
            <Box
              sx={{
                position: 'absolute',
                top: '50%',
                left: 0,
                right: 0,
                height: '1px',
                bgcolor: 'divider',
              }}
            />
            <Typography
              variant="body2"
              sx={{
                position: 'relative',
                textAlign: 'center',
                bgcolor: 'background.paper',
                display: 'inline-block',
                px: 2,
                left: '50%',
                transform: 'translateX(-50%)',
                color: 'text.secondary',
              }}
            >
              HOẶC
            </Typography>
          </Box>

          <Button
            fullWidth
            variant="outlined"
            size="large"
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:5000/api/auth/google/url');
                const data = await response.json();
                if (data.auth_url) {
                  window.location.href = data.auth_url;
                } else {
                  setError('Google Sign-In không khả dụng');
                }
              } catch (err) {
                setError('Không thể kết nối với Google');
              }
            }}
            sx={{
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              borderColor: '#4285f4',
              color: '#4285f4',
              '&:hover': {
                borderColor: '#357ae8',
                bgcolor: 'rgba(66, 133, 244, 0.04)',
              },
            }}
            startIcon={
              <Box
                component="img"
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt="Google"
                sx={{ width: 20, height: 20 }}
              />
            }
          >
            Đăng ký với Google
          </Button>

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Đã có tài khoản?{' '}
              <MuiLink
                component={RouterLink}
                to="/login"
                variant="body2"
                sx={{
                  fontWeight: 600,
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Đăng nhập ngay
              </MuiLink>
            </Typography>
          </Box>
        </form>
      </Paper>
    </Container>
  );
};

export default RegisterPage;
