"""
v2.01 Release Validation — Scoring Engine

Parses claude -p output and computes weighted scores for each test type.
"""

import re


# --- Tier adjacency for partial credit ---
TIER_ORDER = ["STRICT", "STANDARD", "LIGHT", "EXEMPT"]
TIER_INDEX = {t: i for i, t in enumerate(TIER_ORDER)}


def _tier_distance(actual: str, expected: str) -> int:
    """Distance between two tiers. 0 = exact match, 1 = adjacent, 2+ = far."""
    a = TIER_INDEX.get(actual.upper(), -1)
    e = TIER_INDEX.get(expected.upper(), -1)
    if a < 0 or e < 0:
        return 99
    return abs(a - e)


# --- Prose fallback helpers ---

def _find_prose_tier(output: str) -> str | None:
    """Find a tier name mentioned in prose output (not in a structured header).

    Looks for tier names in various natural-language contexts:
      - "STRICT tier", "tier: STRICT", "classify as STRICT"
      - "this is EXEMPT", "falls under STANDARD"
      - Bare tier names surrounded by word boundaries

    Avoids false positives from tier enumeration (e.g., listing all four tiers
    while explaining the classification system).
    """
    # First, check if the output is enumerating tiers (lists 3+ tier names).
    # In that case, we need stronger contextual signal to identify the *selected* tier.
    tier_mention_counts = {
        tier: len(re.findall(rf"\b{tier}\b", output))
        for tier in TIER_ORDER
    }
    tiers_mentioned = sum(1 for c in tier_mention_counts.values() if c > 0)
    is_enumeration = tiers_mentioned >= 3

    # Strong contextual patterns (tier used in self-classification context)
    # These indicate the model is classifying the *current task*, not describing tiers
    for tier in TIER_ORDER:
        self_classification_patterns = [
            rf"(?:this|the\s+task)\s+(?:is|falls?|classif\w*)\s+(?:as\s+|under\s+|into\s+)?{tier}\b",
            rf"(?:classify|categorize|assign)\s+(?:this\s+)?(?:as\s+)?{tier}\b",
            rf"(?:correctly\s+)?classif\w*\s+as\s+{tier}\b",
            rf"{tier}\s+tier\s+(?:per|because|since|as|due)",
            rf"(?:expected|suggested|recommended|appropriate)\s+tier[:\s]+{tier}\b",
        ]
        for pat in self_classification_patterns:
            if re.search(pat, output, re.IGNORECASE):
                return tier

    # If not an enumeration, use broader contextual patterns
    if not is_enumeration:
        for tier in TIER_ORDER:
            contextual_patterns = [
                rf"\b{tier}\b\s+tier",
                rf"tier[:\s]+{tier}\b",
                rf"classif\w*\s+(?:as\s+)?{tier}\b",
                rf"falls?\s+(?:under|into|in)\s+{tier}\b",
                rf"(?:is|be|as)\s+{tier}\b",
                rf"\b{tier}\b\s+(?:compliance|classification|category)",
            ]
            for pat in contextual_patterns:
                if re.search(pat, output, re.IGNORECASE):
                    return tier

        # Weak match: bare tier name with word boundaries (case-sensitive to
        # avoid false positives like "standard" in prose meaning "normal")
        for tier in TIER_ORDER:
            if re.search(rf"\b{tier}\b", output):
                return tier

    # For enumerations: only return a tier if one stands out significantly
    # (mentioned 2x+ more than others), suggesting emphasis rather than listing
    if is_enumeration:
        max_count = max(tier_mention_counts.values())
        if max_count >= 2:
            leaders = [
                t for t, c in tier_mention_counts.items()
                if c == max_count and c >= 2
            ]
            # Only return if exactly one tier dominates
            if len(leaders) == 1:
                return leaders[0]

    return None


