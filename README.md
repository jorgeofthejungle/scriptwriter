# 🎙️ Scriptwriter OS: Oral Documentary Scriptwriting Engine

A turnkey, high-volume production engine for 3,000–3,600-word conversational YouTube narration scripts in the exact storytelling register of **Carolina Case Files**, **Lighthouse Mysteries**, and **MrBallen**.

Engineered for zero client revisions: strict plain language, zero purple prose, verified safe outcomes, 100% factual traceability, cold-read pronunciation guides, and an automated deterministic linter.

---

## ⚡ The Architecture at a Glance

```
[Raw Topic / Encounter]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 1: Topic Screener                               │
│  - 100% Safe Outcome Verification (Zero True Crime)    │
│  - Archival Depth Gate (8+ Chronological Beats)        │
└────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Epistemic Research Dossier                   │
│  - Fact Nodes tagged [FACT], [WITNESS], [SPECULATION]  │
│  - Live Archival Source URLs & Primary Logs            │
│  - Cold-Read Phonetic Pronunciation Guide Map          │
└────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: 7-Movement Beat Blueprint                    │
│  - Math-backed word budgeting (3,000-3,600 words)      │
│  - Strict "Camera Horizon" Lock (Zero spoilers)        │
└────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 4: Spoken Prose Drafting                        │
│  - Subject-Verb-Object cadence (Flesch Grade 5.0-7.0)  │
│  - Zero personification, zero flowery descriptions     │
└────────────────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 5: Deterministic Linter (`cli.py lint`)         │
│  - Word Count Gate (3,000 - 3,600 words body)          │
│  - Banned Regex Kill-List (250+ purple prose patterns) │
│  - Max Sentence Cap (<= 25 words)                      │
│  - Pronunciation Guide Detector                        │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Quick Start & CLI Usage

### 1. View the Story Bible (Lifecycle Ledger & Deduplication)
```bash
python cli.py bible
```
Displays all evaluated topics, spacetime entity hashes, lifecycle status (`COMPLETED`, `IN_PIPELINE`, `REJECTED_UNSAFE`, `REJECTED_SHALLOW`), word counts, and readability grades.

### 2. Auto-Launch Story Scout Agent (Autonomous Discovery)
```bash
python cli.py scout --count 2
```
Scouts historical archives for novel, unique encounters, verifies safe outcomes, checks archival depth (>= 8 chronological beats), prevents duplicate collisions via spacetime entity hashing, and registers qualified candidates directly into the Story Bible.

### 3. Audit / Lint a Script & Auto-Export DOCX
Run the automated compiler against any Markdown script:
```bash
python cli.py lint scripts/kecksburg_1965_script.md
```
*When a script passes with 0 violations and 3,000–3,600 words, it automatically updates the Story Bible AND compiles an executive-ready `.docx` in the `exports/` folder.*

### 4. Export to Google-Docs-Ready Word Document (.docx)
Export individual scripts or batch-export all completed stories in the Bible:
```bash
# Export single script
python cli.py export scripts/kecksburg_1965_script.md

# Batch export all completed scripts in the Story Bible
python cli.py export --all
```
All `.docx` files are formatted specifically for Google Docs sharing and teleprompter sight-reading (13pt high-legibility font, 1.25 line spacing, 6pt paragraph breaks, highlighted purple pronunciation guides, executive metadata table, and clean sources appendix).
Output:
```
============================================================
[LINT] SCRIPTWRITER OS -- AUDIT REPORT
============================================================
File: examples\socorro_1964_zamora.md
Word Count: 3,111 words [PASS (3,000-3,600 target)]
Estimated Narration Duration: 20.7 minutes (@ 150 WPM)
Readability Grade (Flesch-Kincaid): 6.63 [PASS (<= 7.0)]
Total Sentences: 300 (Avg words/sentence: 10.4)
Sentences Exceeding 25-Word Cap: 0 [PASS (0)]
Pronunciation Guides Detected (9):
  * Lonnie Zamora (Zuh-MOR-uh)
  * Socorro (suh-KOR-oh)
  * Nep Lopez (LO-pez)
  ...
[OK] ZERO VIOLATIONS! Clean, direct, conversational prose.
============================================================
OVERALL STATUS: PASS
============================================================
```

To see how the linter instantly flags and rejects purple prose, test the flawed sample:
```bash
python cli.py lint examples/bad_script_sample.md
```

### 2. Generate a 7-Beat Word Budget Blueprint
```bash
python cli.py blueprint --topic "The Kecksburg Incident" --words 3300
```

### 3. Review the Style Guide & Calibration Matrix
```bash
python cli.py style
```

### 4. Run the Automated Test Suite
```bash
python -m unittest discover tests
```

---

## 📐 Project Structure

```
c:\Users\jordsofthejungle\Documents\Projects\Scriptwriter\
├── engine/
│   ├── config.py           # Word budgets, banned vocabularies, regex patterns
│   ├── models.py           # Pydantic schemas (Dossier, FactNode, Blueprint, LintReport)
│   ├── linter.py           # Deterministic quality compiler & Flesch-Kincaid calculator
│   ├── blueprint.py        # 7-movement beat budgeting algorithm
│   └── style_guide.py      # Codified plain-spoken storytelling rules
├── cli.py                  # Terminal CLI tool for linting, blueprints, and style
├── templates/
│   └── prompt_pack.md      # Copy-pasteable execution prompts for Stages 1 through 5
├── examples/
│   ├── socorro_1964_zamora.md   # Benchmark script (3,111 words, 100% PASS)
│   └── bad_script_sample.md     # Flawed sample demonstrating linter catches
├── tests/
│   └── test_linter.py      # Unit tests verifying linter detection accuracy
└── .scriptwriter/          # Local persistent output directory (lint reports, dossiers)
```

---

## 🎯 The Calibration Standard (Before & After)

| Flawed / Flowery / AI (REJECT) | Plain Spoken / Direct (DELIVER) |
| :--- | :--- |
| *"An eerie silence draped itself over the sleepy town."* | **"The town was quiet."** |
| *"The moon cast its silver veil across the lonely stretch of asphalt."* | **"The moon lit the road."** |
| *"An icy wave of terror gripped him as he gazed upon the mysterious figure."* | **"He was frightened when he saw the figure."** |
| *"Little did he know, this normal Tuesday was about to take a terrifying turn."* | **"At 3:15 that afternoon, he parked his truck by the depot."** |
| *"Fast forward thirty years, and the mystery still haunts the valley."* | **"Thirty years later, the town police logs still include the report."** |
| *"Words cannot describe the breathtaking sight that unfolded."* | **"He saw a white, egg-shaped craft hovering above the brush."** |
