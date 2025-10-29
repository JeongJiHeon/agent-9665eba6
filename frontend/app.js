// API Base URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// State
let accessToken = localStorage.getItem('accessToken');
let currentUser = null;
let sessionId = generateSessionId();

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    if (accessToken) {
        getCurrentUser();
    } else {
        showSection('login');
    }
}

function setupEventListeners() {
    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('register');
    });
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('login');
    });
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Dashboard actions
    document.getElementById('connect-google-btn').addEventListener('click', connectGoogleCalendar);
    document.getElementById('chat-form').addEventListener('submit', handleChatSubmit);
    document.getElementById('refresh-events-btn').addEventListener('click', loadEvents);
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            accessToken = data.access_token;
            localStorage.setItem('accessToken', accessToken);
            showMessage('로그인 성공!', 'success');
            getCurrentUser();
        } else {
            showMessage(data.detail || '로그인 실패', 'error');
        }
    } catch (error) {
        showMessage('로그인 중 오류가 발생했습니다', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('회원가입 성공! 로그인해주세요.', 'success');
            showSection('login');
        } else {
            showMessage(result.detail || '회원가입 실패', 'error');
        }
    } catch (error) {
        showMessage('회원가입 중 오류가 발생했습니다', 'error');
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-display').textContent = currentUser.username;
            showSection('dashboard');
            loadEvents();
        } else {
            handleLogout();
        }
    } catch (error) {
        handleLogout();
    }
}

function handleLogout() {
    accessToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    showSection('login');
    showMessage('로그아웃 되었습니다', 'info');
}

// Google Calendar
async function connectGoogleCalendar() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/google/authorize`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.open(data.authorization_url, '_blank');
            showMessage('Google Calendar 인증 창이 열렸습니다', 'info');
        } else {
            showMessage('인증 URL 생성 실패', 'error');
        }
    } catch (error) {
        showMessage('Google Calendar 연결 중 오류 발생', 'error');
    }
}

// Chat
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/agent/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        removeTypingIndicator(typingId);
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToChat(data.message, 'assistant');
            
            if (data.calendar_event_created) {
                showMessage('일정이 생성되었습니다! ✅', 'success');
                loadEvents();
            }
        } else {
            addMessageToChat(data.detail || '오류가 발생했습니다', 'assistant');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessageToChat('메시지 전송 중 오류가 발생했습니다', 'assistant');
    }
}

function addMessageToChat(content, role) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message assistant-message';
    typingDiv.innerHTML = '<div class="message-content">AI가 생각 중입니다...</div>';
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function formatMessage(text) {
    // Simple formatting
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/✅/g, '<span style="color: var(--secondary-color);">✅</span>')
        .replace(/❌/g, '<span style="color: var(--danger-color);">❌</span>');
}

// Events
async function loadEvents() {
    const eventsList = document.getElementById('events-list');
    eventsList.innerHTML = '<p class="loading">일정을 불러오는 중...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/events/?limit=10`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (response.ok) {
            const events = await response.json();
            displayEvents(events);
        } else {
            eventsList.innerHTML = '<p class="loading">일정을 불러올 수 없습니다</p>';
        }
    } catch (error) {
        eventsList.innerHTML = '<p class="loading">오류가 발생했습니다</p>';
    }
}

function displayEvents(events) {
    const eventsList = document.getElementById('events-list');
    
    if (events.length === 0) {
        eventsList.innerHTML = '<p class="loading">일정이 없습니다</p>';
        return;
    }
    
    eventsList.innerHTML = '';
    
    events.forEach(event => {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'event-item';
        
        const startTime = new Date(event.start_time).toLocaleString('ko-KR');
        const endTime = new Date(event.end_time).toLocaleString('ko-KR');
        
        eventDiv.innerHTML = `
            <div class="event-title">${event.title}</div>
            <div class="event-time">📅 ${startTime} ~ ${endTime}</div>
            ${event.location ? `<div class="event-description">📍 ${event.location}</div>` : ''}
            ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
        `;
        
        eventsList.appendChild(eventDiv);
    });
}

// UI Utilities
function showSection(section) {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'none';
    
    if (section === 'login') {
        document.getElementById('login-section').style.display = 'block';
    } else if (section === 'register') {
        document.getElementById('register-section').style.display = 'block';
    } else if (section === 'dashboard') {
        document.getElementById('dashboard-section').style.display = 'block';
    }
}

function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('status-message');
    messageDiv.textContent = message;
    messageDiv.className = `status-message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}
