# Extraction Pipeline Reference

Reference document for Wave 1B: Detection & Analysis. Contains the 8-step extraction pipeline, domain keyword dictionaries, ID assignment rules, chunked extraction protocol, and 4-pass completeness verification.

---

## 8-Step Extraction Pipeline

Process the specification file in 8 sequential steps. Each step produces structured output that feeds into subsequent steps.

### Step 1: Title & Overview Extraction

Extract the project title, version, and high-level summary from the spec's opening sections (typically H1 heading, metadata block, and executive summary).

**Output**: `project_title`, `project_version`, `summary` (1-3 sentences)

### Step 2: Functional Requirements (FRs)

Scan the spec for functional requirements. Look for:
- Explicit requirement sections (headings containing "requirement", "feature", "capability")
- Behavioral statements ("shall", "must", "will", "should")
- User stories ("As a...", "I want...", "So that...")
- Acceptance criteria blocks

For each FR, extract:
| Field | Description |
|-------|-------------|
| `id` | Assigned in Step 8 |
| `description` | Clear statement of the requirement |
| `domain` | Classified in Step 4 |
| `priority` | P0 (must-have), P1 (should-have), P2 (nice-to-have), P3 (future) |
| `source_lines` | Line range in original spec (e.g., L12-L18) |

**Priority assignment heuristic**:
- "must", "required", "critical", "blocking" → P0
- "should", "important", "expected" → P1
- "nice to have", "optional", "could" → P2
- "future", "planned", "roadmap", "v2", "later" → P3
- No explicit signal → P1 (default)

### Step 3: Non-Functional Requirements (NFRs)

Scan for non-functional requirements:
- Performance constraints (latency, throughput, load)
- Security requirements (auth, encryption, compliance)
- Scalability targets (user count, data volume)
- Reliability (uptime, recovery time)
- Maintainability (code coverage, documentation)

For each NFR, extract:
| Field | Description |
|-------|-------------|
| `id` | Assigned in Step 8 |
| `description` | Clear statement |
| `category` | performance, security, scalability, reliability, maintainability |
| `constraint` | Measurable threshold (e.g., "<200ms response time") |
| `source_lines` | Line range in original spec |

### Step 4: Scope & Domain Classification

Classify every extracted requirement into one or more domains using the domain keyword dictionaries (see below). Compute domain distribution as percentages.

**Classification algorithm**:
1. For each requirement, tokenize the description into words
2. Match tokens against each domain's keyword dictionary
3. Apply keyword weights (primary keywords weight 2.0, secondary keywords weight 1.0)
4. Assign requirement to the domain with highest weighted score
5. If multiple domains score within 15% of each other, assign to all qualifying domains (split attribution)
6. Compute domain distribution: `domain_percentage = (weighted_requirements_in_domain / total_weighted_requirements) * 100`

### Step 5: Dependency Extraction

Identify dependencies between requirements and external dependencies:
- Inter-requirement dependencies ("requires", "depends on", "after", "before", "blocks")
- External dependencies (third-party services, libraries, infrastructure)
- Implicit ordering (sequential spec sections often imply order)

For each dependency:
| Field | Description |
|-------|-------------|
| `id` | Assigned in Step 8 |
| `description` | What depends on what |
| `type` | `internal` (between requirements) or `external` (third-party) |
| `affected_requirements` | List of requirement IDs affected |
| `source_lines` | Line range in original spec |

### Step 6: Success Criteria Extraction

Extract measurable success criteria from the spec:
- Explicit success criteria sections
- Acceptance criteria attached to requirements
- KPIs, metrics, and targets mentioned anywhere in the spec

For each criterion:
| Field | Description |
|-------|-------------|
| `id` | Assigned in Step 8 |
| `description` | Measurable criterion |
| `derived_from` | Requirement IDs this criterion validates |
| `measurable` | Yes/No — is it objectively testable? |
| `source_lines` | Line range in original spec |

### Step 7: Risk Identification

Extract risks mentioned in the spec and infer risks from requirement complexity:

**Explicit risks**: Sections mentioning "risk", "concern", "challenge", "constraint", "limitation"

**Inferred risks** (generate if not explicit):
- High-complexity requirements (many dependencies) → integration risk
- External dependencies → availability risk
- Security requirements → compliance risk
- Performance constraints → scalability risk

