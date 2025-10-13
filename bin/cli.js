#!/usr/bin/env node
const { spawnSync } = require("child_process");
const { detectPython, detectPip } = require("./check_env");
const { checkAndNotify } = require("./check_update");

let pythonCmd = detectPython();
if (!pythonCmd) {
  console.error("❌ Python 3 is required but not found.");
  process.exit(1);
}

const args = process.argv.slice(2);

// Parse command line arguments for update control
const noUpdateCheck = args.includes('--no-update-check');
const autoUpdate = args.includes('--auto-update');
const isQuiet = args.includes('--quiet') || args.includes('-q');

// Special case: update command
if (args[0] === "update") {
  require("./update");
  process.exit(0);
}

// Check for updates unless disabled
if (!noUpdateCheck && !isQuiet) {
  // Run update check asynchronously to avoid blocking
  checkAndNotify({
    autoUpdate: autoUpdate,
    silent: false
  }).then(updated => {
    if (updated) {
      console.log("\n🔄 SuperClaude was updated. Please restart to use the new version.");
      process.exit(0);
    }
  }).catch(() => {
    // Silently ignore update check errors
  });
}

// Forward everything to Python SuperClaude
const result = spawnSync(pythonCmd, ["-m", "SuperClaude", ...args], { stdio: "inherit", shell: true });
process.exit(result.status);
    
