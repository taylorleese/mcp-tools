"""Tests for context_manager.storage module."""

import pytest

from context_manager.storage import ContextStorage
from models import ContextContent, ContextEntry, Todo, TodoListSnapshot


@pytest.mark.unit
class TestContextStorage:
    """Test context storage operations."""

    def test_save_and_get_context(self, temp_db_path: str, sample_context: ContextEntry) -> None:
        """Test saving and retrieving a context."""
        storage = ContextStorage(temp_db_path)

        # Save context
        storage.save_context(sample_context)
        context_id = sample_context.id
        assert context_id is not None

        # Retrieve context
        retrieved = storage.get_context(context_id)
        assert retrieved is not None
        assert retrieved.title == sample_context.title
        assert retrieved.type == sample_context.type
        assert set(retrieved.tags) == set(sample_context.tags)
        assert retrieved.project_path == sample_context.project_path

    def test_list_contexts(self, temp_db_path: str, sample_context: ContextEntry) -> None:
        """Test listing contexts."""
        storage = ContextStorage(temp_db_path)

        # Save multiple contexts
        storage.save_context(sample_context)

        context2 = ContextEntry(
            type="suggestion",
            title="Second Context",
            content=ContextContent(suggestions="Another test context"),
            tags=["test"],
            project_path="/test/project",
        )
        storage.save_context(context2)

        # List contexts
        contexts = storage.list_contexts(limit=10)
        assert len(contexts) == 2
        assert contexts[0].title in ["Test Context", "Second Context"]

    def test_search_contexts_by_query(self, temp_db_path: str, sample_context: ContextEntry) -> None:
        """Test searching contexts by content."""
        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        # Search by content
        results = storage.search_contexts(query="test context")
        assert len(results) >= 1
        assert any(c.title == "Test Context" for c in results)

    def test_filter_contexts_by_type(self, temp_db_path: str) -> None:
        """Test filtering contexts by type."""
        storage = ContextStorage(temp_db_path)

        # Save different types
        code_context = ContextEntry(
            type="code",
            title="Code Context",
            content=ContextContent(code={"test.py": "Some code"}),
            project_path="/test/project",
        )
        suggestion_context = ContextEntry(
            type="suggestion",
            title="Suggestion Context",
            content=ContextContent(suggestions="A suggestion"),
            project_path="/test/project",
        )

        storage.save_context(code_context)
        storage.save_context(suggestion_context)

        # Filter by type
        code_results = storage.list_contexts(type_filter="code")
        assert len(code_results) == 1
        assert code_results[0].type == "code"

        suggestion_results = storage.list_contexts(type_filter="suggestion")
        assert len(suggestion_results) == 1
        assert suggestion_results[0].type == "suggestion"

    def test_delete_context(self, temp_db_path: str, sample_context: ContextEntry) -> None:
        """Test deleting a context."""
        storage = ContextStorage(temp_db_path)

        # Save and delete
        storage.save_context(sample_context)
        result = storage.delete_context(sample_context.id)
        assert result is True

        # Verify deletion
        retrieved = storage.get_context(sample_context.id)
        assert retrieved is None

    def test_get_contexts_by_project(self, temp_db_path: str) -> None:
        """Test getting contexts filtered by project path."""
        storage = ContextStorage(temp_db_path)

        # Save contexts in different projects
        context1 = ContextEntry(
            type="code",
            title="Project A Context",
            content=ContextContent(code={"a.py": "Content A"}),
            project_path="/project/a",
        )
        context2 = ContextEntry(
            type="code",
            title="Project B Context",
            content=ContextContent(code={"b.py": "Content B"}),
            project_path="/project/b",
        )

        storage.save_context(context1)
        storage.save_context(context2)

        # Get contexts for project A
        project_a_contexts = storage.list_contexts(project_path="/project/a")
        assert len(project_a_contexts) == 1
        assert project_a_contexts[0].title == "Project A Context"

        # Get contexts for project B
        project_b_contexts = storage.list_contexts(project_path="/project/b")
        assert len(project_b_contexts) == 1
        assert project_b_contexts[0].title == "Project B Context"

    def test_get_contexts_by_session(self, temp_db_path: str) -> None:
        """Test getting contexts filtered by session ID."""
        storage = ContextStorage(temp_db_path)

        # Save contexts in different sessions
        context1 = ContextEntry(
            type="code",
            title="Session 1 Context",
            content=ContextContent(code={"s1.py": "Content 1"}),
            project_path="/test/project",
            session_id="session-1",
        )
        context2 = ContextEntry(
            type="code",
            title="Session 2 Context",
            content=ContextContent(code={"s2.py": "Content 2"}),
            project_path="/test/project",
            session_id="session-2",
        )

        storage.save_context(context1)
        storage.save_context(context2)

        # Get contexts for session 1
        session1_contexts = storage.get_session_contexts("session-1")
        assert len(session1_contexts) == 1
        assert session1_contexts[0].title == "Session 1 Context"


