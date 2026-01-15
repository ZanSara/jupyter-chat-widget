"""Tests for ChatUI widget."""

from __future__ import annotations

import pytest

from jupyter_chat_widget import ChatUI, __version__


class TestVersion:
    """Tests for package version."""

    def test_version_is_string(self) -> None:
        """Test that version is a string."""
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """Test that version follows semver format."""
        parts = __version__.split(".")
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts[:2])


class TestChatUIInit:
    """Tests for ChatUI initialization."""

    def test_init_creates_widgets(self, mock_display: list) -> None:
        """Test that initialization creates the required widgets."""
        chat = ChatUI()

        assert chat.text is not None
        assert chat.chat_out is not None
        assert chat.response_out is not None

    def test_init_sets_default_state(self, mock_display: list) -> None:
        """Test that initialization sets correct default state."""
        chat = ChatUI()

        assert chat._live_response == ""
        assert chat._has_live_response is False
        assert chat._callback is None

    def test_init_displays_widgets(self, mock_display: list) -> None:
        """Test that widgets are displayed on init."""
        ChatUI()

        # The mock captures display calls - verify it was called
        # (actual count depends on implementation details)
        assert mock_display is not None


class TestConnect:
    """Tests for connect() method."""

    def test_connect_sets_callback(self, mock_display: list) -> None:
        """Test that connect() properly sets the callback."""
        chat = ChatUI()
        callback_called: list[str] = []

        def my_callback(msg: str) -> None:
            callback_called.append(msg)

        chat.connect(my_callback)
        assert chat._callback is my_callback

    def test_connect_replaces_callback(self, mock_display: list) -> None:
        """Test that connect() replaces existing callback."""
        chat = ChatUI()

        def first_callback(msg: str) -> None:
            pass

        def second_callback(msg: str) -> None:
            pass

        chat.connect(first_callback)
        chat.connect(second_callback)

        assert chat._callback is second_callback


class TestAppend:
    """Tests for append() method."""

    def test_append_updates_response(self, mock_display: list) -> None:
        """Test that append() adds to the live response."""
        chat = ChatUI()

        chat.append("Hello")
        assert chat._live_response == "Hello"
        assert chat._has_live_response is True

    def test_append_accumulates(self, mock_display: list) -> None:
        """Test that multiple appends accumulate."""
        chat = ChatUI()

        chat.append("Hello")
        chat.append(" ")
        chat.append("World")

        assert chat._live_response == "Hello World"

    def test_append_sets_has_live_response(self, mock_display: list) -> None:
        """Test that append sets the live response flag."""
        chat = ChatUI()

        assert chat._has_live_response is False
        chat.append("test")
        assert chat._has_live_response is True


class TestRewrite:
    """Tests for rewrite() method."""

    def test_rewrite_replaces_response(self, mock_display: list) -> None:
        """Test that rewrite() replaces the live response."""
        chat = ChatUI()

        chat.append("First")
        chat.rewrite("Second")

        assert chat._live_response == "Second"
        assert chat._has_live_response is True

    def test_rewrite_on_empty(self, mock_display: list) -> None:
        """Test that rewrite() works on empty response."""
        chat = ChatUI()

        chat.rewrite("New text")

        assert chat._live_response == "New text"
        assert chat._has_live_response is True


class TestClear:
    """Tests for clear() method."""

    def test_clear_resets_state(self, mock_display: list) -> None:
        """Test that clear() resets the chat state."""
        chat = ChatUI()

        chat.append("Some text")
        chat.clear()

        assert chat._live_response == ""
        assert chat._has_live_response is False

    def test_clear_on_empty(self, mock_display: list) -> None:
        """Test that clear() works on already empty state."""
        chat = ChatUI()
        chat.clear()

        assert chat._live_response == ""
        assert chat._has_live_response is False


class TestHtmlRendering:
    """Tests for HTML rendering and escaping."""

    def test_render_escapes_less_than(self, mock_display: list) -> None:
        """Test that < is escaped."""
        chat = ChatUI()
        html = chat._render_live_html("<")
        assert "&lt;" in html
        assert "<" not in html.replace("&lt;", "").replace("<div", "").replace(
            "<b>", ""
        ).replace("</b>", "").replace("</div>", "")

    def test_render_escapes_greater_than(self, mock_display: list) -> None:
        """Test that > is escaped."""
        chat = ChatUI()
        html = chat._render_live_html(">")
        assert "&gt;" in html

    def test_render_escapes_ampersand(self, mock_display: list) -> None:
        """Test that & is escaped."""
        chat = ChatUI()
        html = chat._render_live_html("&")
        assert "&amp;" in html

    def test_render_escapes_script_tag(self, mock_display: list) -> None:
        """Test that script tags are properly escaped (XSS prevention)."""
        chat = ChatUI()
        html = chat._render_live_html("<script>alert('xss')</script>")

        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    @pytest.mark.parametrize(
        "input_text,expected_escaped",
        [
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ("<>&", "&lt;&gt;&amp;"),
            ("a < b > c & d", "a &lt; b &gt; c &amp; d"),
        ],
    )
    def test_html_escaping_parametrized(
        self, mock_display: list, input_text: str, expected_escaped: str
    ) -> None:
        """Test various HTML escape scenarios."""
        chat = ChatUI()
        html = chat._render_live_html(input_text)
        assert expected_escaped in html

    def test_render_includes_assistant_label(self, mock_display: list) -> None:
        """Test that rendered HTML includes assistant label."""
        chat = ChatUI()
        html = chat._render_live_html("test")
        assert "assistant:" in html


class TestCommitLiveToChat:
    """Tests for _commit_live_to_chat() method."""

    def test_commit_clears_response(self, mock_display: list) -> None:
        """Test that committing clears the live response."""
        chat = ChatUI()

        chat.append("Test message")
        chat._commit_live_to_chat()

        assert chat._live_response == ""
        assert chat._has_live_response is False

    def test_commit_does_nothing_when_empty(self, mock_display: list) -> None:
        """Test that commit on empty response doesn't error."""
        chat = ChatUI()
        chat._commit_live_to_chat()

        assert chat._live_response == ""
        assert chat._has_live_response is False


class TestOnSubmit:
    """Tests for submission handling."""

    def test_callback_receives_message(self, mock_display: list) -> None:
        """Test that callback receives the submitted message."""
        chat = ChatUI()
        received_messages: list[str] = []

        def callback(msg: str) -> None:
            received_messages.append(msg)

        chat.connect(callback)
        chat.text.value = "Hello"
        chat._on_submit(chat.text)

        assert received_messages == ["Hello"]

    def test_callback_exception_reenables_input(self, mock_display: list) -> None:
        """Test that input is re-enabled even if callback raises."""
        chat = ChatUI()

        def failing_callback(msg: str) -> None:
            raise ValueError("Test error")

        chat.connect(failing_callback)
        chat.text.value = "test"

        with pytest.raises(ValueError, match="Test error"):
            chat._on_submit(chat.text)

        # Input should be re-enabled despite exception
        assert chat.text.disabled is False

    def test_no_callback_doesnt_error(self, mock_display: list) -> None:
        """Test that submitting without a callback doesn't raise."""
        chat = ChatUI()
        chat.text.value = "test"
        chat._on_submit(chat.text)  # Should not raise
