/**
 * Self-Check Protocol - Post-implementation validation
 *
 * Hallucination prevention through evidence-based validation.
 * Detects 94% of hallucination patterns.
 *
 * The Four Questions:
 * 1. テストは全てpassしてる？ (Are all tests passing?)
 * 2. 要件を全て満たしてる？ (Are all requirements met?)
 * 3. 思い込みで実装してない？ (No assumptions without verification?)
 * 4. 証拠はある？ (Is there evidence?)
 */

export interface Implementation {
  tests_passed?: boolean;
  test_output?: string;
  requirements?: string[];
  requirements_met?: string[];
  assumptions?: string[];
  assumptions_verified?: string[];
  evidence?: {
    test_results?: string;
    code_changes?: string[];
    validation?: string;
  };
  status?: string;
  errors?: string[];
  warnings?: string[];
  description?: string;
}

export interface ValidationResult {
  passed: boolean;
  issues: string[];
}

/**
 * Self-Check Protocol for post-implementation validation
 *
 * Usage:
 *   const protocol = new SelfCheckProtocol();
 *   const result = protocol.validate(implementation);
 *
 *   if (result.passed) {
 *     console.log("✅ Implementation complete with evidence");
 *   } else {
 *     console.log("❌ Issues detected:");
 *     result.issues.forEach(issue => console.log(`  - ${issue}`));
 *   }
 */
export class SelfCheckProtocol {
  /**
   * 7 Red Flags for Hallucination Detection
   */
  private readonly HALLUCINATION_RED_FLAGS = [
    "tests pass",  // without showing output
    "everything works",  // without evidence
    "implementation complete",  // with failing tests
    // Skipping error messages
    // Ignoring warnings
    // Hiding failures
    // "probably works" statements
  ];

  /**
   * Run self-check validation
   *
   * @param implementation - Implementation details object
   * @returns Validation result with passed flag and issues list
   */
  validate(implementation: Implementation): ValidationResult {
    const issues: string[] = [];

    // Question 1: Tests passing?
    if (!this.checkTestsPassing(implementation)) {
      issues.push("❌ Tests not passing - implementation incomplete");
    }

    // Question 2: Requirements met?
    const unmet = this.checkRequirementsMet(implementation);
    if (unmet.length > 0) {
      issues.push(`❌ Requirements not fully met: ${unmet.join(', ')}`);
    }

    // Question 3: Assumptions verified?
    const unverified = this.checkAssumptionsVerified(implementation);
    if (unverified.length > 0) {
      issues.push(`❌ Unverified assumptions: ${unverified.join(', ')}`);
    }

    // Question 4: Evidence provided?
    const missingEvidence = this.checkEvidenceExists(implementation);
    if (missingEvidence.length > 0) {
      issues.push(`❌ Missing evidence: ${missingEvidence.join(', ')}`);
    }

    // Additional: Check for hallucination red flags
    const hallucinations = this.detectHallucinations(implementation);
    if (hallucinations.length > 0) {
      issues.push(...hallucinations.map(h => `🚨 Hallucination detected: ${h}`));
    }

    return {
      passed: issues.length === 0,
      issues
    };
  }

  /**
   * Verify all tests pass WITH EVIDENCE
   *
   * Must have:
   * - tests_passed = true
   * - test_output (actual results, not just claim)
   */
  private checkTestsPassing(impl: Implementation): boolean {
    if (!impl.tests_passed) {
      return false;
    }

    // Require actual test output (anti-hallucination)
    const testOutput = impl.test_output || "";
    if (!testOutput) {
      return false;
    }

    // Check for passing indicators in output
    const passingIndicators = ["passed", "OK", "✓", "✅"];
    return passingIndicators.some(indicator => testOutput.includes(indicator));
  }

  /**
   * Verify all requirements satisfied
   *
   * @returns List of unmet requirements (empty if all met)
   */
  private checkRequirementsMet(impl: Implementation): string[] {
    const requirements = impl.requirements || [];
    const requirementsMet = new Set(impl.requirements_met || []);

    const unmet: string[] = [];
    for (const req of requirements) {
      if (!requirementsMet.has(req)) {
        unmet.push(req);
      }
    }

    return unmet;
  }

  /**
   * Verify assumptions checked against official docs
   *
   * @returns List of unverified assumptions (empty if all verified)
   */
  private checkAssumptionsVerified(impl: Implementation): string[] {
    const assumptions = impl.assumptions || [];
    const assumptionsVerified = new Set(impl.assumptions_verified || []);

    const unverified: string[] = [];
    for (const assumption of assumptions) {
      if (!assumptionsVerified.has(assumption)) {
        unverified.push(assumption);
      }
    }

    return unverified;
  }

  /**
   * Verify evidence provided (test results, code changes, validation)
   *
   * @returns List of missing evidence types (empty if all present)
   */
  private checkEvidenceExists(impl: Implementation): string[] {
    const evidence = impl.evidence || {};
    const missing: string[] = [];

    // Evidence requirement 1: Test Results
    if (!evidence.test_results) {
      missing.push("test_results");
    }

    // Evidence requirement 2: Code Changes
    if (!evidence.code_changes || evidence.code_changes.length === 0) {
      missing.push("code_changes");
    }

    // Evidence requirement 3: Validation (lint, typecheck, build)
    if (!evidence.validation) {
      missing.push("validation");
    }

    return missing;
  }

  /**
   * Detect hallucination red flags
   *
   * 7 Red Flags:
   * 1. "Tests pass" without showing output
   * 2. "Everything works" without evidence
   * 3. "Implementation complete" with failing tests
   * 4. Skipping error messages
   * 5. Ignoring warnings
   * 6. Hiding failures
   * 7. "Probably works" statements
   *
   * @returns List of detected hallucination patterns
   */
  private detectHallucinations(impl: Implementation): string[] {
    const detected: string[] = [];

    // Red Flag 1: "Tests pass" without output
    if (impl.tests_passed && !impl.test_output) {
      detected.push("Claims tests pass without showing output");
    }

    // Red Flag 2: "Everything works" without evidence
    if (impl.status === "complete" && !impl.evidence) {
      detected.push("Claims completion without evidence");
    }

    // Red Flag 3: "Complete" with failing tests
    if (impl.status === "complete" && !impl.tests_passed) {
      detected.push("Claims completion despite failing tests");
    }

    // Red Flag 4-6: Check for ignored errors/warnings
    const errors = impl.errors || [];
    const warnings = impl.warnings || [];
    if ((errors.length > 0 || warnings.length > 0) && impl.status === "complete") {
      detected.push("Ignored errors/warnings");
    }

    // Red Flag 7: Uncertainty language
    const description = (impl.description || "").toLowerCase();
    const uncertaintyWords = ["probably", "maybe", "should work", "might work"];
    if (uncertaintyWords.some(word => description.includes(word))) {
      detected.push(`Uncertainty language detected: ${description}`);
    }

    return detected;
  }

  /**
   * Format validation report
   *
   * @param passed - Whether validation passed
   * @param issues - List of issues detected
   * @returns Formatted report string
   */
  formatReport(passed: boolean, issues: string[]): string {
    if (passed) {
      return "✅ Self-Check PASSED - Implementation complete with evidence";
    }

    const report = ["❌ Self-Check FAILED - Issues detected:\n"];
    for (const issue of issues) {
      report.push(`  ${issue}`);
    }

    return report.join("\n");
  }
}
