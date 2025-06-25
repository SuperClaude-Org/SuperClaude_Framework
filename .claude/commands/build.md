**Purpose**: Universal project builder with stack templates

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Build project/feature based on req in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/build --react --magic` - React app w/ UI gen
- `/build --api --c7` - API w/ docs
- `/build --react --magic --pup` - Build & test UI

Pre-build: Remove artifacts (dist/, build/, .next/) | Clean temp files & cache | Validate deps | Remove debug

Build modes:
**--init:** New project w/ stack (React|API|Fullstack|Mobile|CLI) | TS default | Testing setup | Git workflow
**--feature:** Impl feature→existing patterns | Maintain consistency | Include tests  
**--tdd:** Write failing tests→minimal code→pass tests→refactor

Templates:
- **React:** Vite|TS|Router|state mgmt|testing
- **API:** Express|TS|auth|validation|OpenAPI  
- **Fullstack:** React+Node.js+Docker
- **Mobile:** React Native+Expo
- **CLI:** Commander.js+cfg+testing

**--watch:** Continuous build | Real-time feedback | Incremental | Live reload
**--interactive:** Step-by-step cfg | Interactive deps | Build customization

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/execution-patterns.yml#Git_Integration_Patterns

@include shared/universal-constants.yml#Standard_Messages_Templates