# 🗓️ Google Calendar AI Agent

LangChain 기반 AI 에이전트로 자연어를 사용하여 Google Calendar를 관리하는 풀스택 애플리케이션입니다.

## 📋 프로젝트 개요

사용자가 자연어로 일정을 입력하면 AI 에이전트가 이를 이해하고 자동으로 Google Calendar에 이벤트를 생성합니다. 
대화형 인터페이스, 실시간 스트리밍, RAG 기반 컨텍스트 검색, 그리고 완전한 메모리 관리 기능을 제공합니다.

## ✨ 주요 기능

### 백엔드 (FastAPI + LangChain)
- 🤖 **LangChain 에이전트**: OpenAI GPT-4 또는 Anthropic Claude 기반 대화형 AI
- 🛠️ **도구 통합**: Google Calendar API 통합 및 자동 이벤트 생성
- 💾 **메모리 관리**: Redis 기반 대화 히스토리 저장 및 컨텍스트 유지
- 🔍 **RAG (Retrieval Augmented Generation)**: ChromaDB를 사용한 벡터 검색
- 📡 **스트리밍 응답**: 실시간 AI 응답 스트리밍
- 🔐 **OAuth 2.0**: Google Calendar 인증 및 권한 관리
- 📝 **완전한 로깅**: Loguru를 사용한 구조화된 로깅

### 프론트엔드 (React)
- 💬 **대화형 UI**: 직관적인 채팅 인터페이스
- 📅 **일정 대시보드**: 실시간 캘린더 이벤트 표시
- 🎨 **모던 디자인**: 반응형 그라디언트 UI
- ⚡ **실시간 업데이트**: 이벤트 생성 시 자동 갱신

### Infrastructure
- 🐳 **Docker 컨테이너화**: 완전한 Docker Compose 설정
- 🧪 **테스트**: Pytest 기반 단위 및 통합 테스트
- 🔧 **환경 설정**: dotenv를 사용한 구성 관리

## 🏗️ 프로젝트 구조

```
workspace/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── agent/             # LangChain 에이전트
│   │   │   ├── calendar_agent.py  # 메인 에이전트
│   │   │   ├── tools.py           # 에이전트 도구
│   │   │   ├── memory.py          # 메모리 관리
│   │   │   └── prompts.py         # 프롬프트 템플릿
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── google_calendar.py # Google Calendar API
│   │   │   └── vector_store.py    # ChromaDB RAG
│   │   ├── api/               # API 라우트
│   │   │   └── routes.py
│   │   ├── config.py          # 설정 관리
│   │   ├── models.py          # Pydantic 모델
│   │   └── main.py            # FastAPI 앱
│   ├── tests/                 # 테스트 코드
│   └── requirements.txt       # Python 의존성
│
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── components/        # React 컴포넌트
│   │   ├── api/               # API 클라이언트
│   │   ├── App.js             # 메인 앱
│   │   └── index.js
│   ├── public/
│   └── package.json
│
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile.backend          # 백엔드 Dockerfile
├── Dockerfile.frontend         # 프론트엔드 Dockerfile
├── .env.example               # 환경 변수 예시
└── README.md                  # 이 파일
```

## 🚀 시작하기

### 필수 요구사항

- Docker & Docker Compose
- Google Cloud Console 계정 (Calendar API 활성화)
- OpenAI API 키 또는 Anthropic API 키

### 1. Google Cloud 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. Google Calendar API 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. `credentials.json` 다운로드하여 프로젝트 루트에 저장

### 2. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# 환경 변수 설정
# 필수 항목:
# - OPENAI_API_KEY 또는 ANTHROPIC_API_KEY
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
```

### 3. Docker로 실행

```bash
# 모든 서비스 시작
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

서비스가 시작되면:
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 4. 로컬 개발 (Docker 없이)

#### 백엔드

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Redis 시작 (별도 터미널)
redis-server

# 서버 실행
python -m app.main
# 또는
uvicorn app.main:app --reload
```

#### 프론트엔드

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm start
```

## 📖 사용 방법

### 1. Google 인증

1. 프론트엔드에서 "Google 인증" 버튼 클릭
2. Google 계정으로 로그인 및 권한 승인
3. 인증 완료 후 자동으로 캘린더 액세스 가능

### 2. 일정 생성

자연어로 일정을 입력하세요:

```
내일 오후 3시에 팀 미팅 일정 추가해줘
다음주 월요일 오전 10시 회의실 A에서 프로젝트 리뷰
12월 25일 오후 6시 가족 저녁식사
```

AI 에이전트가 자동으로:
- 날짜와 시간 파싱
- 이벤트 제목 추출
- Google Calendar에 이벤트 생성
- 확인 메시지 제공

### 3. 일정 검색

```
이번 주 일정 알려줘
다음 달 회의 일정 찾아줘
```

## 🔧 API 엔드포인트

### 채팅 및 에이전트

- `POST /api/v1/chat` - 메시지 전송 및 에이전트 응답
- `POST /api/v1/chat/stream` - 스트리밍 응답
- `GET /api/v1/chat/history/{session_id}` - 대화 히스토리 조회
- `DELETE /api/v1/chat/history/{session_id}` - 대화 히스토리 삭제

### Google Calendar

