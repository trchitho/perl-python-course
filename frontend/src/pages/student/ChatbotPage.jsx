import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  TextField,
  IconButton,
  Avatar,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
  History as HistoryIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { apiPost, apiGet } from '../../../services/apiConfig';
// Simple markdown-like formatting function
const formatBotMessage = (text) => {
  // Convert markdown to HTML-like formatting
  let formatted = text
    // Bold: **text** -> <strong>text</strong>
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic: *text* -> <em>text</em>
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Code: `code` -> <code>code</code>
    .replace(/`(.+?)`/g, '<code>$1</code>')
    // Headings: ### text -> larger text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Lists: - item -> • item
    .replace(/^- (.+)$/gm, '• $1')
    .replace(/^\* (.+)$/gm, '• $1')
    // Numbered lists: 1. item
    .replace(/^(\d+)\. (.+)$/gm, '$1. $2')
    // Line breaks
    .replace(/\n/g, '<br/>');
  
  return formatted;
};

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [clearingHistory, setClearingHistory] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadHistory = async () => {
    try {
      const data = await apiGet('/ai/history');
      setChatHistory(data);
      // Không tự động load messages vào màn hình chính
      // Chỉ hiển thị lịch sử trong sidebar
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    setSidebarOpen(false);
  };

  const loadSession = async (sessionId) => {
    try {
      const data = await apiGet(`/ai/history/${sessionId}`);
      const formattedMessages = [];
      data.forEach((item) => {
        formattedMessages.push({
          text: item.question,
          sender: 'user',
          timestamp: item.created_at,
        });
        formattedMessages.push({
          text: item.answer,
          sender: 'bot',
          timestamp: item.created_at,
        });
      });
      setMessages(formattedMessages);
      setCurrentSessionId(sessionId);
      setSidebarOpen(false);
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Không thể tải cuộc trò chuyện');
    }
  };

  const clearAllHistory = async () => {
    if (!window.confirm('Bạn có chắc muốn xóa toàn bộ lịch sử chat?')) {
      return;
    }

    setClearingHistory(true);
    try {
      const response = await fetch('http://localhost:5000/api/ai/history', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        setMessages([]);
        setChatHistory([]);
        alert('Đã xóa lịch sử chat thành công!');
      } else {
        throw new Error('Failed to clear history');
      }
    } catch (err) {
      console.error('Failed to clear history:', err);
      alert('Không thể xóa lịch sử. Vui lòng thử lại.');
    } finally {
      setClearingHistory(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const response = await apiPost('/ai/chat', { 
        message: input,
        session_id: currentSessionId 
      });
      
      const botMessage = {
        text: response.response || response.answer || 'Sorry, I could not process your request.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
      
      // Update session ID if this is a new chat
      if (!currentSessionId && response.session_id) {
        setCurrentSessionId(response.session_id);
      }
      
      // Reload history để cập nhật sidebar
      loadHistory();
    } catch (err) {
      setError('Failed to send message: ' + err.message);
      const errorMessage = {
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 100px)', overflow: 'hidden' }}>
      {/* Sidebar - History */}
      <Paper
        sx={{
          width: sidebarOpen ? 280 : 0,
          transition: 'width 0.3s ease',
          overflow: 'hidden',
          borderRight: '1px solid #e0e0e0',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Lịch sử
            </Typography>
            <IconButton size="small" onClick={() => setSidebarOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={startNewChat}
            sx={{ mb: 1 }}
          >
            Cuộc trò chuyện mới
          </Button>
          <Button
            fullWidth
            variant="outlined"
            color="error"
            onClick={clearAllHistory}
            disabled={clearingHistory || chatHistory.length === 0}
            sx={{ mb: 1 }}
          >
            {clearingHistory ? 'Đang xóa...' : 'Xóa toàn bộ lịch sử'}
          </Button>
        </Box>
        
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
          {chatHistory.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              Chưa có lịch sử
            </Typography>
          ) : (
            chatHistory.map((session) => (
              <Paper
                key={session.session_id}
                sx={{
                  p: 1.5,
                  mb: 1,
                  cursor: 'pointer',
                  bgcolor: currentSessionId === session.session_id ? '#e3f2fd' : 'white',
                  '&:hover': { bgcolor: currentSessionId === session.session_id ? '#e3f2fd' : '#f5f5f5' },
                  transition: 'all 0.2s',
                }}
                onClick={() => loadSession(session.session_id)}
              >
                <Typography variant="body2" noWrap fontWeight={500}>
                  {session.title}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(session.last_updated).toLocaleDateString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {session.message_count} tin nhắn
                  </Typography>
                </Box>
              </Paper>
            ))
          )}
        </Box>
      </Paper>

      {/* Main Chat Area */}
      <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%', p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <IconButton onClick={() => setSidebarOpen(!sidebarOpen)}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h4" fontWeight={700}>
            AI Assistant
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

      <Paper
        sx={{
          flexGrow: 1,
          p: 2,
          mb: 2,
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: '#f5f5f5',
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <BotIcon sx={{ fontSize: 60, color: '#ccc', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Start a conversation with the AI assistant!
            </Typography>
          </Box>
        ) : (
          messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              {message.sender === 'bot' && (
                <Avatar sx={{ bgcolor: '#6366f1', mr: 1 }}>
                  <BotIcon />
                </Avatar>
              )}
              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.sender === 'user' ? '#6366f1' : 'white',
                  color: message.sender === 'user' ? 'white' : 'inherit',
                  '& h1, & h2, & h3': { 
                    mt: 2, 
                    mb: 1, 
                    fontWeight: 600,
                    fontSize: message.sender === 'bot' ? '1.2rem' : '1rem'
                  },
                  '& h3': { fontSize: '1.1rem' },
                  '& p': { mb: 1, lineHeight: 1.6 },
                  '& ul, & ol': { pl: 3, mb: 1 },
                  '& li': { mb: 0.5 },
                  '& code': {
                    bgcolor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : '#f5f5f5',
                    p: 0.5,
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.9em'
                  },
                  '& pre': {
                    bgcolor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : '#f5f5f5',
                    p: 2,
                    borderRadius: 2,
                    overflow: 'auto',
                    '& code': {
                      bgcolor: 'transparent',
                      p: 0
                    }
                  },
                  '& strong': { fontWeight: 700 },
                  '& em': { fontStyle: 'italic' },
                  '& hr': { 
                    my: 2, 
                    border: 'none', 
                    borderTop: message.sender === 'user' ? '1px solid rgba(255,255,255,0.3)' : '1px solid #e0e0e0' 
                  }
                }}
              >
                {message.sender === 'bot' ? (
                  <Typography 
                    variant="body1" 
                    component="div"
                    dangerouslySetInnerHTML={{ __html: formatBotMessage(message.text) }}
                  />
                ) : (
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.text}
                  </Typography>
                )}
              </Paper>
              {message.sender === 'user' && (
                <Avatar sx={{ bgcolor: '#10b981', ml: 1 }}>
                  <PersonIcon />
                </Avatar>
              )}
            </Box>
          ))
        )}
        <div ref={messagesEndRef} />
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          multiline
          maxRows={3}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          sx={{
            bgcolor: '#6366f1',
            color: 'white',
            '&:hover': { bgcolor: '#5558dd' },
            '&:disabled': { bgcolor: '#ccc' },
          }}
        >
          {loading ? <CircularProgress size={24} /> : <SendIcon />}
        </IconButton>
      </Box>
      </Container>
    </Box>
  );
};

export default ChatbotPage;
