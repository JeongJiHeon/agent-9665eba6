# 🚀 Google Calendar AI Agent 설정 가이드

이 가이드는 Google Calendar AI Agent를 처음부터 설정하는 자세한 방법을 제공합니다.

## 목차

1. [필수 준비사항](#1-필수-준비사항)
2. [Google Cloud 설정](#2-google-cloud-설정)
3. [OpenAI API 설정](#3-openai-api-설정)
4. [프로젝트 설정](#4-프로젝트-설정)
5. [실행](#5-실행)
6. [첫 사용](#6-첫-사용)

---

## 1. 필수 준비사항

### 소프트웨어 설치

- **Docker Desktop**: [다운로드](https://www.docker.com/products/docker-desktop/)
- **Git**: [다운로드](https://git-scm.com/downloads)
- **텍스트 에디터**: VS Code 권장

### 계정 준비

- **Google 계정**: Gmail 계정
- **OpenAI 계정**: [가입](https://platform.openai.com/signup)

---

## 2. Google Cloud 설정

### Step 1: 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 드롭다운 클릭
3. "새 프로젝트" 선택
4. 프로젝트 이름 입력 (예: "calendar-ai-agent")
5. "만들기" 클릭

### Step 2: Google Calendar API 활성화

1. 좌측 메뉴에서 "APIs & Services" > "Library" 선택
2. 검색창에 "Google Calendar API" 입력
3. "Google Calendar API" 클릭
4. "사용 설정" 버튼 클릭

### Step 3: OAuth 2.0 클라이언트 ID 생성

1. "APIs & Services" > "Credentials" 선택
2. "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 선택
3. 동의 화면이 구성되지 않았다면 먼저 구성:
   - "동의 화면 구성" 클릭
   - User Type: "외부" 선택
   - 앱 이름: "Calendar AI Agent"
   - 사용자 지원 이메일: 본인 이메일
   - 저장 후 계속
   - 범위: "...googleapis.com/auth/calendar" 추가
   - 저장 후 계속

4. 다시 "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID":
   - 애플리케이션 유형: "웹 애플리케이션"
   - 이름: "Calendar AI Agent Client"
   - 승인된 자바스크립트 원본:
     ```
     http://localhost:8000
     ```
   - 승인된 리디렉션 URI:
     ```
     http://localhost:8000/api/v1/auth/google/callback
     ```
   - "만들기" 클릭

5. **중요**: 표시되는 클라이언트 ID와 클라이언트 보안 비밀을 복사하여 안전한 곳에 저장

### Step 4: 테스트 사용자 추가 (개발 중)

1. "OAuth 동의 화면" 페이지로 이동
2. "테스트 사용자" 섹션에서 "+ ADD USERS" 클릭
3. 본인의 Gmail 주소 추가

---

## 3. OpenAI API 설정

### Step 1: API 키 생성

1. [OpenAI Platform](https://platform.openai.com/) 로그인
2. 우측 상단 프로필 > "View API keys" 선택
3. "Create new secret key" 클릭
4. 이름 입력 (예: "calendar-agent")
5. **중요**: 생성된 API 키를 복사 (다시 볼 수 없음!)

### Step 2: 크레딧 확인

1. "Usage" 메뉴에서 남은 크레딧 확인
2. 필요시 "Billing" 메뉴에서 결제 정보 추가

---

## 4. 프로젝트 설정

### Step 1: 코드 다운로드

```bash
# 저장소 클론
git clone <repository-url>
cd workspace
```

### Step 2: 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env
```

### Step 3: .env 파일 편집

텍스트 에디터로 `.env` 파일을 열고 다음 값들을 설정:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx  # 3단계에서 복사한 키

# Google Calendar API
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com  # 2단계에서 복사한 ID
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx  # 2단계에서 복사한 Secret

# JWT Secret (랜덤 문자열로 변경 권장)
SECRET_KEY=your-very-secure-random-secret-key-change-this-in-production

# 나머지는 기본값 사용 가능
```

**보안 팁**: `SECRET_KEY`는 다음 명령으로 안전한 랜덤 키 생성:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 5. 실행

### Docker로 실행 (권장)

```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인 (문제 발생 시)
docker-compose logs -f app

# 실행 중인 컨테이너 확인
docker-compose ps
```

### 로컬 개발 환경 (선택사항)

```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# DB와 Redis만 Docker로 실행
docker-compose up -d db redis

# 애플리케이션 실행
uvicorn app.main:app --reload
```

### 서비스 확인

브라우저에서 다음 URL들을 확인:

- ✅ 헬스체크: http://localhost:8000/health
- 📚 API 문서: http://localhost:8000/api/docs
- 🏠 홈페이지: http://localhost:8000/

---

## 6. 첫 사용

### Step 1: 프론트엔드 열기

`frontend/index.html` 파일을 브라우저에서 열거나:

```bash
# 간단한 웹 서버로 실행
cd frontend
python -m http.server 3000
# 그 다음 http://localhost:3000 접속
```

### Step 2: 회원가입

1. 프론트엔드 페이지에서 "회원가입" 링크 클릭
2. 정보 입력:
   - 이메일: 본인 이메일
   - 사용자 이름: 원하는 닉네임
   - 비밀번호: 안전한 비밀번호
3. "가입하기" 버튼 클릭

### Step 3: 로그인

1. 생성한 계정으로 로그인
2. 대시보드로 이동

### Step 4: Google Calendar 연결

1. "Google Calendar 연결" 버튼 클릭
2. 새 창에서 Google 로그인
3. Calendar 접근 권한 승인
4. 브라우저로 자동 리디렉션

### Step 5: AI 에이전트 테스트

채팅창에 다음과 같이 입력해보세요:

```
내일 오후 3시에 팀 회의 일정 잡아줘
```

```
다음주 월요일 오전 10시부터 11시까지 치과 예약
```

AI가 자동으로 일정을 파싱하고 Google Calendar에 추가합니다!

---

## 🔧 문제 해결

### 1. Docker 실행 오류

```bash
# Docker 재시작
docker-compose down
docker-compose up -d --build

# 캐시 없이 재빌드
docker-compose build --no-cache
```

### 2. Google Calendar 연결 오류

- Redirect URI가 정확한지 확인
- 테스트 사용자에 본인 이메일이 추가되었는지 확인
- 동의 화면 설정 완료 확인

### 3. OpenAI API 오류

- API 키가 정확한지 확인
- 크레딧이 남아있는지 확인
- 로그 확인: `docker-compose logs -f app`

### 4. 데이터베이스 오류

```bash
# 데이터베이스 재시작
docker-compose restart db

# 컨테이너 삭제 후 재생성
docker-compose down -v
docker-compose up -d
```

---

## 📞 지원

문제가 계속되면 다음을 확인하세요:

1. 로그 파일 확인
   ```bash
   docker-compose logs -f
   ```

2. 환경 변수 확인
   ```bash
   cat .env
   ```

3. 포트 충돌 확인
   ```bash
   # 8000번 포트 사용 중인 프로세스 확인
   # Mac/Linux:
   lsof -i :8000
   # Windows:
   netstat -ano | findstr :8000
   ```

---

**축하합니다! 🎉** 이제 Google Calendar AI Agent를 사용할 준비가 완료되었습니다!
