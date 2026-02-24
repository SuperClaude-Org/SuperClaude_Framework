# Scoring Reference

Reference document for Wave 1B and Wave 2. Contains the complexity scoring formula, classification thresholds, template compatibility scoring, and persona confidence calculation.

---

## Complexity Scoring Formula

Complexity is computed as a weighted sum of 5 normalized factors. Each factor is normalized to [0, 1] before weighting.

### Factor Definitions

| Factor | Raw Value | Normalization | Weight |
|--------|-----------|---------------|--------|
| `requirement_count` | Total FRs + NFRs extracted | `min(count / 50, 1.0)` — 50+ requirements = maximum complexity | 0.25 |
| `dependency_depth` | Maximum chain length in the dependency graph | `min(depth / 8, 1.0)` — depth 8+ = maximum complexity | 0.25 |
| `domain_spread` | Number of distinct domains with ≥10% representation | `min(domains / 5, 1.0)` — 5 domains = maximum spread | 0.20 |
| `risk_severity` | Weighted risk score: `(high_count * 3 + medium_count * 2 + low_count * 1) / total_risks` | `(weighted_avg - 1.0) / 2.0` — normalizes [1.0, 3.0] to [0, 1] | 0.15 |
| `scope_size` | Total line count of the specification | `min(lines / 1000, 1.0)` — 1000+ lines = maximum scope | 0.15 |

### Formula

```
complexity_score = (requirement_count_norm * 0.25)
                 + (dependency_depth_norm * 0.25)
                 + (domain_spread_norm * 0.20)
                 + (risk_severity_norm * 0.15)
                 + (scope_size_norm * 0.15)
```

**Weight sum**: 0.25 + 0.25 + 0.20 + 0.15 + 0.15 = 1.00

**Output range**: [0.0, 1.0]

### Classification Thresholds

| Class | Score Range | Milestone Count | Interleave Ratio |
|-------|-----------|-----------------|------------------|
| LOW | < 0.4 | 3-4 milestones | 1:3 (one validation per three work milestones) |
| MEDIUM | 0.4 - 0.7 | 5-7 milestones | 1:2 (one validation per two work milestones) |
| HIGH | > 0.7 | 8-12 milestones | 1:1 (one validation per work milestone) |

### Worked Example

**Input**: 25 FRs + 5 NFRs = 30 requirements, dependency depth 4, 3 domains at ≥10%, 2 high + 3 medium + 1 low risks, 600-line spec.

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 30 | 0.60 | 0.25 | 0.150 |
| dependency_depth | 4 | 0.50 | 0.25 | 0.125 |
| domain_spread | 3 | 0.60 | 0.20 | 0.120 |
| risk_severity | 2.17 | 0.58 | 0.15 | 0.087 |
| scope_size | 600 | 0.60 | 0.15 | 0.090 |

**Total**: 0.150 + 0.125 + 0.120 + 0.087 + 0.090 = **0.572**

**Classification**: MEDIUM (0.4 ≤ 0.572 ≤ 0.7) → 5-7 milestones, 1:2 interleave ratio

---

## Template Compatibility Scoring

When Wave 2 discovers template files via the 4-tier search, each template is scored for compatibility with the extraction data.

### 4-Factor Formula

| Factor | Weight | Calculation |
|--------|--------|-------------|
| `domain_match` | 0.40 | Jaccard similarity between template's `domains` field and spec's detected domains (domains with ≥10% representation). `intersection_count / union_count` |
| `complexity_alignment` | 0.30 | `1.0 - abs(template.target_complexity - spec.complexity_score)`. Perfect alignment = 1.0, maximum misalignment = 0.0 |
| `type_match` | 0.20 | 1.0 if template `type` matches spec's dominant requirement type, 0.5 if related type, 0.0 if unrelated |
| `version_compatibility` | 0.10 | 1.0 if template's `min_version` ≤ current sc:roadmap version, 0.0 otherwise |

### Formula

```
template_score = (domain_match * 0.40)
               + (complexity_alignment * 0.30)
               + (type_match * 0.20)
               + (version_compatibility * 0.10)
```

**Weight sum**: 0.40 + 0.30 + 0.20 + 0.10 = 1.00

### Selection Rule

- Use the highest-scoring template with score ≥ 0.6
- If no template scores ≥ 0.6, fall back to inline generation
- If `--template` flag is explicitly set by the user, skip scoring entirely and use the specified template type

### Type Match Lookup

| Spec Dominant Type | Exact Match (1.0) | Related (0.5) | Unrelated (0.0) |
|--------------------|-------------------|---------------|------------------|
| feature | feature | improvement, migration | docs, security |
| security | security | improvement | feature, docs |
| migration | migration | improvement | feature, docs |
| docs | docs | — | feature, security |
| performance | performance | improvement | feature, docs |
| quality | quality, improvement | feature | docs, security |

---

## Persona Confidence Calculation

Personas are selected based on domain distribution from the extraction. The primary persona corresponds to the dominant domain; consulting personas cover secondary domains.

### Confidence Formula

For each candidate persona:
```
confidence = base_confidence * domain_weight * coverage_bonus
```

Where:
- `base_confidence`: 0.7 (default starting confidence)
- `domain_weight`: The persona's primary domain percentage / 100 (e.g., if backend is 45%, backend persona gets 0.45)
- `coverage_bonus`: 1.0 + (0.1 * number_of_secondary_domains_covered). Max 1.3

### Assignment Rules

| Role | Selection Criterion | Minimum Confidence |
|------|--------------------|--------------------|
| Primary | Highest confidence score among all candidates | 0.3 (if no persona exceeds 0.3, use "architect" as safe default) |
| Consulting | Second and third highest confidence scores | 0.2 |

### Persona-Domain Mapping

| Persona | Primary Domain | Secondary Domains |
|---------|---------------|-------------------|
| frontend | frontend | performance, documentation |
| backend | backend | performance |
| security | security | backend |
| performance | performance | backend, frontend |
| architect | (any — generalist) | all domains |
| scribe | documentation | — |

### Override

If `--persona` flag is provided by the user, skip confidence calculation entirely. Set primary persona to the user-specified value with confidence 1.0.

---

*Reference document for sc:roadmap v2.0.0 — loaded on-demand during Wave 1B and Wave 2*
