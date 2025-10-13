#!/usr/bin/env node
const { run, detectPython, detectPip, detectPipx, isSuperClaudeInstalled, isSuperClaudeInstalledPipx, checkPythonEnvironment } = require("./check_env");

console.log("🔍 Checking environment...");

let pythonCmd = detectPython();
if (!pythonCmd) {
  console.error("❌ Python 3 is required but not found.");
  console.error("   Please install Python 3.8 or later from https://python.org");
  process.exit(1);
}
console.log(`✅ Found Python: ${pythonCmd}`);

// Check if we're in an externally managed environment (PEP 668)
const isExternallyManaged = checkPythonEnvironment();
let installMethod = null;
let isInstalled = false;

if (isExternallyManaged) {
  console.log("📦 Detected externally managed Python environment (PEP 668)");
  
  // Try pipx first for externally managed environments
  let pipxCmd = detectPipx();
  if (pipxCmd) {
    console.log(`✅ Found pipx: ${pipxCmd}`);
    installMethod = "pipx";
    isInstalled = isSuperClaudeInstalledPipx();
  } else {
    console.log("⚠️  pipx is recommended for this system but not found.");
    console.log("   You can install pipx with: apt install pipx (Ubuntu/Debian) or brew install pipx (macOS)");
    console.log("   Alternatively, use one of these:");
    console.log("     pip install --user SuperClaude  # Recommended");
    console.log("     pip install --break-system-packages SuperClaude  # Force (use with caution)");
    
    // Fall back to pip with --user flag
    let pipCmd = detectPip();
    if (pipCmd) {
      console.log(`✅ Found pip: ${pipCmd}`);
      console.log("   Will attempt installation with --user flag");
      installMethod = "pip-user";
      isInstalled = isSuperClaudeInstalled(pipCmd);
    } else {
      console.error("❌ Neither pipx nor pip found. Please install one of them.");
      process.exit(1);
    }
  }
} else {
  // Standard environment - use pip normally
  let pipCmd = detectPip();
  if (!pipCmd) {
    console.error("❌ pip is required but not found.");
    console.error("   Please install pip or use your system's package manager");
    process.exit(1);
  }
  console.log(`✅ Found pip: ${pipCmd}`);
  installMethod = "pip";
  isInstalled = isSuperClaudeInstalled(pipCmd);
}

// Perform installation based on detected method
if (!isInstalled) {
  console.log("📦 Installing SuperClaude from PyPI...");
  
  let result;
  switch(installMethod) {
    case "pipx":
      result = run("pipx", ["install", "SuperClaude"], { stdio: "inherit" });
      break;
    case "pip-user":
      result = run(detectPip(), ["install", "--user", "SuperClaude"], { stdio: "inherit" });
      break;
    case "pip":
      result = run(detectPip(), ["install", "SuperClaude"], { stdio: "inherit" });
      break;
  }
  
  if (result.status !== 0) {
    console.error("❌ Installation failed.");
    if (installMethod === "pip" && isExternallyManaged) {
      console.error("   Your system requires pipx or --user flag for pip installations.");
      console.error("   Try: pipx install SuperClaude");
      console.error("   Or:  pip install --user SuperClaude");
    }
    process.exit(1);
  }
  console.log("✅ SuperClaude installed successfully!");
  
  // For pipx installations, ensure it's in PATH
  if (installMethod === "pipx") {
    console.log("\n📌 Note: If 'SuperClaude' command is not found, run:");
    console.log("   pipx ensurepath");
    console.log("   Then restart your terminal or run: source ~/.bashrc");
  }
} else {
  console.log("✅ SuperClaude already installed.");
}

// Try to run SuperClaude install
console.log("\n🚀 Running SuperClaude installation...");
const installResult = run("SuperClaude", ["install"], { stdio: "inherit" });

if (installResult.status !== 0) {
  console.log("\n⚠️  Could not run 'SuperClaude install' automatically.");
  console.log("   Please run it manually after ensuring SuperClaude is in your PATH:");
  console.log("   SuperClaude install");
  
  if (installMethod === "pipx") {
    console.log("\n   If command not found, try:");
    console.log("   pipx ensurepath && source ~/.bashrc");
  } else if (installMethod === "pip-user") {
    console.log("\n   If command not found, add Python user bin to PATH:");
    console.log("   export PATH=\"$HOME/.local/bin:$PATH\"");
  }
}