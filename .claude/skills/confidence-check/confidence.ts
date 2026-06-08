/**
 * Confidence Check - Pre-implementation confidence assessment
 *
 * Prevents wrong-direction execution by assessing confidence BEFORE starting.
 * Requires ≥90% confidence to proceed with implementation.
 *
 * Token Budget: 100-200 tokens
 * ROI: 25-250x token savings when stopping wrong direction
 *
 * Test Results (2025-10-21):
 * - Precision: 1.000 (no false positives)
 * - Recall: 1.000 (no false negatives)
 * - 8/8 test cases passed
 *
 * Confidence Levels:
 *    - High (≥90%): Root cause identified, solution verified, no duplication, architecture-compliant
 *    - Medium (70-89%): Multiple approaches possible, trade-offs require consideration
 *    - Low (<70%): Investigation incomplete, unclear root cause, missing official docs
 */

import { existsSync, readdirSync, readFileSync, statSync } from 'fs';
import { join, dirname, relative } from 'path';

export interface Context {
  task?: string;
  test_file?: string;
  test_name?: string;
  markers?: string[];
  duplicate_check_complete?: boolean;
  architecture_check_complete?: boolean;
  official_docs_verified?: boolean;
  oss_reference_complete?: boolean;
  root_cause_identified?: boolean;
  confidence_checks?: string[];
  // Investigation inputs (used when the corresponding *_complete flag is absent)
  project_root?: string;
  feature_name?: string;
  target_name?: string;
  proposed_technology?: string;
  proposed_solution?: string;
  root_cause?: string;
  oss_references?: string[];
  documentation_urls?: string[];
  references?: string[];
  research_notes?: string;
  // Investigation outputs populated by the checks
  potential_duplicates?: string[];
  detected_tech_stack?: Record<string, boolean>;
  architecture_warnings?: string[];
  oss_recommendation?: string;
  root_cause_warning?: string;
  [key: string]: any;
}

/**
 * Pre-implementation confidence assessment
 *
 * Usage:
 *   const checker = new ConfidenceChecker();
 *   const confidence = await checker.assess(context);
 *
 *   if (confidence >= 0.9) {
 *     // High confidence - proceed immediately
 *   } else if (confidence >= 0.7) {
 *     // Medium confidence - present options to user
 *   } else {
 *     // Low confidence - STOP and request clarification
 *   }
 */
export class ConfidenceChecker {
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
  async assess(context: Context): Promise<number> {
    let score = 0.0;
    const checks: string[] = [];

    // Check 1: No duplicate implementations (25%)
    if (this.noDuplicates(context)) {
      score += 0.25;
      checks.push("✅ No duplicate implementations found");
    } else {
      checks.push("❌ Check for existing implementations first");
    }

    // Check 2: Architecture compliance (25%)
    if (this.architectureCompliant(context)) {
      score += 0.25;
      checks.push("✅ Uses existing tech stack (e.g., Supabase)");
    } else {
      checks.push("❌ Verify architecture compliance (avoid reinventing)");
    }

    // Check 3: Official documentation verified (20%)
    if (this.hasOfficialDocs(context)) {
      score += 0.2;
      checks.push("✅ Official documentation verified");
    } else {
      checks.push("❌ Read official docs first");
    }

    // Check 4: Working OSS implementations referenced (15%)
    if (this.hasOssReference(context)) {
      score += 0.15;
      checks.push("✅ Working OSS implementation found");
    } else {
      checks.push("❌ Search for OSS implementations");
    }

    // Check 5: Root cause identified (15%)
    if (this.rootCauseIdentified(context)) {
      score += 0.15;
      checks.push("✅ Root cause identified");
    } else {
      checks.push("❌ Continue investigation to identify root cause");
    }

    // Store check results for reporting
    context.confidence_checks = checks;

    // Display checks
    console.log("📋 Confidence Checks:");
    checks.forEach(check => console.log(`   ${check}`));
    console.log("");

    return score;
  }

