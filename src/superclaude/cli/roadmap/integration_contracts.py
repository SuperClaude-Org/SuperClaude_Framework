"""Integration contract extraction and verification.

Extracts non-obvious integration points from spec text and verifies
each has an explicit corresponding task in the roadmap. Catches the
"pattern-matching trap" where LLMs assume standard skeleton->implement
phasing covers custom dispatch/wiring mechanisms.

Pure function: content in, findings out. No I/O.

Implements FR-MOD2.1 through FR-MOD2.6.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# --- FR-MOD2.1: 7-category dispatch pattern scanner with compiled regexes ---

DISPATCH_PATTERNS = [
    # Category 1: Dict dispatch tables
    re.compile(
        r"\b(?:dispatch[_\s]?table|DISPATCH_TABLE|PROGRAMMATIC_RUNNERS|"
        r"RUNNERS|_RUNNERS|HANDLERS|"
        r"routing[_\s]?table|command[_\s]?map|step[_\s]?map|"
        r"plugin[_\s]?registry|"
        # NEW: compound dispatch nouns — keeps mechanism semantics,
        # rejects bare "dispatch" AND bare "priority dispatch" in prose
        # (bare `priority` removed from list per t7 design intent —
        # Layer 3 identifier-overlap guard is the false-positive defense)
        r"(?:[a-z]+-)?(?:class-priority|named-theme|role-keyed|"
        r"theme|severity-keyed|module-tier|subprocess|gRPC)[\s_-]?dispatch"
        r")\b",
        re.IGNORECASE,
    ),
    # Category 2: Plugin registry / explicit wiring
    re.compile(
        r"\b(?:populate|register|wire|inject|bind|map|route)\s+"
        r"(?:the\s+|all\s+|each\s+)?"
        r"(?:implementations?|runners?|handlers?|plugins?|steps?|commands?)\b",
        re.IGNORECASE,
    ),
    # Category 3: Callback injection / constructor injection
    re.compile(
        r"\b(?:accepts?|takes?|requires?|expects?)\s+(?:a\s+)?"
        r"(?:Callable|Protocol|ABC|Interface|Factory|Provider|Registry)\b",
        re.IGNORECASE,
    ),
    # Category 3 (continued): Type annotations for dispatch
    re.compile(
        r"\b(?:Dict|Mapping|dict)\s*\[\s*str\s*,\s*(?:Callable|Awaitable|Coroutine)\b",
        re.IGNORECASE,
    ),
    # Category 4: Strategy pattern (code-specific patterns only, not section headings)
    # Bare "Strategy" removed — it matches headings like "Testing Strategy" and
    # "Migration Strategy" which are document structure, not code patterns.
    re.compile(
        r"\b(?:Context\s*\(\s*strategy\s*=|ConcreteStrategy|"
        r"set_strategy|get_strategy|StrategyPattern|"
        r"strategy_registry|STRATEGY_MAP|AbstractStrategy)\b",
        re.IGNORECASE,
    ),
    # Category 5: Middleware chain
    re.compile(
        r"\b(?:middleware|app\.use|pipeline\.add|add_middleware|"
        r"use_middleware)\b",
        re.IGNORECASE,
    ),
    # Category 6: Event binding
    re.compile(
        r"\b(?:emitter\.on|addEventListener|subscribe|on_event|"
        r"event_handler|add_listener)\b",
        re.IGNORECASE,
    ),
    # Category 7: DI container
    re.compile(
        r"\b(?:container\.bind|container\.register|Provider|"
        r"Injector|inject_dependency|DependencyContainer)\b",
        re.IGNORECASE,
    ),
]

# FR-MOD2.3: Verb-anchored wiring task coverage patterns
WIRING_TASK_PATTERNS = [
    # Explicit creation/population of dispatch/registry mechanisms
    re.compile(
        r"\b(?:create|build|construct|populate|wire|assemble|register)\s+"
        r"(?:the\s+|a\s+)?"
        r"(?:dispatch|routing|registry|runner|handler|command|middleware|"
        r"event|strategy|plugin)\s*"
        r"(?:table|map|dict|registry|lookup|chain|binding|container)\b",
        re.IGNORECASE,
    ),
    # Explicit wiring of implementations into mechanisms
    re.compile(
        r"\b(?:wire|connect|bind|inject|register|plug)\s+.*?"
        r"(?:implementations?|runners?|handlers?|plugins?|strategies?|"
        r"middlewares?|listeners?)\s+"
        r"(?:into|to|with|in)\b",
        re.IGNORECASE,
    ),
    # FR-MOD2.4: Specific named mechanisms (UPPER_SNAKE_CASE, PascalCase)
    re.compile(
        r"\bPROGRAMMATIC_RUNNERS\b|\bDISPATCH_TABLE\b|\bHANDLER_REGISTRY\b|"
        r"\bMIDDLEWARE_CHAIN\b|\bEVENT_BINDINGS\b|\bROUTE_MAP\b",
    ),
    # Strategy/middleware/event-specific wiring verbs
    re.compile(
        r"\b(?:configure|set[_\s]up|initialize|bootstrap)\s+"
        r"(?:the\s+)?"
        r"(?:strategy|middleware|event\s+binding|DI\s+container|"
        r"dependency\s+injection|plugin\s+registry)\b",
        re.IGNORECASE,
    ),
]


# --- FR-MOD2.6: Dataclasses ---


@dataclass
class IntegrationContract:
    """A single integration point extracted from a spec."""

    id: str  # IC-001, IC-002, ...
    mechanism: str  # "dispatch_table", "registry", "injection", etc.
    spec_evidence: str  # verbatim quote from spec
    spec_location: str  # line number or section heading
    description: str  # human-readable description
    requires_explicit_wiring: bool  # True if cannot be implicit
    # NEW
    mechanism_signature: tuple[str, frozenset[str]] = field(
        default=(("", frozenset()))
    )
    # signature = (mechanism, frozenset of normalized identifiers)


@dataclass
class WiringCoverage:
    """Result of checking whether a contract is covered by roadmap tasks."""

    contract: IntegrationContract
    covered: bool
    roadmap_evidence: str  # quote from roadmap if covered, empty if not
    roadmap_location: str  # phase/task if covered


@dataclass
class IntegrationAuditResult:
    """Full audit result: all contracts and their coverage status."""

    contracts: list[IntegrationContract] = field(default_factory=list)
    coverage: list[WiringCoverage] = field(default_factory=list)
    uncovered_count: int = 0
    total_count: int = 0

    @property
    def all_covered(self) -> bool:
        """Returns True only when uncovered_contracts == 0."""
        return self.uncovered_count == 0


# --- Public API ---


def extract_integration_contracts(spec_text: str) -> list[IntegrationContract]:
    """Extract integration contracts from spec text using pattern matching.

    FR-MOD2.1: Scans spec text for 7-category dispatch patterns.
    FR-MOD2.2: Context capture (3 lines), mechanism classification,
               sequential ID assignment, deduplication.

    Returns a list of IntegrationContract instances.
    """
    contracts: list[IntegrationContract] = []
    lines = spec_text.splitlines()
    seen_signatures: dict[tuple[str, frozenset[str]], int] = {}
    counter = 1

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("- ["):
            continue

        for pattern in DISPATCH_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue

            evidence = line.strip()
            context_start = max(0, i - 3)
            context_end = min(len(lines), i + 4)
            context = "\n".join(lines[context_start:context_end])

            mechanism = _classify_mechanism(match.group(0))
            idents = frozenset(_extract_identifiers(context))
            signature = (mechanism, idents)

            # Signature-based dedup — collapse contracts whose
            # (mechanism, identifier-set) is identical OR is a strict
            # subset of an already-seen signature.
            if _signature_subsumed(signature, seen_signatures):
                continue
            seen_signatures[signature] = counter

            contracts.append(IntegrationContract(
                id=f"IC-{counter:03d}",
                mechanism=mechanism,
                spec_evidence=context,
                spec_location=f"line {i + 1}",
                description=f"{mechanism}: {evidence}",
                requires_explicit_wiring=True,
                mechanism_signature=signature,
            ))
            counter += 1
            break  # one contract per line max

    return contracts


def check_roadmap_coverage(
    contracts: list[IntegrationContract],
    roadmap_text: str,
) -> IntegrationAuditResult:
    """Check whether each integration contract has explicit roadmap coverage.

    FR-MOD2.3: Verb-anchored wiring task coverage check.
    FR-MOD2.5: Wiring-task-specific coverage semantics — a contract is
    "covered" only if the roadmap contains a task that explicitly mentions
    creating, populating, or wiring the mechanism.

    Returns IntegrationAuditResult with all contracts and their coverage.
    """
    result = IntegrationAuditResult(
        contracts=contracts,
        total_count=len(contracts),
    )

    roadmap_lines = roadmap_text.splitlines()

    for contract in contracts:
        covered = False
        evidence = ""
        location = ""

        # Check for explicit wiring tasks in roadmap
        for pattern in WIRING_TASK_PATTERNS:
            for j, rline in enumerate(roadmap_lines):
                if pattern.search(rline):
                    covered = True
                    evidence = rline.strip()
                    location = f"line {j + 1}"
                    break
            if covered:
                break

        # FR-MOD2.4: Also check for specific mechanism identifiers
        if not covered:
            identifiers = _extract_identifiers(contract.spec_evidence)
            for ident in identifiers:
                for j, rline in enumerate(roadmap_lines):
                    if ident.upper() in rline.upper():
                        covered = True
                        evidence = rline.strip()
                        location = f"line {j + 1}"
                        break
                if covered:
                    break

        # FR-MOD2.7: Broad mechanism-term coverage check (3-layer).
        # Layer 1: dispatch-family-specific tolerance for adjective-compound
        #          dispatch nouns (class-priority/named-theme/etc.).
        # Layer 2: existing literal mechanism-term substring + impl verb
        #          (same line or 3-line window).
        # Layer 3: generic stem-fallback for any compound mechanism term,
        #          constrained by identifier-overlap against the contract's
        #          persisted mechanism_signature (defeats the
        #          "Implement priority dispatch for logging" false-positive).
        if not covered:
            mechanism_term = contract.mechanism.replace("_", " ")
            raw_terms = [mechanism_term]
            if "middleware" in contract.description.lower():
                raw_terms.append("middleware")
            if "strategy" in contract.description.lower():
                raw_terms.append("strategy")

            # Layer 1: dispatch-family-specific tolerance (Opus base).
            # NOTE: bare `priority` removed from alternation list — Layer 3
            # identifier-overlap guard is the design's false-positive defense
            # for prose-level "priority dispatch" without identifier context.
            dispatch_family = re.compile(
                r"\b(?:[a-z]+-)?(?:class-priority|named-theme|"
                r"role-keyed|theme|severity-keyed|module-tier|subprocess|gRPC)"
                r"[\s_-]?dispatch(?:\s+table)?\b",
                re.IGNORECASE,
            )

            impl_verbs = re.compile(
                r"\b(?:implement|configure|add|create|set\s*up|deploy|"
                r"build|integrate|wire|enable|install|bound|attach|"
                r"apply|use|route|log|emit|handle|populate)\b",  # +populate (Opus)
                re.IGNORECASE,
            )

            # Layer 1+2: full-term and dispatch-family — same-line or 3-line window verb
            for j, rline in enumerate(roadmap_lines):
                hit_term = any(t.lower() in rline.lower() for t in raw_terms)
                hit_family = (
                    contract.mechanism == "dispatch_table"
                    and dispatch_family.search(rline)
                )
                if not (hit_term or hit_family):
                    continue
                if impl_verbs.search(rline):
                    covered = True
                    evidence = rline.strip()
                    location = f"line {j + 1}"
                    break
                window_start = max(0, j - 2)
                window_end = min(len(roadmap_lines), j + 3)
                window_text = " ".join(roadmap_lines[window_start:window_end])
                if impl_verbs.search(window_text):
                    covered = True
                    evidence = rline.strip()
                    location = f"lines {window_start + 1}-{window_end}"
                    break

            # Layer 3 (NEW from Sonnet, with overlap guard from Sonnet's counter-arg
            # mitigation): generic stem fallback for ANY compound mechanism term.
            # SAME-LINE constraint AND identifier-overlap guard against the
            # contract's persisted mechanism_signature.
            if not covered:
                stem_terms: list[str] = []
                for mt in raw_terms:
                    parts = mt.split()
                    if len(parts) >= 2:
                        stem_terms.append(parts[0])  # "dispatch" from "dispatch table"

                contract_idents = contract.mechanism_signature[1]  # frozenset
                for stem in stem_terms:
                    for j, rline in enumerate(roadmap_lines):
                        if stem.lower() not in rline.lower():
                            continue
                        if not impl_verbs.search(rline):
                            continue
                        # IDENTIFIER-OVERLAP GUARD: require at least one of the
                        # contract's mechanism_signature identifiers to appear in
                        # the matching line's 3-line window. Defeats the
                        # "Implement priority dispatch for logging" false-positive
                        # class (Sonnet's own counter-argument scenario).
                        if contract_idents:
                            window_start = max(0, j - 2)
                            window_end = min(len(roadmap_lines), j + 3)
                            window_text = " ".join(roadmap_lines[window_start:window_end])
                            if not any(ident in window_text for ident in contract_idents):
                                continue
                        covered = True
                        evidence = rline.strip()
                        location = f"line {j + 1} (stem+overlap)"
                        break
                    if covered:
                        break

        result.coverage.append(
            WiringCoverage(
                contract=contract,
                covered=covered,
                roadmap_evidence=evidence,
                roadmap_location=location,
            )
        )

        if not covered:
            result.uncovered_count += 1

    return result


# --- Internal helpers ---


def _classify_mechanism(matched_text: str) -> str:
    """Classify matched text into a mechanism category."""
    lower = matched_text.lower()
    if any(
        k in lower for k in ("dispatch", "runner", "handler", "command_map", "step_map")
    ):
        return "dispatch_table"
    if "registry" in lower or "register" in lower:
        return "registry"
    if any(
        k in lower for k in ("inject", "callable", "protocol", "factory", "provider")
    ):
        return "dependency_injection"
    if any(k in lower for k in ("wire", "bind", "populate")):
        return "explicit_wiring"
    if any(k in lower for k in ("route", "routing")):
        return "routing"
    if any(k in lower for k in ("strategy", "concretestrategy")):
        return "strategy_pattern"
    if any(k in lower for k in ("middleware", "app.use", "pipeline.add")):
        return "middleware_chain"
    if any(
        k in lower for k in ("emitter", "addeventlistener", "subscribe", "listener")
    ):
        return "event_binding"
    if any(k in lower for k in ("container", "injector", "dependencycontainer")):
        return "di_container"
    return "integration_point"


def _extract_identifiers(text: str) -> list[str]:
    """Extract UPPER_SNAKE_CASE and PascalCase identifiers from text.

    FR-MOD2.4: Named mechanism identifier matching.
    """
    # UPPER_SNAKE_CASE (likely constants/tables)
    upper_snake = re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", text)
    # PascalCase class names
    pascal = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", text)
    return upper_snake + pascal


def _signature_subsumed(
    sig: tuple[str, frozenset[str]],
    seen: dict[tuple[str, frozenset[str]], int],
) -> bool:
    """Subsume sig if same mechanism AND identifier-set ⊆ an existing one
    that shares ≥1 identifier. Empty-identifier signatures dedup by exact
    match only (preserves test_duplicate_lines_deduplicated)."""
    mech, idents = sig
    if not idents:
        return sig in seen
    for (smech, sidents) in seen:
        if smech != mech:
            continue
        if idents and sidents and idents.issubset(sidents) and (idents & sidents):
            return True
        if idents == sidents:
            return True
    return False
