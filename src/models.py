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
    project_path: str  # Required: project directory where context was created
    session_id: str | None = None  # UUID of the Claude Code session
    session_timestamp: datetime | None = None  # When the session started
    metadata: dict[str, Any] = Field(default_factory=dict)
    chatgpt_response: str | None = None
    claude_response: str | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class ContextSearchResult(BaseModel):
    """Search result with relevance scoring."""

    context: ContextEntry
    relevance_score: float = 1.0


class Todo(BaseModel):
    """Represents a single todo item."""

    content: str
    status: str  # "pending" | "in_progress" | "completed"
    activeForm: str  # noqa: N815 - matches Claude Code TodoWrite tool format


class TodoListSnapshot(BaseModel):
    """Represents a saved snapshot of a todo list."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    project_path: str
    git_branch: str | None = None
    todos: list[Todo]
    context: str | None = None
    session_context_id: str | None = None
    is_active: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config: ClassVar[ConfigDict] = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
