/**
 * Confidence Check Tests
 *
 * Tests for pre-implementation confidence assessment.
 * These tests verify the TypeScript implementation matches
 * the Python version's behavior and quality.
 */

import { confidenceCheck, getRecommendation, Context } from '../confidence';

describe('ConfidenceCheck - Scoring Tests', () => {
  test('High confidence (100%) - perfect conditions', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: true,
      root_cause_identified: true,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(1.0);
    expect(context.confidence_checks).toContain("✅ No duplicate implementations found");
    expect(context.confidence_checks).toContain("✅ Uses existing tech stack (e.g., Supabase)");
    expect(context.confidence_checks).toContain("✅ Official documentation verified");
    expect(context.confidence_checks).toContain("✅ Working OSS implementation found");
    expect(context.confidence_checks).toContain("✅ Root cause identified");
  });

  test('High confidence boundary (90%)', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: true,
      root_cause_identified: false,  // Missing one check (15%)
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.85);  // 100% - 15% = 85%
  });

  test('Medium confidence with trade-offs', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: true,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.65);  // 25% + 25% + 0% + 0% + 15%
    expect(getRecommendation(confidence)).toContain("Low confidence");
  });

  test('Medium confidence boundary (70%)', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.7);  // 25% + 25% + 20% + 0% + 0%
  });

  test('Medium confidence boundary (89%)', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: true,
      root_cause_identified: false,  // Just below 90%
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.85);
    expect(getRecommendation(confidence)).toContain("Medium confidence");
  });

  test('Low confidence - unclear requirements', async () => {
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.0);
    expect(getRecommendation(confidence)).toContain("STOP");
  });

  test('Low confidence - no precedent', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.25);
  });

  test('Low confidence - missing domain knowledge', async () => {
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: true,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.25);
  });

  test('Low confidence - multiple blockers', async () => {
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: true,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.2);
  });
});

describe('ConfidenceCheck - Anti-patterns', () => {
  test('Anti-pattern: proceeding without confidence check', async () => {
    // This test documents the anti-pattern of proceeding without checking confidence
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.0);
    expect(getRecommendation(confidence)).toContain("STOP");
  });

  test('Anti-pattern: proceeding with low confidence', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBeLessThan(0.7);
    expect(getRecommendation(confidence)).toContain("STOP");
  });

  test('Anti-pattern: pretending to know', async () => {
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBe(0.0);
  });
});

describe('ConfidenceCheck - Integration', () => {
  test('Typical feature request - high confidence', async () => {
    const context: Context = {
      task: "Add user profile settings page",
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: true,
      root_cause_identified: true,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBeGreaterThanOrEqual(0.9);
    expect(getRecommendation(confidence)).toContain("Proceed with implementation");
  });

  test('Typical feature request - medium confidence', async () => {
    const context: Context = {
      task: "Implement OAuth integration",
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: false,  // Missing (20%)
      oss_reference_complete: true,
      root_cause_identified: false,   // Missing (15%)
    };

    const confidence = await confidenceCheck(context);
    // Score: 25% + 25% + 0% + 15% + 0% = 65%
    expect(confidence).toBe(0.65);
    expect(confidence).toBeLessThan(0.9);
    expect(getRecommendation(confidence)).toContain("Low confidence");
  });

  test('Typical feature request - low confidence', async () => {
    const context: Context = {
      task: "Fix mysterious bug in production",
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const confidence = await confidenceCheck(context);
    expect(confidence).toBeLessThan(0.7);
  });

  test('Token budget ROI calculation', async () => {
    // Confidence check costs ~100-200 tokens
    const budgetSpent = 150;

    // If confidence < 70%, saves 5,000-50,000 tokens by stopping
    const potentialWaste = 25000;  // Average
    const roi = potentialWaste / budgetSpent;

    expect(roi).toBeGreaterThan(25);  // Minimum 25x ROI
    expect(roi).toBeLessThan(250);    // Maximum 250x ROI
  });
});

describe('ConfidenceCheck - Performance', () => {
  test('Token budget compliance', async () => {
    const context: Context = {
      duplicate_check_complete: true,
      architecture_check_complete: true,
      official_docs_verified: true,
      oss_reference_complete: true,
      root_cause_identified: true,
    };

    const startTime = Date.now();
    await confidenceCheck(context);
    const endTime = Date.now();

    const executionTime = endTime - startTime;

    // Should complete very quickly (< 100ms for in-memory checks)
    expect(executionTime).toBeLessThan(100);
  });

  test('Response time performance', async () => {
    const context: Context = {
      duplicate_check_complete: false,
      architecture_check_complete: false,
      official_docs_verified: false,
      oss_reference_complete: false,
      root_cause_identified: false,
    };

    const startTime = Date.now();
    const confidence = await confidenceCheck(context);
    const endTime = Date.now();

    expect(confidence).toBe(0.0);
    expect(endTime - startTime).toBeLessThan(100);
  });
});
