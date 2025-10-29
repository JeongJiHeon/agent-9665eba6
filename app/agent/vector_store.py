"""Vector store for RAG implementation"""

import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import settings


class CalendarKnowledgeBase:
    """Vector store for calendar-related knowledge"""
    
    def __init__(self):
        """Initialize the knowledge base"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create persist directory if it doesn't exist
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        # Initialize Chroma vector store
        self.vectorstore = Chroma(
            collection_name="calendar_knowledge",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the knowledge base"""
        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vectorstore.add_documents(split_docs)
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add texts to the knowledge base"""
        # Split texts
        documents = [Document(page_content=text, metadata=metadata or {}) 
                    for text, metadata in zip(texts, metadatas or [{}] * len(texts))]
        
        split_docs = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vectorstore.add_documents(split_docs)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with relevance scores"""
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Get relevant context for a query"""
        docs = self.similarity_search(query, k=k)
        
        if not docs:
            return ""
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    
    def clear(self) -> None:
        """Clear the knowledge base"""
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name="calendar_knowledge",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
    
    @staticmethod
    def load_default_knowledge() -> List[Document]:
        """Load default calendar knowledge"""
        knowledge_texts = [
            """
            캘린더 이벤트 생성 가이드:
            - 제목은 필수입니다
            - 시작 시간과 종료 시간이 필요합니다
            - 종료 시간이 없으면 시작 시간 + 1시간으로 설정됩니다
            - 한국 시간대(Asia/Seoul)를 기본으로 사용합니다
            """,
            """
            날짜/시간 표현 해석:
            - "내일": 오늘 날짜 + 1일
            - "모레": 오늘 날짜 + 2일
            - "다음주": 오늘 날짜 + 7일
            - "오전 10시": 당일 10:00
            - "오후 3시": 당일 15:00
            - "저녁 7시": 당일 19:00
            """,
            """
            일정 종류별 기본 설정:
            - 회의: 1시간 기본 길이
            - 식사: 1시간 기본 길이
            - 운동: 1시간 기본 길이
            - 수업/강의: 2시간 기본 길이
            - 미팅: 30분 기본 길이
            """,
            """
            참석자 관리:
            - 이메일 주소 형식이어야 합니다
            - 여러 참석자를 쉼표로 구분합니다
            - 참석자가 추가되면 자동으로 초대 이메일이 발송됩니다
            """,
            """
            일정 수정 및 삭제:
            - 일정을 수정하려면 이벤트 ID가 필요합니다
            - 일정 조회로 이벤트 ID를 확인할 수 있습니다
            - 삭제된 일정은 복구할 수 없습니다
            """
        ]
        
        documents = [
            Document(
                page_content=text.strip(),
                metadata={"source": "default_knowledge", "type": "guide"}
            )
            for text in knowledge_texts
        ]
        
        return documents


def initialize_knowledge_base() -> CalendarKnowledgeBase:
    """Initialize and populate the knowledge base"""
    kb = CalendarKnowledgeBase()
    
    # Load default knowledge
    default_docs = CalendarKnowledgeBase.load_default_knowledge()
    kb.add_documents(default_docs)
    
    return kb
