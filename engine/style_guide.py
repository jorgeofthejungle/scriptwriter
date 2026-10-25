"""Codified Style Guide and Calibration Matrix for Spoken YouTube Storytelling."""

STYLE_GUIDE_TEXT = """
# Oral Storytelling & Scriptwriting Style Guide
### Reference Standards: Carolina Case Files, Lighthouse Mysteries, MrBallen

---

## 1. Core Philosophy: The Single-Threaded Spoken State Machine
When people listen to a story while driving, doing chores, or relaxing, they cannot rewind or re-read a sentence. 
Every sentence must update only ONE variable at a time in plain Subject-Verb-Object order:
- A physical location ("Miller drove south on Highway 85.")
- A concrete sensory observation ("He saw a blue flash behind the hill.")
- An action ("He stopped the car and rolled down the window.")
- A simple, direct reaction ("He was frightened.")

Never stack subordinate clauses or poetic metaphors. Let the events make the story interesting.

---

## 2. The Strict Negative Rules (The Kill List)

1. **NO Flowery or Melodramatic Adjectives**:
   - Banned: eerie, spine-chilling, haunting, inexplicable, tapestry, veil, abyss, fateful, ominous, harrowing, blood-curdling, uncanny, ethereal, shrouded, palpable.
2. **NO Inanimate Personification**:
   - Silence cannot "drape," "fall heavy," or "swallow."
   - The moon/sun cannot "cast its veil," "pour," or "kiss."
   - Fear/terror cannot "grip," "wash over," or "seize."
   - Shadows cannot "creep" or "dance."
   - The wind cannot "whisper" or "howl."
3. **NO AI Suspense Formulas or Meta-Commentary**:
   - Banned: "Little did he know," "What happened next would shock," "It was a normal day until," "Fast forward to," "Needless to say," "To this day, the mystery remains unsolved," "Buckle up."
4. **NO Rhetorical Question Clusters**:
   - Don't ask: "Could it be an alien craft? Or was it a top-secret government test?"
   - Write: "Investigators considered two main possibilities: an aircraft test from the nearby base, or an atmospheric reflection."
5. **NO Invented Dialogue or Unverified Micro-Details**:
   - Never invent what someone ate, what color shirt they wore, or quotes unless they appear in official transcripts or published news archives.

---

## 3. The Before & After Calibration Matrix

| Cliché / Flowery / AI (REJECT) | Plain Spoken / Direct (DELIVER) |
| :--- | :--- |
| "An eerie silence draped itself over the sleepy town." | "The town was quiet." |
| "The moon cast its silver veil across the lonely stretch of asphalt." | "The moon lit the road." |
| "An icy wave of terror gripped him as he gazed upon the mysterious figure." | "He was frightened when he saw the figure." |
| "Little did he know, this ordinary Tuesday would take a harrowing turn." | "At 3:15 that afternoon, he parked his truck by the gate." |
| "A chilling presence seemed to lurk just beyond his sight, sending shivers down his spine." | "He heard gravel crunch behind him. He turned around. The driveway was empty." |
| "Fast forward thirty years, and the enigma still haunts the quiet valleys." | "Thirty years later, the town records still include the police report." |
| "Words cannot describe the breathtaking sight that unfolded before his eyes." | "He saw a white, egg-shaped craft hovering four feet above the ground." |

---

## 4. Pronunciation Guides (Cold-Read Ergonomics)
Every unfamiliar person, town, foreign word, or geographic landmark MUST include an intuitive English phonetic guide in parentheses on first mention:
- Socorro (suh-KOR-oh)
- Ocracoke (OH-kruh-koke)
- Lonnie Zamora (Zuh-MOR-uh)
- Pascagoula (pas-kuh-GOO-luh)
- Kecksburg (KEX-berg)

---

## 5. Topic Eligibility & Safe Outcome Verification
- **Permitted**: Strange sightings, radar/visual anomalies, historical cryptids or unexplained lights, unusual navigational encounters, documented civilian/pilot events.
- **Strictly Banned**: True crime, homicides, unsolved violent deaths, child endangerment, abductions involving physical harm or ongoing trauma, mental health crises.
- **Mandatory Safe Outcome**: The script must explicitly state and verify that all participants survived and returned safely to their everyday lives.
"""


def get_style_guide() -> str:
    return STYLE_GUIDE_TEXT.strip()
