# 🚀 상세 설정 가이드

이 문서는 구글 캘린더 AI 에이전트를 처음부터 설정하는 상세한 가이드입니다.

## 목차

1. [Google Cloud 설정](#1-google-cloud-설정)
2. [OpenAI API 설정](#2-openai-api-설정)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [Docker 실행](#4-docker-실행)
5. [로컬 개발 환경](#5-로컬-개발-환경)

## 1. Google Cloud 설정

### 1.1 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 드롭다운 클릭
3. "새 프로젝트" 클릭
4. 프로젝트 이름 입력 (예: "calendar-ai-agent")
5. "만들기" 클릭

### 1.2 Google Calendar API 활성화

1. 왼쪽 메뉴에서 "API 및 서비스" > "라이브러리" 선택
2. 검색창에 "Google Calendar API" 입력
3. "Google Calendar API" 선택
4. "사용 설정" 클릭

### 1.3 OAuth 2.0 자격증명 생성

1. "API 및 서비스" > "사용자 인증 정보" 선택
2. "+ 사용자 인증 정보 만들기" 클릭
3. "OAuth 클라이언트 ID" 선택

### 1.4 OAuth 동의 화면 구성 (처음인 경우)

1. "외부" 사용자 유형 선택 (테스트용)
2. 앱 정보 입력:
   - 앱 이름: "Google Calendar AI Agent"
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일
3. "저장 후 계속" 클릭
4. 범위 추가:
   - ".../auth/calendar" 선택
5. "저장 후 계속" 클릭
6. 테스트 사용자 추가 (본인 이메일 추가)
7. "저장 후 계속" 클릭

### 1.5 OAuth 클라이언트 ID 생성

1. 애플리케이션 유형: "웹 애플리케이션" 선택
2. 이름: "Calendar AI Agent Web Client"
3. 승인된 자바스크립트 원본:
   - `http://localhost`
   - `http://localhost:8000`
4. 승인된 리디렉션 URI:
   - `http://localhost:8000/api/v1/auth/google/callback`
5. "만들기" 클릭
6. 클라이언트 ID와 클라이언트 보안 비밀번호 복사 (나중에 사용)

## 2. OpenAI API 설정

### 2.1 OpenAI 계정 생성

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 계정 생성 또는 로그인

### 2.2 API 키 생성

1. 우측 상단 프로필 메뉴에서 "API keys" 선택
2. "+ Create new secret key" 클릭
3. 이름 입력 (예: "calendar-agent")
4. API 키 복사 (한 번만 표시됨!)
5. 안전한 곳에 저장

### 2.3 결제 설정 (필요한 경우)

1. "Settings" > "Billing" 메뉴
2. 결제 방법 추가
3. 사용량 한도 설정 (권장)

## 3. 환경 변수 설정

### 3.1 .env 파일 생성

프로젝트 루트에서:

```bash
cp .env.example .env
```

### 3.2 필수 값 입력

`.env` 파일을 편집기로 열고 다음 값을 입력:

```bash
# OpenAI API (필수)
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Google Calendar API (필수)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# JWT 시크릿 키 생성 (필수)
# 다음 명령어로 생성할 수 있습니다:
# openssl rand -hex 32
SECRET_KEY=your-generated-secret-key-here

# 선택사항 - 기본값 사용 가능
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
DEBUG=true
```

### 3.3 시크릿 키 생성

터미널에서 실행:

```bash
# macOS/Linux
openssl rand -hex 32

# Python 사용 (모든 OS)
python -c "import secrets; print(secrets.token_hex(32))"
```

생성된 값을 `SECRET_KEY`에 입력합니다.

## 4. Docker 실행

### 4.1 Docker 설치 확인

```bash
docker --version
docker-compose --version
```

설치가 안 되어 있다면 [Docker 공식 사이트](https://docs.docker.com/get-docker/)에서 설치.

### 4.2 애플리케이션 시작

```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
```

### 4.3 상태 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 모든 컨테이너가 "Up" 상태여야 함
```

### 4.4 접속 확인

1. 웹 브라우저에서 http://localhost 접속
2. 프론트엔드 대시보드 확인
3. http://localhost:8000/docs 에서 API 문서 확인

### 4.5 Google OAuth 인증

1. 대시보드에서 "구글 캘린더 연결" 버튼 클릭
2. Google 로그인 페이지로 이동
3. 계정 선택 및 권한 승인
4. 리디렉션 후 "구글 캘린더와 연결됨" 상태 확인

## 5. 로컬 개발 환경

Docker 없이 로컬에서 개발하려면:

### 5.1 Python 환경 설정

```bash
cd backend

# Python 3.11+ 필요
python --version

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 5.2 PostgreSQL 설치 및 실행

#### macOS (Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
createdb calendar_agent
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb calendar_agent
```

#### Windows
1. [PostgreSQL 공식 사이트](https://www.postgresql.org/download/windows/)에서 설치
2. pgAdmin을 사용하여 `calendar_agent` 데이터베이스 생성

### 5.3 환경 변수 설정

```bash
# DATABASE_URL 수정 (로컬 PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/calendar_agent
```

### 5.4 백엔드 실행

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.5 프론트엔드 실행

간단한 HTTP 서버:

```bash
# Python 사용
cd frontend
python -m http.server 3000

# Node.js 사용 (npx)
cd frontend
npx http-server -p 3000
```

또는 VSCode의 Live Server 확장 사용.

### 5.6 개발 모드 확인

- 백엔드: http://localhost:8000
- 프론트엔드: http://localhost:3000
- API 문서: http://localhost:8000/docs

## 🔍 문제 해결

### Port Already in Use

```bash
# macOS/Linux
sudo lsof -i :8000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Docker 빌드 실패

```bash
# 캐시 없이 다시 빌드
docker-compose build --no-cache

# 볼륨 삭제 후 재시작
docker-compose down -v
docker-compose up -d
```

### Google OAuth 리디렉션 오류

1. Google Cloud Console에서 리디렉션 URI 확인
2. http:// vs https:// 확인
3. 포트 번호 확인 (8000)
4. 브라우저 쿠키/캐시 삭제

### Database Connection Error

```bash
# PostgreSQL 실행 확인
docker-compose ps db

# 데이터베이스 접속 테스트
docker-compose exec db psql -U postgres -d calendar_agent

# 연결 문자열 확인
echo $DATABASE_URL
```

## 📞 추가 지원

더 많은 도움이 필요하시면:
- GitHub Issues에 문제 등록
- 상세한 로그 첨부 (`docker-compose logs`)
- 환경 정보 포함 (OS, Docker 버전 등)

---

**축하합니다! 🎉 이제 구글 캘린더 AI 에이전트를 사용할 준비가 되었습니다!**
