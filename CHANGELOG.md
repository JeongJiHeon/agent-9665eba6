# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-29

### Added

#### Backend
- LangChain-based AI agent with OpenAI GPT-4 and Anthropic Claude support
- Google Calendar API integration for event management
- Conversational memory with Redis backend
- Vector database (ChromaDB) for RAG functionality
- Streaming response support
- Comprehensive API endpoints (chat, events, auth, search)
- Full test suite with pytest
- Docker containerization
- Structured logging with Loguru
- Environment-based configuration

#### Frontend
- React-based modern UI
- Real-time chat interface with AI agent
- Calendar events dashboard
- Google OAuth authentication flow
- Responsive design with gradient styling
- Markdown support in chat messages
- Event cards with time formatting

#### Infrastructure
- Docker Compose setup for multi-service orchestration
- Redis for session and memory storage
- ChromaDB for vector embeddings
- Comprehensive documentation (README, DEPLOYMENT, CONTRIBUTING)

#### Tools
- Natural language datetime parsing
- Calendar event creation tool
- Event search functionality
- Similar events search with RAG

### Features

- 🤖 Natural language understanding for calendar events
- 📅 Automatic event creation in Google Calendar
- 💬 Conversational interface with context awareness
- 🔍 RAG-based similar event search
- 📡 Real-time streaming responses
- 🔐 OAuth 2.0 authentication
- 💾 Persistent conversation memory
- 🧪 Comprehensive test coverage
- 🐳 Production-ready Docker setup

### Technical Details

- Python 3.11+ with FastAPI
- LangChain 0.1.0 framework
- React 18 with modern hooks
- ChromaDB for vector storage
- Redis for memory management
- Sentence transformers for embeddings

## [Unreleased]

### Planned

- Multi-language support
- Voice input capability
- Event editing UI
- Recurring events support
- Multiple calendar accounts
- Email notifications
- Slack/Discord bot integration
- Mobile app (React Native)
- Advanced analytics dashboard
- Calendar sharing features

---

## Version History

- **1.0.0** (2025-10-29): Initial release with full features
