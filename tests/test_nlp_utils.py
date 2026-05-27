"""Tests for NLP keyword extraction fallbacks."""

import sys

from janusz import nlp_utils


def test_extract_keywords_returns_empty_for_blank_text():
    """Blank input should never call optional NLP dependencies."""
    assert nlp_utils.extract_keywords("") == []
    assert nlp_utils.extract_keywords("   ") == []


def test_extract_keywords_fallback_finds_capitalized_and_technical_terms():
    """The built-in fallback should provide useful keywords without network access."""
    keywords = nlp_utils.extract_keywords_fallback(
        "Janusz indexes skill_packs for MCP2 agents. Janusz keeps MCP2 searchable."
    )
    by_text = {keyword.text: keyword.confidence_level for keyword in keywords}

    assert by_text["Janusz"] == "low"
    assert by_text["MCP2"] == "medium"
    assert by_text["skill_packs"] == "medium"


def test_extract_keywords_uses_fallback_when_nlp_dependencies_are_missing(monkeypatch):
    """Missing optional NLP packages should fall back to the local heuristic extractor."""
    original_import = __import__

    def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"spacy", "nltk"} or name.startswith("nltk."):
            raise ImportError(name)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked_import)
    sys.modules.pop("spacy", None)
    sys.modules.pop("nltk", None)

    keywords = nlp_utils.extract_keywords("Janusz prepares Tool123 manifests.")

    assert {keyword.text for keyword in keywords} >= {"Janusz", "Tool123"}


def test_extract_keywords_falls_back_when_nlp_runtime_fails(monkeypatch):
    """Unexpected optional NLP failures should not break core conversion."""

    def raising_nlp(_text: str):
        raise RuntimeError("optional model failed")

    monkeypatch.setattr(nlp_utils, "extract_keywords_nlp", raising_nlp)

    keywords = nlp_utils.extract_keywords("Janusz creates Package99 outputs.")

    assert {keyword.text for keyword in keywords} >= {"Janusz", "Package99"}
