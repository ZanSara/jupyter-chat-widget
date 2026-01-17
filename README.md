# jupyter-chat-widget

A simple chat UI widget for Jupyter notebooks with streaming response support, designed to integrate easily with LLM APIs.

> *Note: this widget uses ipywidgets<8.0.0 for compatibility with Colab.*

[![CI](https://github.com/zansara/jupyter-chat-widget/workflows/CI/badge.svg)](https://github.com/zansara/jupyter-chat-widget/actions)
[![Docs](https://github.com/zansara/jupyter-chat-widget/workflows/Deploy%20Docs/badge.svg)](https://zansara.github.io/jupyter-chat-widget/)
[![PyPI version](https://badge.fury.io/py/jupyter-chat-widget.svg)](https://badge.fury.io/py/jupyter-chat-widget)
[![Python versions](https://img.shields.io/pypi/pyversions/jupyter-chat-widget.svg)](https://pypi.org/project/jupyter-chat-widget/)

## Installation

```bash
pip install jupyter-chat-widget
```

## Quick Start

```python
from jupyter_chat_widget import ChatUI

# Create the chat widget
chat = ChatUI()

# Define a handler for user messages
def handle_message(message: str) -> None:
    # Stream a response token by token
    for word in message.split():
        chat.append(word + " ")

# Connect the handler
chat.connect(handle_message)
```

## Documentation

See the [live documentation](https://zansara.github.io/jupyter-chat-widget/) or the [example notebook](examples/basic_usage.ipynb) in `examples/`.

## API Reference

### `ChatUI`

The main chat widget class.

#### Methods

| Method | Description |
|--------|-------------|
| `connect(callback)` | Connect a callback function to handle user messages |
| `append(token)` | Append text to the current assistant response (streaming) |
| `rewrite(text)` | Replace the entire assistant response |
| `clear()` | Clear all chat history and current response |

#### Example: Streaming Responses

```python
from jupyter_chat_widget import ChatUI
from time import sleep

chat = ChatUI()

def slow_echo(message: str) -> None:
    """Echo back the message word by word."""
    for word in message.split():
        sleep(0.5)  # Simulate processing time
        chat.append(word + " ")
    chat.rewrite(f"You said: {message}")

chat.connect(slow_echo)
```

#### Example: Integration with LLM

```python
from jupyter_chat_widget import ChatUI

chat = ChatUI()

def llm_handler(message: str) -> None:
    """Stream responses from an LLM API."""
    # Replace with your LLM API call
    for token in your_llm_api.stream(message):
        chat.append(token)

chat.connect(llm_handler)
```

## Development

```bash
# Clone the repository
git clone https://github.com/zansara/jupyter-chat-widget.git
cd jupyter-chat-widget

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src tests
ruff format src tests

# Build the package
python -m build
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## License

MIT License - see [LICENSE](LICENSE) for details.
