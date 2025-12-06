import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Backup as BackupIcon,
} from '@mui/icons-material';
import { getSettings, updateSettings, runBackup } from '../../../services/adminAPI';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    site_name: '',
    site_description: '',
    contact_email: '',
    max_upload_size: '',
    smtp_host: '',
    smtp_port: '',
    smtp_user: '',
    smtp_password: '',
    ai_key: '',
    ai_model: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getSettings();
      setSettings(data);
    } catch (err) {
      setError('Không thể tải settings: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setError('');
      setSuccess('');
      await updateSettings(settings);
      setSuccess('Settings đã được cập nhật!');
    } catch (err) {
      setError('Không thể cập nhật settings: ' + err.message);
    }
  };

  const handleBackup = async () => {
    try {
      setError('');
      setSuccess('');
      await runBackup();
      setSuccess('Backup đã được tạo thành công!');
    } catch (err) {
      setError('Không thể tạo backup: ' + err.message);
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
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        System Settings
      </Typography>

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

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          General Settings
        </Typography>
        <TextField
          fullWidth
          label="Site Name"
          value={settings.site_name || ''}
          onChange={(e) => setSettings({ ...settings, site_name: e.target.value })}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Site Description"
          value={settings.site_description || ''}
          onChange={(e) => setSettings({ ...settings, site_description: e.target.value })}
          margin="normal"
          multiline
          rows={3}
        />
        <TextField
          fullWidth
          label="Contact Email"
          type="email"
          value={settings.contact_email || ''}
          onChange={(e) => setSettings({ ...settings, contact_email: e.target.value })}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Max Upload Size (MB)"
          type="number"
          value={settings.max_upload_size || ''}
          onChange={(e) => setSettings({ ...settings, max_upload_size: e.target.value })}
          margin="normal"
        />
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          SMTP Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Configure email server settings for sending notifications
        </Typography>
        <TextField
          fullWidth
          label="SMTP Host"
          value={settings.smtp_host || ''}
          onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
          margin="normal"
          placeholder="smtp.gmail.com"
        />
        <TextField
          fullWidth
          label="SMTP Port"
          type="number"
          value={settings.smtp_port || ''}
          onChange={(e) => setSettings({ ...settings, smtp_port: e.target.value })}
          margin="normal"
          placeholder="587"
        />
        <TextField
          fullWidth
          label="SMTP User"
          value={settings.smtp_user || ''}
          onChange={(e) => setSettings({ ...settings, smtp_user: e.target.value })}
          margin="normal"
          placeholder="your-email@gmail.com"
        />
        <TextField
          fullWidth
          label="SMTP Password"
          type="password"
          value={settings.smtp_password || ''}
          onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
          margin="normal"
          placeholder="••••••••"
        />
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          AI/Chatbot Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Configure AI chatbot settings (Google Gemini API)
        </Typography>
        <TextField
          fullWidth
          label="AI API Key"
          type="password"
          value={settings.ai_key || ''}
          onChange={(e) => setSettings({ ...settings, ai_key: e.target.value })}
          margin="normal"
          placeholder="AIza..."
        />
        <TextField
          fullWidth
          label="AI Model"
          value={settings.ai_model || ''}
          onChange={(e) => setSettings({ ...settings, ai_model: e.target.value })}
          margin="normal"
          placeholder="gemini-2.0-flash-exp"
        />
      </Paper>

      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<SaveIcon />}
          onClick={handleSave}
        >
          Save All Settings
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Database Backup
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Create a backup of the database. This may take a few minutes.
        </Typography>
        <Button
          variant="outlined"
          startIcon={<BackupIcon />}
          onClick={handleBackup}
        >
          Run Backup
        </Button>
      </Paper>
    </Container>
  );
};

export default SettingsPage;
