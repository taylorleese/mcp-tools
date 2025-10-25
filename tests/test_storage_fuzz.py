"""Property-based fuzz tests for storage layer using Hypothesis.

These tests generate random inputs to discover edge cases and potential crashes.
"""

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from context_manager.storage import ContextStorage
from models import ContextContent, ContextEntry, Todo, TodoListSnapshot


# Custom strategies for generating valid but random data
@st.composite
def context_content_strategy(draw: st.DrawFn) -> ContextContent:
    """Generate random ContextContent instances."""
    return ContextContent(
        messages=draw(st.one_of(st.none(), st.lists(st.text(min_size=0, max_size=1000), max_size=10))),
        code=draw(st.one_of(st.none(), st.dictionaries(st.text(min_size=1, max_size=100), st.text(max_size=5000), max_size=5))),
        suggestions=draw(st.one_of(st.none(), st.text(max_size=5000))),
        errors=draw(st.one_of(st.none(), st.text(max_size=5000))),
    )


@st.composite
def context_entry_strategy(draw: st.DrawFn) -> ContextEntry:
    """Generate random but valid ContextEntry instances."""
    context_types = st.sampled_from(["conversation", "code", "suggestion", "error"])

    return ContextEntry(
        type=draw(context_types),
        title=draw(st.text(min_size=1, max_size=200)),
        content=draw(context_content_strategy()),
        tags=draw(st.lists(st.text(min_size=1, max_size=50).filter(lambda x: "," not in x), max_size=10)),
        project_path=draw(st.text(min_size=1, max_size=500)),
        session_id=draw(st.one_of(st.none(), st.uuids().map(str))),
        metadata=draw(
            st.dictionaries(st.text(min_size=1, max_size=50), st.one_of(st.text(max_size=100), st.integers(), st.booleans()), max_size=5)
        ),
    )


@st.composite
def todo_strategy(draw: st.DrawFn) -> Todo:
    """Generate random Todo instances."""
    statuses = st.sampled_from(["pending", "in_progress", "completed"])

    return Todo(
        content=draw(st.text(min_size=1, max_size=500)),
        status=draw(statuses),
        activeForm=draw(st.text(min_size=1, max_size=500)),
    )


@st.composite
def todo_snapshot_strategy(draw: st.DrawFn) -> TodoListSnapshot:
    """Generate random TodoListSnapshot instances."""
    return TodoListSnapshot(
        project_path=draw(st.text(min_size=1, max_size=500)),
        git_branch=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        todos=draw(st.lists(todo_strategy(), min_size=0, max_size=20)),
        context=draw(st.one_of(st.none(), st.text(max_size=1000))),
        is_active=draw(st.booleans()),
    )


class TestContextStorageFuzz:
    """Fuzz tests for ContextStorage."""

    @given(context=context_entry_strategy())
    @settings(max_examples=50, deadline=1000)
    def test_fuzz_save_and_retrieve_context(self, context: ContextEntry) -> None:
        """Fuzz test context save and retrieve with random data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save context
            storage.save_context(context)

            # Retrieve and verify
            retrieved = storage.get_context(context.id)
            assert retrieved is not None
            assert retrieved.id == context.id
            assert retrieved.type == context.type
            assert retrieved.title == context.title
            assert retrieved.project_path == context.project_path

    @given(contexts=st.lists(context_entry_strategy(), min_size=0, max_size=20))
    @settings(max_examples=20, deadline=2000)
    def test_fuzz_list_contexts(self, contexts: list[ContextEntry]) -> None:
        """Fuzz test listing contexts with random data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save all contexts
            for context in contexts:
                storage.save_context(context)

            # List all contexts
            results = storage.list_contexts(limit=100)
            assert len(results) == len(contexts)

    @given(
        context=context_entry_strategy(),
        search_text=st.text(min_size=1, max_size=100),
    )
    @settings(max_examples=30, deadline=1000)
    def test_fuzz_search_contexts(self, context: ContextEntry, search_text: str) -> None:
        """Fuzz test context search with random queries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save context
            storage.save_context(context)

            # Search should not crash regardless of query
            results = storage.search_contexts(search_text)
            assert isinstance(results, list)

    @given(
        title=st.text(min_size=1, max_size=500),
        content_text=st.text(max_size=10000),
    )
    @settings(max_examples=30, deadline=1000)
    def test_fuzz_large_content(self, title: str, content_text: str) -> None:
        """Fuzz test with large content sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            context = ContextEntry(
                type="code",
                title=title,
                content=ContextContent(suggestions=content_text),
                project_path="/test/project",
            )

            storage.save_context(context)
            retrieved = storage.get_context(context.id)
            assert retrieved is not None
            assert retrieved.content.suggestions == content_text


