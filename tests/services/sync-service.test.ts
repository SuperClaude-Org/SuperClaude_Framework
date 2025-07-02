import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { SyncService } from '../../src/services/sync-service.js';
import { DatabaseService } from '../../src/services/database-service.js';
import { GitHubLoader } from '../../src/github-loader.js';
import { mockCommands, mockPersonas, mockRules, createMockCommand, createMockPersona } from '../mocks/data.js';
import path from 'path';
import fs from 'fs/promises';

vi.mock('../../src/github-loader.js');

describe('SyncService', () => {
  let syncService: SyncService;
  let databaseService: DatabaseService;
  let githubLoader: GitHubLoader;
  let testDbPath: string;

  beforeEach(async () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(7);
    const processId = process.pid;
    testDbPath = path.join(process.cwd(), 'tests', 'fixtures', `sync-test-db-${timestamp}-${processId}-${random}.json`);
    await fs.mkdir(path.dirname(testDbPath), { recursive: true });
    
    githubLoader = new GitHubLoader();
    databaseService = new DatabaseService(testDbPath);
    await databaseService.initialize();
    
    syncService = new SyncService(githubLoader, databaseService, 30);
  });

  afterEach(async () => {
    try {
      await fs.unlink(testDbPath);
    } catch (error) {
      // Ignore if file doesn't exist
    }
    vi.clearAllMocks();
  });

  describe('syncFromGitHub', () => {
    it('should sync commands, personas, and rules from GitHub', async () => {
      vi.mocked(githubLoader.loadCommands).mockResolvedValue(mockCommands);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({
        developer: mockPersonas[0],
        architect: mockPersonas[1]
      });
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: mockRules.rules.rules });

      await syncService.syncFromGitHub();

      const commands = await databaseService.getAllCommands();
      const personas = await databaseService.getAllPersonas();
      const rules = await databaseService.getRules();

      expect(commands).toHaveLength(mockCommands.length);
      expect(personas).toHaveLength(mockPersonas.length);
      expect(rules).toBeTruthy();
      expect(rules?.rules).toEqual(mockRules.rules);
    });

    it('should update sync metadata on success', async () => {
      vi.mocked(githubLoader.loadCommands).mockResolvedValue([]);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({});
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: [] });

      await syncService.syncFromGitHub();

      const lastSync = await databaseService.getLastSync();
      expect(lastSync.getTime()).toBeGreaterThan(0);
    });

    it('should update sync metadata on failure', async () => {
      const error = new Error('Network error');
      vi.mocked(githubLoader.loadCommands).mockRejectedValue(error);

      await expect(syncService.syncFromGitHub()).rejects.toThrow('Network error');

      const dbContent = JSON.parse(await fs.readFile(testDbPath, 'utf-8'));
      expect(dbContent.syncMetadata.syncStatus).toBe('failed');
      expect(dbContent.syncMetadata.errorMessage).toBe('Network error');
    });

    it('should skip sync if already in progress', async () => {
      vi.mocked(githubLoader.loadCommands).mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
        return [];
      });
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({});
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: [] });

      const promise1 = syncService.syncFromGitHub();
      const promise2 = syncService.syncFromGitHub();

      await Promise.all([promise1, promise2]);

      expect(vi.mocked(githubLoader.loadCommands)).toHaveBeenCalledTimes(1);
    });

    it('should only update changed items based on hash', async () => {
      // First sync
      vi.mocked(githubLoader.loadCommands).mockResolvedValue(mockCommands);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({
        developer: mockPersonas[0]
      });
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: mockRules.rules.rules });

      await syncService.syncFromGitHub();

      // Second sync with one modified command
      const modifiedCommands = [
        mockCommands[0],
        { ...mockCommands[1], description: 'Modified description' }
      ];
      
      vi.mocked(githubLoader.loadCommands).mockResolvedValue(modifiedCommands);

      await syncService.syncFromGitHub();

      const commands = await databaseService.getAllCommands();
      const modifiedCommand = commands.find(c => c.id === mockCommands[1].id);
      expect(modifiedCommand?.description).toBe('Modified description');
    });

    it('should handle partial failures gracefully', async () => {
      vi.mocked(githubLoader.loadCommands).mockResolvedValue(mockCommands);
      vi.mocked(githubLoader.loadPersonas).mockRejectedValue(new Error('Personas load failed'));
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: mockRules.rules.rules });

      await expect(syncService.syncFromGitHub()).rejects.toThrow('Personas load failed');

      // Commands should not be saved due to transaction failure
      const commands = await databaseService.getAllCommands();
      expect(commands).toHaveLength(0);
    });
  });

  describe('loadFromDatabase', () => {
    beforeEach(async () => {
      await databaseService.upsertCommands(mockCommands);
      await databaseService.upsertPersonas(mockPersonas);
      await databaseService.upsertRules(mockRules);
    });

    it('should load all data from database', async () => {
      const data = await syncService.loadFromDatabase();

      expect(data.commands).toHaveLength(mockCommands.length);
      expect(Object.keys(data.personas)).toHaveLength(mockPersonas.length);
      expect(data.rules).toBeTruthy();
    });

    it('should return personas as a record keyed by id', async () => {
      const data = await syncService.loadFromDatabase();

      expect(data.personas['developer']).toBeTruthy();
      expect(data.personas['developer'].name).toBe('Developer');
      expect(data.personas['architect']).toBeTruthy();
      expect(data.personas['architect'].name).toBe('Software Architect');
    });

    it('should return null for rules if none exist', async () => {
      await databaseService.clearAll();

      const data = await syncService.loadFromDatabase();

      expect(data.commands).toEqual([]);
      expect(data.personas).toEqual({});
      expect(data.rules).toBeNull();
    });
  });

  describe('periodic sync', () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.mocked(githubLoader.loadCommands).mockResolvedValue([]);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({});
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: [] });
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('should start periodic sync with correct interval', async () => {
      const syncIntervalMinutes = 5;
      const service = new SyncService(githubLoader, databaseService, syncIntervalMinutes);

      service.startPeriodicSync();

      expect(vi.mocked(githubLoader.loadCommands)).not.toHaveBeenCalled();

      await vi.advanceTimersByTimeAsync(syncIntervalMinutes * 60 * 1000);

      expect(vi.mocked(githubLoader.loadCommands)).toHaveBeenCalledTimes(1);

      await vi.advanceTimersByTimeAsync(syncIntervalMinutes * 60 * 1000);

      expect(vi.mocked(githubLoader.loadCommands)).toHaveBeenCalledTimes(2);

      service.stopPeriodicSync();
    });

    it('should handle errors in periodic sync', async () => {
      vi.mocked(githubLoader.loadCommands).mockRejectedValue(new Error('Periodic sync error'));

      syncService.startPeriodicSync();

      await vi.advanceTimersByTimeAsync(30 * 60 * 1000);

      // Should not throw, just log the error
      expect(vi.mocked(githubLoader.loadCommands)).toHaveBeenCalled();

      syncService.stopPeriodicSync();
    });

    it('should not start multiple periodic syncs', () => {
      syncService.startPeriodicSync();
      syncService.startPeriodicSync();

      expect(vi.getTimerCount()).toBe(1);

      syncService.stopPeriodicSync();
    });

    it('should stop periodic sync', () => {
      syncService.startPeriodicSync();
      expect(vi.getTimerCount()).toBe(1);

      syncService.stopPeriodicSync();
      expect(vi.getTimerCount()).toBe(0);

      // Should handle stopping when already stopped
      syncService.stopPeriodicSync();
      expect(vi.getTimerCount()).toBe(0);
    });
  });

  describe('hash-based change detection', () => {
    it('should detect changes in command content', async () => {
      const originalCommand = mockCommands[0];
      vi.mocked(githubLoader.loadCommands).mockResolvedValue([originalCommand]);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({});
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: [] });

      await syncService.syncFromGitHub();

      // Modify command
      const modifiedCommand = { ...originalCommand, prompt: 'Modified prompt' };
      vi.mocked(githubLoader.loadCommands).mockResolvedValue([modifiedCommand]);

      await syncService.syncFromGitHub();

      const commands = await databaseService.getAllCommands();
      expect(commands[0].prompt).toBe('Modified prompt');
    });

    it('should not update unchanged items', async () => {
      vi.mocked(githubLoader.loadCommands).mockResolvedValue(mockCommands);
      vi.mocked(githubLoader.loadPersonas).mockResolvedValue({});
      vi.mocked(githubLoader.loadRules).mockResolvedValue({ rules: [] });

      await syncService.syncFromGitHub();

      const firstCommands = await databaseService.getAllCommands();
      const firstTimestamp = firstCommands[0].lastUpdated;

      // Wait a bit to ensure different timestamp if updated
      await new Promise(resolve => setTimeout(resolve, 10));

      // Sync again with same data
      await syncService.syncFromGitHub();

      const secondCommands = await databaseService.getAllCommands();
      const secondTimestamp = secondCommands[0].lastUpdated;

      expect(secondTimestamp.getTime()).toBe(firstTimestamp.getTime());
    });
  });
});