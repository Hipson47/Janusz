"""Import-safe tests for optional AI integration models."""

import pytest

from janusz.ai.ai_content_analyzer import AIContentAnalyzer, OpenRouterClient
from janusz.models import AIExtractionResult, AIInsight


def test_ai_models_can_be_constructed() -> None:
    """AI response models should be importable without provider network access."""
    insight = AIInsight(
        text="Test insight",
        insight_type="improvement",
        confidence_score=0.8,
        reasoning="Test reasoning",
    )
    result = AIExtractionResult(summary="Test summary", quality_score=0.7)

    assert insight.text == "Test insight"
    assert result.summary == "Test summary"


def test_ai_analyzer_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """The AI analyzer should fail clearly without a configured OpenRouter key."""
    monkeypatch.delenv("JANUSZ_OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OpenRouter API key not provided"):
        AIContentAnalyzer()


def test_ai_client_fails_actionably_without_httpx(monkeypatch: pytest.MonkeyPatch) -> None:
    """Importing the optional AI module should not require httpx until used."""
    original_import = __import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "httpx":
            raise ImportError(name)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked_import)

    with pytest.raises(RuntimeError, match=r"janusz\[ai\]"):
        OpenRouterClient(api_key="test-key")
