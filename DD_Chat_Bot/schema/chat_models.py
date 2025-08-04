from pydantic import BaseModel, Field
from typing import Optional

class ChatInput(BaseModel):
    """Input model for chat requests"""
    user_id: str = Field(..., description="Unique identifier for the user")
    query: str = Field(..., description="User's message or question", min_length=1)

class ChatResponse(BaseModel):
    """Response model for chat requests"""
    response: str = Field(..., description="Bot's response to the user's query")
    topic: Optional[str]  = Field(default="general", description="Classified topic of the query")
    confidence: Optional[str]  = Field(default=None, description="Confidence level of topic classification")
    user_id: Optional[str] = Field(default=None, description="User ID for session tracking") 