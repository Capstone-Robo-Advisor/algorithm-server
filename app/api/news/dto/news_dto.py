from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsArticleDTO(BaseModel):
    """뉴스 기사 데이터 전송 객체"""
    id: str
    title: str
    source: Optional[str] = None
    published_date: Optional[datetime] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
