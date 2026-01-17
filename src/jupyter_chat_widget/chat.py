"""Chat UI widget for Jupyter notebooks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import ipywidgets as widgets
from IPython.display import HTML, display

if TYPE_CHECKING:
    pass

# Type alias for message callback
MessageCallback = Callable[[str], None]


class ChatUI:
    """A simple chat UI widget for Jupyter notebooks.

    This widget provides a text input for user messages and displays
    a conversation history with streaming assistant responses.

    Example:
        >>> chat = ChatUI()
        >>> def my_handler(message: str) -> None:
        ...     for word in message.split():
        ...         chat.append(word + " ")
        >>> chat.connect(my_handler)
    """

    def __init__(self, escape_html: bool = False) -> None:
        """Initialize the ChatUI widget.

        Args:
            wrap_text: Whether to wrap long text in the output. Defaults to True.
                When False, long lines will scroll horizontally.
        """
        self.escape_html = escape_html
        self.text: widgets.Text = widgets.Text(description="user: ")
        self.chat_out: widgets.Output = widgets.Output()
        self.response_out: widgets.Output = widgets.Output()
        self._live_response: str = ""
        self._has_live_response: bool = False
        self._callback: MessageCallback | None = None
        display(self.chat_out, self.response_out, self.text)
        self.text.on_submit(self._on_submit)

    def _on_submit(self, _) -> None:
        """Handle text submission."""
        message = self.text.value
        if not message:
            return
        self._commit_live_to_chat()
        with self.chat_out:
            display(HTML("<b>user:</b> " + message))
        self.text.value = ""
        self.text.disabled = True
        try:
            if self._callback is not None:
                self._callback(message)
        finally:
            self.text.disabled = False

    def connect(self, callback: MessageCallback) -> None:
        """Connect a callback function to handle user messages.

        The callback will be invoked each time the user submits a message.
        While the callback is running, the input field is disabled.

        Args:
            callback: A function that takes a message string and handles it.
                The callback can use `append()` or `rewrite()` to stream
                responses back to the user.
        """
        self._callback = callback

    def _render_live_html(self, text: str) -> str:
        """Render the live response as HTML.

        Args:
            text: The text to render.

        Returns:
            HTML string with proper escaping and styling.
        """
        if self.escape_html:
            text = (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
            )
        return f"<b>assistant:</b> {text}"

    def _update_live_line(self) -> None:
        """Update the live response display."""
        with self.response_out:
            self.response_out.clear_output(wait=True)
            display(HTML(self._render_live_html(self._live_response)))

    def _commit_live_to_chat(self) -> None:
        """Commit the live response to the chat history."""
        if self._has_live_response:
            with self.chat_out:
                display(HTML("<b>assistant:</b> " + self._live_response))
        self._live_response = ""
        self._has_live_response = False
        self._update_live_line()

    def append(self, token: str) -> None:
        """Append text to the current assistant response.

        Use this method for streaming responses token by token.

        Args:
            token: The text to append to the current response.

        Example:
            >>> for word in response.split():
            ...     chat.append(word + " ")
        """
        self._has_live_response = True
        self._live_response += token
        self._update_live_line()

    def rewrite(self, text: str) -> None:
        """Replace the entire current assistant response.

        Use this method to update the response in place, such as
        when you want to show a final formatted message.

        Args:
            text: The new text for the assistant response.

        Example:
            >>> chat.rewrite("Processing complete!")
        """
        self._has_live_response = True
        self._live_response = text
        self._update_live_line()

    def clear(self) -> None:
        """Clear all chat history and the current response.

        This resets the widget to its initial empty state.
        """
        self.chat_out.clear_output()
        self._live_response = ""
        self._has_live_response = False
        self._update_live_line()
