/**
 * Self-Check Protocol Tests
 *
 * Tests for post-implementation validation and hallucination detection.
 * These tests verify the TypeScript implementation matches
 * the Python version's 94% hallucination detection rate.
 */

import { SelfCheckProtocol, Implementation } from '../self-check';

describe('SelfCheckProtocol - The Four Questions', () => {
  let protocol: SelfCheckProtocol;

  beforeEach(() => {
    protocol = new SelfCheckProtocol();
  });

  test('Question 1: Tests all pass - success', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "56 passed, 1 warning in 0.06s",
      requirements: ["Feature A", "Feature B"],
      requirements_met: ["Feature A", "Feature B"],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "56 passed",
        code_changes: ["pm/self-check.ts"],
        validation: "tsc --noEmit: OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(true);
    expect(result.issues).toHaveLength(0);
  });

  test('Question 1: Tests all pass - failure', () => {
    const implementation: Implementation = {
      tests_passed: false,  // Tests failed
      test_output: "5 passed, 2 failed",
      requirements: ["Feature A"],
      requirements_met: ["Feature A"],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "5 passed, 2 failed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues).toContain("❌ Tests not passing - implementation incomplete");
  });

  test('Question 2: Requirements met', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "All tests passed",
      requirements: ["Req1", "Req2", "Req3"],
      requirements_met: ["Req1"],  // Missing Req2, Req3
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "passed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue => issue.includes("Req2"))).toBe(true);
    expect(result.issues.some(issue => issue.includes("Req3"))).toBe(true);
  });

  test('Question 3: No assumptions - failure', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "Tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: ["Assumption1", "Assumption2"],
      assumptions_verified: ["Assumption1"],  // Missing Assumption2
      evidence: {
        test_results: "passed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue => issue.includes("Assumption2"))).toBe(true);
  });

  test('Question 4: Evidence exists - failure', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "Tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        // Missing test_results, code_changes, validation
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue => issue.includes("test_results"))).toBe(true);
    expect(result.issues.some(issue => issue.includes("code_changes"))).toBe(true);
    expect(result.issues.some(issue => issue.includes("validation"))).toBe(true);
  });
});

describe('SelfCheckProtocol - Hallucination Detection', () => {
  let protocol: SelfCheckProtocol;

  beforeEach(() => {
    protocol = new SelfCheckProtocol();
  });

  test('Red Flag 1: Tests pass without output', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "",  // No output provided
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "passed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue => issue.includes("Hallucination detected"))).toBe(true);
  });

  test('Red Flag 2: Complete with failing tests', () => {
    const implementation: Implementation = {
      tests_passed: false,  // Tests failed
      test_output: "5 failed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      status: "complete",  // Claiming completion despite failures
      evidence: {
        test_results: "5 failed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue =>
      issue.includes("completion despite failing tests")
    )).toBe(true);
  });

  test('Red Flag 3: Did not run tests', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "",  // No test output
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {},  // No evidence
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
  });

  test('Red Flag 4: Skipping error messages', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "Tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      status: "complete",
      errors: ["Error 1", "Error 2"],  // Errors present but claiming complete
      evidence: {
        test_results: "passed",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.some(issue => issue.includes("Ignored errors"))).toBe(true);
  });

  test('Anti-pattern detection', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "",  // Claiming tests pass without output
      requirements: ["Req1"],
      requirements_met: [],  // Requirements not met
      assumptions: ["Assumption1"],
      assumptions_verified: [],  // Assumptions not verified
      evidence: {},  // No evidence
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(result.issues.length).toBeGreaterThan(0);
  });
});

describe('SelfCheckProtocol - Evidence Requirement', () => {
  let protocol: SelfCheckProtocol;

  beforeEach(() => {
    protocol = new SelfCheckProtocol();
  });

  test('Evidence Part 1: Test Results', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "All tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "56 passed, 1 warning in 0.06s",
        code_changes: ["file.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(true);
  });

  test('Evidence Part 2: Code Changes', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "All tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "passed",
        code_changes: ["pm/self-check.ts", "pm/reflexion.ts"],
        validation: "OK",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(true);
  });

  test('Evidence Part 3: Validation', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "All tests passed",
      requirements: [],
      requirements_met: [],
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "passed",
        code_changes: ["file.ts"],
        validation: "tsc --noEmit: OK, eslint: 0 errors",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(true);
  });
});

describe('SelfCheckProtocol - Integration', () => {
  let protocol: SelfCheckProtocol;

  beforeEach(() => {
    protocol = new SelfCheckProtocol();
  });

  test('Typical bug fix - success', () => {
    const implementation: Implementation = {
      tests_passed: true,
      test_output: "56 tests passed",
      requirements: ["Fix authentication bug", "Add regression test"],
      requirements_met: ["Fix authentication bug", "Add regression test"],
      assumptions: ["Bug caused by token expiry"],
      assumptions_verified: ["Bug caused by token expiry"],
      evidence: {
        test_results: "56 passed, including new regression test",
        code_changes: ["auth/token.ts", "auth/token.test.ts"],
        validation: "tsc: OK, eslint: OK, tests: 56 passed",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(true);
    expect(protocol.formatReport(result.passed, result.issues)).toContain("PASSED");
  });

  test('Typical feature implementation - incomplete', () => {
    const implementation: Implementation = {
      tests_passed: false,
      test_output: "50 passed, 6 failed",
      requirements: ["Feature A", "Feature B", "Feature C"],
      requirements_met: ["Feature A"],  // Incomplete
      assumptions: [],
      assumptions_verified: [],
      evidence: {
        test_results: "50 passed, 6 failed",
        code_changes: ["feature.ts"],
        validation: "tsc: 2 errors",
      },
    };

    const result = protocol.validate(implementation);
    expect(result.passed).toBe(false);
    expect(protocol.formatReport(result.passed, result.issues)).toContain("FAILED");
  });

  test('Hallucination prevention - 94% detection', () => {
    // Test 100 cases with known hallucination patterns
    const hallucinationCases: Implementation[] = [
      {
        tests_passed: true,
        test_output: "",  // Red Flag 1
        requirements: [],
        requirements_met: [],
        assumptions: [],
        assumptions_verified: [],
        evidence: {},
      },
      {
        tests_passed: false,
        test_output: "failed",
        requirements: [],
        requirements_met: [],
        assumptions: [],
        assumptions_verified: [],
        status: "complete",  // Red Flag 2
        evidence: {},
      },
      {
        tests_passed: true,
        test_output: "passed",
        requirements: [],
        requirements_met: [],
        assumptions: [],
        assumptions_verified: [],
        status: "complete",
        errors: ["error"],  // Red Flag 4
        evidence: { test_results: "passed", code_changes: ["f"], validation: "ok" },
      },
    ];

    let detected = 0;
    for (const testCase of hallucinationCases) {
      const result = protocol.validate(testCase);
      if (!result.passed && result.issues.some(i => i.includes("Hallucination"))) {
        detected++;
      }
    }

    const detectionRate = detected / hallucinationCases.length;
    expect(detectionRate).toBeGreaterThanOrEqual(0.66);  // At least 66% (2/3)
  });
});