def _find_prose_confidence(output: str) -> float:
    """Extract a confidence signal from prose output.

    Returns a score from 0.0 to 1.0 representing confidence-awareness:
      - 1.0: explicit high confidence (percentage >= 70% or "high confidence")
      - 0.75: explicit percentage stated (any value)
      - 0.60: protocol-correct behavior (asking questions due to low confidence)
      - 0.50: mentions confidence concept at all
      - 0.0: no confidence signal
    """
    # Explicit percentage (e.g., "95%", "confidence: 0.85", "confidence of 85%")
    pct_match = re.search(
        r"(?:confidence|certainty)[:\s]*(?:of\s+)?(\d{1,3})(?:\s*%|\.\d+)",
        output,
        re.IGNORECASE,
    )
    if pct_match:
        val = int(pct_match.group(1))
        # Handle "0.85" format (captured as "0")
        if val == 0:
            float_match = re.search(r"(\d\.\d+)", pct_match.group(0))
            if float_match:
                val = int(float(float_match.group(1)) * 100)
        return 1.0 if val >= 70 else 0.75

    # Decimal confidence (e.g., "confidence 0.9", "confidence: 0.85")
    dec_match = re.search(
        r"(?:confidence|certainty)[:\s]*(\d\.\d+)", output, re.IGNORECASE
    )
    if dec_match:
        val = float(dec_match.group(1))
        return 1.0 if val >= 0.70 else 0.75

    # High confidence phrases
    high_conf_patterns = [
        r"high\s+confidence",
        r"(?:very\s+)?confident\s+(?:that|this)",
        r"clearly\s+(?:a|an)\s+\w+\s+tier",
        r"(?:definitely|certainly|obviously)\s+(?:a\s+)?\w+\s+tier",
    ]
    for pat in high_conf_patterns:
        if re.search(pat, output, re.IGNORECASE):
            return 1.0

    # Protocol-correct: asking questions due to low confidence
    low_conf_question_patterns = [
        r"confidence\s*<\s*\d",
        r"(?:low|insufficient)\s+confidence",
        r"(?:need|require)\s+(?:more\s+)?(?:information|clarification|context)",
        r"(?:ask|asking)\s+(?:for\s+)?(?:clarification|questions)",
        r"unclear\s+(?:where|what|how|whether)",
        r"what\s+(?:would\s+you|do\s+you)\s+(?:like|want|mean)",
    ]
    for pat in low_conf_question_patterns:
        if re.search(pat, output, re.IGNORECASE):
            return 0.60

    # Any mention of confidence concept
    if re.search(r"\bconfiden(?:ce|t)\b", output, re.IGNORECASE):
        return 0.50

    return 0.0


def _find_prose_keywords(output: str, expected_tier: str) -> float:
    """Detect classification-relevant keywords in prose output.

    Returns a score from 0.0 to 1.0:
      - 1.0: multiple tier-relevant keywords found
      - 0.75: at least one tier-relevant keyword found
      - 0.50: general classification vocabulary present
      - 0.0: no keyword signal
    """
    # Tier-specific keyword families
    tier_keywords = {
        "STRICT": [
            r"\bsecurit(?:y|ies)\b", r"\bvulnerabilit(?:y|ies)\b",
            r"\bauth(?:entication|orization)?\b", r"\bdatabase\b",
            r"\bmulti-?file\b", r"\brefactor\b", r"\bcompliance\b",
            r"\bthreat\b", r"\bcritical\b",
        ],
        "STANDARD": [
            r"\badd\b", r"\bimplement\b", r"\bfix\b", r"\bupdate\b",
            r"\bfeature\b", r"\bendpoint\b", r"\bpagination\b",
            r"\bdevelop\b", r"\bcreate\b",
        ],
        "LIGHT": [
            r"\btypo\b", r"\bcomment\b", r"\bformatting\b",
            r"\bminor\b", r"\btrivial\b", r"\bwhitespace\b",
            r"\bspelling\b",
        ],
        "EXEMPT": [
            r"\bexplain\b", r"\bread-?only\b", r"\bsearch\b",
            r"\bbrainstorm\b", r"\bgit\s+status\b", r"\bunderstand\b",
            r"\bexploration\b", r"\bno\s+(?:code\s+)?modif(?:ication|y)\b",
        ],
    }

    # Check expected tier keywords
    expected_kws = tier_keywords.get(expected_tier.upper(), [])
    matches = sum(
        1 for pat in expected_kws if re.search(pat, output, re.IGNORECASE)
    )

    if matches >= 2:
        return 1.0
    elif matches >= 1:
        return 0.75

    # General classification vocabulary
    general_patterns = [
        r"\btier\b", r"\bclassif(?:y|ication)\b", r"\bcompliance\b",
        r"\bscope\b", r"\brisk\b", r"\bseverity\b",
    ]
    general_matches = sum(
        1 for pat in general_patterns if re.search(pat, output, re.IGNORECASE)
    )
    if general_matches >= 1:
        return 0.50

    return 0.0


