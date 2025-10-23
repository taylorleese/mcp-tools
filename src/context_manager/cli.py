"""CLI interface for context manager."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from context_manager.openai_client import ChatGPTClient
from context_manager.storage import ContextStorage
from models import ContextContent, ContextEntry, Todo, TodoListSnapshot

# Load environment variables
load_dotenv()


def get_storage() -> ContextStorage:
    """Get the context storage instance."""
    db_path = os.getenv("MCP_TOOLS_DB_PATH", "./data/contexts.db")
    return ContextStorage(db_path)


@click.group()
def cli() -> None:
    """Claude Code ↔ ChatGPT context sharing CLI."""


@cli.group()
def context() -> None:
    """Manage context entries."""


@context.command()
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


@context.command("save-and-query")
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


@context.command("ask-chatgpt")
@click.argument("context_id")
@click.option("--question", help="Specific question to ask (optional)")
def ask_chatgpt(context_id: str, question: str | None) -> None:
    """Ask ChatGPT a question about a context, or get a general second opinion."""
    storage = get_storage()
    context = storage.get_context(context_id)

    if not context:
        click.echo(f"Error: Context {context_id} not found", err=True)
        sys.exit(1)

    if question:
        click.echo(f"⏳ Asking ChatGPT: '{question}'")
    else:
        click.echo(f"⏳ Querying ChatGPT about '{context.title}'...")

    try:
        chatgpt = ChatGPTClient()
        response = chatgpt.get_second_opinion(context, question)

        # Only save if it's a generic second opinion (no custom question)
        if not question:
            storage.update_chatgpt_response(context.id, response)

        # Display response
        click.echo("\n" + "=" * 60)
        header = "ChatGPT's Answer:" if question else "ChatGPT's Second Opinion:"
        click.echo(header)
        click.echo("=" * 60)
        click.echo(response)
        click.echo("=" * 60)

        if not question:
            click.echo("\n✓ Response saved to context entry")

    except Exception as e:
        click.echo(f"\n✗ Error querying ChatGPT: {e}", err=True)
        sys.exit(1)


@context.command("ask-claude")
@click.argument("context_id")
@click.option("--question", help="Specific question to ask (optional)")
def ask_claude(context_id: str, question: str | None) -> None:
    """Ask Claude a question about a context, or get a general second opinion."""
    storage = get_storage()
    context = storage.get_context(context_id)

    if not context:
        click.echo(f"Error: Context {context_id} not found", err=True)
        sys.exit(1)

    if question:
        click.echo(f"⏳ Asking Claude: '{question}'")
    else:
        click.echo(f"⏳ Querying Claude about '{context.title}'...")

    try:
        from context_manager.anthropic_client import ClaudeClient

        claude = ClaudeClient()
        response = claude.get_second_opinion(context, question)

        # Only save if it's a generic second opinion (no custom question)
        if not question:
            storage.update_claude_response(context.id, response)

        # Display response
        click.echo("\n" + "=" * 60)
        header = "Claude's Answer:" if question else "Claude's Second Opinion:"
        click.echo(header)
        click.echo("=" * 60)
        click.echo(response)
        click.echo("=" * 60)

        if not question:
            click.echo("\n✓ Response saved to context entry")

    except Exception as e:
        click.echo(f"\n✗ Error querying Claude: {e}", err=True)
        sys.exit(1)


@context.command("list")
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


@context.command("search")
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


@context.command("show")
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


# Todo group commands


@cli.group()
def todo() -> None:
    """Manage todo list snapshots."""


@todo.command("save")
@click.option("--context", "context_desc", help="Description of what you're working on")
@click.option("--link-context", "context_id", help="Link to existing context ID")
@click.option("--todos", required=True, help="JSON array of todo items")
@click.option("--project-path", help="Project path (defaults to current directory)")
def save_todos(
    context_desc: str | None,
    context_id: str | None,
    todos: str,
    project_path: str | None,
) -> None:
    """Save current todo list."""
    import json

    # Parse todos JSON
    try:
        todos_data = json.loads(todos)
        todo_list = [Todo(**todo) for todo in todos_data]
    except Exception as e:
        click.echo(f"Error: Invalid todos JSON: {e}", err=True)
        sys.exit(1)

    # Get project path
    if not project_path:
        project_path = os.getcwd()

    # Create snapshot
    snapshot = TodoListSnapshot(
        project_path=project_path,
        todos=todo_list,
        context=context_desc,
        session_context_id=context_id,
        is_active=True,
    )

    # Save to storage
    storage = get_storage()
    storage.save_todo_snapshot(snapshot)

    click.echo(f"✓ Todo list saved (ID: {snapshot.id})")
    click.echo(f"  Project: {project_path}")
    click.echo(f"  Todos: {len(todo_list)}")


@todo.command("restore")
@click.argument("snapshot_id", required=False)
@click.option("--project-path", help="Project path (defaults to current directory)")
def restore_todos(snapshot_id: str | None, project_path: str | None) -> None:
    """Restore todo list from a snapshot."""
    import json

    storage = get_storage()

    if snapshot_id:
        # Restore specific snapshot
        snapshot = storage.get_todo_snapshot(snapshot_id)
        if not snapshot:
            click.echo(f"Error: Snapshot {snapshot_id} not found", err=True)
            sys.exit(1)
    else:
        # Restore active snapshot for current project
        if not project_path:
            project_path = os.getcwd()

        snapshot = storage.get_active_todo_snapshot(project_path)
        if not snapshot:
            click.echo(f"No active todo snapshot found for {project_path}", err=True)
            sys.exit(1)

    # Display snapshot info
    click.echo(f"\n{'=' * 60}")
    click.echo(f"Snapshot ID: {snapshot.id}")
    click.echo(f"Saved: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Project: {snapshot.project_path}")
    if snapshot.context:
        click.echo(f"Context: {snapshot.context}")
    click.echo(f"{'=' * 60}\n")

    # Display todos
    click.echo("Todo List:\n")
    for i, todo_item in enumerate(snapshot.todos, 1):
        status_icon = {"pending": "○", "in_progress": "⟳", "completed": "✓"}.get(todo_item.status, "○")
        click.echo(f"{i}. {status_icon} [{todo_item.status}] {todo_item.content}")

    # Output JSON for easy parsing by Claude Code
    click.echo(f"\n{'=' * 60}")
    click.echo("JSON (for restore):")
    click.echo(json.dumps([todo.model_dump() for todo in snapshot.todos], indent=2))


@todo.command("list")
@click.option("--project-path", help="Filter by project path")
@click.option("--limit", default=20, help="Number of results")
@click.option("--offset", default=0, help="Offset for pagination")
def list_todos(project_path: str | None, limit: int, offset: int) -> None:
    """List saved todo snapshots."""
    storage = get_storage()

    # Use current directory if no project path specified
    if not project_path:
        project_path = os.getcwd()

    snapshots = storage.list_todo_snapshots(project_path=project_path, limit=limit, offset=offset)

    if not snapshots:
        click.echo(f"No todo snapshots found for {project_path}")
        return

    click.echo(f"\nFound {len(snapshots)} todo snapshots:\n")
    for snapshot in snapshots:
        active_icon = "★" if snapshot.is_active else "○"
        completed = sum(1 for t in snapshot.todos if t.status == "completed")
        total = len(snapshot.todos)

        click.echo(f"{active_icon} {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"   ID: {snapshot.id}")
        if snapshot.context:
            click.echo(f"   Context: {snapshot.context}")
        click.echo(f"   Progress: {completed}/{total} completed")
        click.echo()


@todo.command("show")
@click.argument("snapshot_id")
def show_todo(snapshot_id: str) -> None:
    """Show full details of a todo snapshot."""
    storage = get_storage()
    snapshot = storage.get_todo_snapshot(snapshot_id)

    if not snapshot:
        click.echo(f"Error: Snapshot {snapshot_id} not found", err=True)
        sys.exit(1)

    click.echo(f"\n{'=' * 60}")
    click.echo(f"Snapshot ID: {snapshot.id}")
    click.echo(f"Saved: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Project: {snapshot.project_path}")
    if snapshot.context:
        click.echo(f"Context: {snapshot.context}")
    if snapshot.session_context_id:
        click.echo(f"Linked Context: {snapshot.session_context_id}")
    click.echo(f"Active: {'Yes' if snapshot.is_active else 'No'}")
    click.echo(f"{'=' * 60}\n")

    # Display todos
    click.echo("Todo List:\n")
    for i, todo_item in enumerate(snapshot.todos, 1):
        status_icon = {"pending": "○", "in_progress": "⟳", "completed": "✓"}.get(todo_item.status, "○")
        click.echo(f"{i}. {status_icon} [{todo_item.status}] {todo_item.content}")
        click.echo(f"   Active form: {todo_item.activeForm}")
        click.echo()


if __name__ == "__main__":
    cli()
