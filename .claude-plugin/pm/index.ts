/**
 * PM Agent - Project Manager with Confidence-Driven Workflow
 *
 * Auto-executes on session start via hooks/hooks.json
 * Orchestrates sub-agents with 90% confidence threshold
 */

import { execSync } from 'child_process';
import { confidenceCheck } from './confidence';

interface SessionContext {
  gitStatus: string;
  tokenBudget: number;
  projectRoot: string;
}

/**
 * Session Start Protocol
 * Auto-executes when Claude Code starts
 */
export async function sessionStart(): Promise<void> {
  console.log("🚀 PM Agent activated");

  // 1. Check git status
  const gitStatus = checkGitStatus();
  console.log(`📊 Git: ${gitStatus}`);

  // 2. Token budget check (from Claude Code UI)
  console.log("💡 Check token budget with /context");

  // 3. Ready
  console.log("✅ PM Agent ready to accept tasks");
  console.log("");
  console.log("**Core Capabilities**:");
  console.log("- 🔍 Pre-implementation confidence check (≥90% required)");
  console.log("- ⚡ Parallel investigation and execution");
  console.log("- 📊 Token-budget-aware operations");
  console.log("");
  console.log("**Usage**: Assign tasks directly - PM Agent will orchestrate");
}

/**
 * Check git repository status
 */
function checkGitStatus(): string {
  try {
    const status = execSync('git status --porcelain', { encoding: 'utf-8' });
    if (!status.trim()) {
      return 'clean';
    }
    const lines = status.trim().split('\n').length;
    return `${lines} file(s) modified`;
  } catch {
    return 'not a git repo';
  }
}

/**
 * Main task handler
 * Called when user assigns a task
 */
export async function handleTask(task: string): Promise<void> {
  console.log(`📝 Task received: ${task}`);
  console.log("");

  // Start confidence-driven workflow
  await confidenceDrivenWorkflow(task);
}

/**
 * Confidence-Driven Workflow
 *
 * 1. Investigation phase (loop until 90% confident)
 * 2. Confidence check
 * 3. Implementation (only when ≥90%)
 */
async function confidenceDrivenWorkflow(task: string): Promise<void> {
  let confidence = 0;
  let iteration = 0;
  const MAX_ITERATIONS = 10;

  console.log("🔍 Starting investigation phase...");
  console.log("");

  while (confidence < 0.9 && iteration < MAX_ITERATIONS) {
    iteration++;
    console.log(`🔄 Investigation iteration ${iteration}...`);

    // Investigation actions (delegated to sub-agents)
    const context = await investigate(task);

    // Self-evaluate confidence
    confidence = await confidenceCheck(context);

    console.log(`📊 Confidence: ${(confidence * 100).toFixed(0)}%`);

    if (confidence < 0.9) {
      console.log("⚠️ Confidence < 90% - Continue investigation");
      console.log("");
    }
  }

  if (confidence >= 0.9) {
    console.log("✅ High confidence (≥90%) - Proceeding to implementation");
    console.log("");
    // Implementation phase
    await implement(task);
  } else {
    console.log("❌ Max iterations reached - Request user clarification");
  }
}

/**
 * Investigation phase
 * Delegates to sub-agents: research, index, grep, etc.
 */
async function investigate(task: string): Promise<any> {
  // This will be orchestrated by Claude using:
  // - /research for web research
  // - /index-repo for codebase structure
  // - Glob/Grep for code search
  // - WebFetch for official docs

  return {
    task,
    duplicate_check_complete: false,
    architecture_check_complete: false,
    official_docs_verified: false,
    oss_reference_complete: false,
    root_cause_identified: false
  };
}

/**
 * Implementation phase
 * Only executed when confidence ≥ 90%
 */
async function implement(task: string): Promise<void> {
  console.log(`🚀 Implementing: ${task}`);
  // Actual implementation delegated to Claude
}

/**
 * Memory Management (Mindbase MCP integration)
 * Zero-footprint: No auto-load, explicit load/save only
 */
export const memory = {
  load: async () => {
    console.log("💾 Use /sc:load to load context from Mindbase MCP");
  },
  save: async () => {
    console.log("💾 Use /sc:save to persist session to Mindbase MCP");
  }
};

// Auto-execute on session start
if (require.main === module) {
  sessionStart();
}
