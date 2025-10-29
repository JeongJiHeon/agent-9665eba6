import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatMessage from './components/ChatMessage';
import EventCard from './components/EventCard';
import { sendMessage, getEvents, authenticateGoogle } from './api/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [events, setEvents] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await getEvents();
      setEvents(data.events || []);
    } catch (error) {
      console.error('Failed to load events:', error);
    }
  };

  const handleAuthenticate = async () => {
    try {
      const data = await authenticateGoogle();
      if (data.auth_url) {
        window.open(data.auth_url, '_blank');
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Authentication failed:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(input, sessionId);
      
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }

      const aiMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        events: response.events_created || [],
      };

      setMessages(prev => [...prev, aiMessage]);

      // Reload events if any were created
      if (response.events_created && response.events_created.length > 0) {
        await loadEvents();
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
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
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>📅 구글 캘린더 AI 에이전트</h1>
          <p>자연어로 일정을 말씀해주세요</p>
        </div>
        {!isAuthenticated && (
          <button className="auth-button" onClick={handleAuthenticate}>
            🔐 Google 인증
          </button>
        )}
      </header>

      <div className="main-content">
        <div className="chat-section">
          <div className="chat-container">
            <div className="messages">
              {messages.length === 0 && (
                <div className="welcome-message">
                  <h2>👋 환영합니다!</h2>
                  <p>자연어로 일정을 입력하면 자동으로 캘린더에 추가해드립니다.</p>
                  <div className="examples">
                    <h3>예시:</h3>
                    <ul>
                      <li>"내일 오후 3시에 팀 미팅 일정 추가해줘"</li>
                      <li>"다음주 월요일 오전 10시 회의실 A에서 프로젝트 리뷰"</li>
                      <li>"12월 25일 오후 6시 가족 저녁식사"</li>
                    </ul>
                  </div>
                </div>
              )}
              
              {messages.map((msg, index) => (
                <ChatMessage key={index} message={msg} />
              ))}
              
              {loading && (
                <div className="loading-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="일정을 자연어로 입력하세요... (예: 내일 오후 3시에 미팅)"
                rows="2"
                disabled={loading}
              />
              <button onClick={handleSend} disabled={loading || !input.trim()}>
                {loading ? '전송 중...' : '전송'}
              </button>
            </div>
          </div>
        </div>

        <div className="events-section">
          <h2>📆 다가오는 일정</h2>
          <div className="events-list">
            {events.length === 0 ? (
              <p className="no-events">일정이 없습니다</p>
            ) : (
              events.slice(0, 10).map((event, index) => (
                <EventCard key={index} event={event} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
