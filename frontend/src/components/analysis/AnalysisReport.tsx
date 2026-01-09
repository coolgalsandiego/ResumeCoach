/**
 * Analysis Report Component
 * Displays the complete resume analysis results
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Divider,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import StarIcon from '@mui/icons-material/Star';

interface AnalysisReportProps {
  analysis: {
    fit_analysis: string;
    gap_analysis: string;
    strengths_analysis: string;
    coaching_advice: string;
    summary: {
      overall_fit: string;
      match_score: number;
      critical_gaps: string[];
      top_strengths: string[];
    };
  };
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ analysis }) => {
  const { summary } = analysis;

  const getFitColor = (fit: string): 'success' | 'info' | 'warning' | 'error' => {
    const colors: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
      Excellent: 'success',
      Good: 'info',
      Fair: 'warning',
      Poor: 'error',
    };
    return colors[fit] || 'info';
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#2196f3';
    if (score >= 40) return '#ff9800';
    return '#f44336';
  };

  return (
    <Box>
      {/* Summary Card */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="white">
            Analysis Summary
          </Typography>

          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="rgba(255,255,255,0.8)">
                Overall Fit
              </Typography>
              <Chip
                label={summary.overall_fit}
                color={getFitColor(summary.overall_fit)}
                sx={{ mt: 1, fontSize: '1.1rem', fontWeight: 'bold', height: '36px', px: 2 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="rgba(255,255,255,0.8)">
                Match Score
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <Typography variant="h3" color="white" sx={{ mr: 2 }}>
                  {summary.match_score}
                </Typography>
                <Typography variant="h6" color="rgba(255,255,255,0.8)">
                  / 100
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={summary.match_score}
                sx={{
                  mt: 1,
                  height: 10,
                  borderRadius: 5,
                  bgcolor: 'rgba(255,255,255,0.3)',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: getScoreColor(summary.match_score),
                  },
                }}
              />
            </Grid>
          </Grid>

          {/* Quick Insights */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <WarningIcon sx={{ color: '#ff9800', mr: 1 }} />
                    <Typography variant="subtitle2" color="white">
                      Critical Gaps
                    </Typography>
                  </Box>
                  {summary.critical_gaps.length > 0 ? (
                    <List dense>
                      {summary.critical_gaps.slice(0, 3).map((gap, idx) => (
                        <ListItem key={idx} sx={{ py: 0 }}>
                          <ListItemText
                            primary={gap}
                            primaryTypographyProps={{
                              color: 'rgba(255,255,255,0.9)',
                              variant: 'body2',
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      No critical gaps identified
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <StarIcon sx={{ color: '#ffd700', mr: 1 }} />
                    <Typography variant="subtitle2" color="white">
                      Top Strengths
                    </Typography>
                  </Box>
                  {summary.top_strengths.length > 0 ? (
                    <List dense>
                      {summary.top_strengths.slice(0, 3).map((strength, idx) => (
                        <ListItem key={idx} sx={{ py: 0 }}>
                          <ListItemText
                            primary={strength}
                            primaryTypographyProps={{
                              color: 'rgba(255,255,255,0.9)',
                              variant: 'body2',
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      Various relevant strengths
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Sections */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <CheckCircleIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6">Fit Analysis</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ '& h2': { fontSize: '1.2rem', mt: 2, mb: 1 }, '& h3': { fontSize: '1rem', mt: 1.5, mb: 0.5 } }}>
            <ReactMarkdown>{analysis.fit_analysis}</ReactMarkdown>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <WarningIcon color="warning" sx={{ mr: 1 }} />
            <Typography variant="h6">Skill Gaps</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ '& h2': { fontSize: '1.2rem', mt: 2, mb: 1 }, '& h3': { fontSize: '1rem', mt: 1.5, mb: 0.5 } }}>
            <ReactMarkdown>{analysis.gap_analysis}</ReactMarkdown>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <StarIcon sx={{ color: '#ffd700', mr: 1 }} />
            <Typography variant="h6">Your Strengths</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ '& h2': { fontSize: '1.2rem', mt: 2, mb: 1 }, '& h3': { fontSize: '1rem', mt: 1.5, mb: 0.5 } }}>
            <ReactMarkdown>{analysis.strengths_analysis}</ReactMarkdown>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Coaching Advice
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ '& h2': { fontSize: '1.2rem', mt: 2, mb: 1 }, '& h3': { fontSize: '1rem', mt: 1.5, mb: 0.5 } }}>
            <ReactMarkdown>{analysis.coaching_advice}</ReactMarkdown>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisReport;
