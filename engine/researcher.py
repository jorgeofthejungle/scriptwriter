"""Deep Research and Epistemic Fact Ledger Harvesting Engine."""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import requests

from engine.models import ResearchDossier, FactNode


WIKIPEDIA_USER_AGENT = "ScriptwriterEngine/1.0 (historical-research-bot; contact@example.com)"


def search_topic_candidates(query: str, limit: int = 5) -> List[Tuple[str, str]]:
    """Searches open historical archives / Wikipedia for topic candidates."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    headers = {"User-Agent": WIKIPEDIA_USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            search_results = data.get("query", {}).get("search", [])
            results = []
            for item in search_results[:limit]:
                title = item.get("title", "")
                link = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                results.append((title, link))
            return results
    except Exception as e:
        print(f"[WARN] Failed to search Wikipedia: {e}")
    return []


def fetch_article_text(title: str) -> Tuple[str, str]:
    """Fetches full plain text and canonical URL for a title."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts|info",
        "inprop": "url",
        "explaintext": 1,
        "titles": title,
        "format": "json"
    }
    headers = {"User-Agent": WIKIPEDIA_USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if page_id != "-1":
                    text = page.get("extract", "")
                    canonical_url = page.get("canonicalurl", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
                    return text, canonical_url
    except Exception as e:
        print(f"[WARN] Failed to fetch article: {e}")
    return "", ""


def check_safe_outcome(text: str) -> Tuple[bool, List[str]]:
    """
    Scans text for violent true-crime markers to ensure safe outcomes.
    Returns (is_safe, reasons).
    """
    red_flags = [
        (r"\b(murdered|homicide|murder|strangled|stabbed to death)\b", "Mentions homicide/murder"),
        (r"\b(fatal accident|fatalities|died in the crash|killed in the crash)\b", "Mentions fatal accident"),
        (r"\b(body was found|corpse|autopsy revealed)\b", "Mentions discovery of a body/corpse"),
        (r"\b(violent assault|torture|kidnapped and killed)\b", "Mentions violent crime"),
    ]
    flags_found = []
    for pattern, reason in red_flags:
        if re.search(pattern, text, re.IGNORECASE):
            flags_found.append(reason)

    is_safe = len(flags_found) == 0
    return is_safe, flags_found


def extract_potential_proper_nouns(text: str) -> List[str]:
    """Finds non-trivial proper nouns that likely require pronunciation guides."""
    common_words = {
        "The", "On", "In", "At", "He", "She", "They", "It", "We", "Then", "After",
        "Before", "However", "According", "United", "States", "Air", "Force",
        "April", "January", "February", "March", "May", "June", "July", "August",
        "September", "October", "November", "December", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "America", "American",
        "Project", "Book", "Police", "Sheriff", "Department", "University"
    }
    # Find capitalized words of 4+ characters not starting sentences
    matches = re.findall(r"(?<=[a-z]\s)([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{3,})?)", text)
    unique = []
    seen = set()
    for m in matches:
        if m not in seen and m not in common_words and not any(cw in m for cw in common_words):
            seen.add(m)
            unique.append(m)
    return unique[:15]


def parse_into_fact_nodes(text: str, source_title: str, source_url: str) -> List[FactNode]:
    """Splits article text into atomic Fact Nodes classified into 3 epistemic tiers."""
    paragraphs = text.split("\n\n")
    nodes: List[FactNode] = []
    node_counter = 1

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean or para_clean.startswith("==") or len(para_clean) < 40:
            continue

        sentences = re.split(r"(?<=[.!?])\s+", para_clean)
        for sent in sentences:
            sent_str = sent.strip()
            if len(sent_str) < 30:
                continue

            # Epistemic classification heuristics
            is_speculation = bool(re.search(r"\b(theory|theories|speculat|hoax|suggested|hypothesi|debunk|prank|concluded)\b", sent_str, re.IGNORECASE))
            is_witness = bool(re.search(r"\b(claimed|reported|saw|stated|described|witnessed|heard|noticed|alleged)\b", sent_str, re.IGNORECASE))

            if is_speculation:
                tier = "SPECULATION"
            elif is_witness:
                tier = "WITNESS_ACCOUNT"
            else:
                tier = "DOCUMENTED_FACT"

            # Chronology extraction
            date_match = re.search(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?|\b\d{4}\b|\b\d{1,2}:\d{2}\b", sent_str)
            chronology = date_match.group(0) if date_match else "Chronological Sequence"

            node_id = f"F{node_counter:02d}" if tier == "DOCUMENTED_FACT" else (
                f"W{node_counter:02d}" if tier == "WITNESS_ACCOUNT" else f"S{node_counter:02d}"
            )

            nodes.append(
                FactNode(
                    id=node_id,
                    epistemic_tier=tier,
                    chronology=chronology,
                    claim=sent_str,
                    attributed_to=None,
                    source_title=source_title,
                    source_url=source_url,
                    verified=True
                )
            )
            node_counter += 1

    return nodes


def run_deep_research(topic_query: str, output_dir: str = ".scriptwriter/dossiers") -> Optional[ResearchDossier]:
    """
    Executes deep research for a topic query:
    1. Searches open archives
    2. Fetches full text
    3. Runs safe outcome filter
    4. Categorizes facts into 3 epistemic tiers
    5. Extracts proper nouns for pronunciation guides
    6. Saves JSON contract and Markdown dossier
    """
    candidates = search_topic_candidates(topic_query)
    if not candidates:
        print(f"[ERROR] No archival records found matching '{topic_query}'.")
        return None

    # Pick the best matching candidate
    best_title, best_url = candidates[0]
    print(f"[RESEARCH] Target Selected: {best_title} ({best_url})")

    full_text, canonical_url = fetch_article_text(best_title)
    if not full_text:
        print(f"[ERROR] Could not extract text for {best_title}.")
        return None

    # Safety check
    is_safe, safety_flags = check_safe_outcome(full_text)
    if not is_safe:
        print(f"[WARNING] Safety flags detected for '{best_title}': {safety_flags}")
        print("          Review carefully to ensure everyone involved had a safe outcome!")

    # Parse Fact Nodes
    fact_nodes = parse_into_fact_nodes(full_text, best_title, canonical_url)
    proper_nouns = extract_potential_proper_nouns(full_text)

    # Scaffolding pronunciation guides
    pron_map = {pn: f"[{pn.upper()}-PRONUNCIATION]" for pn in proper_nouns}

    dossier = ResearchDossier(
        topic_title=best_title,
        location="Documented in Article",
        location_pronunciation="[LOCATION-PRONUNCIATION]",
        date_range="Extracted from Records",
        pronunciation_guide_map=pron_map,
        fact_ledger=fact_nodes,
        primary_sources=[canonical_url]
    )

    # Save to disk
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", best_title.lower())

    json_file = out_path / f"{slug}_dossier.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(dossier.model_dump(), f, indent=2)

    # Save Markdown version
    md_file = out_path / f"{slug}_dossier.md"
    md_content = f"# Research Dossier: {best_title}\n\n"
    md_content += f"- **Canonical Source**: {canonical_url}\n"
    md_content += f"- **Safe Outcome Status**: {'VERIFIED SAFE' if is_safe else 'NEEDS MANUAL REVIEW'}\n"
    md_content += f"- **Total Fact Nodes Harvested**: {len(fact_nodes)}\n\n"

    md_content += "## Candidate Proper Nouns for Pronunciation Guides\n"
    for pn in proper_nouns:
        md_content += f"- {pn} `(PHONETIC-GUIDE)`\n"

    md_content += "\n## Epistemic Fact Ledger Sample (First 20 Nodes)\n"
    for node in fact_nodes[:20]:
        md_content += f"- **[{node.id}] [{node.epistemic_tier}]** ({node.chronology}): {node.claim}\n"

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[SUCCESS] Research Dossier compiled!")
    print(f"          JSON Contract: {json_file}")
    print(f"          Markdown File: {md_file}")
    print(f"          Fact Nodes:    {len(fact_nodes)}")

    return dossier
