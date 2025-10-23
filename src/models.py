"""Data models for context entries."""

from datetime import datetime
from typing import Any, ClassVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ContextContent(BaseModel):
    """Flexible content structure for different context types."""

    messages: list[str] | None = None
    code: dict[str, str] | None = None  # file_path -> code content
    suggestions: str | None = None
    errors: str | None = None


class ContextEntry(BaseModel):
    """Represents a saved context from Claude Code."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str  # "conversation" | "code" | "suggestion" | "error"
    title: str
    content: ContextContent
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    chatgpt_response: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class ContextSearchResult(BaseModel):
    """Search result with relevance scoring."""

    context: ContextEntry
    relevance_score: float = 1.0
