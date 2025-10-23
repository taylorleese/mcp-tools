"""OpenAI API client for getting ChatGPT responses."""

import os

from openai import OpenAI

from models import ContextEntry


class ChatGPTClient:
    """Client for interacting with OpenAI's ChatGPT API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the ChatGPT client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            msg = "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable"
            raise ValueError(msg)

        self.model = model or os.getenv("CLAUDE_CONTEXT_MODEL", "gpt-5")
        self.client = OpenAI(api_key=self.api_key)

    def get_second_opinion(self, context: ContextEntry) -> str:
        """Get ChatGPT's second opinion on a context."""
        system_prompt = """You are a senior software engineering consultant providing second opinions on code, \
architecture decisions, and implementation plans from Claude Code.

Your role is to:
- Provide constructive, balanced feedback
- Highlight both strengths and potential issues
- Suggest alternatives when appropriate
- Point out edge cases or security concerns
- Be concise but thorough

Format your response clearly with sections as needed."""

        user_content = self._format_context_for_chatgpt(context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content or ""

    def _format_context_for_chatgpt(self, context: ContextEntry) -> str:
        """Format a context entry for ChatGPT consumption."""
        parts = [
            f"# Context from Claude Code: {context.title}",
            f"\n**Type:** {context.type}",
            f"**Timestamp:** {context.timestamp.isoformat()}",
        ]

        if context.tags:
            parts.append(f"**Tags:** {', '.join(context.tags)}")

        parts.append("\n## Content\n")

        # Add specific content based on type
        if context.content.messages:
            parts.append("### Conversation\n")
            for msg in context.content.messages:
                parts.append(msg)

        if context.content.code:
            parts.append("### Code\n")
            for file_path, code in context.content.code.items():
                parts.append(f"**File:** `{file_path}`\n```\n{code}\n```\n")

        if context.content.suggestions:
            parts.append(f"### Suggestion\n{context.content.suggestions}\n")

        if context.content.errors:
            parts.append(f"### Error/Debug Info\n```\n{context.content.errors}\n```\n")

        parts.append("\n---\nPlease provide a second opinion on the above context from Claude Code.")

        return "\n".join(parts)
