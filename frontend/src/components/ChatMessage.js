import React from 'react';
import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';

function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}>
      <div className="message-header">
        <span className="message-role">
          {isUser ? '👤 사용자' : '🤖 AI 에이전트'}
        </span>
        <span className="message-time">{timestamp}</span>
      </div>
      <div className="message-content">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
      {message.events && message.events.length > 0 && (
        <div className="message-events">
          <p>✅ {message.events.length}개의 일정이 생성되었습니다</p>
        </div>
      )}
    </div>
  );
}

export default ChatMessage;