- `GET /api/v1/events` - 이벤트 목록 조회
- `GET /api/v1/events/{event_id}` - 특정 이벤트 조회
- `DELETE /api/v1/events/{event_id}` - 이벤트 삭제
- `GET /api/v1/auth/google` - OAuth 인증 URL 생성
- `POST /api/v1/auth/callback` - OAuth 콜백 처리

### Vector Store (RAG)

- `POST /api/v1/search` - 유사 이벤트 검색
- `GET /api/v1/vector-store/stats` - 벡터 스토어 통계

### 헬스 체크

- `GET /` - 기본 헬스 체크
- `GET /health` - 상세 헬스 체크

## 🧪 테스트

```bash
cd backend

# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html

# 특정 테스트 파일
pytest tests/test_agent.py
```

## 🎯 LangChain 구현 세부사항

### Agent Architecture

```python
# OpenAI Tools Agent 사용
agent = create_openai_tools_agent(
    llm=llm,                    # GPT-4 or Claude
    tools=calendar_tools,       # 커스텀 도구
    prompt=agent_prompt,        # 구조화된 프롬프트
)

# Agent Executor로 실행
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=conversation_memory,  # Redis 기반
    verbose=True,
)
```

### Tools

4가지 주요 도구 구현:

1. **create_calendar_event**: Google Calendar에 이벤트 생성
2. **search_calendar_events**: 기존 이벤트 검색
3. **parse_datetime**: 자연어 날짜/시간 파싱
4. **search_similar_events**: RAG 기반 유사 이벤트 검색

### Memory Management

- **ConversationBufferMemory**: 대화 히스토리 저장
- **RedisChatMessageHistory**: Redis 백엔드로 영구 저장
- **Token Limit**: 2000 토큰 제한으로 컨텍스트 관리

### RAG Implementation

```python
# ChromaDB로 벡터 저장
collection.add(
    documents=[event_text],
    metadatas=[event_metadata],
    embeddings=[embedding],
)

# 유사도 검색
results = collection.query(
    query_texts=[user_query],
    n_results=5,
)
```

## 📊 주요 기술 스택

### 백엔드
- **Framework**: FastAPI 0.104+
- **AI/ML**: LangChain 0.1, OpenAI GPT-4, Anthropic Claude
- **Vector DB**: ChromaDB 0.4
- **Cache/Memory**: Redis 5.0
- **API Integration**: Google Calendar API
- **Testing**: Pytest, pytest-asyncio

### 프론트엔드
- **Framework**: React 18
- **HTTP Client**: Axios
- **Date Handling**: date-fns
- **Markdown**: react-markdown

### DevOps
- **Containerization**: Docker, Docker Compose
- **Logging**: Loguru
- **Configuration**: python-dotenv

## 🔐 보안 고려사항

- 환경 변수로 API 키 관리
- OAuth 2.0으로 Google 인증
- CORS 설정으로 출처 제한
- Redis 비밀번호 보호
- 민감한 정보 로깅 방지

## 🐛 문제 해결

### Google 인증 실패

```bash
# credentials.json 확인
# - 올바른 위치에 있는지
# - Client ID와 Secret이 .env와 일치하는지
# - Redirect URI가 정확히 설정되어 있는지
```

### Redis 연결 오류

```bash
# Redis 실행 확인
docker-compose ps

# Redis 재시작
docker-compose restart redis
```

### LLM API 오류

```bash
# API 키 확인
echo $OPENAI_API_KEY
# 또는
echo $ANTHROPIC_API_KEY

# .env 파일에 올바르게 설정되어 있는지 확인
```

## 📝 환경 변수

필수 환경 변수:

```env
# LLM Provider (openai 또는 anthropic)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
# 또는
ANTHROPIC_API_KEY=your_key_here

# Google Calendar
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Redis (Docker 사용 시 기본값)
REDIS_HOST=redis
REDIS_PORT=6379
```

전체 환경 변수 목록은 `.env.example` 참조

## 🚀 프로덕션 배포

### Docker를 사용한 배포

```bash
# 프로덕션 빌드
docker-compose -f docker-compose.yml up -d --build

# 로그 확인
docker-compose logs -f
```

### 성능 최적화

- Redis 영구 저장소 설정
- Gunicorn worker 수 조정
- Nginx 리버스 프록시 추가
- HTTPS 설정

## 📈 향후 개선 사항

- [ ] 다국어 지원
- [ ] 음성 입력 기능
- [ ] 캘린더 이벤트 수정/삭제 UI
- [ ] 반복 일정 지원
- [ ] 여러 캘린더 계정 관리
- [ ] 이메일 알림 통합
- [ ] Slack/Discord 봇 통합
- [ ] 모바일 앱 (React Native)

## 🤝 기여

기여를 환영합니다! Pull Request를 보내주세요.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 👥 제작자

LangChain Google Calendar Agent - AI 기반 스마트 일정 관리 솔루션

## 🙏 감사의 말

- [LangChain](https://langchain.com/) - 강력한 LLM 프레임워크
- [OpenAI](https://openai.com/) - GPT-4 API
- [Anthropic](https://anthropic.com/) - Claude API
- [Google Calendar API](https://developers.google.com/calendar)
- [ChromaDB](https://www.trychroma.com/) - 벡터 데이터베이스

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.

---

**Happy Scheduling! 📅✨**
