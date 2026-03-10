#!/bin/sh
# repo-inventory.sh — File inventory for /sc:cleanup-audit
# Usage: repo-inventory.sh [target-path] [batch-size]
# Output: Domain-grouped file inventory with batch assignments

set -e

TARGET="${1:-.}"
BATCH_SIZE="${2:-50}"

# Validate target exists
if [ ! -d "$TARGET" ]; then
    echo "ERROR: Target directory '$TARGET' does not exist" >&2
    exit 1
fi

# --- File Enumeration ---
# Use git ls-files for .gitignore-respecting enumeration
# Fall back to find if not in a git repo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    FILE_LIST=$(git ls-files -- "$TARGET" 2>/dev/null)
else
    FILE_LIST=$(find "$TARGET" -type f \
        -not -path '*/.git/*' \
        -not -path '*/node_modules/*' \
        -not -path '*/__pycache__/*' \
        -not -path '*/.cache/*' \
        -not -path '*/dist/*' \
        -not -path '*/build/*' \
        -not -path '*/.next/*' \
        -not -path '*/vendor/*' \
        -not -path '*/.venv/*' \
        -not -path '*/venv/*' \
        -not -path '*/.tox/*' \
        -not -path '*/.mypy_cache/*' \
        -not -path '*/.pytest_cache/*' \
        -not -path '*/coverage/*' \
        2>/dev/null)
fi

TOTAL=$(echo "$FILE_LIST" | grep -c . 2>/dev/null || echo 0)

# --- File Type Distribution ---
echo "=== FILE TYPE DISTRIBUTION ==="
echo "$FILE_LIST" | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
echo ""

# --- Domain Classification ---
# Classify files into domains for batch grouping
classify_domain() {
    file="$1"
    case "$file" in
        *Dockerfile*|*docker-compose*|*.yml|*.yaml|*Makefile|*Justfile|*.sh|*Jenkinsfile|*.tf|*.tfvars)
            echo "infrastructure" ;;
        */.github/*|*/.gitlab-ci*|*/.circleci/*|*/ci/*|*/deploy/*)
            echo "infrastructure" ;;
        *.jsx|*.tsx|*.vue|*.svelte|*.css|*.scss|*.less|*.html|*/components/*|*/pages/*|*/views/*)
            echo "frontend" ;;
        *.py|*.go|*.rs|*.java|*.rb|*.php|*/api/*|*/services/*|*/models/*|*/controllers/*)
            echo "backend" ;;
        *test*|*spec*|*__tests__*|*/tests/*|*/test/*)
            echo "tests" ;;
        *.md|*.rst|*.txt|*.adoc|*/docs/*|*/doc/*)
            echo "documentation" ;;
        *.json|*.toml|*.ini|*.cfg|*.conf|*.env*|*.config*)
            echo "config" ;;
        *.png|*.jpg|*.jpeg|*.gif|*.svg|*.ico|*.woff*|*.ttf|*.eot|*.mp4|*.webm|*.pdf)
            echo "assets" ;;
        *)
            echo "other" ;;
    esac
}

echo "=== DOMAIN DISTRIBUTION ==="
for domain in infrastructure frontend backend tests documentation config assets other; do
    count=0
    echo "$FILE_LIST" | while IFS= read -r file; do
        d=$(classify_domain "$file")
        if [ "$d" = "$domain" ]; then
            count=$((count + 1))
        fi
    done
    # Use grep-based counting for accuracy
    domain_count=$(echo "$FILE_LIST" | while IFS= read -r file; do classify_domain "$file"; done | grep -c "^${domain}$" 2>/dev/null || echo 0)
    if [ "$domain_count" -gt 0 ]; then
        printf "  %-15s %s files\n" "$domain:" "$domain_count"
    fi
done
echo ""

# --- Batch Assignments ---
echo "=== BATCH ASSIGNMENTS (batch_size=$BATCH_SIZE) ==="
batch_num=1
file_count=0

# Priority ordering: infrastructure > config > tests > backend > frontend > documentation > assets > other
for domain in infrastructure config tests backend frontend documentation assets other; do
    domain_files=$(echo "$FILE_LIST" | while IFS= read -r file; do
        d=$(classify_domain "$file")
        if [ "$d" = "$domain" ]; then
            echo "$file"
        fi
    done)

    if [ -z "$domain_files" ]; then
        continue
    fi

    domain_total=$(echo "$domain_files" | grep -c . 2>/dev/null || echo 0)
    if [ "$domain_total" -eq 0 ]; then
        continue
    fi

    echo ""
    echo "## Domain: $domain ($domain_total files)"

    echo "$domain_files" | while IFS= read -r file; do
        if [ $((file_count % BATCH_SIZE)) -eq 0 ] && [ "$file_count" -gt 0 ]; then
            batch_num=$((batch_num + 1))
        fi
        echo "  [batch-$batch_num] $file"
        file_count=$((file_count + 1))
    done
done

echo ""

# --- Summary ---
BATCH_COUNT=$(( (TOTAL + BATCH_SIZE - 1) / BATCH_SIZE ))
echo "=== SUMMARY ==="
echo "  Total files: $TOTAL"
echo "  Batch size: $BATCH_SIZE"
echo "  Estimated batches: $BATCH_COUNT"
echo "  Target: $TARGET"
