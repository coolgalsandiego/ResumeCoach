/**
 * Chat Interface Component
 * Real-time chat with the AI career coach
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Avatar,
  CircularProgress,
  IconButton,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import DeleteIcon from '@mui/icons-material/Delete';
import ApiService from '../../services/api.service';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatInterfaceProps {
  sessionId: string;
  analysisId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, analysisId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await ApiService.sendChatMessage({
        session_id: sessionId,
        message: input,
        analysis_id: analysisId,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = async () => {
    if (window.confirm('Clear chat history?')) {
      try {
        await ApiService.clearChatSession(sessionId);
        setMessages([]);
      } catch (error) {
        console.error('Failed to clear chat:', error);
      }
    }
  };

  return (
    <Box sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}
      >
        <Typography variant="subtitle2" color="text.secondary">
          Ask me anything about your resume analysis
        </Typography>
        <IconButton onClick={handleClear} size="small" disabled={messages.length === 0}>
          <DeleteIcon />
        </IconButton>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Messages Container */}
      <Paper
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          bgcolor: 'grey.50',
          mb: 2,
        }}
      >
        {messages.length === 0 && (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            height="100%"
          >
            <SmartToyIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
            <Typography variant="body1" color="text.secondary" align="center">
              Start a conversation with your career coach!
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              You can ask about your analysis, get clarifications, or seek additional advice.
            </Typography>
          </Box>
        )}

        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              mb: 2,
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                mx: 1,
              }}
            >
              {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
            </Avatar>

            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: message.role === 'user' ? 'primary.light' : 'white',
                borderRadius: 2,
              }}
            >
              <Typography
                variant="body1"
                sx={{
                  color: message.role === 'user' ? 'white' : 'text.primary',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {message.content}
              </Typography>
              {message.timestamp && (
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 0.5,
                    color: message.role === 'user' ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  }}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              )}
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', mx: 1 }}>
              <SmartToyIcon />
            </Avatar>
            <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
              <Box display="flex" alignItems="center">
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  Thinking...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Box */}
      <Box display="flex" gap={1}>
        <TextField
          fullWidth
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          multiline
          maxRows={4}
          disabled={loading}
          variant="outlined"
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          endIcon={<SendIcon />}
          sx={{ minWidth: '100px' }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface;