@pytest.mark.unit
class TestTodoStorage:
    """Test todo storage operations."""

    def test_save_and_get_todo_snapshot(self, temp_db_path: str, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test saving and retrieving a todo snapshot."""
        storage = ContextStorage(temp_db_path)

        # Save snapshot
        storage.save_todo_snapshot(sample_todo_snapshot)
        snapshot_id = sample_todo_snapshot.id
        assert snapshot_id is not None

        # Retrieve snapshot
        retrieved = storage.get_todo_snapshot(snapshot_id)
        assert retrieved is not None
        assert len(retrieved.todos) == 3
        assert retrieved.context == sample_todo_snapshot.context
        assert retrieved.project_path == sample_todo_snapshot.project_path

    def test_list_todo_snapshots(self, temp_db_path: str, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test listing todo snapshots."""
        storage = ContextStorage(temp_db_path)

        # Save multiple snapshots
        storage.save_todo_snapshot(sample_todo_snapshot)

        snapshot2 = TodoListSnapshot(
            todos=[Todo(content="New task", status="pending", activeForm="Doing new task")],
            context="Second snapshot",
            project_path="/test/project",
        )
        storage.save_todo_snapshot(snapshot2)

        # List snapshots
        snapshots = storage.list_todo_snapshots(limit=10)
        assert len(snapshots) == 2

    def test_get_active_todo_snapshot(self, temp_db_path: str, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test getting the most recent active snapshot for a project."""
        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        # Get active snapshot
        active = storage.get_active_todo_snapshot(sample_todo_snapshot.project_path)
        assert active is not None
        assert active.project_path == sample_todo_snapshot.project_path
        assert len(active.todos) == 3

    def test_search_todo_snapshots(self, temp_db_path: str, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test searching todo snapshots."""
        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        # Search by content
        results = storage.search_todo_snapshots(query="Testing todos")
        assert len(results) >= 1

    def test_delete_todo_snapshot(self, temp_db_path: str, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test deleting a todo snapshot."""
        storage = ContextStorage(temp_db_path)

        # Save and delete
        storage.save_todo_snapshot(sample_todo_snapshot)
        result = storage.delete_todo_snapshot(sample_todo_snapshot.id)
        assert result is True

        # Verify deletion
        retrieved = storage.get_todo_snapshot(sample_todo_snapshot.id)
        assert retrieved is None

    def test_todo_snapshots_by_project(self, temp_db_path: str) -> None:
        """Test getting todo snapshots filtered by project."""
        storage = ContextStorage(temp_db_path)

        # Save snapshots in different projects
        snapshot1 = TodoListSnapshot(
            todos=[Todo(content="Task A", status="pending", activeForm="Doing task A")],
            context="Project A work",
            project_path="/project/a",
        )
        snapshot2 = TodoListSnapshot(
            todos=[Todo(content="Task B", status="pending", activeForm="Doing task B")],
            context="Project B work",
            project_path="/project/b",
        )

        storage.save_todo_snapshot(snapshot1)
        storage.save_todo_snapshot(snapshot2)

        # List for specific project
        project_a_snapshots = storage.list_todo_snapshots(project_path="/project/a")
        assert len(project_a_snapshots) == 1
        assert project_a_snapshots[0].project_path == "/project/a"
