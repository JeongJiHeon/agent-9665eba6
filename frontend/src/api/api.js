import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendMessage = async (message, sessionId = null) => {
  try {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId,
      user_id: 'default_user',
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getEvents = async (query = null, maxResults = 10) => {
  try {
    const params = { max_results: maxResults };
    if (query) params.query = query;
    
    const response = await api.get('/events', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching events:', error);
    return { events: [] };
  }
};

export const getEvent = async (eventId) => {
  try {
    const response = await api.get(`/events/${eventId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching event:', error);
    throw error;
  }
};

export const deleteEvent = async (eventId) => {
  try {
    const response = await api.delete(`/events/${eventId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting event:', error);
    throw error;
  }
};

export const authenticateGoogle = async () => {
  try {
    const response = await api.get('/auth/google');
    return response.data;
  } catch (error) {
    console.error('Error authenticating with Google:', error);
    throw error;
  }
};

export const getChatHistory = async (sessionId) => {
  try {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw error;
  }
};

export const clearChatHistory = async (sessionId) => {
  try {
    const response = await api.delete(`/chat/history/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Error clearing chat history:', error);
    throw error;
  }
};

export const searchSimilarEvents = async (query, topK = 5) => {
  try {
    const response = await api.post('/search', {
      query,
      top_k: topK,
      user_id: 'default_user',
    });
    return response.data;
  } catch (error) {
    console.error('Error searching similar events:', error);
    throw error;
  }
};

export default api;