# --- Classification header parser ---
def parse_classification_header(output: str) -> dict | None:
    """Extract tier classification from SC:TASK-UNIFIED:CLASSIFICATION block."""
    # Try strict HTML comment format first
    pattern = (
        r"SC:TASK-UNIFIED:CLASSIFICATION\s*-->\s*\n"
        r"TIER:\s*(\w+)\s*\n"
        r"CONFIDENCE:\s*([\d.]+)\s*\n"
        r"KEYWORDS:\s*(.+?)\s*\n"
        r"OVERRIDE:\s*(\w+)\s*\n"
        r"RATIONALE:\s*(.+?)\s*\n"
    )
    match = re.search(pattern, output)

    if not match:
        # Fallback: try looser pattern (some models may format slightly differently)
        tier_match = re.search(r"TIER:\s*(\w+)", output)
        conf_match = re.search(r"CONFIDENCE:\s*([\d.]+)", output)
        kw_match = re.search(r"KEYWORDS:\s*(.+?)(?:\n|$)", output)

        if tier_match:
            return {
                "tier": tier_match.group(1).upper(),
                "confidence": float(conf_match.group(1)) if conf_match else 0.0,
                "keywords": (
                    [k.strip() for k in kw_match.group(1).split(",")]
                    if kw_match
                    else []
                ),
                "override": False,
                "rationale": "",
                "partial_parse": True,
            }
        return None

    return {
        "tier": match.group(1).upper(),
        "confidence": float(match.group(2)),
        "keywords": [k.strip() for k in match.group(3).split(",")],
        "override": match.group(4).lower() == "true",
        "rationale": match.group(5).strip(),
        "partial_parse": False,
    }


# --- Structural scoring ---
def score_structural(test_id: str, output: str, exit_code: int) -> dict:
    """Score a structural test."""
    if test_id == "S5":
        # S5 is proportional: count of 5 commands with correct frontmatter
        match = re.search(r"(\d+)/(\d+)", output)
        if match:
            found = int(match.group(1))
            total = int(match.group(2))
            ratio = found / total if total > 0 else 0.0
            return {
                "pass": exit_code == 0,
                "found": found,
                "total": total,
                "weighted_total": ratio,
            }

    # Binary scoring for S1-S4
    passed = exit_code == 0
    return {
        "pass": passed,
        "weighted_total": 1.0 if passed else 0.0,
    }


# --- Classification scoring ---
def score_classification(output: str, expected_tier: str) -> dict:
    """Score a tier classification behavioral test.

    Rubric (weights unchanged):
      header_present: 0.25 weight
      tier_correct:   0.40 weight
      confidence:     0.20 weight
      keywords:       0.15 weight

    Scoring paths:
      FORMAT PATH — full or partial header parsed (as before)
      PROSE FALLBACK — no header, but correct behavior expressed in natural language

    Design: format compliance is always rewarded more than prose compliance.
    A format-compliant output with correct tier scores 1.0.
    A prose-only output with correct tier and good signals scores ~0.52 max.
    This eliminates the cliff effect (previous max without header: 0.10).
    """
    parsed = parse_classification_header(output)
    scores = {}

    # 1. Header present (0.25) — unchanged, format compliance only
    if parsed and not parsed.get("partial_parse"):
        scores["header_present"] = 1.0
    elif parsed:
        scores["header_present"] = 0.5  # Partial header
    else:
        scores["header_present"] = 0.0

    # 2. Tier correct (0.40)
    if parsed:
        # FORMAT PATH: tier extracted from structured header
        distance = _tier_distance(parsed["tier"], expected_tier)
        if distance == 0:
            scores["tier_correct"] = 1.0
        elif distance == 1:
            scores["tier_correct"] = 0.5
        else:
            scores["tier_correct"] = 0.0
    else:
        # PROSE FALLBACK: check for tier mention in natural language
        prose_tier = _find_prose_tier(output)
        if prose_tier:
            distance = _tier_distance(prose_tier, expected_tier)
            if distance == 0:
                scores["tier_correct"] = 0.65  # Correct tier in prose
            elif distance == 1:
                scores["tier_correct"] = 0.35  # Adjacent tier in prose
            else:
                scores["tier_correct"] = 0.10  # Wrong tier but tier-aware
        else:
            # Legacy: bare word match (weaker signal)
            if re.search(rf"\b{expected_tier}\b", output, re.IGNORECASE):
                scores["tier_correct"] = 0.25  # Mentioned but no context
            else:
                scores["tier_correct"] = 0.0

    # 3. Confidence adequate (0.20)
    if parsed and parsed.get("confidence", 0) >= 0.70:
        scores["confidence_adequate"] = 1.0
    elif parsed and parsed.get("confidence", 0) >= 0.50:
        scores["confidence_adequate"] = 0.5
    elif parsed:
        scores["confidence_adequate"] = 0.0
    else:
        # PROSE FALLBACK: detect confidence signals in natural language
        scores["confidence_adequate"] = _find_prose_confidence(output)

    # 4. Keywords present (0.15)
    if parsed and parsed.get("keywords") and parsed["keywords"] != ["none"]:
        scores["keywords_relevant"] = 1.0
    elif parsed:
        scores["keywords_relevant"] = 0.5
    else:
        # PROSE FALLBACK: detect classification-relevant keywords
        scores["keywords_relevant"] = _find_prose_keywords(output, expected_tier)

    # Weighted total
    weights = {
        "header_present": 0.25,
        "tier_correct": 0.40,
        "confidence_adequate": 0.20,
        "keywords_relevant": 0.15,
    }
    scores["weighted_total"] = sum(
        scores.get(k, 0) * w for k, w in weights.items()
    )
    scores["parsed"] = parsed or {}

    return scores


