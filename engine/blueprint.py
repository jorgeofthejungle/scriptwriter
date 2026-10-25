"""Narrative Beat Architecture and Word-Budget Engine for 3,000-3,600 Word Scripts."""

from typing import List
from engine.models import BeatBlueprint, BeatSection, ResearchDossier


def generate_beat_blueprint(dossier: ResearchDossier, target_words: int = 3300) -> BeatBlueprint:
    """
    Allocates a strict 7-movement chronological beat architecture.
    Ensures the script reaches 3,000 - 3,600 words naturally without fluff or repetition.
    """
    if target_words < 3000 or target_words > 3600:
        target_words = 3300

    # Calculate proportional word budgets for 7 movements (total 3,300 words)
    beats_spec = [
        (
            1,
            "Beat 1: Cold Open & Sensory Baseline",
            int(target_words * 0.11),  # ~360 words
            "Establish the primary witness, their everyday routine, exact date, time, and weather. Lock camera to their ordinary reality until the first concrete anomaly appears.",
        ),
        (
            2,
            "Beat 2: Geographical & Physical Grounding",
            int(target_words * 0.13),  # ~430 words
            "Lay out the physical map: highway names, distances, local topography, nearest towns, and lighting conditions. Ground secondary characters.",
        ),
        (
            3,
            "Beat 3: The Initial Anomaly",
            int(target_words * 0.15),  # ~495 words
            "Chronological step-by-step account of what was first seen or heard. Keep the camera locked strictly to what the witness knew at that exact minute.",
        ),
        (
            4,
            "Beat 4: The Escalation & Close Encounter",
            int(target_words * 0.17),  # ~560 words
            "The peak encounter. Proximity, physical behavior of the object/entity, duration, physical effects (sound, temperature, vehicle reaction). Zero invented thoughts.",
        ),
        (
            5,
            "Beat 5: The Departure & Immediate Aftermath",
            int(target_words * 0.15),  # ~495 words
            "How the encounter ended. The witness's physical reaction, driving to safety, contacting local dispatch or family. Initial inspection of the scene.",
        ),
        (
            6,
            "Beat 6: Official Investigation & Corroboration",
            int(target_words * 0.16),  # ~530 words
            "Police reports, military or radar checks, physical ground evidence (scorch marks, impressions), secondary witness statements. Distinguish facts from witness claims.",
        ),
        (
            7,
            "Beat 7: Safe Resolution & Competing Theories",
            int(target_words * 0.13),  # ~430 words
            "Document that all witnesses returned to normal life safely. Review the leading official and investigative theories neutrally. Deliver a grounded conclusion.",
        ),
    ]

    beats: List[BeatSection] = []
    for num, title, budget, horizon in beats_spec:
        beats.append(
            BeatSection(
                beat_number=num,
                title=title,
                target_words=budget,
                actual_words=0,
                camera_horizon=horizon,
                facts_referenced=[],
                body=""
            )
        )

    # Re-normalize sum exactly to target_words
    diff = target_words - sum(b.target_words for b in beats)
    beats[3].target_words += diff

    return BeatBlueprint(
        topic_title=dossier.topic_title,
        total_target_words=target_words,
        beats=beats
    )
