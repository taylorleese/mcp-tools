"""Google Gemini API client for getting Gemini responses."""

import os

import google.generativeai as genai

from models import ContextEntry


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the Gemini client."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            msg = "Google API key must be provided or set in GOOGLE_API_KEY environment variable"
            raise ValueError(msg)

        self.model_name: str = model or os.getenv("MCP_TOOLZ_GEMINI_MODEL") or "gemini-2.0-flash-thinking-exp-01-21"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def get_second_opinion(self, context: ContextEntry, question: str | None = None) -> str:
        """Get Gemini's second opinion on a context, or answer a specific question.

        Args:
            context: The context entry to analyze
            question: Optional specific question to ask. If None, provides general second opinion.
        """
        if question:
            # Custom question mode
            system_instruction = """You are a senior software engineering consultant answering questions about code, \
architecture decisions, and implementation plans.

Provide clear, actionable answers based on the context provided."""
            user_content = self._format_context_for_gemini(context, question)
        else:
            # Generic second opinion mode
            system_instruction = """You are a senior software engineering consultant providing second opinions on code, \
architecture decisions, and implementation plans.

Your role is to:
- Provide constructive, balanced feedback
- Highlight both strengths and potential issues
- Suggest alternatives when appropriate
- Point out edge cases or security concerns
- Be concise but thorough

Format your response clearly with sections as needed."""
            user_content = self._format_context_for_gemini(context)

        # Configure model with system instruction
        model_with_instruction = genai.GenerativeModel(self.model_name, system_instruction=system_instruction)

        response = model_with_instruction.generate_content(user_content)

        return str(response.text)

    def _format_context_for_gemini(self, context: ContextEntry, question: str | None = None) -> str:
        """Format a context entry for Gemini consumption.

        Args:
            context: The context entry to format
            question: Optional specific question to append
        """
        parts = [
            f"# Context: {context.title}",
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

        # Add question or default request
        if question:
            parts.append(f"\n---\n**Question:** {question}")
        else:
            parts.append("\n---\nPlease provide a second opinion on the above context.")

        return "\n".join(parts)
