#!/usr/bin/env python3
"""
NLP Utilities for Janusz - Document-to-TOON Pipeline

Provides NLP-based keyword extraction with graceful fallback to heuristics.
"""

import logging
import re
from typing import List

from .models import Keyword

logger = logging.getLogger(__name__)

# Common English stopwords for fallback keyword extraction
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will',
    'with', 'but', 'or', 'not', 'this', 'these', 'those', 'i', 'you', 'we',
    'they', 'he', 'she', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
    'our', 'their', 'his', 'what', 'which', 'who', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'too', 'very', 'can', 'just', 'should'
}


def extract_keywords_nlp(text: str) -> List[Keyword]:
    """
    Extract keywords using NLP libraries (spaCy preferred).

    Returns a list of keywords with confidence levels.
    """
    keywords = []

    try:
        # Try spaCy first
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Try to download the model
            logger.info("Downloading spaCy language model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"],
                         check=True, capture_output=True)
            nlp = spacy.load("en_core_web_sm")

        doc = nlp(text)

        # Extract noun phrases and important nouns
        for chunk in doc.noun_chunks:
            if len(chunk.text.strip()) > 3 and chunk.text.lower().strip() not in STOPWORDS:
                keywords.append(Keyword(
                    text=chunk.text.strip(),
                    confidence_level="high"
                ))

        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON', 'WORK_OF_ART']:
                keywords.append(Keyword(
                    text=ent.text.strip(),
                    confidence_level="high"
                ))

    except ImportError:
        logger.warning("spaCy not available, falling back to NLTK")
        try:
            # Fallback to NLTK
            import nltk
            from nltk.tag import pos_tag
            from nltk.tokenize import word_tokenize

            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)

            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)

            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)

            # Extract nouns and proper nouns
            for word, tag in tagged:
                if tag in ['NN', 'NNS', 'NNP', 'NNPS'] and len(word) > 3 and word.lower() not in STOPWORDS:
                    keywords.append(Keyword(
                        text=word,
                        confidence_level="medium"
                    ))

        except ImportError:
            logger.warning("NLTK not available, using basic heuristics")
            keywords = extract_keywords_fallback(text)

    # Limit to top keywords and deduplicate
    seen = set()
    unique_keywords = []
    for kw in keywords[:100]:  # Limit to top 100
        if kw.text.lower() not in seen:
            seen.add(kw.text.lower())
            unique_keywords.append(kw)

    return unique_keywords[:50]  # Return top 50


def extract_keywords_fallback(text: str) -> List[Keyword]:
    """
    Extract keywords using simple heuristics when NLP libraries are unavailable.

    Returns keywords with low confidence levels.
    """
    keywords = []

    # Extract capitalized words (potential proper nouns)
    capitalized = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', text)
    for word in capitalized:
        if word.lower() not in STOPWORDS:
            keywords.append(Keyword(
                text=word,
                confidence_level="low"
            ))

    # Extract technical terms (words with numbers, underscores, or mixed case)
    technical = re.findall(r'\b[a-zA-Z]+[0-9]+[a-zA-Z]*\b|\b[a-z]+_[a-z]+\b', text)
    for term in technical:
        keywords.append(Keyword(
            text=term,
            confidence_level="medium"
        ))

    # Deduplicate and limit
    seen = set()
    unique_keywords = []
    for kw in keywords[:100]:
        if kw.text.lower() not in seen:
            seen.add(kw.text.lower())
            unique_keywords.append(kw)

    return unique_keywords[:30]  # More conservative limit for fallback


def extract_keywords(text: str) -> List[Keyword]:
    """
    Main keyword extraction function with automatic NLP detection and fallback.

    Returns keywords with appropriate confidence levels.
    """
    if not text or not text.strip():
        return []

    try:
        return extract_keywords_nlp(text)
    except Exception as e:
        logger.warning(f"NLP extraction failed: {e}, falling back to heuristics")
        return extract_keywords_fallback(text)
