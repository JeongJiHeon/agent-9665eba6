# 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 프로젝트 클론

```bash
git clone <repository-url>
cd workspace
```

### 2단계: 환경 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env
```

`.env` 파일 편집:

```env
# 필수: OpenAI 또는 Anthropic API 키
OPENAI_API_KEY=sk-your-key-here
# 또는
ANTHROPIC_API_KEY=your-key-here

# Google Calendar (나중에 설정 가능)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3단계: Docker로 실행

```bash
# 모든 서비스 시작
docker-compose up --build
```

### 4단계: 브라우저에서 열기

- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 첫 번째 일정 생성하기

1. http://localhost:3000 접속
2. 입력창에 자연어로 입력:
   ```
   내일 오후 3시에 팀 미팅 일정 추가해줘
   ```
3. AI가 자동으로 일정을 생성합니다!

## Google Calendar 연동 (선택)

### Google Cloud Console 설정

1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성
3. "API 및 서비스" → "라이브러리"
4. "Google Calendar API" 검색 및 활성화
5. "사용자 인증 정보" → "OAuth 2.0 클라이언트 ID" 생성
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI: `http://localhost:8000/auth/callback`
6. `credentials.json` 다운로드
7. `.env` 파일에 Client ID와 Secret 추가

### 앱에서 인증

1. 프론트엔드에서 "Google 인증" 버튼 클릭
2. Google 계정으로 로그인
3. 권한 승인
4. 완료!

## 문제 해결

### Docker가 설치되지 않음

```bash
# macOS
brew install docker

# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# Windows
# Docker Desktop 다운로드: https://www.docker.com/products/docker-desktop
```

### Redis 연결 오류

```bash
# Redis 재시작
docker-compose restart redis
```

### API 키 오류

- `.env` 파일에 API 키가 올바르게 설정되어 있는지 확인
- `OPENAI_API_KEY` 또는 `ANTHROPIC_API_KEY` 중 하나는 필수
- API 키에 따옴표 없이 직접 입력

## 다음 단계

- [README.md](README.md) - 전체 문서
- [DEPLOYMENT.md](DEPLOYMENT.md) - 배포 가이드
- [CONTRIBUTING.md](CONTRIBUTING.md) - 기여 가이드

## 예제 질의

시도해볼 수 있는 자연어 입력:

```
내일 오후 3시에 팀 미팅
다음주 월요일 오전 10시 회의실 A에서 프로젝트 리뷰
12월 25일 저녁 6시 가족 저녁식사
이번 주 일정 알려줘
다음 달 회의 일정 찾아줘
```

즐거운 사용 되세요! 🎉