For each risk:
| Field | Description |
|-------|-------------|
| `id` | Assigned in Step 8 |
| `description` | Risk statement |
| `probability` | Low, Medium, High |
| `impact` | Low, Medium, High |
| `affected_requirements` | List of requirement IDs |
| `source_lines` | Line range (or "inferred" if generated) |

### Step 8: ID Assignment

Assign deterministic IDs to all extracted items:

| Entity | Format | Sequence |
|--------|--------|----------|
| Functional Requirements | `FR-{3digits}` | FR-001, FR-002, ... ordered by `source_lines` |
| Non-Functional Requirements | `NFR-{3digits}` | NFR-001, NFR-002, ... ordered by `source_lines` |
| Dependencies | `DEP-{3digits}` | DEP-001, DEP-002, ... ordered by `source_lines` |
| Success Criteria | `SC-{3digits}` | SC-001, SC-002, ... ordered by `source_lines` |
| Risks | `RISK-{3digits}` | RISK-001, RISK-002, ... (explicit first, then inferred) |

**Ordering rule**: Items are assigned IDs in order of their `source_lines` position in the original spec. This ensures deterministic ID assignment across runs. Inferred items (no source line) are appended after explicit items.

**Cross-reference resolution**: After ID assignment, update all `affected_requirements`, `derived_from`, and `affected_requirements` fields with the assigned IDs.

---

## Domain Keyword Dictionaries

Five domain dictionaries for requirement classification. Each keyword has a weight: **primary** (2.0) keywords are strong domain indicators, **secondary** (1.0) keywords are weaker signals.

### Frontend Domain

**Primary** (weight 2.0): component, UI, UX, responsive, accessibility, WCAG, layout, CSS, styling, viewport, animation, render, DOM, browser, SPA, SSR, hydration

**Secondary** (weight 1.0): button, form, input, modal, dropdown, navigation, menu, page, screen, view, display, theme, dark mode, mobile, tablet, desktop, interaction, click, hover, scroll, toast, notification, badge

### Backend Domain

**Primary** (weight 2.0): API, endpoint, server, database, schema, migration, query, ORM, REST, GraphQL, microservice, service, controller, middleware, route, handler, CRUD, transaction, model

**Secondary** (weight 1.0): request, response, payload, JSON, HTTP, status code, webhook, queue, worker, job, cache, session, cookie, rate limit, pagination, filter, sort, batch, bulk, seed, fixture

### Security Domain

**Primary** (weight 2.0): authentication, authorization, encryption, vulnerability, threat, compliance, OWASP, CVE, token, JWT, OAuth, RBAC, ACL, XSS, CSRF, injection, sanitize, hash, salt, certificate

**Secondary** (weight 1.0): password, credential, permission, role, access control, audit log, security header, CORS, CSP, HTTPS, TLS, firewall, rate limit, brute force, session hijack, privilege escalation, data protection, GDPR, PCI, SOC2, secret, key rotation

### Performance Domain

**Primary** (weight 2.0): latency, throughput, optimization, benchmark, profiling, bottleneck, cache, CDN, load balancing, scaling, horizontal, vertical, memory, CPU, concurrent, parallel, async, lazy load

**Secondary** (weight 1.0): response time, load time, bundle size, compression, minification, tree shaking, code splitting, prefetch, preload, connection pooling, query optimization, index, denormalization, batch processing, pagination, infinite scroll, virtual scroll, web worker, service worker

### Documentation Domain

**Primary** (weight 2.0): documentation, README, guide, tutorial, reference, API docs, changelog, release notes, specification, wiki, onboarding, glossary

**Secondary** (weight 1.0): comment, docstring, type annotation, schema description, example, sample, walkthrough, FAQ, troubleshooting, architecture decision record, ADR, diagram, flowchart, sequence diagram

---

## Chunked Extraction Protocol

Activated when a specification file exceeds 500 lines. Processes the spec in multiple passes with full completeness verification.

### Activation

**Threshold**: 500 lines. Below this, use standard single-pass extraction (the 8-step pipeline above).

### Algorithm

#### 1. Section Index

Scan the spec for headings (H1-H3, detected by `#`, `##`, `###` prefixes) to build a structural map.

For each section, record:
- `heading`: The heading text
- `level`: 1, 2, or 3
- `start_line`: First line of the section (the heading line)
- `end_line`: Last line before the next same-or-higher-level heading (or EOF)
- `line_count`: `end_line - start_line + 1`
- `relevance_tag`: One of `FR_BLOCK`, `NFR_BLOCK`, `SCOPE`, `DEPS`, `RISKS`, `SUCCESS`, `OTHER`

