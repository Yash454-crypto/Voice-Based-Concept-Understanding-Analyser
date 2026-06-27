"""
src/analysis/scorer.py
=========================
Scoring Engine — produces the final understanding score for a session
by blending:

    1. Concept match result   (from src.nlp.concept_matcher)  -> WHAT was said
    2. Audio fluency features (from src.analysis.audio_features) -> HOW it was said

The concept match (semantic correctness) is weighted much more heavily
than delivery — a hesitant but correct answer should still score well,
while a fluent but wrong answer should not.

Usage:
    from src.analysis.scorer import UnderstandingScorer

    scorer = UnderstandingScorer()
    final = scorer.score(match_result_dict, audio_features_dict)
    print(final.final_score, final.grade, final.feedback_summary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------
# Result container
# ---------------------------------------------------------
@dataclass
class FinalScore:
    final_score: float                 # 0-100
    concept_score: float                # 0-100 (from concept matcher)
    fluency_score: float                # 0-100 (from audio features)
    grade: str                           # e.g. "A", "B", "C", "D", "F"
    understanding_level: str             # e.g. "Strong", "Moderate", "Weak"
    passed: bool
    feedback_summary: list = field(default_factory=list)
    strengths: list = field(default_factory=list)
    improvement_areas: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "final_score": self.final_score,
            "concept_score": self.concept_score,
            "fluency_score": self.fluency_score,
            "grade": self.grade,
            "understanding_level": self.understanding_level,
            "passed": self.passed,
            "feedback_summary": self.feedback_summary,
            "strengths": self.strengths,
            "improvement_areas": self.improvement_areas,
        }


class ScoringError(Exception):
    """Raised when scoring inputs are invalid or incomplete."""


# ---------------------------------------------------------
# Main scoring engine
# ---------------------------------------------------------
class UnderstandingScorer:
    """
    Combines concept-match correctness and audio delivery fluency into
    a single final understanding score, plus a qualitative breakdown.

    Parameters
    ----------
    concept_weight : float
        Weight given to conceptual correctness (default 0.8 — content
        matters far more than delivery for assessing UNDERSTANDING).
    fluency_weight : float
        Weight given to speech delivery/fluency (default 0.2).
    pass_threshold : float
        Minimum final_score (0-100) to be considered a "pass".
    """

    GRADE_BANDS = [
        (90, "A"),
        (75, "B"),
        (60, "C"),
        (40, "D"),
        (0, "F"),
    ]

    def __init__(
        self,
        concept_weight: float = 0.8,
        fluency_weight: float = 0.2,
        pass_threshold: float = 60.0,
    ):
        if abs((concept_weight + fluency_weight) - 1.0) > 1e-6:
            raise ValueError("concept_weight + fluency_weight must sum to 1.0")

        self.concept_weight = concept_weight
        self.fluency_weight = fluency_weight
        self.pass_threshold = pass_threshold

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------
    def score(
        self,
        match_result: dict,
        audio_features: Optional[dict] = None,
    ) -> FinalScore:
        """
        Compute the final blended understanding score.

        Parameters
        ----------
        match_result : dict
            Output of ConceptMatcher.match(...).to_dict() — must contain
            'overall_score', 'matched_keywords', 'missing_keywords'.
        audio_features : dict, optional
            Output of AudioFeatureExtractor.extract(...).to_dict().
            If omitted, the score is based on concept match alone
            (weights are renormalized automatically).
        """
        self._validate_match_result(match_result)

        concept_score = float(match_result["overall_score"])

        if audio_features is not None:
            fluency_score = float(audio_features.get("fluency_score", 0.0))
            final = (self.concept_weight * concept_score) + (self.fluency_weight * fluency_score)
        else:
            fluency_score = 0.0
            final = concept_score  # no audio signal -> content score only

        final = round(max(0.0, min(100.0, final)), 1)
        grade = self._score_to_grade(final)
        level = match_result.get("understanding_level") or self._score_to_level(concept_score)
        passed = final >= self.pass_threshold

        strengths, improvements, summary = self._build_feedback(
            match_result, audio_features, concept_score, fluency_score, final
        )

        return FinalScore(
            final_score=final,
            concept_score=round(concept_score, 1),
            fluency_score=round(fluency_score, 1),
            grade=grade,
            understanding_level=level,
            passed=passed,
            feedback_summary=summary,
            strengths=strengths,
            improvement_areas=improvements,
        )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------
    @staticmethod
    def _validate_match_result(match_result: dict) -> None:
        if not isinstance(match_result, dict):
            raise ScoringError("match_result must be a dict (use MatchResult.to_dict()).")
        if "overall_score" not in match_result:
            raise ScoringError("match_result is missing 'overall_score'.")

    # -----------------------------------------------------
    # Score -> grade / level mapping
    # -----------------------------------------------------
    def _score_to_grade(self, score: float) -> str:
        for threshold, grade in self.GRADE_BANDS:
            if score >= threshold:
                return grade
        return "F"

    @staticmethod
    def _score_to_level(score: float) -> str:
        if score >= 80:
            return "Strong"
        if score >= 60:
            return "Moderate"
        if score >= 40:
            return "Weak"
        return "Very Weak"

    # -----------------------------------------------------
    # Feedback generation
    # -----------------------------------------------------
    def _build_feedback(
        self, match_result: dict, audio_features: Optional[dict],
        concept_score: float, fluency_score: float, final_score: float,
    ) -> tuple:
        strengths, improvements, summary = [], [], []

        matched = match_result.get("matched_keywords", [])
        partial = match_result.get("partially_matched_keywords", [])
        missing = match_result.get("missing_keywords", [])

        if matched:
            strengths.append(f"Correctly covered: {', '.join(matched)}.")
        if partial:
            strengths.append(f"Touched on related ideas for: {', '.join(partial)} (consider using more precise terms).")
        if missing:
            improvements.append(f"Did not mention: {', '.join(missing)}.")

        if concept_score >= 80:
            summary.append("Strong conceptual understanding demonstrated.")
        elif concept_score >= 60:
            summary.append("Moderate understanding — some key ideas were missing or underdeveloped.")
        elif concept_score >= 40:
            summary.append("Weak understanding — most key concepts were not clearly explained.")
        else:
            summary.append("Very weak understanding — the response did not address the core concept.")

        if audio_features is not None:
            notes = audio_features.get("fluency_notes", [])
            if notes:
                improvements.extend(notes)
            elif fluency_score >= 85:
                strengths.append("Delivered the answer fluently with good pacing.")

        if final_score >= self.pass_threshold:
            summary.append(f"Overall result: PASS ({final_score}/100).")
        else:
            summary.append(f"Overall result: NOT YET PASSING ({final_score}/100) — review the missing concepts above.")

        return strengths, improvements, summary


# ---------------------------------------------------------
# Convenience function (matches the original stub signature)
# ---------------------------------------------------------
def compute_understanding_score(matched: list, missing: list, audio_features: Optional[dict] = None) -> float:
    """
    Lightweight scoring helper matching the original project-scaffold
    stub signature (keyword-list based, no full MatchResult required).

    For full scoring with semantic similarity + feedback, use
    UnderstandingScorer.score() with a ConceptMatcher result instead.
    """
    total = len(matched) + len(missing)
    if total == 0:
        return 0.0
    concept_score = (len(matched) / total) * 100

    if audio_features:
        fluency_score = float(audio_features.get("fluency_score", 0.0))
        final = 0.8 * concept_score + 0.2 * fluency_score
    else:
        final = concept_score

    return round(max(0.0, min(100.0, final)), 1)


# ---------------------------------------------------------
# CLI entry point — runs the full pipeline end-to-end for manual testing
# ---------------------------------------------------------
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Score a spoken response: audio -> transcript -> concept match -> final score."
    )
    parser.add_argument("audio_path", help="Path to the audio file")
    parser.add_argument("--definition", required=True, help="Reference concept definition")
    parser.add_argument("--keywords", required=True, help="Comma-separated expected keywords")
    parser.add_argument("--engine", choices=["whisper", "vosk"], default="whisper")
    args = parser.parse_args()

    from src.speech_to_text.transcriber import Transcriber
    from src.nlp.concept_matcher import ConceptMatcher
    from src.analysis.audio_features import AudioFeatureExtractor

    transcriber = Transcriber(engine=args.engine)
    transcription = transcriber.transcribe(args.audio_path)

    matcher = ConceptMatcher()
    keywords = [k.strip() for k in args.keywords.split(",")]
    match_result = matcher.match(transcription.text, args.definition, keywords).to_dict()

    extractor = AudioFeatureExtractor()
    word_count = len(transcription.text.split())
    audio_features = extractor.extract(args.audio_path, transcript_word_count=word_count).to_dict()

    scorer = UnderstandingScorer()
    final = scorer.score(match_result, audio_features)

    print(json.dumps({
        "transcript": transcription.text,
        "match_result": match_result,
        "audio_features": audio_features,
        "final_score": final.to_dict(),
    }, indent=2))