  /**
   * Check if official documentation exists
   *
   * Looks for:
   * - README.md in project
   * - CLAUDE.md with relevant patterns
   * - docs/ directory with related content
   */
  private hasOfficialDocs(context: Context): boolean {
    // Check context flag first (for testing)
    if ('official_docs_verified' in context) {
      return context.official_docs_verified ?? false;
    }

    // Check for test file path
    const testFile = context.test_file;
    if (!testFile) {
      return false;
    }

    // Walk up directory tree to find project root (same logic as Python version)
    let projectRoot = dirname(testFile);

    while (true) {
      // Check for documentation files
      if (existsSync(join(projectRoot, 'README.md'))) {
        return true;
      }
      if (existsSync(join(projectRoot, 'CLAUDE.md'))) {
        return true;
      }
      if (existsSync(join(projectRoot, 'docs'))) {
        return true;
      }

      // Move up one directory
      const parent = dirname(projectRoot);
      if (parent === projectRoot) break; // Reached root (same as Python: parent != project_root)
      projectRoot = parent;
    }

    return false;
  }

  /**
   * Check for duplicate implementations
   *
   * Before implementing, verify:
   * - No existing similar functions/modules (Glob/Grep)
   * - No helper functions that solve the same problem
   * - No libraries that provide this functionality
   *
   * Returns true if no duplicates found (investigation complete)
   */
  private noDuplicates(context: Context): boolean {
    // Allow explicit override via context flag (testing / pre-checked scenarios)
    if ('duplicate_check_complete' in context) {
      return context.duplicate_check_complete ?? false;
    }

    const featureName =
      context.feature_name || context.target_name || context.test_name || '';
    if (!featureName) {
      return false;
    }

    const projectRoot = this.findProjectRoot(context);
    if (!projectRoot) {
      return false; // Can't verify without project root
    }

    const similar = this.searchCodebase(projectRoot, featureName, [
      'node_modules', '.venv', 'venv', '__pycache__', '.git',
    ]);

    if (similar.length > 0) {
      context.potential_duplicates = similar.slice(0, 5);
      return false;
    }

    return true;
  }

  /**
   * Check architecture compliance
   *
   * Verify solution uses existing tech stack:
   * - Supabase project → Use Supabase APIs (not custom API)
   * - Next.js project → Use Next.js patterns (not custom routing)
   * - Turborepo → Use workspace patterns (not manual scripts)
   *
   * Returns true if solution aligns with project architecture
   */
  private architectureCompliant(context: Context): boolean {
    // Allow explicit override via context flag
    if ('architecture_check_complete' in context) {
      return context.architecture_check_complete ?? false;
    }

    const projectRoot = this.findProjectRoot(context);
    if (!projectRoot) {
      return false;
    }

    const techStack = this.readTechStack(projectRoot);
    if (Object.keys(techStack).length === 0) {
      return false;
    }

    context.detected_tech_stack = techStack;

    const proposedTech = context.proposed_technology ?? '';
    if (!proposedTech) {
      // Tech stack is known and nothing risky proposed -> compliant
      return true;
    }

    const antiPatterns = this.checkArchitectureAntiPatterns(techStack, proposedTech);
    if (antiPatterns.length > 0) {
      context.architecture_warnings = antiPatterns;
      return false;
    }

    return true;
  }

  /**
   * Check if working OSS implementations referenced
   *
   * Search for:
   * - Similar open-source solutions
   * - Reference implementations in popular projects
   * - Community best practices
   *
   * Returns true if OSS reference found and analyzed
   */
  private hasOssReference(context: Context): boolean {
    // Allow explicit override via context flag
    if ('oss_reference_complete' in context) {
      return context.oss_reference_complete ?? false;
    }

    // Explicit references gathered during investigation
    if (context.oss_references?.length) return true;
    if (context.documentation_urls?.length) return true;
    if (context.references?.length) return true;

    const notes = context.research_notes ?? '';
    if (notes.length > 50) return true;

    // Check if docs/research directory has relevant analysis
    const projectRoot = this.findProjectRoot(context);
    if (projectRoot) {
      const researchDir = join(projectRoot, 'docs', 'research');
      if (existsSync(researchDir)) {
        try {
          if (readdirSync(researchDir).some(f => f.endsWith('.md'))) {
            return true;
          }
        } catch {
          // ignore unreadable dir
        }
      }
    }

    context.oss_recommendation =
      'Search for OSS implementations using WebSearch or Context7 MCP';
    return false;
  }

