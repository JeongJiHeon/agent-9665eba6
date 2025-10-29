# 기여 가이드

Google Calendar AI Agent 프로젝트에 기여해주셔서 감사합니다! 🎉

## 기여 방법

### 1. 이슈 생성

버그를 발견하거나 새로운 기능을 제안하고 싶다면:

1. [GitHub Issues](../../issues)에서 이슈 생성
2. 명확한 제목과 설명 작성
3. 재현 가능한 예제 제공 (버그의 경우)
4. 레이블 추가 (bug, enhancement, question 등)

### 2. Pull Request

1. **Fork & Clone**

```bash
git clone https://github.com/your-username/calendar-agent.git
cd calendar-agent
```

2. **브랜치 생성**

```bash
git checkout -b feature/amazing-feature
# 또는
git checkout -b bugfix/fix-issue-123
```

3. **개발**

- 코드 스타일 가이드 준수
- 테스트 작성
- 문서 업데이트

4. **커밋**

```bash
git add .
git commit -m "Add amazing feature"
```

커밋 메시지 형식:
```
<type>: <subject>

<body>

<footer>
```

타입:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

5. **Push & PR**

```bash
git push origin feature/amazing-feature
```

GitHub에서 Pull Request 생성

## 개발 환경 설정

### 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구

# 코드 포맷팅
black app/ tests/
isort app/ tests/

# 린팅
flake8 app/ tests/
pylint app/

# 타입 체킹
mypy app/
```

### 프론트엔드

```bash
cd frontend
npm install

# 린팅
npm run lint

# 포맷팅
npm run format
```

## 코드 스타일

### Python

- PEP 8 준수
- Black 포맷터 사용
- Type hints 사용
- Docstring 작성 (Google 스타일)

```python
def create_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
) -> EventCreationResult:
    """
    Create a calendar event.
    
    Args:
        summary: Event title
        start_time: Event start datetime
        end_time: Event end datetime
        
    Returns:
        EventCreationResult with success status
        
    Raises:
        ValueError: If times are invalid
    """
    pass
```

### JavaScript/React

- ESLint 설정 준수
- Prettier 포맷터 사용
- 함수형 컴포넌트 사용
- PropTypes 또는 TypeScript 사용

```javascript
/**
 * Chat message component
 * @param {Object} props - Component props
 * @param {Object} props.message - Message object
 * @returns {JSX.Element}
 */
function ChatMessage({ message }) {
  // ...
}
```

## 테스트

### 백엔드 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지
pytest --cov=app --cov-report=html

# 특정 테스트
pytest tests/test_agent.py::TestCalendarAgent::test_initialization
```

테스트 작성 예제:

```python
@pytest.mark.asyncio
async def test_create_event(mock_calendar_service):
    """Test event creation."""
    result = await mock_calendar_service.create_event(
        summary="Test Event",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
    )
    
    assert result.success is True
    assert result.event_id is not None
```

### 프론트엔드 테스트

```bash
# 테스트 실행
npm test

# 커버리지
npm test -- --coverage
```

## 문서

### README 업데이트

새로운 기능을 추가할 때는 README.md 업데이트:

- 기능 설명 추가
- 사용 예제 추가
- API 문서 업데이트

### Docstring

모든 함수/클래스에 docstring 작성:

```python
class CalendarAgent:
    """
    Main Calendar Agent class.
    
    This agent processes natural language input and creates
    calendar events using LangChain and Google Calendar API.
    
    Attributes:
        llm: Language model instance
        agent_executor: LangChain agent executor
        
    Example:
        >>> agent = CalendarAgent()
        >>> agent.initialize()
        >>> result = await agent.process_message("내일 미팅")
    """
```

## 리뷰 프로세스

Pull Request 제출 후:

1. 자동 CI/CD 체크 통과
2. 코드 리뷰어 배정
3. 리뷰어 피드백 반영
4. 승인 후 메인 브랜치에 머지

## 버그 리포트

버그를 발견하면 다음 정보 포함:

- **환경**: OS, Python/Node 버전, Docker 버전
- **재현 단계**: 1, 2, 3...
- **예상 동작**: 어떻게 동작해야 하는지
- **실제 동작**: 실제로 어떻게 동작하는지
- **로그/스크린샷**: 에러 메시지나 스크린샷

## 기능 제안

새 기능 제안 시:

- **사용 사례**: 왜 이 기능이 필요한지
- **제안 구현**: 어떻게 구현할지 (선택)
- **대안**: 다른 방법이 있는지 (선택)

## 질문 및 토론

- GitHub Discussions 사용
- 명확하고 구체적인 질문
- 관련 코드/로그 포함

## 행동 강령

- 존중하고 포용적인 태도
- 건설적인 피드백
- 협력적인 문제 해결

## 라이선스

기여한 코드는 프로젝트의 MIT 라이선스를 따릅니다.

---

다시 한번 기여해주셔서 감사합니다! 🙏
