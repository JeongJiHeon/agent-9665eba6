# 📅 구글 캘린더 AI 에이전트

LangChain 기반의 구글 캘린더 자동 관리 AI 에이전트 애플리케이션입니다. 사용자가 자연어로 일정을 입력하면 자동으로 구글 캘린더에 이벤트를 생성하고 관리합니다.

## ✨ 주요 기능

- 🤖 **자연어 처리**: 사용자의 자연어 입력을 이해하고 일정으로 변환
- 📆 **구글 캘린더 통합**: 구글 캘린더 API를 통한 완전한 일정 관리
- 💬 **대화형 인터페이스**: AI 어시스턴트와의 자연스러운 대화
- 🔄 **실시간 동기화**: 생성, 수정, 삭제된 일정이 즉시 반영
- 📊 **대화 기록 관리**: 과거 대화 내용 저장 및 조회
- 🎨 **현대적인 UI**: 반응형 웹 대시보드

## 🏗️ 기술 스택

### Backend
- **Framework**: FastAPI
- **AI Framework**: LangChain
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Vector DB**: ChromaDB
- **Database**: PostgreSQL
- **Auth**: Google OAuth 2.0, JWT
- **Testing**: pytest

### Frontend
- **HTML5, CSS3, JavaScript (Vanilla)**
- **반응형 디자인**

### Infrastructure
- **Docker & Docker Compose**
- **Nginx (리버스 프록시)**

## 📋 사전 요구사항

1. **Docker 및 Docker Compose** 설치
2. **OpenAI API 키** 또는 **Anthropic API 키**
3. **Google Cloud Console** 프로젝트 및 OAuth 2.0 자격증명

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd workspace
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 입력합니다:

```bash
cp .env.example .env
```

필수 환경 변수:
- `OPENAI_API_KEY` 또는 `ANTHROPIC_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `SECRET_KEY`

### 3. Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "라이브러리"에서 "Google Calendar API" 활성화
4. "사용자 인증 정보" > "OAuth 2.0 클라이언트 ID" 생성
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI: `http://localhost:8000/api/v1/auth/google/callback`
5. 클라이언트 ID와 시크릿을 `.env` 파일에 추가

### 4. Docker Compose로 실행

```bash
docker-compose up -d
```

### 5. 애플리케이션 접속

- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🛠️ 로컬 개발 환경 설정

### Backend 개발

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp ../.env.example ../.env
# .env 파일을 편집하여 필요한 값 입력

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 테스트 실행

```bash
cd backend

# 모든 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=app --cov-report=html

# 특정 테스트 파일 실행
pytest tests/test_agent.py -v
```

## 📁 프로젝트 구조

```
workspace/
├── backend/
│   ├── app/
│   │   ├── agents/              # LangChain 에이전트
│   │   │   ├── calendar_agent.py
│   │   │   └── tools.py
│   │   ├── routes/              # API 엔드포인트
│   │   │   ├── agent.py
│   │   │   └── calendar.py
│   │   ├── services/            # 비즈니스 로직
│   │   │   ├── agent_service.py
│   │   │   └── calendar_service.py
│   │   ├── models/              # 데이터베이스 모델
│   │   ├── database/            # DB 설정
│   │   ├── utils/               # 유틸리티
│   │   ├── config.py            # 설정 관리
│   │   └── main.py              # FastAPI 앱
│   ├── tests/                   # 테스트 코드
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docker-compose.yml
├── nginx.conf
├── .env.example
└── README.md
```

## 🎯 사용 예시

### 일정 추가

```
사용자: "내일 오후 3시에 팀 회의 일정 추가해줘"
AI: "이벤트가 성공적으로 생성되었습니다: '팀 회의' (2024-01-16T15:00:00 ~ 2024-01-16T16:00:00)"
```

### 일정 조회

```
사용자: "이번 주 일정 보여줘"
AI: "일정 목록:
- 팀 회의 (시작: 2024-01-16T15:00:00) [ID: abc123]
- 프로젝트 리뷰 (시작: 2024-01-18T10:00:00) [ID: def456]"
```

### 복잡한 일정

```
사용자: "다음 주 월요일 오전 10시부터 12시까지 서울 강남구에서 클라이언트 미팅"
AI: "이벤트가 성공적으로 생성되었습니다: '클라이언트 미팅' (위치: 서울 강남구)"
```

## 📚 API 문서

API 엔드포인트는 FastAPI의 자동 문서화 기능을 통해 제공됩니다:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

#### 에이전트
- `POST /api/v1/agent/chat` - AI 에이전트와 대화
- `GET /api/v1/agent/history/{user_id}` - 대화 기록 조회
- `DELETE /api/v1/agent/history/{user_id}` - 대화 기록 삭제

#### 캘린더
- `POST /api/v1/calendar/events` - 이벤트 생성
- `POST /api/v1/calendar/events/list` - 이벤트 목록 조회
- `PUT /api/v1/calendar/events` - 이벤트 수정
- `DELETE /api/v1/calendar/events/{user_id}/{event_id}` - 이벤트 삭제
- `GET /api/v1/calendar/auth/url/{user_id}` - Google OAuth URL 생성

## 🔧 설정

### LLM 제공자 변경

`.env` 파일에서 LLM 제공자를 변경할 수 있습니다:

```bash
# OpenAI 사용
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your-key

# Anthropic Claude 사용
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=your-key
```

### 에이전트 설정

```bash
AGENT_MAX_ITERATIONS=10        # 최대 반복 횟수
AGENT_MEMORY_SIZE=10           # 메모리 크기
LLM_TEMPERATURE=0.7            # 응답 다양성
MAX_TOKENS=2000                # 최대 토큰 수
```

## 🐛 문제 해결

### Docker 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker-compose logs backend

# 컨테이너 재시작
docker-compose restart backend
```

### Google OAuth 인증 오류

1. Google Cloud Console에서 리디렉션 URI가 정확한지 확인
2. Google Calendar API가 활성화되어 있는지 확인
3. OAuth 동의 화면이 설정되어 있는지 확인

### LLM API 오류

1. API 키가 올바른지 확인
2. API 사용량 제한을 확인
3. 로그에서 상세 오류 메시지 확인

## 🧪 테스트

```bash
# 전체 테스트 실행
cd backend
pytest

# 특정 테스트만 실행
pytest tests/test_agent.py::TestCalendarAgent::test_agent_initialization

# 커버리지 리포트 생성
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📊 로깅

로그는 다음 위치에 저장됩니다:
- **개발 환경**: `backend/logs/app.log`
- **Docker 환경**: `backend_logs` 볼륨

로그 레벨 변경:
```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔒 보안

- Google OAuth 2.0을 통한 안전한 인증
- JWT 기반 세션 관리
- 환경 변수를 통한 민감한 정보 관리
- CORS 설정으로 허용된 도메인만 접근 가능

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.

## 👥 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

## 🗺️ 로드맵

- [ ] 반복 일정 지원
- [ ] 다중 사용자 관리
- [ ] 이메일 알림
- [ ] 캘린더 공유 기능
- [ ] 모바일 앱
- [ ] 음성 인식 통합
- [ ] 다국어 지원
- [ ] 통계 및 분석 대시보드

## 📝 변경 로그

### v1.0.0 (2024-01-15)
- 초기 릴리스
- LangChain 기반 AI 에이전트
- Google Calendar API 통합
- FastAPI 백엔드
- 반응형 웹 프론트엔드
- Docker 컨테이너화
- 테스트 코드 포함

---

**Powered by LangChain, FastAPI, and Google Calendar API** 🚀
