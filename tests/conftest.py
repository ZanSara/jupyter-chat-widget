"""Pytest configuration and fixtures for jupyter-chat-widget tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_display(monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    """Mock IPython display functions to capture displayed items.

    Returns:
        A list that will contain all items passed to display().
    """
    displayed_items: list[Any] = []

    def mock_display_func(*args: Any, **kwargs: Any) -> None:
        displayed_items.extend(args)

    monkeypatch.setattr("IPython.display.display", mock_display_func)
    return displayed_items


@pytest.fixture
def mock_widgets(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    """Mock ipywidgets to avoid requiring a Jupyter kernel.

    Returns:
        A dict containing the mock Text and Output widgets.
    """
    mock_text = MagicMock()
    mock_text.value = ""
    mock_text.disabled = False

    mock_output = MagicMock()
    mock_output.__enter__ = MagicMock(return_value=None)
    mock_output.__exit__ = MagicMock(return_value=None)

    def create_text(**kwargs: Any) -> MagicMock:
        return mock_text

    def create_output(**kwargs: Any) -> MagicMock:
        return MagicMock()

    monkeypatch.setattr("ipywidgets.Text", create_text)
    monkeypatch.setattr("ipywidgets.Output", create_output)

    return {"text": mock_text, "output": mock_output}
