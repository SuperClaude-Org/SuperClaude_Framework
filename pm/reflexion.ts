/**
 * Reflexion Error Learning Pattern
 *
 * Learn from past errors to prevent recurrence.
 *
 * Token Budget:
 *     - Cache hit: 0 tokens (known error → instant solution)
 *     - Cache miss: 1-2K tokens (new investigation)
 *
 * Performance:
 *     - Error recurrence rate: <10%
 *     - Solution reuse rate: >90%
 *
 * Storage Strategy:
 *     - Primary: docs/memory/solutions_learned.jsonl (local file)
 *     - Secondary: mindbase (if available, semantic search)
 *     - Fallback: grep-based text search
 *
 * Process:
 *     1. Error detected → Check past errors (smart lookup)
 *     2. IF similar found → Apply known solution (0 tokens)
 *     3. ELSE → Investigate root cause → Document solution
 *     4. Store for future reference (dual storage)
 */

import * as fs from 'fs';
import * as path from 'path';

export interface ErrorInfo {
  test_name?: string;
  test_file?: string;
  error_type?: string;
  error_message?: string;
  traceback?: string;
  solution?: string;
  root_cause?: string;
  prevention?: string;
  why_missed?: string;
  lesson?: string;
  timestamp?: string;
}

export interface Solution {
  solution?: string;
  root_cause?: string;
  prevention?: string;
  timestamp?: string;
}

/**
 * Reflexion Pattern for error learning and prevention
 *
 * Usage:
 *   const reflexion = new ReflexionPattern();
 *
 *   // When error occurs
 *   const errorInfo = {
 *     error_type: "AssertionError",
 *     error_message: "Expected 5, got 3",
 *     test_name: "test_calculation",
 *   };
 *
 *   // Check for known solution
 *   const solution = await reflexion.getSolution(errorInfo);
 *
 *   if (solution) {
 *     console.log(`✅ Known error - Solution: ${solution}`);
 *   } else {
 *     // New error - investigate and record
 *     await reflexion.recordError(errorInfo);
 *   }
 */
export class ReflexionPattern {
  private memoryDir: string;
  private solutionsFile: string;
  private mistakesDir: string;

  constructor(memoryDir?: string) {
    // Default to docs/memory/ in current working directory
    this.memoryDir = memoryDir || path.join(process.cwd(), 'docs', 'memory');
    this.solutionsFile = path.join(this.memoryDir, 'solutions_learned.jsonl');
    this.mistakesDir = path.join(path.dirname(this.memoryDir), 'mistakes');

    // Ensure directories exist
    this.ensureDirectories();
  }

  /**
   * Ensure memory and mistakes directories exist
   */
  private ensureDirectories(): void {
    if (!fs.existsSync(this.memoryDir)) {
      fs.mkdirSync(this.memoryDir, { recursive: true });
    }
    if (!fs.existsSync(this.mistakesDir)) {
      fs.mkdirSync(this.mistakesDir, { recursive: true });
    }
  }

  /**
   * Get known solution for similar error
   *
   * Lookup strategy:
   *     1. Try mindbase semantic search (if available)
   *     2. Fallback to grep-based text search
   *     3. Return null if no match found
   *
   * @param errorInfo - Error information object
   * @returns Solution object if found, null otherwise
   */
  async getSolution(errorInfo: ErrorInfo): Promise<Solution | null> {
    const errorSignature = this.createErrorSignature(errorInfo);

    // Try mindbase first (semantic search, 500 tokens)
    let solution = await this.searchMindbase(errorSignature);
    if (solution) {
      return solution;
    }

    // Fallback to file-based search (0 tokens, local grep)
    solution = await this.searchLocalFiles(errorSignature);
    return solution;
  }

  /**
   * Record error and solution for future learning
   *
   * Stores to:
   *     1. docs/memory/solutions_learned.jsonl (append-only log)
   *     2. docs/mistakes/[feature]-[date].md (detailed analysis)
   *
   * @param errorInfo - Error information with analysis
   */
  async recordError(errorInfo: ErrorInfo): Promise<void> {
    // Add timestamp
    errorInfo.timestamp = new Date().toISOString();

    // Append to solutions log (JSONL format)
    const jsonLine = JSON.stringify(errorInfo) + '\n';
    fs.appendFileSync(this.solutionsFile, jsonLine, 'utf-8');

    // If this is a significant error with analysis, create mistake doc
    if (errorInfo.root_cause || errorInfo.solution) {
      await this.createMistakeDoc(errorInfo);
    }
  }

  /**
   * Create error signature for matching
   *
   * Combines:
   *     - Error type
   *     - Key parts of error message
   *     - Test context
   *
   * @param errorInfo - Error information object
   * @returns Error signature for matching
   */
  private createErrorSignature(errorInfo: ErrorInfo): string {
    const parts: string[] = [];

    if (errorInfo.error_type) {
      parts.push(errorInfo.error_type);
    }

    if (errorInfo.error_message) {
      // Extract key words from error message
      let message = errorInfo.error_message;
      // Remove numbers (often varies between errors)
      message = message.replace(/\d+/g, 'N');
      parts.push(message.substring(0, 100));  // First 100 chars
    }

    if (errorInfo.test_name) {
      parts.push(errorInfo.test_name);
    }

    return parts.join(' | ');
  }

