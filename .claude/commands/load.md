# Project Context Loading

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Load & analyze project context in $ARGUMENTS→build comprehensive understanding.

--depth flag:
- shallow: Quick overview→project structure & purpose
- normal: Standard analysis→main files & architecture
- deep: Comprehensive analysis→entire codebase

Loading process:
1. Scan project structure & directory layout 2. Read key cfg & docs files
3. Analyze code architecture & patterns 4. Build mental model→project org 5. ID techs & deps

Files→analyze:

Essential:
- README.md→project overview | package.json/requirements.txt/go.mod→deps
- Cfg files (.env.example, cfg/*) | Build cfg (webpack, vite, etc.) | CI/CD cfg files

Source structure:
- Main entry points | Directory org | Module boundaries | Shared components/utilities
- Test structure

Version control:
- Current git status
- Recent commit history
- Branch structure
- Uncommitted changes

Depth-specific analysis:

Shallow depth:
- Project purpose and goals
- Main technologies used
- High-level architecture
- Key dependencies
- Quick start information

Normal depth:
- Detailed file structure
- Main components and modules
- API endpoints or routes
- Database schema
- Testing approach
- Development workflow

Deep depth:
- Complete code analysis
- All file relationships
- Detailed dependency graph
- Performance bottlenecks
- Security considerations
- Technical debt areas
- Optimization opportunities

Build mental model including:
- How components interact
- Data flow through system
- External integrations
- Deployment architecture
- Development patterns used

Deliverables: Comprehensive project understanding summary, identified next steps or recommendations, key areas requiring attention, and quick reference guide for project navigation.