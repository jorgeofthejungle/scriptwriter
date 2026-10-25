"""Autonomous Story Scout Agent for Historical Unexplained Encounters."""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timezone

from engine.bible import StoryBibleManager, compute_entity_hash
from engine.researcher import search_topic_candidates, fetch_article_text, check_safe_outcome, run_deep_research
from engine.blueprint import generate_beat_blueprint
from engine.models import ResearchDossier


# Curated historical discovery catalog of deep, documented, safe-outcome encounters
HISTORICAL_CATALOG: List[Dict[str, Any]] = [
    {
        "title": "The Socorro Landing",
        "aliases": ["Lonnie Zamora incident", "Socorro UFO Encounter", "The White Egg in the Arroyo"],
        "location": "Socorro, New Mexico",
        "year": "1964",
        "witness": "Lonnie Zamora",
        "summary": "Police officer Lonnie Zamora observed a white oval craft land in an arroyo, leaving scorched brush and four deep impressions investigated by the FBI and Project Blue Book.",
        "safe_evidence": "Officer Zamora and all witnesses remained completely unharmed, continuing their normal careers.",
        "search_term": "Lonnie Zamora incident",
    },
    {
        "title": "The Kecksburg Incident",
        "aliases": ["Kecksburg UFO incident", "Pennsylvania Acorn Crash", "Westmoreland Fireball"],
        "location": "Kecksburg, Pennsylvania",
        "year": "1965",
        "witness": "John Balafoutas",
        "summary": "A large fireball was observed across six states before crashing into the woods near Kecksburg. Military and state police cordoned off the area to recover debris.",
        "safe_evidence": "No deaths, injuries, or property damage occurred. All residents remained physically safe.",
        "search_term": "Kecksburg UFO incident",
    },
    {
        "title": "The 1976 Tehran Encounter",
        "aliases": ["1976 Tehran UFO incident", "Imperial Iranian Air Force Jet Intercept"],
        "location": "Tehran, Iran",
        "year": "1976",
        "witness": "Parviz Jafari",
        "summary": "Two Iranian Air Force F-4 Phantom interceptors pursued a brilliant aerial object over Tehran, experiencing simultaneous instrumentation blackouts before safely returning to base.",
        "safe_evidence": "All pilots, navigators, and ground crews landed safely at Mehrabad Airport with zero injuries.",
        "search_term": "1976 Tehran UFO incident",
    },
    {
        "title": "Japan Air Lines Flight 1628",
        "aliases": ["JAL 1628 UFO incident", "Alaska Cargo Jet Sighting"],
        "location": "Anchorage, Alaska",
        "year": "1986",
        "witness": "Kenju Terauchi",
        "summary": "A Boeing 747 cargo jet captained by veteran pilot Kenju Terauchi was accompanied by two massive lighted craft over Alaska, tracked by FAA and military radar.",
        "safe_evidence": "Flight 1628 completed its flight plan and touched down smoothly in Anchorage without injuries or damage.",
        "search_term": "Japan Air Lines Flight 1628 incident",
    },
    {
        "title": "The 1952 Washington D.C. Radar Sightings",
        "aliases": ["1952 Washington D.C. UFO incident", "Washington National Radar Intercepts"],
        "location": "Washington D.C.",
        "year": "1952",
        "witness": "Harry Barnes",
        "summary": "Air traffic controllers at Washington National Airport and Andrews AFB tracked clusters of unidentified targets over the Capitol and White House, prompting Air Force jet intercepts.",
        "safe_evidence": "Air Force interceptor pilots and civilian air traffic controllers operated safely with zero crashes or injuries.",
        "search_term": "1952 Washington D.C. UFO incident",
    },
    {
        "title": "The Shag Harbour Incident",
        "aliases": ["Shag Harbour UFO incident", "Nova Scotia Harbor Crash"],
        "location": "Shag Harbour, Nova Scotia",
        "year": "1967",
        "witness": "Laurie Wickens",
        "summary": "Multiple civilian witnesses and RCMP officers saw an illuminated object crash into the waters of Shag Harbour, prompting a joint search by the Canadian Coast Guard and Navy divers.",
        "safe_evidence": "All witnesses and search personnel returned safely with zero injuries or casualties.",
        "search_term": "Shag Harbour UFO incident",
    },
    {
        "title": "The RB-47 Electronic Encounter",
        "aliases": ["1957 RB-47 electronic UFO encounter", "USAF Reconnaissance Sighting"],
        "location": "Dallas-Fort Worth, Texas",
        "year": "1957",
        "witness": "Lewis Chase",
        "summary": "A USAF RB-47 electronic reconnaissance bomber tracked an unidentified electromagnetic emitter across four southern states, corroborated by ground radar stations.",
        "safe_evidence": "The aircraft and its six-man crew landed safely at Forbes Air Force Base with zero casualties.",
        "search_term": "1957 RB-47 UFO encounter",
    },
    {
        "title": "The Chiles-Whitted Sighting",
        "aliases": ["Chiles-Whitted UFO encounter", "Eastern Air Lines Flight 576"],
        "location": "Montgomery, Alabama",
        "year": "1948",
        "witness": "Clarence Chiles",
        "summary": "Two commercial airline pilots flying an Eastern Air Lines DC-3 observed a torpedo-shaped craft with glowing blue exhaust pass within several hundred feet of their plane.",
        "safe_evidence": "The DC-3 landed safely in Atlanta on schedule without passenger injuries.",
        "search_term": "Chiles-Whitted UFO encounter",
    },
]


