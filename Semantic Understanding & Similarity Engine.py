"""
tests/test_concept_matcher.py
================================
Unit tests for src/nlp/concept_matcher.py

Uses real sentence-transformers + scikit-learn (small/fast model)
since semantic similarity is the core thing being tested — mocking
it would defeat the purpose. Falls back gracefully if the model
can't be downloaded (e.g. no network in CI).
"""

import pytest

from src.nlp.concept_matcher import (
    ConceptMatcher,
    ConceptMatcherError,
    MatchResult,
    match_concepts,
)


PHOTOSYNTHESIS_DEFINITION = (
    "Photosynthesis is the process by which plants convert light energy "
    "into chemical energy, using carbon dioxide and water to produce "
    "glucose and oxygen."
)
PHOTOSYNTHESIS_KEYWORDS = [
    "light energy", "carbon dioxide", "water", "glucose", "oxygen", "chlorophyll"
]


@pytest.fixture(scope="module")
def matcher():
    return ConceptMatcher()


@pytest.fixture(scope="module")
def embedder_available(matcher):
    """Skip semantic tests gracefully if the model can't be loaded (no network)."""
    try:
        matcher._load_embedder()
        return True
    except ConceptMatcherError:
        return False


# ---------------------------------------------------------
# Input validation
# ---------------------------------------------------------
def test_empty_transcript_raises(matcher):
    with pytest.raises(ConceptMatcherError):
        matcher.match("", PHOTOSYNTHESIS_DEFINITION, PHOTOSYNTHESIS_KEYWORDS)


def test_empty_definition_raises(matcher):
    with pytest.raises(ConceptMatcherError):
        matcher.match("plants make food", "", PHOTOSYNTHESIS_KEYWORDS)


def test_invalid_weights_raise():
    with pytest.raises(ValueError):
        ConceptMatcher(weights={"semantic": 0.5, "keyword": 0.5, "lexical": 0.5})


# ---------------------------------------------------------
# Keyword coverage (doesn't require the embedding model)
# ---------------------------------------------------------
def test_keyword_coverage_exact_matches(matcher):
    transcript = "Plants use water and carbon dioxide and produce glucose and oxygen using light energy."
    score, matched, missing, partial = matcher._keyword_coverage(transcript, PHOTOSYNTHESIS_KEYWORDS)

    assert "water" in matched
    assert "carbon dioxide" in matched
    assert "glucose" in matched
    assert "oxygen" in matched
    assert "light energy" in matched
    assert score > 0


def test_keyword_coverage_no_keywords_returns_full_score(matcher):
    score, matched, missing, partial = matcher._keyword_coverage("anything at all", [])
    assert score == 100.0
    assert matched == []
    assert missing == []


# ---------------------------------------------------------
# Lexical similarity (TF-IDF) — no model download needed
# ---------------------------------------------------------
def test_lexical_similarity_identical_text_is_high():
    score = ConceptMatcher._lexical_similarity(PHOTOSYNTHESIS_DEFINITION, PHOTOSYNTHESIS_DEFINITION)
    assert score > 95.0


def test_lexical_similarity_unrelated_text_is_low():
    score = ConceptMatcher._lexical_similarity(
        "I went to the store to buy some bread and milk yesterday",
        PHOTOSYNTHESIS_DEFINITION,
    )
    assert score < 30.0


# ---------------------------------------------------------
# Score-to-level mapping
# ---------------------------------------------------------
@pytest.mark.parametrize("score,expected_level", [
    (95, "Strong"),
    (80, "Strong"),
    (65, "Moderate"),
    (45, "Weak"),
    (10, "Very Weak"),
])
def test_score_to_level_mapping(score, expected_level):
    assert ConceptMatcher._score_to_level(score) == expected_level


# ---------------------------------------------------------
# Full integration test (requires embedding model — skipped if unavailable)
# ---------------------------------------------------------
def test_full_match_strong_understanding(matcher, embedder_available):
    if not embedder_available:
        pytest.skip("sentence-transformers model unavailable (no network)")

    transcript = (
        "Photosynthesis is how plants take light energy from the sun and use "
        "carbon dioxide and water to make glucose and release oxygen."
    )
    result = matcher.match(transcript, PHOTOSYNTHESIS_DEFINITION, PHOTOSYNTHESIS_KEYWORDS)

    assert isinstance(result, MatchResult)
    assert result.overall_score > 60
    assert result.understanding_level in ("Strong", "Moderate")
    assert len(result.matched_keywords) >= 4


def test_full_match_weak_understanding_off_topic(matcher, embedder_available):
    if not embedder_available:
        pytest.skip("sentence-transformers model unavailable (no network)")

    transcript = "I think plants are green and grow in soil and need to be watered sometimes."
    result = matcher.match(transcript, PHOTOSYNTHESIS_DEFINITION, PHOTOSYNTHESIS_KEYWORDS)

    assert result.overall_score < 60
    assert len(result.missing_keywords) >= 2


# ---------------------------------------------------------
# Convenience function
# ---------------------------------------------------------
def test_match_concepts_keyword_only_fallback():
    transcript = "Water and oxygen and glucose are produced."
    result_dict = match_concepts(transcript, PHOTOSYNTHESIS_KEYWORDS)  # no definition passed

    assert result_dict["semantic_similarity"] == 0.0
    assert result_dict["lexical_similarity"] == 0.0
    assert "water" in result_dict["matched_keywords"]
    assert isinstance(result_dict["overall_score"], float)