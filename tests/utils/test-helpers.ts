import { DatabaseService } from '../../src/services/database-service.js';
import path from 'path';
import fs from 'fs/promises';
import { randomBytes } from 'crypto';

/**
 * Creates a completely isolated DatabaseService instance for testing.
 * Each instance gets its own unique database file that is guaranteed
 * to be empty and isolated from other tests.
 */
export async function createTestDatabase(): Promise<{
  dbService: DatabaseService;
  dbPath: string;
  cleanup: () => Promise<void>;
}> {
  // Generate a truly unique database path using multiple sources of randomness
  const timestamp = Date.now();
  const random = randomBytes(8).toString('hex');
  const processId = process.pid;
  const nanoTime = process.hrtime.bigint().toString();
  
  const dbPath = path.join(
    process.cwd(),
    'tests',
    'fixtures',
    'temp',
    `test-db-${timestamp}-${processId}-${random}-${nanoTime}.json`
  );
  
  // Ensure the temp directory exists
  const dbDir = path.dirname(dbPath);
  await fs.mkdir(dbDir, { recursive: true });
  
  // Verify directory was created
  try {
    await fs.access(dbDir);
  } catch (error) {
    throw new Error(`Failed to create test database directory: ${dbDir}`);
  }
  
  // Create the database service
  const dbService = new DatabaseService(dbPath);
  
  // Initialize with empty database
  await dbService.initialize();
  
  // Cleanup function to remove the database file and any temp files
  const cleanup = async () => {
    try {
      await fs.unlink(dbPath);
    } catch (error) {
      // Ignore if file doesn't exist
    }
    
    try {
      await fs.unlink(dbPath + '.tmp');
    } catch (error) {
      // Ignore if file doesn't exist
    }
  };
  
  return { dbService, dbPath, cleanup };
}

/**
 * Helper to wait for a condition to be true
 */
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Timeout waiting for condition after ${timeout}ms`);
}

/**
 * Helper to verify database is empty
 */
export async function verifyEmptyDatabase(dbService: DatabaseService): Promise<boolean> {
  const commands = await dbService.getAllCommands();
  const personas = await dbService.getAllPersonas();
  const rules = await dbService.getRules();
  
  return commands.length === 0 && personas.length === 0 && rules === null;
}