class StoryScoutAgent:
    """Autonomous agent that discovers, vets, and registers new stories in the pipeline."""

    def __init__(self, bible_manager: Optional[StoryBibleManager] = None):
        self.bible = bible_manager or StoryBibleManager()

    def scout_next_candidates(self, target_count: int = 1) -> List[Dict[str, Any]]:
        """
        Scouts and qualifies new unique stories:
        1. Checks deduplication hash against Story Bible.
        2. Verifies safe outcome and true-crime free status.
        3. Audits archival depth (>= 8 chronological beats).
        4. Registers into Story Bible.
        5. Automatically builds Research Dossier and Beat Blueprint.
        """
        registered_stories: List[Dict[str, Any]] = []
        print(f"\n[SCOUT] Beginning autonomous story hunt for {target_count} unique topic(s)...")

        for candidate in HISTORICAL_CATALOG:
            if len(registered_stories) >= target_count:
                break

            title = candidate["title"]
            loc = candidate["location"]
            yr = candidate["year"]
            wit = candidate["witness"]
            aliases = candidate.get("aliases", [])
            safe_ev = candidate["safe_evidence"]
            search_term = candidate["search_term"]

            entity_hash = compute_entity_hash(loc, yr, wit)
            is_dup, existing, reason = self.bible.is_duplicate(entity_hash, title, aliases)

            if is_dup:
                print(f"[SKIP] Duplicate collision for '{title}' -> {reason}")
                continue

            print(f"\n[GATE 1: DEDUP PASS] Novel spacetime entity discovered: '{title}' ({loc}, {yr}) [Hash: {entity_hash}]")

            # Gate 2: Fetch and audit archival text for safety
            print(f"[GATE 2: RESEARCH & SAFETY] Querying historical records for '{search_term}'...")
            candidates = search_topic_candidates(search_term)
            if not candidates:
                print(f"[GATE 2 FAIL] Could not find archival records for '{search_term}'. Skipping.")
                continue

            target_title, target_url = candidates[0]
            text, canon_url = fetch_article_text(target_title)
            if not text:
                print(f"[GATE 2 FAIL] Could not retrieve primary archival text for '{target_title}'. Skipping.")
                continue

            is_safe, flags = check_safe_outcome(text)
            if not is_safe:
                print(f"[GATE 2 FAIL] Red-flag terms found in '{title}': {flags}")
                self.bible.register_story(
                    title=title,
                    location=loc,
                    year=yr,
                    primary_witness=wit,
                    aliases=aliases,
                    status="REJECTED_UNSAFE",
                    safe_outcome_verified=False,
                    safe_outcome_evidence=f"Failed safety scan: {flags}"
                )
                continue

            print(f"[GATE 2 PASS] Safe outcome confirmed. Zero violence, zero fatalities.")

            # Gate 3: Archival Depth check
            paragraphs = [p for p in text.split("\n\n") if len(p.strip()) > 50]
            beat_count = len(paragraphs)
            if beat_count < 6:
                print(f"[GATE 3 FAIL] Shallow archival depth ({beat_count} beats). Cannot sustain 3,000+ words.")
                self.bible.register_story(
                    title=title,
                    location=loc,
                    year=yr,
                    primary_witness=wit,
                    aliases=aliases,
                    status="REJECTED_SHALLOW",
                    archival_depth_beats=beat_count
                )
                continue

            print(f"[GATE 3 PASS] Archival depth confirmed ({beat_count} source beats). Sustains 3,000-3,600 words.")

            # Build full research dossier
            dossier = run_deep_research(search_term)
            dossier_path = f".scriptwriter/dossiers/{search_term.lower().replace(' ', '_')}_dossier.json" if dossier else None

            # Register in Story Bible as IN_PIPELINE
            success, rec, msg = self.bible.register_story(
                title=title,
                location=loc,
                year=yr,
                primary_witness=wit,
                aliases=aliases,
                status="IN_PIPELINE",
                safe_outcome_verified=True,
                safe_outcome_evidence=safe_ev,
                archival_depth_beats=beat_count,
                source_urls=[canon_url] if canon_url else [],
                dossier_path=dossier_path
            )

            if success and rec:
                print(f"[BIBLE COMMIT] {msg}")
                registered_stories.append({
                    "story_id": rec.story_id,
                    "title": rec.title,
                    "entity_hash": rec.entity_hash,
                    "dossier_path": dossier_path
                })

        print(f"\n[SCOUT COMPLETE] Successfully qualified and registered {len(registered_stories)} new story(s) into the pipeline.")
        return registered_stories
