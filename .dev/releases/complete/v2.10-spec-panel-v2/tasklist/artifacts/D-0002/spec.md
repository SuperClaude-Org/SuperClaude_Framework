# D-0002 Evidence: Five Attack Methodology Definitions

## Deliverable
Five attack methodology definitions added to Whittaker persona in spec-panel.md.

## Methodologies Defined
1. **FR-2.1 Zero/Empty Attack** - Probes zero, empty, null, negative degenerate inputs against every guard condition and default assumption
2. **FR-2.2 Divergence Attack** - Targets condition boundaries where behavior diverges, testing simultaneous branch applicability
3. **FR-2.3 Sentinel Collision Attack** - Tests legitimate input collision with sentinel values, magic numbers, and reserved constants
4. **FR-2.4 Sequence Attack** - Tests out-of-order, repeated, and skipped steps in multi-step processes, pipelines, and state machines
5. **FR-2.5 Accumulation Attack** - Tests overflow, underflow, and capacity boundaries on counters, collections, buffers, and aggregates

## Verification
- Each methodology is concrete and mechanically applicable (specific probe questions, not abstract guidance)
- All five use existing severity classification: CRITICAL, MAJOR, MINOR (per NFR-3)
- Located in Attack Methodologies field of Whittaker persona block

## Traceability
- Roadmap Item: R-002
- Task: T01.02
- Deliverable: D-0002
