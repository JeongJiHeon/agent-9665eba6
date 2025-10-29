"""Prompt templates for the calendar agent."""

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

# System prompt for the calendar agent
CALENDAR_AGENT_SYSTEM_PROMPT = """당신은 구글 캘린더를 관리하는 AI 어시스턴트입니다. 
사용자가 자연어로 일정을 말하면, 그것을 이해하고 구글 캘린더에 이벤트를 생성합니다.

주요 기능:
1. 자연어로 표현된 일정을 파싱하여 이해
2. 날짜, 시간, 제목, 설명, 장소 등을 정확하게 추출
3. 구글 캘린더 API를 사용하여 이벤트 생성
4. 생성된 이벤트 정보를 사용자에게 확인

대화 가이드라인:
- 친근하고 도움이 되는 어투를 사용하세요
- 일정 정보가 불명확하면 명확히 질문하세요
- 날짜/시간이 명시되지 않으면 기본값을 제안하세요
- 이벤트 생성 후 확인 메시지를 제공하세요

현재 시간: {current_time}
오늘 날짜: {current_date}

사용 가능한 도구:
- create_calendar_event: 구글 캘린더에 이벤트를 생성합니다
- search_calendar_events: 기존 일정을 검색합니다
- parse_datetime: 자연어를 날짜/시간으로 변환합니다
- search_similar_events: 유사한 이벤트를 검색합니다 (RAG)
"""

# Prompt template for the agent
AGENT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", CALENDAR_AGENT_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Datetime parsing prompt
DATETIME_PARSER_PROMPT = PromptTemplate(
    input_variables=["text", "current_date", "current_time"],
    template="""다음 텍스트에서 날짜와 시간 정보를 추출하세요.

텍스트: {text}
현재 날짜: {current_date}
현재 시간: {current_time}

다음 형식으로 응답하세요:
시작 날짜: YYYY-MM-DD
시작 시간: HH:MM
종료 날짜: YYYY-MM-DD  
종료 시간: HH:MM

명시되지 않은 정보는 합리적으로 추정하세요.
- "내일"이면 현재 날짜 + 1일
- "다음주 월요일"이면 다음주 월요일 날짜
- 시간이 없으면 09:00을 기본값으로
- 종료 시간이 없으면 시작 시간 + 1시간

응답:
"""
)

# Event summary generation prompt
EVENT_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["user_input", "event_details"],
    template="""사용자 입력을 기반으로 캘린더 이벤트 요약을 생성하세요.

사용자 입력: {user_input}
추출된 정보: {event_details}

다음 형식으로 이벤트 정보를 구조화하세요:

제목: [간단명료한 제목]
설명: [상세 설명 (선택)]
시작: [시작 날짜 및 시간]
종료: [종료 날짜 및 시간]
장소: [장소 (선택)]

응답:
"""
)

# Confirmation message prompt
CONFIRMATION_PROMPT = PromptTemplate(
    input_variables=["event", "event_link"],
    template="""다음 일정이 생성되었습니다:

📅 {event[summary]}
🕐 {event[start]} ~ {event[end]}
📍 {event[location]}

캘린더 링크: {event_link}

일정이 성공적으로 추가되었습니다! 다른 도움이 필요하신가요?
"""
)

# RAG context prompt
RAG_CONTEXT_PROMPT = PromptTemplate(
    input_variables=["query", "context"],
    template="""사용자 질문과 관련된 과거 이벤트 정보입니다:

{context}

이 정보를 참고하여 사용자 질문에 답변하세요:
{query}

답변:
"""
)
