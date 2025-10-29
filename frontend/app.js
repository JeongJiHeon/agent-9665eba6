// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentUserId = 'demo_user';

// DOM Elements
const authButton = document.getElementById('auth-button');
const authStatus = document.getElementById('auth-status');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const loading = document.getElementById('loading');
const eventsList = document.getElementById('events-list');
const historyList = document.getElementById('history-list');
const clearHistoryButton = document.getElementById('clear-history');
const refreshEventsButton = document.getElementById('refresh-events');
const quickButtons = document.querySelectorAll('.quick-btn');

// Event Listeners
document.addEventListener('DOMContentLoaded', init);
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
authButton.addEventListener('click', handleAuth);
clearHistoryButton.addEventListener('click', clearHistory);
refreshEventsButton.addEventListener('click', refreshEvents);
quickButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const message = e.currentTarget.getAttribute('data-message');
        userInput.value = message;
        sendMessage();
    });
});

// Initialize
function init() {
    console.log('Google Calendar AI Agent initialized');
    loadConversationHistory();
}

// Send Message
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    userInput.value = '';
    
    // Show loading
    loading.style.display = 'flex';
    sendButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/agent/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: currentUserId
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessageToChat('assistant', data.message);
            
            // Refresh events if calendar operation was performed
            if (message.includes('추가') || message.includes('생성') || message.includes('일정')) {
                setTimeout(refreshEvents, 1000);
            }
        } else {
            if (data.requires_auth) {
                addMessageToChat('assistant', data.message);
                showAuthPrompt();
            } else {
                addMessageToChat('assistant', `오류: ${data.message}`);
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('assistant', '죄송합니다. 서버와 통신 중 오류가 발생했습니다.');
    } finally {
        loading.style.display = 'none';
        sendButton.disabled = false;
    }
}

// Add Message to Chat
function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parse content and convert to HTML
    const formattedContent = content.replace(/\n/g, '<br>');
    contentDiv.innerHTML = `<p>${formattedContent}</p>`;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Authentication
async function handleAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/calendar/auth/url/${currentUserId}`);
        const data = await response.json();
        
        if (data.auth_url) {
            window.open(data.auth_url, '_blank');
            showAuthSuccess();
        }
    } catch (error) {
        console.error('Error getting auth URL:', error);
        alert('인증 URL을 가져오는 중 오류가 발생했습니다.');
    }
}

// Show Auth Prompt
function showAuthPrompt() {
    authStatus.innerHTML = `
        <span class="status-indicator not-connected"></span>
        <span>구글 캘린더 인증이 필요합니다</span>
    `;
    authButton.style.display = 'block';
}

// Show Auth Success
function showAuthSuccess() {
    authStatus.innerHTML = `
        <span class="status-indicator connected"></span>
        <span>구글 캘린더와 연결됨</span>
    `;
    authButton.style.display = 'none';
    addMessageToChat('assistant', '구글 캘린더 인증이 완료되었습니다! 이제 일정을 관리할 수 있습니다.');
}

// Load Conversation History
async function loadConversationHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/history/${currentUserId}`);
        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            historyList.innerHTML = '';
            data.history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div class="history-user">👤 ${item.content}</div>
                `;
                historyList.appendChild(historyItem);
            });
        }
    } catch (error) {
        console.error('Error loading conversation history:', error);
    }
}

// Clear History
async function clearHistory() {
    if (!confirm('대화 기록을 삭제하시겠습니까?')) return;
    
    try {
        await fetch(`${API_BASE_URL}/agent/history/${currentUserId}`, {
            method: 'DELETE'
        });
        
        historyList.innerHTML = '<p class="placeholder">대화 기록이 표시됩니다.</p>';
        addMessageToChat('assistant', '대화 기록이 삭제되었습니다.');
    } catch (error) {
        console.error('Error clearing history:', error);
        alert('기록 삭제 중 오류가 발생했습니다.');
    }
}

// Refresh Events
async function refreshEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/calendar/events/list`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUserId,
                max_results: 10
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.events && data.events.length > 0) {
            eventsList.innerHTML = '';
            data.events.forEach(event => {
                const eventItem = document.createElement('div');
                eventItem.className = 'event-item';
                
                const startTime = event.start?.dateTime || event.start?.date || '';
                const location = event.location || '';
                
                eventItem.innerHTML = `
                    <div class="event-title">${event.summary || '제목 없음'}</div>
                    <div class="event-time">📅 ${formatDateTime(startTime)}</div>
                    ${location ? `<div class="event-location">📍 ${location}</div>` : ''}
                `;
                
                eventsList.appendChild(eventItem);
            });
        } else {
            eventsList.innerHTML = '<p class="placeholder">일정이 없습니다.</p>';
        }
    } catch (error) {
        console.error('Error refreshing events:', error);
        eventsList.innerHTML = '<p class="placeholder">일정을 불러오는 중 오류가 발생했습니다.</p>';
    }
}

// Format DateTime
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    
    try {
        const date = new Date(dateTimeStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    } catch (error) {
        return dateTimeStr;
    }
}

// Demo mode notification
console.log('%c🚀 Google Calendar AI Agent', 'font-size: 20px; color: #4285f4; font-weight: bold;');
console.log('%cDemo Mode: Using user ID "demo_user"', 'font-size: 14px; color: #34a853;');
console.log('%cTo use your own Google Calendar, authenticate using the button above.', 'font-size: 12px; color: #5f6368;');
