# Development Environment Setup

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Setup comprehensive dev env or CI/CD pipeline based on $ARGUMENTS.

Thinking flags (optional):
- --think→multi-tool env coordination
- --think-hard→complex CI/CD pipeline architecture
- --ultrathink→enterprise dev infrastructure design

Examples:
- `/user:dev-setup --install --think` - Tool installation w/ dependency analysis
- `/user:dev-setup --ci --think-hard` - CI/CD pipeline w/ comprehensive workflow design
- `/user:dev-setup --monitor --ultrathink` - Complete observability infrastructure

--install flag:
- Install & cfg dev tools (Node.js, Git, Docker, DBs) | Setup IDE cfgs→consistent dev experience
- Create npm scripts→common tasks | Cfg pre-commit hooks→code quality | Setup linting & testing frameworks

--ci flag:
- Cfg CI/CD pipelines (GitHub Actions, GitLab CI, other platforms) | Setup build, test & deployment stages
- Cfg envs: dev, staging & prod | Add security scanning & dep checking | Setup deployment automation

--monitor flag:
- Cfg observability tools | Setup logging & monitoring | Add perf tracking
- Cfg error reporting | Setup alerts→critical issues

## Best Practices & Security

Ensure all cfgs follow security practices & include comprehensive docs.

@include shared/command-templates.yml#Research_Requirements

@include shared/command-templates.yml#Report_Output

@include shared/constants.yml#Success_Messages