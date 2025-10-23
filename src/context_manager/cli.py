"""CLI interface for context manager."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from src.context_manager.openai_client import ChatGPTClient
from src.context_manager.storage import ContextStorage
from src.models import ContextContent, ContextEntry

# Load environment variables
load_dotenv()


def get_storage() -> ContextStorage:
    """Get the context storage instance."""
    db_path = os.getenv("CHATMCP_DB_PATH", "./data/contexts.db")
    return ContextStorage(db_path)


@click.group()
def cli() -> None:
    """Claude Code ↔ ChatGPT context sharing CLI."""


@cli.command()
@click.option("--type", "context_type", required=True, help="Context type")
@click.option("--title", required=True, help="Context title")
@click.option("--content", help="Content as text")
@click.option("--file", "file_path", type=click.Path(exists=True), help="Read content from file")
@click.option("--tags", help="Comma-separated tags")
def save(
    context_type: str,
    title: str,
    content: str | None,
    file_path: str | None,
    tags: str | None,
) -> None:
    """Save context without querying ChatGPT."""
    if not content and not file_path:
        click.echo("Error: Either --content or --file must be provided", err=True)
        sys.exit(1)

    # Read content from file if provided
    if file_path:
        content = Path(file_path).read_text()

    # Parse content based on type
    context_content = _parse_content(context_type, content or "")

    # Create context entry
    context_entry = ContextEntry(
        type=context_type,
        title=title,
        content=context_content,
        tags=tags.split(",") if tags else [],
    )

    # Save to storage
    storage = get_storage()
    storage.save_context(context_entry)

    click.echo(f"✓ Context saved (ID: {context_entry.id})")


@cli.command("save-and-query")
@click.option("--type", "context_type", required=True, help="Context type")
@click.option("--title", required=True, help="Context title")
@click.option("--content", help="Content as text")
@click.option("--file", "file_path", type=click.Path(exists=True), help="Read content from file")
@click.option("--tags", help="Comma-separated tags")
def save_and_query(
    context_type: str,
    title: str,
    content: str | None,
    file_path: str | None,
    tags: str | None,
) -> None:
    """Save context and get ChatGPT's second opinion."""
    if not content and not file_path:
        click.echo("Error: Either --content or --file must be provided", err=True)
        sys.exit(1)

    # Read content from file if provided
    if file_path:
        content = Path(file_path).read_text()

    # Parse content based on type
    context_content = _parse_content(context_type, content or "")

    # Create context entry
    context_entry = ContextEntry(
        type=context_type,
        title=title,
        content=context_content,
        tags=tags.split(",") if tags else [],
    )

    # Save to storage
    storage = get_storage()
    storage.save_context(context_entry)
    click.echo(f"✓ Context saved (ID: {context_entry.id})")

    # Query ChatGPT
    click.echo("⏳ Querying ChatGPT...")
    try:
        chatgpt = ChatGPTClient()
        response = chatgpt.get_second_opinion(context_entry)

        # Update context with response
        storage.update_chatgpt_response(context_entry.id, response)

        # Display response
        click.echo("\n" + "=" * 60)
        click.echo("ChatGPT's Second Opinion:")
        click.echo("=" * 60)
        click.echo(response)
        click.echo("=" * 60)
        click.echo("\n✓ Response saved to context entry")

    except Exception as e:
        click.echo(f"\n✗ Error querying ChatGPT: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("context_id")
def query(context_id: str) -> None:
    """Query ChatGPT about an existing context."""
    storage = get_storage()
    context = storage.get_context(context_id)

    if not context:
        click.echo(f"Error: Context {context_id} not found", err=True)
        sys.exit(1)

    click.echo(f"⏳ Querying ChatGPT about '{context.title}'...")
    try:
        chatgpt = ChatGPTClient()
        response = chatgpt.get_second_opinion(context)

        # Update context with response
        storage.update_chatgpt_response(context.id, response)

        # Display response
        click.echo("\n" + "=" * 60)
        click.echo("ChatGPT's Second Opinion:")
        click.echo("=" * 60)
        click.echo(response)
        click.echo("=" * 60)
        click.echo("\n✓ Response saved to context entry")

    except Exception as e:
        click.echo(f"\n✗ Error querying ChatGPT: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--type", "context_type", help="Filter by type")
@click.option("--limit", default=20, help="Number of results")
@click.option("--offset", default=0, help="Offset for pagination")
def list_contexts(context_type: str | None, limit: int, offset: int) -> None:
    """List saved contexts."""
    storage = get_storage()
    contexts = storage.list_contexts(type_filter=context_type, limit=limit, offset=offset)

    if not contexts:
        click.echo("No contexts found")
        return

    click.echo(f"\nFound {len(contexts)} contexts:\n")
    for ctx in contexts:
        has_response = "✓" if ctx.chatgpt_response else "○"
        tags_str = f" [{', '.join(ctx.tags)}]" if ctx.tags else ""
        click.echo(
            f"{has_response} [{ctx.type}] {ctx.title}{tags_str}\n   ID: {ctx.id}\n   {ctx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )


@cli.command()
@click.argument("query_text")
@click.option("--type", "context_type", help="Filter by type")
@click.option("--limit", default=10, help="Number of results")
def search(query_text: str, context_type: str | None, limit: int) -> None:
    """Search contexts."""
    storage = get_storage()
    contexts = storage.search_contexts(query_text, type_filter=context_type, limit=limit)

    if not contexts:
        click.echo(f"No contexts found matching '{query_text}'")
        return

    click.echo(f"\nFound {len(contexts)} contexts matching '{query_text}':\n")
    for ctx in contexts:
        has_response = "✓" if ctx.chatgpt_response else "○"
        tags_str = f" [{', '.join(ctx.tags)}]" if ctx.tags else ""
        click.echo(
            f"{has_response} [{ctx.type}] {ctx.title}{tags_str}\n   ID: {ctx.id}\n   {ctx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )


@cli.command()
@click.argument("context_id")
def show(context_id: str) -> None:
    """Show full details of a context."""
    storage = get_storage()
    context = storage.get_context(context_id)

    if not context:
        click.echo(f"Error: Context {context_id} not found", err=True)
        sys.exit(1)

    click.echo(f"\n{'=' * 60}")
    click.echo(f"Title: {context.title}")
    click.echo(f"Type: {context.type}")
    click.echo(f"ID: {context.id}")
    click.echo(f"Timestamp: {context.timestamp}")
    if context.tags:
        click.echo(f"Tags: {', '.join(context.tags)}")
    click.echo(f"{'=' * 60}\n")

    if context.content.messages:
        click.echo("Messages:")
        for msg in context.content.messages:
            click.echo(f"  {msg}")

    if context.content.code:
        click.echo("\nCode:")
        for file_path, code in context.content.code.items():
            click.echo(f"\n  File: {file_path}")
            click.echo(f"  {'-' * 50}")
            click.echo(f"  {code}")

    if context.content.suggestions:
        click.echo(f"\nSuggestion:\n{context.content.suggestions}")

    if context.content.errors:
        click.echo(f"\nErrors:\n{context.content.errors}")

    if context.chatgpt_response:
        click.echo(f"\n{'=' * 60}")
        click.echo("ChatGPT's Response:")
        click.echo(f"{'=' * 60}")
        click.echo(context.chatgpt_response)


def _parse_content(context_type: str, content: str) -> ContextContent:
    """Parse content based on context type."""
    context_content = ContextContent()

    if context_type == "conversation":
        context_content.messages = [content]
    elif context_type == "code":
        context_content.code = {"inline": content}
    elif context_type == "suggestion":
        context_content.suggestions = content
    elif context_type == "error":
        context_content.errors = content
    else:
        # Default to suggestions
        context_content.suggestions = content

    return context_content


if __name__ == "__main__":
    cli()
