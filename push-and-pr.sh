#!/bin/bash
# Push branch and create PR when GitHub is available
# Run this script when GitHub service is restored

set -e  # Exit on error

echo "🚀 SuperClaude PR Creation Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/codebase-assessment-nov-18" ]; then
    echo -e "${RED}❌ Error: Not on feature/codebase-assessment-nov-18 branch${NC}"
    echo "Current branch: $CURRENT_BRANCH"
    echo ""
    echo "Run: git checkout feature/codebase-assessment-nov-18"
    exit 1
fi

echo -e "${GREEN}✅ On correct branch: $CURRENT_BRANCH${NC}"
echo ""

# Verify commits
echo "📋 Verifying commits..."
git log --oneline -4
echo ""

# Push branch to origin
echo "📤 Pushing branch to origin..."
if git push -u origin feature/codebase-assessment-nov-18; then
    echo -e "${GREEN}✅ Branch pushed successfully!${NC}"
else
    echo -e "${RED}❌ Failed to push branch${NC}"
    echo "GitHub may still be experiencing issues. Try again later."
    exit 1
fi
echo ""

# Create PR using GitHub CLI
echo "🎯 Creating Pull Request..."
echo ""

if command -v gh &> /dev/null; then
    # Read PR description from file
    PR_BODY_FILE=".github/PR_DESCRIPTION.md"
    
    if [ -f "$PR_BODY_FILE" ]; then
        echo "Using PR description from $PR_BODY_FILE"
        
        # Create PR with gh CLI
        gh pr create \
            --title "docs: Codebase Assessment & Documentation Updates - Nov 18, 2025" \
            --body-file "$PR_BODY_FILE" \
            --base master \
            --head feature/codebase-assessment-nov-18 \
            --label "documentation" \
            --label "enhancement" \
            --assignee @me
        
        echo ""
        echo -e "${GREEN}✅ Pull Request created successfully!${NC}"
        echo ""
        echo "🔗 View your PR:"
        gh pr view --web
        
    else
        echo -e "${YELLOW}⚠️  PR description file not found: $PR_BODY_FILE${NC}"
        echo "Creating PR with basic description..."
        
        gh pr create \
            --title "docs: Codebase Assessment & Documentation Updates - Nov 18, 2025" \
            --body "Comprehensive codebase assessment with documentation updates. See commits for details." \
            --base master \
            --head feature/codebase-assessment-nov-18 \
            --label "documentation"
        
        echo -e "${GREEN}✅ Pull Request created!${NC}"
    fi
    
else
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) not found${NC}"
    echo ""
    echo "Option 1: Install gh CLI"
    echo "  brew install gh"
    echo ""
    echo "Option 2: Create PR manually"
    echo "  Visit: https://github.com/SuperClaude-Org/SuperClaude_Framework/pull/new/feature/codebase-assessment-nov-18"
    echo ""
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}🎉 All done!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the PR on GitHub"
echo "2. Request reviews from @NomenAK and @mithun50"
echo "3. Address any feedback"
echo "4. Merge when approved"
echo ""

# Optional: Switch back to master and sync
read -p "Do you want to switch back to master and sync with origin? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Switching to master and syncing..."
    git checkout master
    git fetch origin master
    git reset --hard origin/master
    echo -e "${GREEN}✅ Master branch synced with origin${NC}"
    echo ""
    echo "You can switch back to your feature branch with:"
    echo "  git checkout feature/codebase-assessment-nov-18"
fi

echo ""
echo "✨ Done!"

