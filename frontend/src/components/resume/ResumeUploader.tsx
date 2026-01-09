/**
 * Resume Uploader Component
 * Handles resume file upload with drag & drop support
 */
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  LinearProgress,
  Alert,
  Paper,
  Chip,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import ApiService from '../../services/api.service';

interface ResumeUploaderProps {
  onUploadSuccess: (data: any) => void;
}

const ResumeUploader: React.FC<ResumeUploaderProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setUploading(true);
      setError(null);
      setSuccess(false);

      try {
        const response = await ApiService.uploadResume(file);
        setSuccess(true);
        setTimeout(() => {
          onUploadSuccess(response.data);
        }, 500);
      } catch (err: any) {
        console.error('Upload error:', err);
        setError(
          err.response?.data?.detail || 'Failed to upload resume. Please try again.'
        );
      } finally {
        setUploading(false);
      }
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [
        '.docx',
      ],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <Box>
      <Paper
        {...getRootProps()}
        elevation={isDragActive ? 8 : 1}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon
          sx={{
            fontSize: 64,
            color: isDragActive ? 'primary.main' : 'action.active',
            mb: 2,
          }}
        />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Drop your resume here'
            : 'Drag & drop your resume here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          or click to select from your computer
        </Typography>
        <Box display="flex" gap={1} justifyContent="center">
          <Chip
            icon={<DescriptionIcon />}
            label="PDF"
            size="small"
            variant="outlined"
          />
          <Chip
            icon={<DescriptionIcon />}
            label="DOCX"
            size="small"
            variant="outlined"
          />
          <Chip
            icon={<DescriptionIcon />}
            label="TXT"
            size="small"
            variant="outlined"
          />
        </Box>
      </Paper>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            Uploading and parsing your resume...
          </Typography>
        </Box>
      )}

      {success && !error && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Resume uploaded successfully! Proceeding to next step...
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ResumeUploader;
