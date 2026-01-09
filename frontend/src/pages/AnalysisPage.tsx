/**
 * Main Analysis Page Component
 * Orchestrates the resume upload, job input, analysis, and chat flow
 */
import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Box,
  Button,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import ResumeUploader from '../components/resume/ResumeUploader';
import AnalysisReport from '../components/analysis/AnalysisReport';
import ChatInterface from '../components/chat/ChatInterface';
import ApiService from '../services/api.service';
import { v4 as uuidv4 } from 'uuid';

const steps = ['Upload Resume', 'Job Description', 'Analysis', 'Chat'];

const AnalysisPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [resumeId, setResumeId] = useState('');
  const [resumeData, setResumeData] = useState<any>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [analysisId, setAnalysisId] = useState('');
  const [sessionId] = useState(uuidv4());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResumeUpload = (data: any) => {
    setResumeId(data.resume_id);
    setResumeData(data);
    setError(null);
    setActiveStep(1);
  };

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await ApiService.createAnalysis({
        resume_id: resumeId,
        job_description: jobDescription,
      });

      setAnalysis(response.data);
      setAnalysisId(response.data.analysis_id);
      setActiveStep(2);
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(
        err.response?.data?.detail || 'Failed to analyze. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
    setError(null);
  };

  const handleReset = () => {
    setActiveStep(0);
    setResumeId('');
    setResumeData(null);
    setJobDescription('');
    setAnalysis(null);
    setAnalysisId('');
    setError(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Resume Coach
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI-powered career coaching for better job applications
        </Typography>
      </Box>

      {/* Stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Paper sx={{ p: 3, minHeight: '400px' }}>
        {/* Step 0: Upload Resume */}
        {activeStep === 0 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Step 1: Upload Your Resume
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Supported formats: PDF, DOCX, TXT
            </Typography>
            <ResumeUploader onUploadSuccess={handleResumeUpload} />
          </Box>
        )}

        {/* Step 1: Job Description */}
        {activeStep === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Step 2: Provide Job Description
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Paste the full job description below
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={15}
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              sx={{ mb: 2 }}
              variant="outlined"
            />
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button onClick={handleBack} disabled={loading}>
                Back
              </Button>
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={!jobDescription.trim() || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze'}
              </Button>
            </Box>
          </Box>
        )}

        {/* Step 2: Analysis Results */}
        {activeStep === 2 && analysis && (
          <Box>
            <AnalysisReport analysis={analysis} />
            <Box display="flex" gap={2} justifyContent="space-between" mt={3}>
              <Button onClick={handleReset}>Start Over</Button>
              <Button variant="contained" onClick={() => setActiveStep(3)}>
                Continue to Chat
              </Button>
            </Box>
          </Box>
        )}

        {/* Step 3: Chat */}
        {activeStep === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Chat with Your Career Coach
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Ask questions about your analysis, get clarifications, or seek additional advice
            </Typography>
            <ChatInterface sessionId={sessionId} analysisId={analysisId} />
            <Box mt={2}>
              <Button onClick={handleReset}>Start New Analysis</Button>
            </Box>
          </Box>
        )}
      </Paper>

      {/* Footer */}
      <Box textAlign="center" mt={4}>
        <Typography variant="body2" color="text.secondary">
          Resume Coach v1.0 | Powered by AI
        </Typography>
      </Box>
    </Container>
  );
};

export default AnalysisPage;