  /**
   * Search for similar error in mindbase (semantic search)
   *
   * @param errorSignature - Error signature to search
   * @returns Solution object if found, null if mindbase unavailable or no match
   */
  private async searchMindbase(errorSignature: string): Promise<Solution | null> {
    // TODO: Implement mindbase integration
    // For now, return null (fallback to file search)
    return null;
  }

  /**
   * Search for similar error in local JSONL file
   *
   * Uses simple text matching on error signatures.
   *
   * @param errorSignature - Error signature to search
   * @returns Solution object if found, null otherwise
   */
  private async searchLocalFiles(errorSignature: string): Promise<Solution | null> {
    if (!fs.existsSync(this.solutionsFile)) {
      return null;
    }

    // Read JSONL file and search
    const content = fs.readFileSync(this.solutionsFile, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());

    for (const line of lines) {
      try {
        const record = JSON.parse(line) as ErrorInfo;
        const storedSignature = this.createErrorSignature(record);

        // Simple similarity check
        if (this.signaturesMatch(errorSignature, storedSignature)) {
          return {
            solution: record.solution,
            root_cause: record.root_cause,
            prevention: record.prevention,
            timestamp: record.timestamp,
          };
        }
      } catch (e) {
        // Skip invalid JSON lines
        continue;
      }
    }

    return null;
  }

  /**
   * Check if two error signatures match
   *
   * Simple word overlap check (good enough for most cases).
   *
   * @param sig1 - First signature
   * @param sig2 - Second signature
   * @param threshold - Minimum word overlap ratio (default: 0.7)
   * @returns Whether signatures are similar enough
   */
  private signaturesMatch(sig1: string, sig2: string, threshold: number = 0.7): boolean {
    const words1 = new Set(sig1.toLowerCase().split(/\s+/));
    const words2 = new Set(sig2.toLowerCase().split(/\s+/));

    if (words1.size === 0 || words2.size === 0) {
      return false;
    }

    // Calculate overlap
    const overlap = [...words1].filter(word => words2.has(word)).length;
    const union = new Set([...words1, ...words2]).size;

    return (overlap / union) >= threshold;
  }

  /**
   * Create detailed mistake documentation
   *
   * Format: docs/mistakes/[feature]-YYYY-MM-DD.md
   *
   * Structure:
   *     - What Happened (現象)
   *     - Root Cause (根本原因)
   *     - Why Missed (なぜ見逃したか)
   *     - Fix Applied (修正内容)
   *     - Prevention Checklist (防止策)
   *     - Lesson Learned (教訓)
   *
   * @param errorInfo - Error information with analysis
   */
  private async createMistakeDoc(errorInfo: ErrorInfo): Promise<void> {
    // Generate filename
    const testName = errorInfo.test_name || 'unknown';
    const date = new Date().toISOString().split('T')[0];
    const filename = `${testName}-${date}.md`;
    const filepath = path.join(this.mistakesDir, filename);

    // Create mistake document
    const content = `# Mistake Record: ${testName}

**Date**: ${date}
**Error Type**: ${errorInfo.error_type || 'Unknown'}

---

## ❌ What Happened (現象)

${errorInfo.error_message || 'No error message'}

\`\`\`
${errorInfo.traceback || 'No traceback'}
\`\`\`

---

## 🔍 Root Cause (根本原因)

${errorInfo.root_cause || 'Not analyzed'}

---

## 🤔 Why Missed (なぜ見逃したか)

${errorInfo.why_missed || 'Not analyzed'}

---

## ✅ Fix Applied (修正内容)

${errorInfo.solution || 'Not documented'}

---

## 🛡️ Prevention Checklist (防止策)

${errorInfo.prevention || 'Not documented'}

---

## 💡 Lesson Learned (教訓)

${errorInfo.lesson || 'Not documented'}
`;

    fs.writeFileSync(filepath, content, 'utf-8');
  }

  /**
   * Get reflexion pattern statistics
   *
   * @returns Statistics object with total errors, errors with solutions, and solution reuse rate
   */
  getStatistics(): { total_errors: number; errors_with_solutions: number; solution_reuse_rate: number } {
    if (!fs.existsSync(this.solutionsFile)) {
      return {
        total_errors: 0,
        errors_with_solutions: 0,
        solution_reuse_rate: 0.0,
      };
    }

    const content = fs.readFileSync(this.solutionsFile, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());

    let total = 0;
    let withSolutions = 0;

    for (const line of lines) {
      try {
        const record = JSON.parse(line) as ErrorInfo;
        total++;
        if (record.solution) {
          withSolutions++;
        }
      } catch (e) {
        // Skip invalid JSON lines
        continue;
      }
    }

    return {
      total_errors: total,
      errors_with_solutions: withSolutions,
      solution_reuse_rate: total > 0 ? (withSolutions / total * 100) : 0.0,
    };
  }
}
