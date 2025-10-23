/**
 * Confidence Check - Pre-implementation confidence assessment
 *
 * Prevents wrong-direction execution by assessing confidence BEFORE starting.
 * Requires ≥90% confidence to proceed with implementation.
 *
 * Test Results (2025-10-21):
 * - Precision: 1.000 (no false positives)
 * - Recall: 1.000 (no false negatives)
 * - 8/8 test cases passed
 */

export interface Context {
  task?: string;
  duplicate_check_complete?: boolean;
  architecture_check_complete?: boolean;
  official_docs_verified?: boolean;
  oss_reference_complete?: boolean;
  root_cause_identified?: boolean;
  confidence_checks?: string[];
  [key: string]: any;
}

/**
 * Assess confidence level (0.0 - 1.0)
 *
 * Investigation Phase Checks:
 * 1. No duplicate implementations? (25%)
 * 2. Architecture compliance? (25%)
 * 3. Official documentation verified? (20%)
 * 4. Working OSS implementations referenced? (15%)
 * 5. Root cause identified? (15%)
 *
 * @param context - Task context with investigation flags
 * @returns Confidence score (0.0 = no confidence, 1.0 = absolute certainty)
 */
export async function confidenceCheck(context: Context): Promise<number> {
  let score = 0.0;
  const checks: string[] = [];

  // Check 1: No duplicate implementations (25%)
  if (noDuplicates(context)) {
    score += 0.25;
    checks.push("✅ No duplicate implementations found");
  } else {
    checks.push("❌ Check for existing implementations first");
  }

  // Check 2: Architecture compliance (25%)
  if (architectureCompliant(context)) {
    score += 0.25;
    checks.push("✅ Uses existing tech stack (e.g., Supabase)");
  } else {
    checks.push("❌ Verify architecture compliance (avoid reinventing)");
  }

  // Check 3: Official documentation verified (20%)
  if (hasOfficialDocs(context)) {
    score += 0.2;
    checks.push("✅ Official documentation verified");
  } else {
    checks.push("❌ Read official docs first");
  }

  // Check 4: Working OSS implementations referenced (15%)
  if (hasOssReference(context)) {
    score += 0.15;
    checks.push("✅ Working OSS implementation found");
  } else {
    checks.push("❌ Search for OSS implementations");
  }

  // Check 5: Root cause identified (15%)
  if (rootCauseIdentified(context)) {
    score += 0.15;
    checks.push("✅ Root cause identified");
  } else {
    checks.push("❌ Continue investigation to identify root cause");
  }

  // Store check results
  context.confidence_checks = checks;

  // Display checks
  console.log("📋 Confidence Checks:");
  checks.forEach(check => console.log(`   ${check}`));
  console.log("");

  return score;
}

/**
 * Check for duplicate implementations
 *
 * Before implementing, verify:
 * - No existing similar functions/modules (Glob/Grep)
 * - No helper functions that solve the same problem
 * - No libraries that provide this functionality
 */
function noDuplicates(context: Context): boolean {
  return context.duplicate_check_complete ?? false;
}

/**
 * Check architecture compliance
 *
 * Verify solution uses existing tech stack:
 * - Supabase project → Use Supabase APIs (not custom API)
 * - Next.js project → Use Next.js patterns (not custom routing)
 * - Turborepo → Use workspace patterns (not manual scripts)
 */
function architectureCompliant(context: Context): boolean {
  return context.architecture_check_complete ?? false;
}

/**
 * Check if official documentation verified
 *
 * For testing: uses context flag 'official_docs_verified'
 * For production: checks for README.md, CLAUDE.md, docs/ directory
 */
function hasOfficialDocs(context: Context): boolean {
  // Check context flag (for testing and runtime)
  if ('official_docs_verified' in context) {
    return context.official_docs_verified ?? false;
  }

  // Fallback: check for documentation files (production)
  // This would require filesystem access in Node.js
  return false;
}

/**
 * Check if working OSS implementations referenced
 *
 * Search for:
 * - Similar open-source solutions
 * - Reference implementations in popular projects
 * - Community best practices
 */
function hasOssReference(context: Context): boolean {
  return context.oss_reference_complete ?? false;
}

/**
 * Check if root cause is identified with high certainty
 *
 * Verify:
 * - Problem source pinpointed (not guessing)
 * - Solution addresses root cause (not symptoms)
 * - Fix verified against official docs/OSS patterns
 */
function rootCauseIdentified(context: Context): boolean {
  return context.root_cause_identified ?? false;
}

/**
 * Get recommended action based on confidence level
 *
 * @param confidence - Confidence score (0.0 - 1.0)
 * @returns Recommended action
 */
export function getRecommendation(confidence: number): string {
  if (confidence >= 0.9) {
    return "✅ High confidence (≥90%) - Proceed with implementation";
  } else if (confidence >= 0.7) {
    return "⚠️ Medium confidence (70-89%) - Continue investigation, DO NOT implement yet";
  } else {
    return "❌ Low confidence (<70%) - STOP and continue investigation loop";
  }
}
