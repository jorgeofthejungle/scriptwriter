"""Command-line interface for the Scriptwriter Engine."""

import sys
import argparse
import json
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from colorama import init, Fore, Style

from engine.config import (
    TARGET_WORD_COUNT_MIN,
    TARGET_WORD_COUNT_MAX,
    TARGET_READING_WPM,
    MAX_SENTENCE_WORDS,
    TARGET_FLESCH_GRADE_MAX,
)
from engine.linter import ScriptLinter
from engine.researcher import run_deep_research
from engine.blueprint import generate_beat_blueprint
from engine.models import ResearchDossier
from engine.style_guide import get_style_guide
from engine.bible import StoryBibleManager
from engine.scout import StoryScoutAgent
from engine.exporter import DocxScriptExporter

init(autoreset=True)


def cmd_lint(args):
    """Lints a script against all length, prose, and readability guardrails."""
    file_path = args.script_path
    path = Path(file_path)
    if not path.exists():
        print(f"{Fore.RED}[ERROR] Script file not found: {file_path}")
        sys.exit(1)

    linter = ScriptLinter()
    report = linter.audit_file(str(path))

    # Print summary card
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}[LINT] SCRIPTWRITER OS -- AUDIT REPORT")
    print("=" * 60)
    print(f"File: {report.script_path}")
    print(f"Word Count: {report.word_count:,} words " + (
        f"{Fore.GREEN}[PASS (3,000-3,600 target)]" if report.passes_word_count else f"{Fore.RED}[FAIL - Target is 3,000-3,600]"
    ))
    print(f"Estimated Narration Duration: {report.estimated_duration_minutes} minutes (@ 150 WPM)")
    print(f"Readability Grade (Flesch-Kincaid): {report.flesch_kincaid_grade} " + (
        f"{Fore.GREEN}[PASS (<= {TARGET_FLESCH_GRADE_MAX})]" if report.passes_readability else f"{Fore.RED}[FAIL - Too complex]"
    ))
    print(f"Total Sentences: {report.total_sentences} (Avg words/sentence: {report.avg_sentence_words})")
    print(f"Sentences Exceeding 25-Word Cap: {report.sentences_over_cap} " + (
        f"{Fore.GREEN}[PASS (0)]" if report.sentences_over_cap == 0 else f"{Fore.YELLOW}[WARN - Break these up]"
    ))

    if report.pronunciation_guides_found:
        print(f"\nPronunciation Guides Detected ({len(report.pronunciation_guides_found)}):")
        for pg in report.pronunciation_guides_found[:8]:
            print(f"  * {Fore.MAGENTA}{pg}")
        if len(report.pronunciation_guides_found) > 8:
            print(f"  ... and {len(report.pronunciation_guides_found) - 8} more.")

    # Violations listing
    if report.violations:
        print("\n" + "-" * 60)
        print(f"{Fore.YELLOW}[!] VIOLATIONS & ACTIONABLE FIXES ({len(report.violations)} detected):")
        print("-" * 60)
        for idx, v in enumerate(report.violations, 1):
            color = Fore.RED if v.violation_type in ["BANNED_WORD", "PERSONIFICATION", "AI_TRANSITION"] else Fore.YELLOW
            line_info = f"Line {v.line_number}" if v.line_number > 0 else "Sentence Rule"
            print(f"\n{color}[{idx}] {v.violation_type} ({line_info})")
            print(f"  Snippet:    \"{v.snippet.strip()}\"")
            print(f"  Reason:     {v.rule_reason}")
            print(f"  Suggestion: {Fore.GREEN}{v.suggestion}")
    else:
        print(f"\n{Fore.GREEN}[OK] ZERO VIOLATIONS! Clean, direct, conversational prose.")

    print("\n" + "=" * 60)
    status_color = Fore.GREEN if report.overall_status == "PASS" else Fore.RED
    print(f"OVERALL STATUS: {status_color}{Style.BRIGHT}{report.overall_status}")
    print("=" * 60)

    # Save artifact report
    output_dir = Path(".scriptwriter")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = output_dir / "latest_lint_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    # Auto-sync with Story Bible and auto-export to DOCX if clean pass
    if report.overall_status == "PASS":
        bible_mgr = StoryBibleManager()
        slug = path.stem.lower()
        matched = False
        matched_id = "SCRIPT"
        for rec in bible_mgr.bible.stories.values():
            if (rec.script_path and Path(rec.script_path).name == path.name) or (slug in rec.title.lower() or any(slug in a.lower() for a in rec.aliases)):
                bible_mgr.update_status(
                    rec.entity_hash,
                    "COMPLETED",
                    script_path=str(path),
                    word_count=report.word_count,
                    flesch_grade=report.flesch_kincaid_grade
                )
                print(f"{Fore.CYAN}[BIBLE SYNC] Updated [{rec.story_id}] '{rec.title}' to COMPLETED ({report.word_count} words, Flesch {report.flesch_kincaid_grade})")
                matched = True
                matched_id = rec.story_id
                break

        # Auto-export to Word / Google Docs format
        try:
            exporter = DocxScriptExporter(str(path))
            out_file = exporter.export(output_dir="exports", story_id=matched_id)
            print(f"{Fore.GREEN}[DOCX EXPORT] Teleprompter Word document generated: {out_file}\n")
        except Exception as e:
            print(f"{Fore.YELLOW}[WARN] Could not auto-generate .docx: {e}\n")

    sys.exit(0 if report.overall_status == "PASS" else 1)