  /**
   * Check if root cause is identified with high certainty
   *
   * Verify:
   * - Problem source pinpointed (not guessing)
   * - Solution addresses root cause (not symptoms)
   * - Fix verified against official docs/OSS patterns
   *
   * Returns true if root cause clearly identified
   */
  private rootCauseIdentified(context: Context): boolean {
    // Allow explicit override via context flag
    if ('root_cause_identified' in context) {
      return context.root_cause_identified ?? false;
    }

    const rootCause = context.root_cause ?? '';
    if (!rootCause) {
      context.root_cause_warning = 'Root cause not documented in context';
      return false;
    }

    // Validate root cause is specific (not hedged with uncertainty language)
    const uncertaintyPatterns = [
      /\bprobably\b/, /\bmaybe\b/, /\bmight\b/, /\bcould be\b/, /\bpossibly\b/,
      /\bnot sure\b/, /\bguess\b/, /\bthink\b/, /\bassume\b/, /\bunclear\b/, /\bunknown\b/,
    ];
    const lower = rootCause.toLowerCase();
    for (const pattern of uncertaintyPatterns) {
      if (pattern.test(lower)) {
        context.root_cause_warning = `Root cause contains uncertainty language: '${pattern.source}'`;
        return false;
      }
    }

    // A credible root cause comes with a concrete proposed solution
    const solution = context.proposed_solution ?? '';
    if (!solution) {
      context.root_cause_warning = 'No proposed solution documented';
      return false;
    }
    if (solution.length < 20) {
      context.root_cause_warning = 'Proposed solution too brief';
      return false;
    }

    return true;
  }

  /**
   * Find the project root directory from context.
   *
   * Uses an explicit `project_root`, otherwise walks up from `test_file` looking
   * for pyproject.toml / CLAUDE.md / .git / package.json.
   */
  private findProjectRoot(context: Context): string | null {
    if (context.project_root) {
      return context.project_root;
    }

    const testFile = context.test_file;
    if (!testFile) {
      return null;
    }

    let current: string;
    try {
      current = statSync(testFile).isFile() ? dirname(testFile) : testFile;
    } catch {
      current = dirname(testFile);
    }

    const markers = ['pyproject.toml', 'CLAUDE.md', '.git', 'package.json'];
    while (true) {
      if (markers.some(m => existsSync(join(current, m)))) {
        return current;
      }
      const parent = dirname(current);
      if (parent === current) break;
      current = parent;
    }
    return null;
  }

  /**
   * Recursively collect files under `root` (skipping `excludeDirs`), capped to keep
   * the walk cheap on large trees.
   */
  private walkFiles(root: string, excludeDirs: string[], limit = 2000): string[] {
    const out: string[] = [];
    const stack = [root];
    while (stack.length > 0 && out.length < limit) {
      const dir = stack.pop()!;
      let entries: string[];
      try {
        entries = readdirSync(dir);
      } catch {
        continue;
      }
      for (const entry of entries) {
        const full = join(dir, entry);
        if (excludeDirs.includes(entry)) continue;
        let isDir = false;
        try {
          isDir = statSync(full).isDirectory();
        } catch {
          continue;
        }
        if (isDir) {
          stack.push(full);
        } else {
          out.push(full);
        }
      }
    }
    return out;
  }

  /**
   * Search the codebase for files related to `searchTerm`.
   *
   * A file matches when its name resembles the search term, or when it defines a
   * def/class/function with that exact name. Returns project-relative paths (max 10).
   */
  private searchCodebase(root: string, searchTerm: string, excludeDirs: string[]): string[] {
    const results: string[] = [];
    const searchLower = searchTerm.toLowerCase().replace(/[_-]/g, '');
    const exts = ['.py', '.ts', '.js'];

    for (const file of this.walkFiles(root, excludeDirs)) {
      if (!exts.some(e => file.endsWith(e))) continue;

      const base = file.split('/').pop() ?? file;
      const stem = base.replace(/\.[^.]+$/, '').toLowerCase().replace(/[_-]/g, '');
      if (stem.includes(searchLower) || searchLower.includes(stem)) {
        results.push(relative(root, file));
        if (results.length >= 10) break;
        continue;
      }

      try {
        const content = readFileSync(file, 'utf-8');
        if (content.length < 100000) {
          const escaped = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          if (new RegExp(`\\b(def|class|function)\\s+${escaped}\\b`, 'i').test(content)) {
            results.push(relative(root, file));
            if (results.length >= 10) break;
          }
        }
      } catch {
        // ignore unreadable file
      }
    }
    return results.slice(0, 10);
  }

