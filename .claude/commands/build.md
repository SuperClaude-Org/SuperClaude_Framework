# Project & Feature Construction

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Command_Header

Build project/feature based on req in $ARGUMENTS.

@include shared/command-templates.yml#Universal_Flags
@see shared/mcp-flags.yml ∀ MCP controls

Examples:
- `/user:build --react --magic` - React app w/ UI gen
- `/user:build --api --c7` - API w/ docs
- `/user:build --react --magic --pup` - Build & test UI

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

@include shared/command-templates.yml#Research_Requirements
@include shared/execution-lifecycle.yml#Standard_Lifecycle

Deliverables: @include shared/constants.yml#Success_Messages