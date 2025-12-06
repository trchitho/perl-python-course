import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  LinearProgress,
  Typography,
  Alert,
  Chip,
  IconButton,
  Paper,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Close as CloseIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

const FileUpload = ({ 
  onUploadComplete, 
  subfolder = 'general',
  compress = true,
  acceptedTypes = '*',
  maxSizeMB = 100,
  label = 'Upload File'
}) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploadResult, setUploadResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Validate file size
      const fileSizeMB = selectedFile.size / (1024 * 1024);
      if (fileSizeMB > maxSizeMB) {
        setError(`File too large. Maximum size: ${maxSizeMB}MB`);
        return;
      }

      setFile(selectedFile);
      setError('');
      setSuccess('');
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('subfolder', subfolder);
      formData.append('compress', compress.toString());

      const token = localStorage.getItem('token');

      // Create XMLHttpRequest for progress tracking
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          setProgress(percentComplete);
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText);
          setSuccess('File uploaded successfully!');
          setUploadResult(result);
          setFile(null);
          setProgress(100);
          
          if (onUploadComplete) {
            onUploadComplete(result);
          }

          // Reset after 3 seconds
          setTimeout(() => {
            setSuccess('');
            setProgress(0);
            setUploadResult(null);
          }, 3000);
        } else {
          const error = JSON.parse(xhr.responseText);
          setError(error.message || error.error || 'Upload failed');
          setProgress(0);
        }
        setUploading(false);
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        setError('Network error during upload');
        setUploading(false);
        setProgress(0);
      });

      // Send request
      xhr.open('POST', 'http://localhost:5000/api/upload');
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);

    } catch (err) {
      setError(err.message || 'Upload failed');
      setUploading(false);
      setProgress(0);
    }
  };

  const handleCancel = () => {
    setFile(null);
    setError('');
    setSuccess('');
    setProgress(0);
    setUploadResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {label}
      </Typography>

      {/* File Input */}
      <Box sx={{ mb: 2 }}>
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="file-upload-input"
        />
        <label htmlFor="file-upload-input">
          <Button
            variant="outlined"
            component="span"
            startIcon={<UploadIcon />}
            disabled={uploading}
            fullWidth
          >
            Select File
          </Button>
        </label>
      </Box>

      {/* Selected File Info */}
      {file && (
        <Box sx={{ mb: 2 }}>
          <Paper variant="outlined" sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="body2" fontWeight={600}>
                {file.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatFileSize(file.size)}
              </Typography>
            </Box>
            <IconButton size="small" onClick={handleCancel} disabled={uploading}>
              <CloseIcon />
            </IconButton>
          </Paper>
        </Box>
      )}

      {/* Upload Button */}
      {file && !uploading && !success && (
        <Button
          variant="contained"
          onClick={handleUpload}
          fullWidth
          sx={{ mb: 2 }}
        >
          Upload
        </Button>
      )}

      {/* Progress Bar */}
      {uploading && (
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box sx={{ flexGrow: 1, mr: 1 }}>
              <LinearProgress variant="determinate" value={progress} />
            </Box>
            <Typography variant="body2" color="text.secondary">
              {Math.round(progress)}%
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Uploading... Please wait
          </Typography>
        </Box>
      )}

      {/* Success Message */}
      {success && (
        <Alert severity="success" icon={<SuccessIcon />} sx={{ mb: 2 }}>
          {success}
          {uploadResult && uploadResult.compressed && (
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Compressed: {formatFileSize(uploadResult.original_size)} → {formatFileSize(uploadResult.size)}
            </Typography>
          )}
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" icon={<ErrorIcon />} onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Upload Info */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block">
          Maximum file size: {maxSizeMB}MB
        </Typography>
        {compress && (
          <Typography variant="caption" color="text.secondary" display="block">
            Images will be automatically compressed
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default FileUpload;