  /**
   * Read tech stack from CLAUDE.md and project files.
   */
  private readTechStack(projectRoot: string): Record<string, boolean> {
    const techStack: Record<string, boolean> = {};

    const claudeMd = join(projectRoot, 'CLAUDE.md');
    if (existsSync(claudeMd)) {
      try {
        const content = readFileSync(claudeMd, 'utf-8');
        techStack.has_claude_md = true;
        const techPatterns: Record<string, RegExp> = {
          supabase: /\bsupabase\b/i,
          nextjs: /\bnext\.?js\b/i,
          react: /\breact\b/i,
          python: /\bpython\b/i,
          typescript: /\btypescript\b/i,
          turborepo: /\bturborepo\b/i,
          uv: /\buv\b/i,
          pytest: /\bpytest\b/i,
        };
        for (const [tech, pattern] of Object.entries(techPatterns)) {
          if (pattern.test(content)) techStack[tech] = true;
        }
      } catch {
        // ignore unreadable CLAUDE.md
      }
    }

    if (existsSync(join(projectRoot, 'pyproject.toml'))) techStack.python_project = true;
    if (existsSync(join(projectRoot, 'package.json'))) techStack.node_project = true;
    if (existsSync(join(projectRoot, 'turbo.json'))) techStack.turborepo = true;

    return techStack;
  }

  /**
   * Check the proposed approach against the detected tech stack.
   */
  private checkArchitectureAntiPatterns(
    techStack: Record<string, boolean>,
    proposedTech: string
  ): string[] {
    const warnings: string[] = [];
    const proposed = proposedTech.toLowerCase();

    if (techStack.supabase) {
      if (proposed.includes('custom api') || proposed.includes('express')) {
        warnings.push(
          'Supabase project detected - consider using Supabase APIs instead of custom API'
        );
      }
      if (proposed.includes('custom auth')) {
        warnings.push(
          'Supabase project detected - consider using Supabase Auth instead of custom authentication'
        );
      }
    }

    if (techStack.nextjs && proposed.includes('custom routing')) {
      warnings.push(
        'Next.js project detected - use Next.js App Router instead of custom routing'
      );
    }

    if (techStack.uv && proposed.includes('pip install')) {
      warnings.push("UV project detected - use 'uv pip install' instead of 'pip install'");
    }

    return warnings;
  }

  /**
   * Check if existing patterns can be followed
   *
   * Looks for:
   * - Similar test files
   * - Common naming conventions
   * - Established directory structure
   */
  private hasExistingPatterns(context: Context): boolean {
    const testFile = context.test_file;
    if (!testFile) {
      return false;
    }

    const testDir = dirname(testFile);

    // Check for other test files in same directory
    if (existsSync(testDir)) {
      try {
        const files = readdirSync(testDir);
        const testFiles = files.filter(f =>
          f.startsWith('test_') && f.endsWith('.py')
        );
        return testFiles.length > 1;
      } catch {
        return false;
      }
    }

    return false;
  }

  /**
   * Check if implementation path is clear
   *
   * Considers:
   * - Test name suggests clear purpose
   * - Markers indicate test type
   * - Context has sufficient information
   */
  private hasClearPath(context: Context): boolean {
    // Check test name clarity
    const testName = context.test_name ?? '';
    if (!testName || testName === 'test_example') {
      return false;
    }

    // Check for markers indicating test type
    const markers = context.markers ?? [];
    const knownMarkers = new Set([
      'unit', 'integration', 'hallucination',
      'performance', 'confidence_check', 'self_check'
    ]);

    const hasMarkers = markers.some(m => knownMarkers.has(m));

    return hasMarkers || testName.length > 10;
  }

  /**
   * Get recommended action based on confidence level
   *
   * @param confidence - Confidence score (0.0 - 1.0)
   * @returns Recommended action
   */
  getRecommendation(confidence: number): string {
    if (confidence >= 0.9) {
      return "✅ High confidence (≥90%) - Proceed with implementation";
    } else if (confidence >= 0.7) {
      return "⚠️ Medium confidence (70-89%) - Continue investigation, DO NOT implement yet";
    } else {
      return "❌ Low confidence (<70%) - STOP and continue investigation loop";
    }
  }
}

/**
 * Legacy function-based API for backward compatibility
 *
 * @deprecated Use ConfidenceChecker class instead
 */
export async function confidenceCheck(context: Context): Promise<number> {
  const checker = new ConfidenceChecker();
  return checker.assess(context);
}

/**
 * Legacy getRecommendation for backward compatibility
 *
 * @deprecated Use ConfidenceChecker.getRecommendation() instead
 */
export function getRecommendation(confidence: number): string {
  const checker = new ConfidenceChecker();
  return checker.getRecommendation(confidence);
}
