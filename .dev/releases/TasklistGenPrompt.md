/sc:task Generate a detailed tasklist for the {RELEASE} release --compliance strict
   --strategy systematic --seq

  ## Objective

  Execute the Tasklist Generator prompt to transform the {RELEASE} Roadmap into a deterministic,
  execution-ready **multi-file tasklist bundle** compatible with `superclaude sprint run`.

  ## Instructions

  1. **Read the generator prompt** at:
     `/config/workspace/SuperClaude_Framework/.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md`

     This is your operating procedure. Follow it exactly as written — all sections, rules, output format, and compliance tier classification.

  2. **Read the roadmap input** at:
     `{RELEASEROADMAP}`

     This is the roadmap to transform. Feed the full contents as the generator's input per its Input Contract (Section 2).

  3. **Read additional context** at:
     `{RELEASESPEC}`

     This is supplementary context about the /sc:analyze integration that the roadmap is based on. Use it to resolve ambiguities and enrich acceptance criteria — but do NOT treat it as a second roadmap.

  4. **Output**: Write the generated tasklist bundle to `{RELEASETASKLISTDESTINATION}`:
     - `tasklist-index.md` — Sprint index with metadata, registries, traceability, templates
     - `phase-1-tasklist.md` through `phase-N-tasklist.md` — One per phase, execution-focused

     The output must be a multi-file bundle per Section 3.3 of the generator prompt, NOT a single monolithic document.

  ## Constraints

  - Follow the generator prompt's Non-Leakage + Truthfulness Rules (Section 0)
  - Preserve all roadmap deliverables — do not drop or merge items without the generator's explicit merge rules
  - Create Clarification Tasks for any missing information per Section 4.6 of the generator
  - Every task must have a compliance tier with confidence scoring per the generator's classification system
  - Respect the roadmap's P0 → P1 → P2 → P3 priority wave ordering
  - Phase files must use `phase-N-tasklist.md` naming convention (Sprint CLI requirement)
  - Run the Sprint Compatibility Self-Check (Section 8) before finalizing output