from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TopicType(str, Enum):
    """Enumeration of possible topic types"""
    ECONOMY = "economy"
    MARKET = "market"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITIES = "commodities"
    GENERAL = "general"

class NewsSource(BaseModel):
    """Model for news source information"""
    name: str = Field(..., description="Name of the news source")
    url: str = Field(..., description="URL of the news source")
    topic: TopicType = Field(..., description="Primary topic category")
    last_updated: datetime = Field(default_factory=datetime.now)

class NewsItem(BaseModel):
    """Model for individual news items"""
    title: str = Field(..., description="News headline")
    summary: str = Field(..., description="News summary or content")
    link: str = Field(..., description="Link to full article")
    topic: TopicType = Field(..., description="Topic classification")
    date: datetime = Field(default_factory=datetime.now)
    source: str = Field(..., description="Source of the news")

class ChatSession(BaseModel):
    """Model for chat session data"""
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0, description="Number of messages in session")

class ChatMessage(BaseModel):
    """Model for individual chat messages"""
    user_id: str = Field(..., description="User who sent the message")
    query: str = Field(..., description="User's message")
    response: str = Field(..., description="Bot's response")
    topic: TopicType = Field(..., description="Classified topic")
    confidence: float = Field(..., description="Classification confidence")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class HealthStatus(BaseModel):
    """Model for health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: Optional[str] = Field(default=None, description="API version")
    uptime: Optional[float] = Field(default=None, description="Service uptime in seconds")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = Field(default=None, description="Request identifier for tracking")

class TopicClassificationResult(BaseModel):
    """Model for topic classification results"""
    topic: TopicType = Field(..., description="Classified topic")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)")
    method_results: Dict[str, Any] = Field(..., description="Results from each classification method")
    all_votes: Dict[str, float] = Field(..., description="Voting results from all methods") 