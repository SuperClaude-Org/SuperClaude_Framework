# D-0017: Expanded Extract Prompt Body Sections

## Deliverable

`build_extract_prompt()` body updated to request 8 structured sections with ID formats.

## Sections

1. **Functional Requirements** — FR-NNN IDs
2. **Non-Functional Requirements** — NFR-NNN IDs
3. **Complexity Assessment** — scoring rationale
4. **Architectural Constraints** — technology mandates, integration boundaries
5. **Risk Inventory** — severity + mitigation
6. **Dependency Inventory** — external deps, services, integration points
7. **Success Criteria** — measurable thresholds
8. **Open Questions** — ambiguities, gaps

## Verification

- All 8 section headers present in prompt body
- FR-NNN and NFR-NNN ID formats specified
- Body sections positioned before `<output_format>` XML block
