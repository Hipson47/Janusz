"""Import-safe tests for optional AI integration models."""

import pytest

from janusz.ai.ai_content_analyzer import AIContentAnalyzer
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
