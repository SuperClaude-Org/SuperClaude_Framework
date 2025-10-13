#!/usr/bin/env node
/**
 * Auto-update checker for SuperClaude NPM package
 * Checks npm registry for newer versions and offers automatic updates
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const https = require('https');

const CACHE_FILE = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', '.npm_update_check');
const CHECK_INTERVAL = 86400000; // 24 hours in milliseconds
const TIMEOUT = 2000; // 2 seconds
const PACKAGE_NAME = '@bifrost_inc/superclaude';

/**
 * Get the current package version from package.json
 */
function getCurrentVersion() {
  try {
    const packagePath = path.join(__dirname, '..', 'package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    return packageData.version;
  } catch (error) {
    return null;
  }
}

/**
 * Check if we should perform an update check based on last check time
 */
function shouldCheckUpdate(force = false) {
  if (force) return true;
  
  try {
    if (!fs.existsSync(CACHE_FILE)) return true;
    
    const data = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
    const lastCheck = data.lastCheck || 0;
    
    // Check if 24 hours have passed
    return Date.now() - lastCheck > CHECK_INTERVAL;
  } catch {
    return true;
  }
}

/**
 * Save the current timestamp as last check time
 */
function saveCheckTimestamp() {
  const cacheDir = path.dirname(CACHE_FILE);
  
  // Create directory if it doesn't exist
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }
  
  let data = {};
  try {
    if (fs.existsSync(CACHE_FILE)) {
      data = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
    }
  } catch {
    // Ignore errors
  }
  
  data.lastCheck = Date.now();
  fs.writeFileSync(CACHE_FILE, JSON.stringify(data, null, 2));
}

/**
 * Query npm registry for the latest version
 */
function getLatestVersion() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'registry.npmjs.org',
      path: `/${PACKAGE_NAME}/latest`,
      method: 'GET',
      timeout: TIMEOUT,
      headers: {
        'User-Agent': 'SuperClaude-Updater'
      }
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const packageData = JSON.parse(data);
          resolve(packageData.version);
        } catch {
          resolve(null);
        }
      });
    });
    
    req.on('error', () => resolve(null));
    req.on('timeout', () => {
      req.destroy();
      resolve(null);
    });
    
    req.setTimeout(TIMEOUT);
    req.end();
  });
}

/**
 * Compare version strings
 */
function isNewerVersion(current, latest) {
  if (!current || !latest) return false;
  
  const currentParts = current.split('.').map(Number);
  const latestParts = latest.split('.').map(Number);
  
  for (let i = 0; i < Math.max(currentParts.length, latestParts.length); i++) {
    const currentPart = currentParts[i] || 0;
    const latestPart = latestParts[i] || 0;
    
    if (latestPart > currentPart) return true;
    if (latestPart < currentPart) return false;
  }
  
  return false;
}

/**
 * Detect if npm or yarn is being used globally
 */
function detectPackageManager() {
  // Check if installed globally with npm
  const npmResult = spawnSync('npm', ['list', '-g', PACKAGE_NAME], { 
    encoding: 'utf8',
    shell: true 
  });
  
  if (npmResult.status === 0 && npmResult.stdout.includes(PACKAGE_NAME)) {
    return 'npm';
  }
  
  // Check if installed globally with yarn
  const yarnResult = spawnSync('yarn', ['global', 'list'], { 
    encoding: 'utf8',
    shell: true 
  });
  
  if (yarnResult.status === 0 && yarnResult.stdout.includes(PACKAGE_NAME)) {
    return 'yarn';
  }
  
  return 'npm'; // Default to npm
}

/**
 * Get the appropriate update command
 */
function getUpdateCommand() {
  const pm = detectPackageManager();
  
  if (pm === 'yarn') {
    return `yarn global upgrade ${PACKAGE_NAME}`;
  }
  
  return `npm update -g ${PACKAGE_NAME}`;
}

/**
 * Show update banner
 */
function showUpdateBanner(currentVersion, latestVersion, autoUpdate = false) {
  const updateCmd = getUpdateCommand();
  
  console.log('\n\x1b[36m╔════════════════════════════════════════════════╗\x1b[0m');
  console.log(`\x1b[36m║\x1b[33m  🚀 Update Available: ${currentVersion} → ${latestVersion}        \x1b[36m║\x1b[0m`);
  console.log(`\x1b[36m║\x1b[32m  Run: ${updateCmd.padEnd(30)} \x1b[36m║\x1b[0m`);
  console.log('\x1b[36m╚════════════════════════════════════════════════╝\x1b[0m\n');
  
  return autoUpdate || process.env.SUPERCLAUDE_AUTO_UPDATE === 'true';
}

/**
 * Perform the update
 */
function performUpdate() {
  const updateCmd = getUpdateCommand();
  console.log('\x1b[36m🔄 Updating SuperClaude...\x1b[0m');
  
  const cmdParts = updateCmd.split(' ');
  const result = spawnSync(cmdParts[0], cmdParts.slice(1), { 
    stdio: 'inherit',
    shell: true 
  });
  
  if (result.status === 0) {
    console.log('\x1b[32m✅ Update completed successfully!\x1b[0m');
    console.log('\x1b[33mPlease restart SuperClaude to use the new version.\x1b[0m');
    return true;
  } else {
    console.log('\x1b[33m⚠️  Update failed. Please run manually:\x1b[0m');
    console.log(`  ${updateCmd}`);
    return false;
  }
}

/**
 * Main function to check and notify for updates
 */
async function checkAndNotify(options = {}) {
  const { force = false, autoUpdate = false, silent = false } = options;
  
  // Check environment variables
  if (process.env.SUPERCLAUDE_NO_UPDATE_CHECK === 'true') {
    return false;
  }
  
  // Check if enough time has passed
  if (!shouldCheckUpdate(force)) {
    return false;
  }
  
  // Get current version
  const currentVersion = getCurrentVersion();
  if (!currentVersion) {
    return false;
  }
  
  // Get latest version
  const latestVersion = await getLatestVersion();
  if (!latestVersion) {
    return false;
  }
  
  // Save timestamp
  saveCheckTimestamp();
  
  // Compare versions
  if (!isNewerVersion(currentVersion, latestVersion)) {
    return false;
  }
  
  // Show banner unless silent
  if (!silent) {
    const shouldUpdate = showUpdateBanner(currentVersion, latestVersion, autoUpdate);
    
    if (shouldUpdate) {
      return performUpdate();
    }
  }
  
  return false;
}

// Export functions for use in other modules
module.exports = {
  checkAndNotify,
  getCurrentVersion,
  getLatestVersion,
  isNewerVersion
};

// If run directly, perform check
if (require.main === module) {
  checkAndNotify({
    force: process.argv.includes('--force'),
    autoUpdate: process.argv.includes('--auto-update')
  });
}