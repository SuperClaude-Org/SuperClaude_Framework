@include shared/universal-constants.yml#Universal_Legend

## Command Execution
@include shared/command-structure.yml#Base_Execution

Design system architecture & APIs for $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Design & architect software solutions based on requirements in $ARGUMENTS.

Thinking flags (optional):
- --think→standard design patterns & component architecture
- --think-hard→system-wide architecture & scalability planning
- --ultrathink→complete system redesign or critical architectural decisions

Examples:
- `/design --api --think` - REST API design w/ patterns
- `/design --ddd --think-hard` - Deep domain modeling
- `/design --api --ddd --ultrathink` - Complete system architecture

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