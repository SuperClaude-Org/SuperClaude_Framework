import { vi, afterEach, beforeEach, afterAll, beforeAll } from 'vitest';
import fs from 'fs/promises';
import path from 'path';

// Mock logger to reduce noise in tests
vi.mock('../src/logger.js', () => ({
  default: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

// Ensure tests run in isolation
beforeAll(async () => {
  // Clean up any existing test data
  const fixturesDir = path.join(process.cwd(), 'tests', 'fixtures');
  const dataDir = path.join(process.cwd(), 'data');
  
  try {
    await fs.rm(fixturesDir, { recursive: true, force: true });
  } catch (error) {
    // Directory might not exist
  }
  
  try {
    const files = await fs.readdir(dataDir);
    for (const file of files) {
      if (file.endsWith('.json') && !file.includes('backup')) {
        await fs.unlink(path.join(dataDir, file));
      }
    }
  } catch (error) {
    // Directory might not exist
  }
});

// Clean up test fixtures before each test
beforeEach(async () => {
  const fixturesDir = path.join(process.cwd(), 'tests', 'fixtures');
  try {
    await fs.rm(fixturesDir, { recursive: true, force: true });
  } catch (error) {
    // Directory might not exist, that's fine
  }
  await fs.mkdir(fixturesDir, { recursive: true });
  
  // Also clean up any data files that might interfere with tests
  const dataDir = path.join(process.cwd(), 'data');
  try {
    const files = await fs.readdir(dataDir);
    for (const file of files) {
      if (file.endsWith('.json') && !file.includes('backup')) {
        await fs.unlink(path.join(dataDir, file));
      }
    }
  } catch (error) {
    // Directory might not exist, that's fine
  }
});

// Clean up after each test
afterEach(async () => {
  vi.clearAllMocks();
  vi.resetAllMocks();
});

// Clean up after all tests
afterAll(async () => {
  const fixturesDir = path.join(process.cwd(), 'tests', 'fixtures');
  try {
    await fs.rm(fixturesDir, { recursive: true, force: true });
  } catch (error) {
    // Directory might not exist, that's fine
  }
  
  // Restore backup if exists
  const dataDir = path.join(process.cwd(), 'data');
  const backupPath = path.join(dataDir, 'superclaude.json.backup');
  const originalPath = path.join(dataDir, 'superclaude.json');
  try {
    await fs.access(backupPath);
    await fs.rename(backupPath, originalPath);
  } catch (error) {
    // Backup might not exist, that's fine
  }
});