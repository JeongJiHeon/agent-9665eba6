# 🗓️ Google Calendar AI Agent

LangChain 기반의 구글 캘린더 작성 AI 에이전트 애플리케이션입니다. 사용자가 자연어로 일정을 입력하면 AI가 자동으로 파싱하여 구글 캘린더에 이벤트를 생성합니다.

## ✨ 주요 기능

- 🤖 **자연어 처리**: "내일 오후 3시 팀 회의 일정 잡아줘"와 같은 자연어 입력 지원
- 📅 **구글 캘린더 연동**: 자동으로 구글 캘린더에 이벤트 생성/수정/삭제
- 💬 **대화형 AI 에이전트**: LangChain 기반의 대화형 인터페이스
- 🧠 **메모리 관리**: 대화 컨텍스트를 기억하는 세션 관리
- 🔍 **벡터 DB & RAG**: Chroma를 활용한 지식 검색
- 🔐 **인증 시스템**: JWT 기반 사용자 인증 및 OAuth 2.0
- 🎨 **모던 UI**: 반응형 웹 대시보드
- 🐳 **Docker 지원**: 완전한 컨테이너화

## 🏗️ 기술 스택

### Backend
- **Framework**: FastAPI 0.109+
- **AI/ML**: LangChain 0.1+, OpenAI GPT-4
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Vector Store**: ChromaDB
- **Authentication**: JWT, OAuth 2.0

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- 반응형 디자인

### DevOps
- Docker & Docker Compose
- pytest (테스트)

## 📁 프로젝트 구조

```
.
├── app/
│   ├── agent/              # LangChain AI 에이전트
│   │   ├── calendar_agent.py
│   │   ├── tools.py
│   │   ├── prompts.py
│   │   ├── memory.py
│   │   └── vector_store.py
│   ├── api/                # FastAPI 라우터
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── agent.py
│   │       └── events.py
│   ├── core/               # 인증 & 보안
│   │   ├── security.py
│   │   └── deps.py
│   ├── models/             # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── calendar_event.py
│   │   └── conversation.py
│   ├── schemas/            # Pydantic 스키마
│   ├── services/           # 비즈니스 로직
│   │   └── google_calendar.py
│   ├── config.py           # 설정
│   ├── database.py         # DB 연결
│   └── main.py             # FastAPI 앱
├── frontend/               # 프론트엔드
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/                  # 테스트
├── docker-compose.yml      # Docker 구성
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 시작하기

### 사전 요구사항

- Python 3.9+
- Docker & Docker Compose
- Google Cloud Console 계정 (Calendar API 활성화)
- OpenAI API Key

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd workspace

# 환경 변수 설정
cp .env.example .env
```

`.env` 파일을 편집하여 필요한 값들을 설정하세요:

```env
# OpenAI API Key (필수)
OPENAI_API_KEY=your-openai-api-key

# Google Calendar API (필수)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Secret (필수 - 프로덕션에서는 반드시 변경)
SECRET_KEY=your-secret-key-change-this
```

### 2. Google Calendar API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **APIs & Services > Library**에서 "Google Calendar API" 검색 및 활성화
4. **APIs & Services > Credentials**에서 OAuth 2.0 클라이언트 ID 생성
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`
5. 생성된 Client ID와 Client Secret을 `.env` 파일에 추가

### 3. Docker로 실행 (권장)

```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f app
```

애플리케이션이 다음 주소에서 실행됩니다:
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/docs
- **Frontend**: `frontend/index.html` 파일을 브라우저로 열기

### 4. 로컬 개발 환경 (선택)

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (PostgreSQL 실행 필요)
# Docker로 PostgreSQL만 실행
docker-compose up -d db redis

# 애플리케이션 실행
uvicorn app.main:app --reload

# 새 터미널에서 프론트엔드 서버 실행 (선택)
cd frontend
python -m http.server 3000
```

## 📖 사용 방법

### 1. 회원가입 및 로그인

1. 프론트엔드 페이지에서 "회원가입" 클릭
2. 이메일, 사용자 이름, 비밀번호 입력
3. 로그인

### 2. Google Calendar 연결

1. 대시보드에서 "Google Calendar 연결" 버튼 클릭
2. Google 계정으로 로그인
3. Calendar 접근 권한 승인

### 3. AI 에이전트와 대화

채팅 입력창에 자연어로 일정을 입력하세요:

```
내일 오후 3시에 팀 회의 일정 잡아줘
```

```
다음주 월요일 오전 10시부터 11시까지 치과 예약
```

```
12월 25일 저녁 7시 크리스마스 파티, 장소는 강남역 근처 레스토랑
```

AI가 자동으로:
- 날짜와 시간 파싱
- 이벤트 제목, 설명 추출
- 구글 캘린더에 이벤트 생성
- 생성 결과 확인

### 4. API 사용 (선택)

#### 인증

```bash
# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-username&password=your-password"

# 응답에서 access_token 획득
```

#### AI 에이전트와 대화

```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내일 오후 3시 회의 일정 잡아줘",
    "session_id": "unique-session-id"
  }'
```

#### 일정 조회

```bash
curl -X GET "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html

# 특정 테스트 파일 실행
pytest tests/test_auth.py

# 특정 테스트 함수 실행
pytest tests/test_auth.py::test_register_user
```

## 🏗️ 아키텍처

### 1. 요청 흐름

```
사용자 → Frontend → FastAPI → AI Agent → LangChain → OpenAI GPT-4
                                    ↓
                            Google Calendar API
                                    ↓
                              PostgreSQL DB
```

### 2. AI 에이전트 구조

- **LangChain Agent**: OpenAI Functions Agent
- **Tools**: 
  - `create_calendar_event`: 일정 생성
  - `list_calendar_events`: 일정 조회
  - `update_calendar_event`: 일정 수정
  - `delete_calendar_event`: 일정 삭제
- **Memory**: Database-backed conversation memory
- **Vector Store**: ChromaDB for knowledge base

### 3. 데이터베이스 스키마

- **users**: 사용자 정보 및 Google OAuth 토큰
- **calendar_events**: 생성된 캘린더 이벤트 기록
- **conversations**: 대화 히스토리

## 🔧 설정 옵션

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `OPENAI_MODEL` | 사용할 OpenAI 모델 | `gpt-4-turbo-preview` |
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID | 필수 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 시크릿 | 필수 |
| `DATABASE_URL` | PostgreSQL 연결 URL | `postgresql://...` |
| `SECRET_KEY` | JWT 시크릿 키 | 변경 필요 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT 토큰 만료 시간 | `30` |

자세한 내용은 `.env.example` 파일을 참조하세요.

## 📊 API 문서

애플리케이션 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 문제 해결

### Google Calendar 연결 실패

- Google Cloud Console에서 OAuth 2.0 설정 확인
- Redirect URI가 정확히 설정되어 있는지 확인
- Google Calendar API가 활성화되어 있는지 확인

### AI 에이전트 응답 없음

- OpenAI API 키가 유효한지 확인
- OpenAI API 사용량 한도 확인
- 로그에서 오류 메시지 확인: `docker-compose logs -f app`

### 데이터베이스 연결 오류

- Docker 컨테이너 상태 확인: `docker-compose ps`
- PostgreSQL 컨테이너 로그 확인: `docker-compose logs db`

## 📝 라이선스

MIT License

## 👨‍💻 개발자

LangChain Google Calendar AI Agent

## 🙏 감사의 말

- [LangChain](https://www.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI](https://openai.com/)
- [Google Calendar API](https://developers.google.com/calendar)

---

**Made with ❤️ using LangChain and FastAPI**
