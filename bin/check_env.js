const { spawnSync } = require("child_process");

function run(cmd, args = [], opts = {}) {
  return spawnSync(cmd, args, {
    stdio: opts.stdio || "pipe",
    shell: true
  });
}

function checkCommand(cmd, args = ["--version"]) {
  const result = run(cmd, args);
  return result.status === 0;
}

function detectPython() {
  const candidates = ["python3", "python", "py"];
  for (let c of candidates) {
    if (checkCommand(c)) return c;
  }
  return null;
}

function detectPip() {
  const candidates = ["pip3", "pip", "py -m pip"];
  for (let c of candidates) {
    if (checkCommand(c.split(" ")[0])) return c;
  }
  return null;
}

function detectPipx() {
  if (checkCommand("pipx")) return "pipx";
  return null;
}

function isSuperClaudeInstalled(pipCmd) {
  const result = run(pipCmd, ["show", "SuperClaude"]);
  return result.status === 0;
}

function isSuperClaudeInstalledPipx() {
  const result = run("pipx", ["list"]);
  if (result.status === 0 && result.stdout) {
    return result.stdout.toString().includes("SuperClaude");
  }
  return false;
}

function checkPythonEnvironment() {
  // Check if we're in an externally managed environment (PEP 668)
  const result = run("python3", ["-c", "import sysconfig; print(sysconfig.get_path('stdlib'))"]);
  if (result.status === 0 && result.stdout) {
    const stdlibPath = result.stdout.toString().trim();
    const checkPep668 = run("test", ["-f", `${stdlibPath}/EXTERNALLY-MANAGED`]);
    return checkPep668.status === 0;
  }
  return false;
}

module.exports = { run, detectPython, detectPip, detectPipx, isSuperClaudeInstalled, isSuperClaudeInstalledPipx, checkPythonEnvironment };
