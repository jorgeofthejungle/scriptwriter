"""Configuration, rules, and banned vocabularies for the Scriptwriter Engine."""

from typing import List, Dict, Pattern
import re

# Word budget specifications
TARGET_WORD_COUNT_MIN = 3000
TARGET_WORD_COUNT_MAX = 3600
TARGET_READING_WPM = 150  # Average conversational spoken speed (20-24 minutes)

# Readability & sentence ergonomics
MAX_SENTENCE_WORDS = 25
TARGET_FLESCH_GRADE_MAX = 7.5
TARGET_AVG_SENTENCE_WORDS = 14

# Epistemic node tags
TAG_FACT = "[DOCUMENTED_FACT]"
TAG_WITNESS = "[WITNESS_ACCOUNT]"
TAG_SPECULATION = "[SPECULATION]"

# Client-specified banned vocabulary (flowery adjectives, melodramatic pulp, AI filler)
BANNED_WORDS: List[str] = [
    "eerie",
    "spine-chilling",
    "haunting",
    "inexplicable",
    "tapestry",
    "symphony",
    "veil",
    "abyss",
    "fateful",
    "ominous",
    "harrowing",
    "blood-curdling",
    "uncanny",
    "ethereal",
    "shrouded",
    "palpable",
    "bone-chilling",
    "otherworldly",
    "etched into memory",
    "testament to",
    "macabre",
    "chilling",
    "sinister",
    "eldritch",
    "unsettlingly",
    "bizarrely",
    "spectacularly",
    "breathtaking",
    "surreal",
    "stupefied",
    "ghastly",
    "nightmarish",
    "cacophony",
    "labyrinth",
    "clandestine",
    "labyrinthine",
    "ineffable",
    "petrifying",
    "sent shivers",
    "chills down",
]

# Client-specified banned personifications & metaphorical clichés
BANNED_PERSONIFICATION_PATTERNS: List[Dict[str, str]] = [
    {
        "pattern": r"\b(silence|quiet)\b.{1,25}\b(draped|blanketed|descended|hung heavy|swallowed|wrapped|smothered)\b",
        "reason": "Personification of silence/quiet. Replace with simple description (e.g., 'The town was quiet.')."
    },
    {
        "pattern": r"\b(moon|sun|stars?)\b.{1,25}\b(cast|poured|kissed|bathed|danced|smiled|peaked|veiled)\b",
        "reason": "Personification of celestial bodies. Replace with literal action (e.g., 'The moon lit the road.')."
    },
    {
        "pattern": r"\b(fear|terror|dread|panic|horror)\b.{1,25}\b(gripped|washed over|seized|froze|crept|chilled|strangled)\b",
        "reason": "Metaphorical emotion phrasing. State feelings simply (e.g., 'He was frightened.')."
    },
    {
        "pattern": r"\b(darkness|shadows?)\b.{1,25}\b(crept|danced|swallowed|enveloped|loomed|reached|devoured)\b",
        "reason": "Personification of shadows or darkness. Use literal descriptions of lighting."
    },
    {
        "pattern": r"\b(wind|breeze|storm|air)\b.{1,25}\b(whispered|howled|moaned|cried|sighed|screamed|danced)\b",
        "reason": "Personification of weather/wind. State wind speed or temperature directly."
    },
    {
        "pattern": r"\b(road|highway|path|trail)\b.{1,25}\b(wound its way|stretched endlessly|snaked|disappeared into the void)\b",
        "reason": "Melodramatic description of roads/paths. State direction or distance literally."
    },
]

# Banned AI transition phrases and generic suspense clichés
BANNED_AI_TRANSITIONS: List[Dict[str, str]] = [
    {
        "pattern": r"\blittle did (he|she|they|anyone|the|witnesses?)\b\s+know\b",
        "reason": "Banned suspense cliché: 'Little did they know'. Tell the events strictly in real-time order."
    },
    {
        "pattern": r"\bwhat happened next (would|was|shocked|changed)\b",
        "reason": "Banned clickbait/AI phrasing: 'What happened next...'. State the next event directly."
    },
    {
        "pattern": r"\bas fate would have it\b",
        "reason": "Banned cliché: 'As fate would have it'."
    },
    {
        "pattern": r"\bfast forward to\b",
        "reason": "Banned transition: 'Fast forward to'. State the new date, time, or location cleanly."
    },
    {
        "pattern": r"\bit was a normal (day|tuesday|monday|wednesday|thursday|friday|saturday|sunday|morning|evening|night|afternoon) until\b",
        "reason": "Banned generic opening cliché: 'It was a normal [day] until'."
    },
    {
        "pattern": r"\bneedless to say\b",
        "reason": "Filler transition: 'Needless to say'."
    },
    {
        "pattern": r"\bin conclusion\b",
        "reason": "School essay / AI summary marker: 'In conclusion'."
    },
    {
        "pattern": r"\bto this day\b.{1,30}\b(no one knows|remains a mystery|unsolved)\b",
        "reason": "Banned generic mystery outro: 'To this day... remains a mystery'."
    },
    {
        "pattern": r"\blet that sink in\b",
        "reason": "Banned rhetorical filler: 'Let that sink in'."
    },
    {
        "pattern": r"\bone thing was (certain|clear)\b",
        "reason": "Banned AI suspense marker: 'One thing was certain'."
    },
    {
        "pattern": r"\bbuckle up\b",
        "reason": "Informal YouTuber cliché: 'Buckle up'."
    },
    {
        "pattern": r"\ba sight (he|she|they|one) would never forget\b",
        "reason": "Banned pulp cliché: 'A sight they would never forget'."
    },
    {
        "pattern": r"\bcould not believe (his|her|their) eyes\b",
        "reason": "Banned cliché: 'Could not believe their eyes'."
    },
    {
        "pattern": r"\bwords cannot describe\b",
        "reason": "Banned filler: 'Words cannot describe'."
    },
    {
        "pattern": r"\bas the dust settled\b",
        "reason": "Banned cliché: 'As the dust settled'."
    },
]

# Pronunciation guide regex: matches words followed by phonetic guide in parentheses
# e.g., Socorro (suh-KOR-oh) or Ocracoke (OH-kruh-koke) or Chavez (CHAH-vez)
# Requires uppercase syllable notation or hyphens typical of phonetic respelling
PRONUNCIATION_REGEX = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+\(([A-Za-z]+-[A-Za-z\-]+|[A-Z]{2,}(?:\s+[A-Za-z\-]+)*)\)")