**Relevance tagging heuristic**:
- Heading contains "requirement", "feature", "capability", "functional" → `FR_BLOCK`
- Heading contains "non-functional", "performance", "security", "scalability" → `NFR_BLOCK`
- Heading contains "scope", "boundary", "in scope", "out of scope" → `SCOPE`
- Heading contains "dependency", "dependencies", "integration" → `DEPS`
- Heading contains "risk", "concern", "constraint" → `RISKS`
- Heading contains "success", "criteria", "acceptance", "KPI" → `SUCCESS`
- All other headings → `OTHER`

#### 2. Chunk Assembly

Group sections into chunks targeting ~400 lines per chunk (hard maximum 600 lines).

**Rules**:
- Never split a section across chunks — sections are atomic units
- If a single section exceeds 600 lines, split at paragraph boundaries (blank lines)
- Pack sections sequentially until adding the next section would exceed 600 lines
- The title/overview section (first H1 + its content, up to 50 lines) is prepended as a **context header** to every chunk
- Context header lines do NOT count toward the 400/600 target — they are overhead
- Prefer grouping sections with the same `relevance_tag` together when possible

**Output**: Ordered list of chunks, each containing:
- `chunk_id`: 1-based index
- `sections`: List of sections included
- `line_range`: Start-end lines from original spec
- `line_count`: Total lines (excluding context header)
- `context_header`: First section content (prepended for context)

#### 3. Per-Chunk Extraction

Process each chunk through the 8-step extraction pipeline (Steps 1-7 only; Step 8 is deferred to global ID assignment).

**Per-chunk template**:
```
Chunk {chunk_id} of {total_chunks}
Line range: L{start}-L{end}
Sections: {section_list}

Context (from spec overview):
{context_header}

---
Chunk content:
{chunk_content}
```

**Important**:
- Each chunk produces a partial extraction result
- `source_lines` references must point to the ORIGINAL spec line numbers, not chunk-relative numbers
- Global ID counters are passed between chunks: `next_fr`, `next_nfr`, `next_dep`, `next_sc`, `next_risk` — this prevents ID collisions between chunks

#### 4. Merge

Concatenate partial results from all chunks by category in document order:
1. Concatenate all FRs from chunk 1, then chunk 2, etc.
2. Concatenate all NFRs from chunk 1, then chunk 2, etc.
3. Repeat for dependencies, success criteria, risks
4. Domain distribution: recompute from merged requirements (not averaged from chunks)
5. Project title/overview: use from chunk 1 only (which has the true overview section)

**Constraint**: This is a structural combination only — no re-interpretation, re-scoring, or re-classification of requirements during merge.

#### 5. Deduplication

Three deduplication checks on the merged result:

| Check | Condition | Action |
|-------|-----------|--------|
| ID collision | Same ID appears in two chunks | Keep first occurrence, discard second, log as `DEDUP_ID_COLLISION` |
| Exact description match | Normalized descriptions identical (case-insensitive, whitespace-normalized) | Keep first occurrence, discard second, log as `DEDUP_EXACT_MATCH` |
| Substring similarity | Similarity ratio > 0.8 (using normalized descriptions) | Keep BOTH items, flag as `DEDUP_REVIEW_NEEDED` |

**Normalization**: Lowercase, collapse whitespace, strip punctuation, remove articles (a, an, the).

#### 6. Cross-Reference Resolution

After merge, scan for unresolved references (e.g., a dependency referencing a requirement ID from another chunk):
1. For each unresolved reference, search merged results for matching items
2. If found: resolve to the correct ID
3. If not found: log as `UNRESOLVED_XREF` warning — do not invent or guess

#### 7. Global ID Assignment

Apply Step 8 (ID Assignment) to the merged, deduplicated, cross-referenced result:
- IDs that were explicitly assigned during per-chunk extraction are preserved
- Items without explicit IDs (implicit items) are assigned sequential IDs ordered by `source_lines`
- This produces the final, deterministic ID scheme for the entire extraction

### 4-Pass Completeness Verification

After merge and ID assignment, run 4 verification passes:

