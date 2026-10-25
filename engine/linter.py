"""Deterministic Prose Compiler and Quality Linter for Spoken Narration Scripts."""

import re
import math
from typing import List, Tuple, Dict, Any
from pathlib import Path

from engine.config import (
    TARGET_WORD_COUNT_MIN,
    TARGET_WORD_COUNT_MAX,
    TARGET_READING_WPM,
    MAX_SENTENCE_WORDS,
    TARGET_FLESCH_GRADE_MAX,
    TARGET_AVG_SENTENCE_WORDS,
    BANNED_WORDS,
    BANNED_PERSONIFICATION_PATTERNS,
    BANNED_AI_TRANSITIONS,
    PRONUNCIATION_REGEX,
)
from engine.models import LintViolation, LintReport


def count_syllables_word(word: str) -> int:
    """Estimates syllable count using English linguistic heuristics."""
    word = word.lower().strip(".:;?!'\"-()[]{}")
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    # Remove silent e at the end
    if word.endswith("e") and not word.endswith("le"):
        word = word[:-1]

    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    return max(1, count)


def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences while respecting common abbreviations, quotes, and newlines."""
    # Temporarily protect common abbreviations with strict word boundaries
    protected = text
    abbreviations = [
        "Mr.", "Mrs.", "Ms.", "Dr.", "Capt.", "Lt.", "Sgt.", "Col.",
        "approx.", "e.g.", "i.e.", "p.m.", "a.m.", "U.S.", "No.", "St."
    ]
    for abbr in abbreviations:
        pattern = rf"\b{re.escape(abbr)}"
        token = abbr.replace(".", "<DOT>")
        protected = re.sub(pattern, token, protected)

    # Split on newlines first to prevent cross-paragraph grouping
    paragraphs = [p.strip() for p in protected.splitlines() if p.strip()]
    sentences = []
    
    for p in paragraphs:
        # Split on terminal punctuation (fixed-width lookbehinds for python re)
        raw_sents = re.split(r"(?<=[.!?])\s+|(?<=[.!?][\"'”])\s+", p)
        for s in raw_sents:
            clean = s.replace("<DOT>", ".").strip()
            if clean:
                sentences.append(clean)
    return sentences


def extract_narration_body(full_text: str) -> Tuple[str, str]:
    """Separates narration body from metadata and source appendices."""
    # Look for appendix markers like '# Sources', '## References', '--- Sources ---'
    split_markers = [
        r"(?i)\n#+\s*sources",
        r"(?i)\n#+\s*references",
        r"(?i)\n#+\s*research dossier",
        r"(?i)\n---+\s*sources",
    ]
    body = full_text
    appendix = ""
    for marker in split_markers:
        parts = re.split(marker, body, maxsplit=1)
        if len(parts) > 1:
            body = parts[0]
            appendix = parts[1]
            break

    # Strip markdown headers (# Beat 1, etc.) for pure body word count
    clean_lines = []
    for line in body.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("#"):
            continue
        if trimmed.startswith("---"):
            continue
        clean_lines.append(line)

    clean_body = "\n".join(clean_lines).strip()
    return clean_body, appendix


def calculate_flesch_kincaid(words: List[str], sentences: List[str]) -> float:
    """Calculates Flesch-Kincaid Grade Level."""
    if not words or not sentences:
        return 0.0
    num_words = len(words)
    num_sentences = len(sentences)
    num_syllables = sum(count_syllables_word(w) for w in words)

    grade = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    return round(max(0.0, grade), 2)


class ScriptLinter:
    """Audits scripts against client-specified constraints and oral storytelling rules."""

    def __init__(self):
        self.banned_words_regex = [
            (word, re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE))
            for word in BANNED_WORDS
        ]
        self.personification_regexes = [
            (p["pattern"], re.compile(p["pattern"], re.IGNORECASE), p["reason"])
            for p in BANNED_PERSONIFICATION_PATTERNS
        ]
        self.ai_transition_regexes = [
            (t["pattern"], re.compile(t["pattern"], re.IGNORECASE), t["reason"])
            for t in BANNED_AI_TRANSITIONS
        ]

    def audit_text(self, text: str, file_path: str = "memory") -> LintReport:
        body_text, _ = extract_narration_body(text)
        words = re.findall(r"\b[A-Za-z0-9'-]+\b", body_text)
        word_count = len(words)

        sentences = split_into_sentences(body_text)
        total_sentences = len(sentences)

        flesch_grade = calculate_flesch_kincaid(words, sentences) if total_sentences > 0 else 0.0
        avg_sentence_words = round(word_count / total_sentences, 1) if total_sentences > 0 else 0.0

        violations: List[LintViolation] = []
        sentences_over_cap = 0

        # Extract pronunciation guides from body text (excluding markdown headers)
        pronunciation_matches = PRONUNCIATION_REGEX.findall(body_text)
        pronunciation_guides = [f"{match[0]} ({match[1]})" for match in pronunciation_matches]

        # Line-by-line inspection
        lines = text.splitlines()
        for line_idx, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # 1. Banned words check
            for word, regex in self.banned_words_regex:
                if regex.search(line_str):
                    violations.append(
                        LintViolation(
                            line_number=line_idx,
                            violation_type="BANNED_WORD",
                            snippet=line_str,
                            rule_reason=f"Found banned flowery/melodramatic term '{word}'.",
                            suggestion=f"Remove '{word}' and describe the concrete physical reality directly."
                        )
                    )

            # 2. Personification patterns
            for pattern_str, regex, reason in self.personification_regexes:
                match = regex.search(line_str)
                if match:
                    violations.append(
                        LintViolation(
                            line_number=line_idx,
                            violation_type="PERSONIFICATION",
                            snippet=match.group(0),
                            rule_reason=reason,
                            suggestion="Use plain subject-verb-object phrasing (e.g. 'The moon lit the road', 'The town was quiet')."
                        )
                    )

            # 3. AI transition patterns
            for pattern_str, regex, reason in self.ai_transition_regexes:
                match = regex.search(line_str)
                if match:
                    violations.append(
                        LintViolation(
                            line_number=line_idx,
                            violation_type="AI_TRANSITION",
                            snippet=match.group(0),
                            rule_reason=reason,
                            suggestion="Remove transition and jump straight to chronological timestamp or physical action."
                        )
                    )

        # Sentence-level inspection
        consecutive_questions = 0
        for sent in sentences:
            sent_words = re.findall(r"\b[A-Za-z0-9'-]+\b", sent)
            sent_len = len(sent_words)

            if sent_len > MAX_SENTENCE_WORDS:
                sentences_over_cap += 1
                violations.append(
                    LintViolation(
                        line_number=0,
                        violation_type="SENTENCE_TOO_LONG",
                        snippet=sent,
                        rule_reason=f"Sentence is {sent_len} words long (hard cap is {MAX_SENTENCE_WORDS}). Spoken stories must be easy to follow.",
                        suggestion="Break into 2 or 3 shorter, punchier declarative sentences."
                    )
                )

            # Check consecutive rhetorical questions
            if sent.strip().endswith("?"):
                consecutive_questions += 1
                if consecutive_questions >= 2:
                    violations.append(
                        LintViolation(
                            line_number=0,
                            violation_type="RHETORICAL_QUESTION",
                            snippet=sent,
                            rule_reason="Multiple consecutive rhetorical questions detected. Listeners lose momentum.",
                            suggestion="Delete rhetorical questions and present the documented theories or evidence as statements."
                        )
                    )
            else:
                consecutive_questions = 0

        passes_word_count = (TARGET_WORD_COUNT_MIN <= word_count <= TARGET_WORD_COUNT_MAX)
        passes_readability = (flesch_grade <= TARGET_FLESCH_GRADE_MAX and sentences_over_cap == 0)

        critical_violations = [v for v in violations if v.violation_type in ["BANNED_WORD", "PERSONIFICATION", "AI_TRANSITION"]]
        overall_status = "PASS" if (passes_word_count and passes_readability and len(critical_violations) == 0) else "FAIL"

        return LintReport(
            script_path=file_path,
            word_count=word_count,
            passes_word_count=passes_word_count,
            estimated_duration_minutes=round(word_count / TARGET_READING_WPM, 1),
            flesch_kincaid_grade=flesch_grade,
            passes_readability=passes_readability,
            total_sentences=total_sentences,
            avg_sentence_words=avg_sentence_words,
            sentences_over_cap=sentences_over_cap,
            violations=violations,
            pronunciation_guides_found=pronunciation_guides,
            overall_status=overall_status
        )

    def audit_file(self, file_path: str) -> LintReport:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        text = path.read_text(encoding="utf-8")
        return self.audit_text(text, file_path=str(path))
