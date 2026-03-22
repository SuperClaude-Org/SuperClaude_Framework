# Pull Request

## Summary

<!-- Briefly describe the purpose of this PR -->

## Changes

<!-- List the main changes -->
-

## Related Issue

<!-- Reference related issue numbers if applicable -->
Closes #

## Checklist

### Git Workflow
- [ ] External contributors: Followed Fork → topic branch → upstream PR flow
- [ ] Collaborators: Used topic branch (no direct commits to main)
- [ ] Rebased on upstream/main (`git rebase upstream/main`, no conflicts)
- [ ] Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

### Code Quality
- [ ] Changes are limited to a single purpose (not a mega-PR; aim for ~200 lines diff)
- [ ] Follows existing code conventions and patterns
- [ ] Added appropriate tests for new features/fixes
- [ ] Lint/Format/Typecheck all pass
- [ ] CI/CD pipeline succeeds (green status)

### Security
- [ ] No secrets or credentials committed
- [ ] Necessary files excluded via `.gitignore`
- [ ] No breaking changes, or if so: `!` commit + MIGRATION.md documented

### Documentation
- [ ] Updated documentation as needed (README, CLAUDE.md, docs/, etc.)
- [ ] Added comments for complex logic
- [ ] API changes are properly documented

## How to Test

<!-- Describe how to verify this PR works -->

## Screenshots (if applicable)

<!-- Attach screenshots for UI changes -->

## Notes

<!-- Anything you want reviewers to know, technical decisions, etc. -->