class TestTodoStorageFuzz:
    """Fuzz tests for todo snapshots in ContextStorage."""

    @given(snapshot=todo_snapshot_strategy())
    @settings(max_examples=50, deadline=1000)
    def test_fuzz_save_and_retrieve_snapshot(self, snapshot: TodoListSnapshot) -> None:
        """Fuzz test todo snapshot save and retrieve."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save snapshot
            storage.save_todo_snapshot(snapshot)

            # Retrieve and verify
            retrieved = storage.get_todo_snapshot(snapshot.id)
            assert retrieved is not None
            assert retrieved.id == snapshot.id
            assert retrieved.project_path == snapshot.project_path
            assert len(retrieved.todos) == len(snapshot.todos)

    @given(snapshots=st.lists(todo_snapshot_strategy(), min_size=0, max_size=15))
    @settings(max_examples=20, deadline=2000)
    def test_fuzz_list_snapshots(self, snapshots: list[TodoListSnapshot]) -> None:
        """Fuzz test listing snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save all snapshots
            for snapshot in snapshots:
                storage.save_todo_snapshot(snapshot)

            # List all snapshots
            results = storage.list_todo_snapshots(limit=100)
            assert len(results) == len(snapshots)

    @given(
        snapshot=todo_snapshot_strategy(),
        search_text=st.text(min_size=1, max_size=100),
    )
    @settings(max_examples=30, deadline=1000)
    def test_fuzz_search_snapshots(self, snapshot: TodoListSnapshot, search_text: str) -> None:
        """Fuzz test snapshot search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            # Save snapshot
            storage.save_todo_snapshot(snapshot)

            # Search should not crash
            results = storage.search_todo_snapshots(search_text)
            assert isinstance(results, list)


class TestStorageEdgeCases:
    """Edge case fuzz tests for storage."""

    @given(tags=st.lists(st.text(min_size=1, max_size=50).filter(lambda x: "," not in x), min_size=0, max_size=50))
    @settings(max_examples=30)
    def test_fuzz_many_tags(self, tags: list[str]) -> None:
        """Test handling of many tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            context = ContextEntry(
                type="code",
                title="Test",
                content=ContextContent(suggestions="test"),
                tags=tags,
                project_path="/test",
            )

            storage.save_context(context)
            retrieved = storage.get_context(context.id)
            assert retrieved is not None
            assert set(retrieved.tags) == set(tags)

    @given(special_chars=st.text(alphabet=st.characters(blacklist_categories=["Cs"]), min_size=1, max_size=100))
    @settings(max_examples=30)
    def test_fuzz_special_characters(self, special_chars: str) -> None:
        """Test handling of special characters in content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            context = ContextEntry(
                type="code",
                title=special_chars[:50] if special_chars else "test",
                content=ContextContent(suggestions=special_chars),
                project_path="/test",
            )

            storage.save_context(context)
            retrieved = storage.get_context(context.id)
            assert retrieved is not None
            assert retrieved.content.suggestions == special_chars

    @given(path=st.text(min_size=1, max_size=1000))
    @settings(max_examples=30)
    def test_fuzz_project_paths(self, path: str) -> None:
        """Test various project path formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = ContextStorage(str(Path(tmpdir) / "test.db"))

            context = ContextEntry(
                type="code",
                title="Test",
                content=ContextContent(suggestions="test"),
                project_path=path,
            )

            storage.save_context(context)
            retrieved = storage.get_context(context.id)
            assert retrieved is not None
            assert retrieved.project_path == path
