| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |
| > | greater than | | val | validation |
| ∀ | for all/every | | req | requirements |
| ∃ | exists/there is | | deps | dependencies |
| ∴ | therefore | | env | environment |
| ∵ | because | | db | database |
| ≡ | equivalent | | api | interface |
| ≈ | approximately | | docs | documentation |
| 📁 | directory/path | | std | standard |
| 🔢 | number/count | | def | default |
| 📝 | text/string | | ctx | context |
| ⚙ | setting/config | | err | error |
| 🎛 | control/flags | | exec | execution |
| 🔧 | configuration | | qual | quality |
| 📋 | group/category | | rec | recovery |
| 🚨 | critical/urgent | | sev | severity |
| ⚠ | warning/caution | | resp | response |
| 🔄 | retry/recovery | | esc | escalation |
| ✅ | success/fixed | | tok | token |
| ❌ | failure/error | | opt | optimization |
| ℹ | information | | UX | user experience |
| ⚡ | fast/quick | | UI | user interface |
| 🐌 | slow/delayed | | C | critical |
| ✨ | complete/done | | H | high |
| 📖 | read operation | | M | medium |
| ✏ | edit operation | | L | low |
| 🗑 | delete operation | | |

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Design system architecture & APIs for $ARGUMENTS.

## Universal Flags
--plan: "Show execution plan before running"
--uc: "UltraCompressed mode (~70% token reduction)"
--ultracompressed: "Alias for --uc"
--think: "Multi-file analysis w/ context (4K tokens)"
--think-hard: "Deep architectural analysis (10K tokens)"
--ultrathink: "Critical system redesign (32K tokens)"
--c7: "Enable Context7→library documentation lookup"
--seq: "Enable Sequential→complex analysis & thinking"
--magic: "Enable Magic→UI component generation"
--pup: "Enable Puppeteer→browser automation & testing"
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"

Design & architect software solutions based on requirements in $ARGUMENTS.

Thinking flags (optional):
- --think→standard design patterns & component architecture
- --think-hard→system-wide architecture & scalability planning
- --ultrathink→complete system redesign or critical architectural decisions

Examples:
- `/user:design --api --think` - REST API design w/ patterns
- `/user:design --ddd --think-hard` - Deep domain modeling
- `/user:design --api --ddd --ultrathink` - Complete system architecture

Design focus w/ flags:

--api flag:
- Design REST or GraphQL APIs
- w/ --openapi: Generate OpenAPI 3.0 spec | w/ --graphql: Create GraphQL schema & resolvers
- Include auth, rate limiting & error handling | Design→scalability & maintainability

--ddd flag:
- Apply DDD principles | w/ --bounded-context: Define context boundaries & mappings
- Design entities, value objects & aggregates | Create domain services & events | Impl repository patterns

--prd flag:
- Create PRD | w/ --template: Use template (feature/api/integration/migration)
- Include user stories w/ acceptance criteria | Define success metrics & timelines | Document tech requirements

## API Design Mode (--api)

REST API principles:
- Resource-oriented URLs w/ proper HTTP verbs | Consistent status codes & error formats
- Versioning strategy (URL/header/accept) | Pagination, filtering & sorting | HATEOAS→discoverability | OpenAPI docs

GraphQL principles:
- Clear type system w/ schemas | Efficient queries & mutations | Real-time subscriptions where needed
- DataLoader patterns→N+1 prevention | Field-level auth | Error handling practices

Common API elements:
- Auth (JWT/OAuth/API keys) | Rate limiting & throttling | Request/response validation
- Caching strategies | CORS & security headers | Monitoring & logging

## DDD Mode (--ddd)

Building blocks:
- **Entities**: Objects w/ unique identity | **Value Objects**: Immutable objects by attributes
- **Aggregates**: Consistency boundaries w/ roots | **Domain Services**: Business logic not in entities
- **Repositories**: Abstract data access | **Domain Events**: Capture business events

Strategic patterns:
- Bounded contexts w/ clear boundaries | Context mapping (shared kernel, anti-corruption layer)
- Ubiquitous language within contexts | Event-driven architecture | CQRS where appropriate

Structure:
```
domain/          # Core business logic
application/     # Use cases & orchestration  
infrastructure/  # External concerns
presentation/    # UI/API layer
```

## PRD Mode (--prd)

Structure:
1. **Executive Overview**: Problem statement & solution | Expected impact & ROI | Key stakeholders
2. **Goals & Success Metrics**: Primary objectives (must-have) | Secondary goals (nice-to-have) | KPIs & measurement
3. **User Stories & Requirements**: User personas & journeys | Functional requirements | Non-functional requirements | Acceptance criteria
4. **Technical Specs**: Architecture overview | Tech choices | Integration points | Security requirements | Perf targets  
5. **Timeline & Risks**: Dev phases | Dependencies & blockers | Risk mitigation strategies

## Integration

Combined modes:
- API+DDD: Design domain-driven APIs | API+PRD: Create API product requirements
- DDD+PRD: Document domain-driven architecture | All three: Complete system design

Best practices:
- Start w/ user needs & business goals | Design→change & evolution | Consider non-functional early
- Document decisions & rationale | Include examples & diagrams | Plan→testing & monitoring

Research requirements:
- Architecture patterns→C7 & industry practices | API standards→reference OpenAPI/REST/GraphQL specs
- DDD patterns→verify w/ Evans' book or official DDD | Tech choices→WebSearch recent comparisons & case studies
- Never design on assumptions - verify patterns | All decisions cite authoritative sources

Deliverables:
- API: Complete spec, impl guide, docs | DDD: Domain model, bounded contexts, architecture diagrams, code structure
- PRD: Requirements doc, user stories, success metrics, timeline