| Pass | Name | Method | PASS | WARN | FAIL |
|------|------|--------|------|------|------|
| 1 | Source Coverage | Grep original spec for requirement-indicating patterns ("shall", "must", "should", "will" + nouns); verify each pattern location appears in an extracted item's `source_lines` range | 100% | >=95% | <95% |
| 2 | Anti-Hallucination | For each extracted item, read the original spec at `source_lines` and verify the extraction accurately represents the spec content. Zero tolerance for fabricated requirements | 100% (any failure = FAIL) | N/A | Any failure |
| 3 | Section Coverage | Verify every section tagged as extraction-relevant (`FR_BLOCK`, `NFR_BLOCK`, `SCOPE`, `DEPS`, `RISKS`, `SUCCESS`) was assigned to at least one chunk | 100% | N/A | Any section missed |
| 4 | Count Reconciliation | `sum(chunk_counts) - dedup_removals = merged_totals` for each category (FRs, NFRs, deps, SCs, risks) | Exact match | N/A | Any mismatch |

**On verification failure**:
1. Identify which chunks failed
2. Re-process failing chunks (max 1 retry per chunk)
3. Re-run verification
4. If still failing: STOP with error. Do not produce partial extraction. Report: which pass failed, which chunks, and what was missing

### Worked Example: 1500-Line Spec

**Input**: A 1500-line security-focused microservice spec.

**Step 1: Section Index** (15 sections found):
| Section | Lines | Relevance |
|---------|-------|-----------|
| 1. Executive Summary | L1-L45 | OTHER |
| 2. Architecture Overview | L46-L120 | OTHER |
| 3. Authentication System | L121-L280 | FR_BLOCK |
| 4. Authorization & RBAC | L281-L420 | FR_BLOCK |
| 5. API Endpoints | L421-L580 | FR_BLOCK |
| 6. Data Models | L581-L700 | FR_BLOCK |
| 7. Performance Requirements | L701-L780 | NFR_BLOCK |
| 8. Security Requirements | L781-L900 | NFR_BLOCK |
| 9. Integration Points | L901-L980 | DEPS |
| 10. Success Criteria | L981-L1050 | SUCCESS |
| 11. Risk Assessment | L1051-L1150 | RISKS |
| 12. Migration Plan | L1151-L1280 | FR_BLOCK |
| 13. Testing Strategy | L1281-L1380 | OTHER |
| 14. Deployment Guide | L1381-L1450 | OTHER |
| 15. Appendix | L1451-L1500 | OTHER |

**Step 2: Chunk Assembly** (4 chunks):
| Chunk | Sections | Lines | Line Count |
|-------|----------|-------|------------|
| 1 | Context(L1-45) + Sections 1-4 | L1-L420 | 375 (excl. context) |
| 2 | Context(L1-45) + Sections 5-8 | L421-L900 | 480 |
| 3 | Context(L1-45) + Sections 9-12 | L901-L1280 | 380 |
| 4 | Context(L1-45) + Sections 13-15 | L1281-L1500 | 220 |

**Step 3: Per-Chunk Extraction** (partial results):
- Chunk 1: 12 FRs (auth + RBAC), 0 NFRs, 3 deps
- Chunk 2: 15 FRs (API + models), 8 NFRs (perf + security), 2 deps
- Chunk 3: 5 FRs (migration), 0 NFRs, 4 deps, 6 SCs, 8 risks
- Chunk 4: 0 FRs, 0 NFRs, 0 deps, 0 SCs, 0 risks (non-extraction sections)

**Step 4: Merge**: 32 FRs, 8 NFRs, 9 deps, 6 SCs, 8 risks

**Step 5: Deduplication**: 1 exact match found (FR about "user login" appeared in both auth section and API endpoints section). Removed duplicate. Final: 31 FRs.

**Step 6: Cross-Reference**: 2 unresolved references from chunk 3 (migration deps referencing auth FRs from chunk 1) — resolved to FR-003 and FR-007.

**Step 7: Global ID Assignment**: All items assigned sequential IDs by source_line position.

**Verification**:
- Pass 1 (Source Coverage): 98% → WARN (2 "should" statements in appendix not extracted — appendix tagged OTHER)
- Pass 2 (Anti-Hallucination): 100% PASS
- Pass 3 (Section Coverage): 100% PASS
- Pass 4 (Count Reconciliation): 32 - 1 = 31, all categories match → PASS

**Result**: extraction.md written with `extraction_mode: chunked (4 chunks)` metadata.

---

*Reference document for sc:roadmap v2.0.0 — loaded on-demand during Wave 1B*
