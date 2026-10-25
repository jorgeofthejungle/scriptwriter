"""Stateful Story Bible Operating System and Deduplication Ledger."""

import re
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from tabulate import tabulate

from engine.models import StoryBible, StoryRecord, StoryStatus


DEFAULT_BIBLE_PATH = Path(".scriptwriter/story_bible.json")


def normalize_token(text: str) -> str:
    """Strips non-alphanumeric characters and converts to lowercase."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def extract_surname(name: str) -> str:
    """Extracts the primary surname or keyword from a witness name."""
    clean = re.sub(r"[^a-zA-Z\s]", "", name).strip()
    parts = clean.split()
    return parts[-1].lower() if parts else "unknown"


def compute_entity_hash(location: str, year: str, witness_or_entity: str) -> str:
    """
    Computes an immutable 16-character Spacetime Entity Fingerprint.
    Hashes the normalized location key, event year, and witness surname.
    Guarantees that the same historical event cannot be submitted twice under different titles.
    """
    norm_loc = normalize_token(location)
    norm_yr = normalize_token(year)
    norm_wit = extract_surname(witness_or_entity)

    fingerprint = f"{norm_loc}_{norm_yr}_{norm_wit}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]


class StoryBibleManager:
    """Manages the persistent Story Bible lifecycle ledger and prevents duplicate stories."""

    def __init__(self, bible_path: Path = DEFAULT_BIBLE_PATH):
        self.bible_path = Path(bible_path)
        self.bible: StoryBible = self._load_or_initialize()

    def _load_or_initialize(self) -> StoryBible:
        if self.bible_path.exists():
            try:
                with open(self.bible_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return StoryBible(**data)
            except Exception as e:
                print(f"[WARN] Error reading {self.bible_path}: {e}. Creating new Bible.")

        # Initialize fresh Bible
        now = datetime.now(timezone.utc).isoformat()
        bible = StoryBible(updated_at=now, stories={})
        self._save_bible(bible)
        return bible

    def _save_bible(self, bible: Optional[StoryBible] = None):
        if bible is None:
            bible = self.bible
        bible.updated_at = datetime.now(timezone.utc).isoformat()
        self.bible_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.bible_path, "w", encoding="utf-8") as f:
            json.dump(bible.model_dump(), f, indent=2)

    def is_duplicate(
        self,
        entity_hash: str,
        title: str,
        aliases: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[StoryRecord], str]:
        """
        Checks whether a story already exists in the Bible by:
        1. Exact Spacetime Entity Hash
        2. Exact Title match (case-insensitive)
        3. Alias match
        """
        # 1. Spacetime Entity Hash check (Strongest)
        if entity_hash in self.bible.stories:
            rec = self.bible.stories[entity_hash]
            return True, rec, f"Spacetime Entity collision with [{rec.story_id}] '{rec.title}'"

        # 2. Title & Alias checks
        norm_title = normalize_token(title)
        check_aliases = [normalize_token(a) for a in (aliases or [])]

        for rec in self.bible.stories.values():
            rec_title = normalize_token(rec.title)
            if norm_title == rec_title:
                return True, rec, f"Direct title match with [{rec.story_id}] '{rec.title}'"

            # Check if new title matches an existing alias
            rec_aliases = [normalize_token(a) for a in rec.aliases]
            if norm_title in rec_aliases:
                return True, rec, f"Title matches an alias of [{rec.story_id}] '{rec.title}'"

            # Check if existing title matches any of the new aliases
            for ca in check_aliases:
                if ca and (ca == rec_title or ca in rec_aliases):
                    return True, rec, f"Alias collision with [{rec.story_id}] '{rec.title}'"

        return False, None, "Unique story candidate"

    def register_story(
        self,
        title: str,
        location: str,
        year: str,
        primary_witness: str,
        aliases: Optional[List[str]] = None,
        status: StoryStatus = "SCOUTED",
        safe_outcome_verified: bool = False,
        safe_outcome_evidence: str = "",
        archival_depth_beats: int = 0,
        source_urls: Optional[List[str]] = None,
        dossier_path: Optional[str] = None,
        script_path: Optional[str] = None,
        word_count: Optional[int] = None,
        flesch_grade: Optional[float] = None
    ) -> Tuple[bool, Optional[StoryRecord], str]:
        """Registers a new story candidate in the Story Bible if unique."""
        entity_hash = compute_entity_hash(location, year, primary_witness)
        is_dup, existing, reason = self.is_duplicate(entity_hash, title, aliases)

        if is_dup and existing:
            return False, existing, f"REJECTED AS DUPLICATE: {reason}"

        seq_num = len(self.bible.stories) + 1
        story_id = f"STORY-{seq_num:03d}"
        now = datetime.now(timezone.utc).isoformat()

        record = StoryRecord(
            story_id=story_id,
            entity_hash=entity_hash,
            title=title,
            aliases=aliases or [],
            location=location,
            year=year,
            primary_witness=primary_witness,
            status=status,
            safe_outcome_verified=safe_outcome_verified,
            safe_outcome_evidence=safe_outcome_evidence,
            archival_depth_beats=archival_depth_beats,
            source_urls=source_urls or [],
            dossier_path=dossier_path,
            script_path=script_path,
            word_count=word_count,
            flesch_grade=flesch_grade,
            created_at=now,
            updated_at=now
        )

        self.bible.stories[entity_hash] = record
        self._save_bible()
        return True, record, f"Successfully registered [{story_id}] in Story Bible"

    def update_status(
        self,
        identifier: str,  # Can be story_id (e.g. STORY-001) or entity_hash or title
        new_status: StoryStatus,
        **kwargs
    ) -> Optional[StoryRecord]:
        """Updates a story's lifecycle status and metadata."""
        target_rec = None
        target_hash = None

        # Search by hash
        if identifier in self.bible.stories:
            target_hash = identifier
            target_rec = self.bible.stories[identifier]
        else:
            # Search by story_id or title
            norm_id = identifier.strip().upper()
            norm_title = normalize_token(identifier)
            for h, rec in self.bible.stories.items():
                if rec.story_id.upper() == norm_id or normalize_token(rec.title) == norm_title:
                    target_hash = h
                    target_rec = rec
                    break

        if not target_rec or not target_hash:
            return None

        target_rec.status = new_status
        target_rec.updated_at = datetime.now(timezone.utc).isoformat()

        # Update optional fields if provided
        for key in ["script_path", "dossier_path", "word_count", "flesch_grade", "safe_outcome_verified", "safe_outcome_evidence"]:
            if key in kwargs and kwargs[key] is not None:
                setattr(target_rec, key, kwargs[key])

        self.bible.stories[target_hash] = target_rec
        self._save_bible()
        return target_rec

    def get_record_by_script_path(self, script_path: str) -> Optional[StoryRecord]:
        """Finds a story record by its script file path."""
        norm_path = Path(script_path).resolve()
        for rec in self.bible.stories.values():
            if rec.script_path and Path(rec.script_path).resolve() == norm_path:
                return rec
        return None

    def get_summary_stats(self) -> Dict[str, Any]:
        """Computes executive pipeline stats."""
        total = len(self.bible.stories)
        counts = {
            "SCOUTED": 0,
            "APPROVED": 0,
            "IN_PIPELINE": 0,
            "DRAFTED": 0,
            "COMPLETED": 0,
            "REJECTED_UNSAFE": 0,
            "REJECTED_SHALLOW": 0,
        }
        for rec in self.bible.stories.values():
            counts[rec.status] = counts.get(rec.status, 0) + 1

        return {
            "total_stories": total,
            "active_pipeline": counts["APPROVED"] + counts["IN_PIPELINE"] + counts["DRAFTED"],
            "completed": counts["COMPLETED"],
            "rejected": counts["REJECTED_UNSAFE"] + counts["REJECTED_SHALLOW"],
            "breakdown": counts
        }

    def format_table(self) -> str:
        """Formats the Bible ledger as an ASCII table."""
        if not self.bible.stories:
            return "Story Bible is empty. Run 'python cli.py scout' to discover new topics."

        table_data = []
        for rec in self.bible.stories.values():
            words_str = f"{rec.word_count:,}" if rec.word_count else "-"
            flesch_str = f"{rec.flesch_grade:.2f}" if rec.flesch_grade else "-"
            table_data.append([
                rec.story_id,
                rec.title[:28] + ("..." if len(rec.title) > 28 else ""),
                rec.location[:16],
                rec.year,
                rec.primary_witness[:14],
                rec.status,
                words_str,
                flesch_str
            ])

        headers = ["ID", "Title", "Location", "Year", "Witness", "Status", "Words", "Flesch"]
        return tabulate(table_data, headers=headers, tablefmt="github")