def cmd_export(args):
    """Exports markdown scripts to Google-Docs-ready .docx teleprompter files."""
    if args.all:
        bible_mgr = StoryBibleManager()
        completed = [rec for rec in bible_mgr.bible.stories.values() if rec.status == "COMPLETED" and rec.script_path]
        if not completed:
            print(f"{Fore.YELLOW}[INFO] No completed scripts found in Story Bible to export.")
            return

        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}{Style.BRIGHT}[EXPORT] BATCH EXPORTING ALL COMPLETED SCRIPTS TO DOCX")
        print("=" * 60)
        for rec in completed:
            try:
                exp = DocxScriptExporter(rec.script_path)
                out = exp.export(output_dir=args.output_dir, story_id=rec.story_id)
                print(f"  * {Fore.GREEN}[EXPORTED] {rec.story_id}: {out}")
            except Exception as e:
                print(f"  * {Fore.RED}[FAILED] {rec.story_id}: {e}")
        print("=" * 60 + "\n")
    else:
        if not args.script_path:
            print(f"{Fore.RED}[ERROR] Please provide a script path or use --all.")
            sys.exit(1)
        path = Path(args.script_path)
        if not path.exists():
            print(f"{Fore.RED}[ERROR] Script file not found: {args.script_path}")
            sys.exit(1)

        print("\n" + "=" * 60)
        print(f"{Fore.CYAN}{Style.BRIGHT}[EXPORT] EXPORTING TO GOOGLE-DOCS-READY DOCX")
        print("=" * 60)
        exp = DocxScriptExporter(str(path))
        out = exp.export(output_dir=args.output_dir, story_id=args.story_id or "SCRIPT")
        print(f"{Fore.GREEN}[SUCCESS] Teleprompter Word Document: {out}")
        print("=" * 60 + "\n")


def cmd_bible(args):
    """Displays the Story Bible status table and lifecycle telemetry."""
    mgr = StoryBibleManager()
    stats = mgr.get_summary_stats()

    print("\n" + "=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}📖 STORY BIBLE OPERATING SYSTEM — LIFECYCLE LEDGER")
    print("=" * 70)
    print(f"Total Evaluated: {stats['total_stories']}  |  "
          f"Active in Pipeline: {Fore.YELLOW}{stats['active_pipeline']}  |  "
          f"Completed Scripts: {Fore.GREEN}{stats['completed']}  |  "
          f"Rejected (Unsafe/Shallow): {Fore.RED}{stats['rejected']}")
    print("-" * 70)
    print(mgr.format_table())
    print("=" * 70 + "\n")


