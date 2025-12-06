import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Campaign as CampaignIcon,
  PriorityHigh as UrgentIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { apiGet } from '../../../services/apiConfig';

const AnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnnouncements();
  }, []);

  const loadAnnouncements = async () => {
    try {
      setLoading(true);
      const data = await apiGet('/announcements');
      setAnnouncements(data);
    } catch (err) {
      console.error('Failed to load announcements:', err);
      setError('Không thể tải thông báo. Vui lòng thử lại.');
    } finally {
      setLoading(false);
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

  const getPriorityIcon = (priority) => {
    if (priority === 'urgent' || priority === 'high') {
      return <UrgentIcon fontSize="small" />;
    }
    return <InfoIcon fontSize="small" />;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} phút trước`;
    } else if (diffHours < 24) {
      return `${diffHours} giờ trước`;
    } else if (diffDays < 7) {
      return `${diffDays} ngày trước`;
    } else {
      return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Đang tải thông báo...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <CampaignIcon sx={{ fontSize: 40, mr: 2, color: '#6366f1' }} />
        <Typography variant="h4" fontWeight={700}>
          Thông Báo
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {announcements.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CampaignIcon sx={{ fontSize: 60, color: '#ccc', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Chưa có thông báo nào
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Các thông báo từ giáo viên và hệ thống sẽ hiển thị ở đây
          </Typography>
        </Paper>
      ) : (
        <Box>
          {announcements.map((announcement) => (
            <Card
              key={announcement.id}
              sx={{
                mb: 2,
                border: announcement.priority === 'urgent' ? '2px solid #f44336' : '1px solid #e0e0e0',
                boxShadow: announcement.priority === 'urgent' ? 3 : 1,
                '&:hover': { boxShadow: 3 },
                transition: 'all 0.2s',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Chip
                        icon={getPriorityIcon(announcement.priority)}
                        label={announcement.priority.toUpperCase()}
                        color={getPriorityColor(announcement.priority)}
                        size="small"
                      />
                      <Chip
                        label={announcement.course_name}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    </Box>
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                      {announcement.title}
                    </Typography>
                  </Box>
                </Box>

                <Typography
                  variant="body1"
                  sx={{
                    mb: 2,
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                  }}
                >
                  {announcement.content}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    Đăng bởi: <strong>{announcement.created_by}</strong>
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(announcement.created_at)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Container>
  );
};

export default AnnouncementsPage;
