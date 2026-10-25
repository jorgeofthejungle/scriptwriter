"""Pydantic data models for the Scriptwriter Engine."""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class TopicCandidate(BaseModel):
    title: str = Field(..., description="Title of the event or encounter")
    location: str = Field(..., description="Geographic location (State, Country, Region)")
    year: str = Field(..., description="Year or specific date range")
    summary: str = Field(..., description="1-2 sentence neutral summary of events")
    safe_outcome_verified: bool = Field(..., description="True only if all persons emerged unharmed")
    safe_outcome_evidence: str = Field(..., description="Exact details proving no death, disappearance, or severe trauma")
    true_crime_free: bool = Field(True, description="Strictly true: no homicides, kidnappings, or criminal acts")
    archival_depth: Literal["DEEP", "MODERATE", "SHALLOW"] = Field(
        ..., description="Must be DEEP (8+ verifiable chronological beats) to sustain 3,000+ words"
    )
    key_figures: List[str] = Field(default_factory=list, description="Witnesses, officers, investigators")
    source_urls: List[str] = Field(default_factory=list, description="Official logs, contemporary news archives")


class FactNode(BaseModel):
    id: str = Field(..., description="Unique ID e.g. F01, W03, S02")
    epistemic_tier: Literal["DOCUMENTED_FACT", "WITNESS_ACCOUNT", "SPECULATION"]
    chronology: str = Field(..., description="Date, exact time, or relative sequence marker")
    claim: str = Field(..., description="The concrete event, observation, or statement")
    attributed_to: Optional[str] = Field(None, description="Person who made the claim if a witness account")
    source_title: str = Field(..., description="Title of the archival record or news article")
    source_url: str = Field(..., description="Live or archival URL link")
    verified: bool = Field(True, description="Independently cross-checked across primary sources")


class ResearchDossier(BaseModel):
    topic_title: str
    location: str
    location_pronunciation: str = Field(..., description="Phonetic respelling guide e.g. Socorro (suh-KOR-oh)")
    date_range: str
    pronunciation_guide_map: Dict[str, str] = Field(
        default_factory=dict, description="Proper noun -> phonetic respelling e.g. 'Lonnie Zamora': 'Zuh-MOR-uh'"
    )
    fact_ledger: List[FactNode] = Field(default_factory=list)
    primary_sources: List[str] = Field(default_factory=list)


class BeatSection(BaseModel):
    beat_number: int
    title: str
    target_words: int
    actual_words: int = 0
    camera_horizon: str = Field(..., description="What the observer knows at this exact chronological point")
    facts_referenced: List[str] = Field(default_factory=list, description="IDs of FactNodes covered in this beat")
    body: str = ""


class BeatBlueprint(BaseModel):
    topic_title: str
    total_target_words: int = Field(3300, ge=3000, le=3600)
    beats: List[BeatSection] = Field(default_factory=list)


class LintViolation(BaseModel):
    line_number: int
    violation_type: Literal[
        "BANNED_WORD",
        "PERSONIFICATION",
        "AI_TRANSITION",
        "SENTENCE_TOO_LONG",
        "RHETORICAL_QUESTION",
        "MISSING_PRONUNCIATION_FIRST_USE",
        "PASSIVE_CONGESTION"
    ]
    snippet: str
    rule_reason: str
    suggestion: str


class LintReport(BaseModel):
    script_path: str
    word_count: int
    passes_word_count: bool
    estimated_duration_minutes: float
    flesch_kincaid_grade: float
    passes_readability: bool
    total_sentences: int
    avg_sentence_words: float
    sentences_over_cap: int
    violations: List[LintViolation] = Field(default_factory=list)
    pronunciation_guides_found: List[str] = Field(default_factory=list)
    overall_status: Literal["PASS", "FAIL"]


StoryStatus = Literal[
    "SCOUTED",
    "APPROVED",
    "IN_PIPELINE",
    "DRAFTED",
    "COMPLETED",
    "REJECTED_UNSAFE",
    "REJECTED_SHALLOW",
]


class StoryRecord(BaseModel):
    story_id: str = Field(..., description="Unique sequential ID e.g. STORY-001")
    entity_hash: str = Field(..., description="Canonical 16-char Spacetime Entity Fingerprint")
    title: str
    aliases: List[str] = Field(default_factory=list)
    location: str
    year: str
    primary_witness: str = Field(..., description="Key witness or official surname")
    status: StoryStatus = Field("SCOUTED")
    safe_outcome_verified: bool = Field(False)
    safe_outcome_evidence: str = Field("")
    archival_depth_beats: int = Field(0)
    source_urls: List[str] = Field(default_factory=list)
    dossier_path: Optional[str] = None
    script_path: Optional[str] = None
    word_count: Optional[int] = None
    flesch_grade: Optional[float] = None
    created_at: str = Field(...)
    updated_at: str = Field(...)


class StoryBible(BaseModel):
    version: str = Field("1.0.0")
    channel_name: str = Field("Oral Documentary Series")
    updated_at: str = Field(...)
    stories: Dict[str, StoryRecord] = Field(
        default_factory=dict, description="entity_hash -> StoryRecord mapping"
    )