# --- Wiring scoring ---
def score_wiring(output: str, detection_patterns: list[str]) -> dict:
    """Score a skill invocation wiring test.

    Rubric:
      skill_invoked:    0.35 weight  (first pattern = protocol name)
      protocol_flow:    0.35 weight  (remaining patterns = flow signals)
      no_raw_dump:      0.15 weight  (command file not echoed verbatim)
      tool_engagement:  0.15 weight  (evidence of tool use)
    """
    scores = {}

    # 1. Skill invoked (0.35) — first detection pattern is the protocol name
    if detection_patterns:
        skill_pattern = detection_patterns[0]
        if re.search(skill_pattern, output, re.IGNORECASE):
            scores["skill_invoked"] = 1.0
        elif re.search(r"protocol|skill|SKILL\.md", output, re.IGNORECASE):
            scores["skill_invoked"] = 0.5  # Generic protocol reference
        else:
            scores["skill_invoked"] = 0.0
    else:
        scores["skill_invoked"] = 0.0

    # 2. Protocol flow started (0.35) — remaining patterns
    flow_patterns = detection_patterns[1:] if len(detection_patterns) > 1 else []
    if flow_patterns:
        flow_matches = sum(
            1 for p in flow_patterns if re.search(p, output, re.IGNORECASE)
        )
        flow_ratio = flow_matches / len(flow_patterns)
        scores["protocol_flow"] = min(1.0, flow_ratio * 1.25)  # Slight boost
    else:
        scores["protocol_flow"] = 0.0

    # 3. No raw command dump (0.15)
    # Check if the command file was echoed verbatim (bad sign)
    raw_dump_indicators = [
        r"^---\nname:",  # YAML frontmatter echoed
        r"allowed-tools:.*\n.*mcp-servers:",  # Two consecutive frontmatter fields
    ]
    is_dump = any(re.search(p, output, re.MULTILINE) for p in raw_dump_indicators)
    scores["no_raw_dump"] = 0.0 if is_dump else 1.0

    # 4. Tool engagement (0.15)
    tool_indicators = [
        r"Read|Grep|Glob|Edit|Write|Bash|Task|Skill",  # Tool names
        r"reading file|searching|found \d+",  # Action descriptions
        r"```",  # Code blocks (often from tool output)
    ]
    tool_matches = sum(
        1 for p in tool_indicators if re.search(p, output, re.IGNORECASE)
    )
    scores["tool_engagement"] = min(1.0, tool_matches / 2.0)

    # Weighted total
    weights = {
        "skill_invoked": 0.35,
        "protocol_flow": 0.35,
        "no_raw_dump": 0.15,
        "tool_engagement": 0.15,
    }
    scores["weighted_total"] = sum(
        scores.get(k, 0) * w for k, w in weights.items()
    )

    return scores
