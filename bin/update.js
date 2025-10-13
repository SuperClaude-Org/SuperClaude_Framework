#!/usr/bin/env node
const { run, detectPip, detectPipx, isSuperClaudeInstalledPipx, checkPythonEnvironment } = require("./check_env");

console.log("🔄 Checking for SuperClaude updates...");

// Detect installation method
const isExternallyManaged = checkPythonEnvironment();
let updateMethod = null;

// Check if installed via pipx
if (detectPipx() && isSuperClaudeInstalledPipx()) {
  updateMethod = "pipx";
  console.log("✅ Detected pipx installation");
} else {
  // Check for pip installation
  let pipCmd = detectPip();
  if (!pipCmd) {
    console.error("❌ Neither pipx nor pip found, cannot update.");
    console.error("   Please install SuperClaude first using:");
    console.error("   pipx install SuperClaude");
    console.error("   or");
    console.error("   pip install SuperClaude");
    process.exit(1);
  }
  
  if (isExternallyManaged) {
    updateMethod = "pip-user";
    console.log("✅ Detected pip installation with --user flag");
  } else {
    updateMethod = "pip";
    console.log("✅ Detected standard pip installation");
  }
}

// Perform update based on detected method
console.log("🔄 Updating SuperClaude from PyPI...");

let result;
switch(updateMethod) {
  case "pipx":
    result = run("pipx", ["upgrade", "SuperClaude"], { stdio: "inherit" });
    break;
  case "pip-user":
    result = run(detectPip(), ["install", "--upgrade", "--user", "SuperClaude"], { stdio: "inherit" });
    break;
  case "pip":
    result = run(detectPip(), ["install", "--upgrade", "SuperClaude"], { stdio: "inherit" });
    break;
}

if (result.status !== 0) {
  console.error("❌ Update failed.");
  if (updateMethod === "pip" && isExternallyManaged) {
    console.error("   Your system requires pipx or --user flag for pip operations.");
    console.error("   Try: pipx upgrade SuperClaude");
    console.error("   Or:  pip install --upgrade --user SuperClaude");
  }
  process.exit(1);
}

console.log("✅ SuperClaude updated successfully!");

// Run SuperClaude update command
console.log("\n🚀 Running SuperClaude update...");
const updateResult = run("SuperClaude", ["update"], { stdio: "inherit" });

if (updateResult.status !== 0) {
  console.log("\n⚠️  Could not run 'SuperClaude update' automatically.");
  console.log("   Please run it manually:");
  console.log("   SuperClaude update");
}