def cmd_scout(args):
    """Auto-launches the Story Scout Agent to discover and qualify new stories."""
    count = args.count
    scout = StoryScoutAgent()
    new_stories = scout.scout_next_candidates(target_count=count)
    if new_stories:
        print(f"\n{Fore.GREEN}✨ Successfully queued {len(new_stories)} story(s) into the pipeline.")
        for s in new_stories:
            print(f"  • {Fore.YELLOW}{s['story_id']}: {s['title']} (Dossier: {s['dossier_path']})")
    else:
        print(f"\n{Fore.YELLOW}[INFO] No new stories needed or all candidate topics already in Bible.")


def cmd_research(args):
    """Executes automated deep research on an open topic."""
    query = args.query
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}[RESEARCH] DEEP RESEARCH HARVESTER: \"{query}\"")
    print("=" * 60)
    dossier = run_deep_research(query)
    if not dossier:
        print(f"{Fore.RED}[FAILED] Could not complete research for '{query}'.")
        sys.exit(1)
    print("=" * 60 + "\n")


def cmd_blueprint(args):
    """Outputs the 7-beat word budget blueprint for a topic."""
    if args.dossier:
        dossier_path = Path(args.dossier)
        if not dossier_path.exists():
            print(f"{Fore.RED}[ERROR] Dossier file not found: {args.dossier}")
            sys.exit(1)
        with open(dossier_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            dossier = ResearchDossier(**data)
    else:
        dossier = ResearchDossier(
            topic_title=args.topic,
            location="Target Location",
            location_pronunciation="LO-kay-shun",
            date_range="Historical Date Range",
        )
    blueprint = generate_beat_blueprint(dossier, target_words=args.words)
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}[BLUEPRINT] 7-BEAT WORD BUDGET: {blueprint.topic_title.upper()}")
    print(f"Total Target Word Count: {blueprint.total_target_words:,} words (~{round(blueprint.total_target_words/150, 1)} minutes audio)")
    print("=" * 60)
    for b in blueprint.beats:
        print(f"\n{Fore.YELLOW}Movement {b.beat_number}: {b.title}")
        print(f"  Target Budget:  {Fore.GREEN}{b.target_words} words")
        print(f"  Camera Horizon: {b.camera_horizon}")
    print("=" * 60 + "\n")


def cmd_style(args):
    """Prints the codified style guide."""
    print(get_style_guide())


def main():
    parser = argparse.ArgumentParser(description="Scriptwriter Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # lint command
    lint_parser = subparsers.add_parser("lint", help="Audit a script file against length, prose, and style rules")
    lint_parser.add_argument("script_path", help="Path to markdown script file")

    # export command
    exp_parser = subparsers.add_parser("export", help="Export script to Google-Docs-ready .docx format")
    exp_parser.add_argument("script_path", nargs="?", help="Path to markdown script file")
    exp_parser.add_argument("--all", action="store_true", help="Batch export all completed scripts in Story Bible")
    exp_parser.add_argument("--output-dir", default="exports", help="Output directory for .docx files")
    exp_parser.add_argument("--story-id", default=None, help="Custom Story ID e.g. STORY-002")

    # bible command
    subparsers.add_parser("bible", help="View Story Bible lifecycle ledger and telemetry")

    # scout command
    scout_parser = subparsers.add_parser("scout", help="Auto-launch Story Scout Agent to find new stories")
    scout_parser.add_argument("--count", type=int, default=1, help="Number of new stories to scout and register")

    # research command
    res_parser = subparsers.add_parser("research", help="Execute deep research on a historical topic")
    res_parser.add_argument("query", help="Topic name or event query")

    # blueprint command
    bp_parser = subparsers.add_parser("blueprint", help="Generate 7-beat word-budget blueprint")
    bp_parser.add_argument("--dossier", help="Path to research dossier JSON file")
    bp_parser.add_argument("--topic", default="Unexplained Encounter", help="Topic name")
    bp_parser.add_argument("--words", type=int, default=3300, help="Target total words (3,000-3,600)")

    # style command
    subparsers.add_parser("style", help="Print style guide and calibration matrix")

    args = parser.parse_args()
    if args.command == "lint":
        cmd_lint(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "bible":
        cmd_bible(args)
    elif args.command == "scout":
        cmd_scout(args)
    elif args.command == "research":
        cmd_research(args)
    elif args.command == "blueprint":
        cmd_blueprint(args)
    elif args.command == "style":
        cmd_style(args)


if __name__ == "__main__":
    main()
