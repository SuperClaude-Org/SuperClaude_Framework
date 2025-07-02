import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { DatabaseService } from '../../src/services/database-service.js';
import { CommandModelSchema, PersonaModelSchema, RulesModelSchema, DatabaseSchemaSchema } from '../../src/schemas.js';
import { createMockCommand, createMockPersona, createMockRules, mockCommands, mockPersonas, mockRules } from '../mocks/data.js';
import path from 'path';
import fs from 'fs/promises';
import { CommandModel, PersonaModel, RulesModel } from '../../src/database.js';

describe('DatabaseService', () => {
  let dbService: DatabaseService;
  let testDbPath: string;

  beforeEach(async () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(7);
    const processId = process.pid;
    testDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-${timestamp}-${processId}-${random}.json`);
    await fs.mkdir(path.dirname(testDbPath), { recursive: true });
    
    // Ensure the file doesn't exist
    try {
      await fs.unlink(testDbPath);
    } catch (error) {
      // File doesn't exist, that's fine
    }
    
    dbService = new DatabaseService(testDbPath);
  });

  afterEach(async () => {
    try {
      await fs.unlink(testDbPath);
    } catch (error) {
      // Ignore if file doesn't exist
    }
  });

  describe('initialize', () => {
    it('should create database file if it does not exist', async () => {
      await dbService.initialize();
      
      const fileExists = await fs.access(testDbPath).then(() => true).catch(() => false);
      expect(fileExists).toBe(true);
    });

    it('should not reinitialize if already initialized', async () => {
      await dbService.initialize();
      const firstMtime = (await fs.stat(testDbPath)).mtime;
      
      await new Promise(resolve => setTimeout(resolve, 10));
      await dbService.initialize();
      
      const secondMtime = (await fs.stat(testDbPath)).mtime;
      expect(firstMtime.getTime()).toBe(secondMtime.getTime());
    });

    it('should create valid database schema', async () => {
      await dbService.initialize();
      
      const dbContent = JSON.parse(await fs.readFile(testDbPath, 'utf-8'));
      
      // Convert date strings to Date objects for validation
      const transformedContent = {
        ...dbContent,
        commands: dbContent.commands.map((cmd: any) => ({
          ...cmd,
          lastUpdated: new Date(cmd.lastUpdated)
        })),
        personas: dbContent.personas.map((persona: any) => ({
          ...persona,
          lastUpdated: new Date(persona.lastUpdated)
        })),
        rules: dbContent.rules.map((rule: any) => ({
          ...rule,
          lastUpdated: new Date(rule.lastUpdated)
        })),
        syncMetadata: {
          ...dbContent.syncMetadata,
          lastSync: new Date(dbContent.syncMetadata.lastSync)
        }
      };
      
      const result = DatabaseSchemaSchema.safeParse(transformedContent);
      
      expect(result.success).toBe(true);
    });
  });

  describe('commands', () => {
    beforeEach(async () => {
      await dbService.initialize();
    });

    describe('upsertCommand', () => {
      it('should insert new command', async () => {
        const command = mockCommands[0];
        await dbService.upsertCommand(command);
        
        const commands = await dbService.getAllCommands();
        expect(commands).toHaveLength(1);
        expect(commands[0].id).toBe(command.id);
        expect(commands[0].name).toBe(command.name);
        expect(commands[0].description).toBe(command.description);
        expect(commands[0].prompt).toBe(command.prompt);
        expect(commands[0].arguments).toEqual(command.arguments);
      });

      it('should update existing command', async () => {
        const command = mockCommands[0];
        await dbService.upsertCommand(command);
        
        const updatedCommand = { ...command, description: 'Updated description' };
        await dbService.upsertCommand(updatedCommand);
        
        const commands = await dbService.getAllCommands();
        expect(commands).toHaveLength(1);
        expect(commands[0].description).toBe('Updated description');
      });

      it('should validate command with Zod schema', async () => {
        const command = createMockCommand();
        await dbService.upsertCommand(command);
        
        const commands = await dbService.getAllCommands();
        const result = CommandModelSchema.safeParse(commands[0]);
        expect(result.success).toBe(true);
      });
    });

    describe('upsertCommands', () => {
      it('should insert multiple commands', async () => {
        // Create fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-multi-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        await freshDbService.upsertCommands(mockCommands);
        
        const commands = await freshDbService.getAllCommands();
        expect(commands).toHaveLength(mockCommands.length);
        
        await fs.unlink(freshDbPath);
      });

      it('should update existing commands', async () => {
        // Create fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-update-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        await freshDbService.upsertCommands(mockCommands);
        
        const updatedCommands = mockCommands.map(cmd => ({
          ...cmd,
          description: `Updated: ${cmd.description}`
        }));
        
        await freshDbService.upsertCommands(updatedCommands);
        
        const commands = await freshDbService.getAllCommands();
        expect(commands).toHaveLength(mockCommands.length);
        commands.forEach(cmd => {
          expect(cmd.description).toContain('Updated:');
        });
        
        await fs.unlink(freshDbPath);
      });
    });

    describe('getAllCommands', () => {
      it('should return empty array when no commands exist', async () => {
        // Create a fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-empty-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        const commands = await freshDbService.getAllCommands();
        expect(commands).toEqual([]);
        
        await fs.unlink(freshDbPath);
      });

      it('should return all commands with ISO8601 dates', async () => {
        // Create fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-dates-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        const testCommands = Array.from({ length: 3 }, () => createMockCommand());
        await freshDbService.upsertCommands(testCommands);
        
        const commands = await freshDbService.getAllCommands();
        expect(commands).toHaveLength(3);
        
        commands.forEach(cmd => {
          expect(cmd.lastUpdated).toBeInstanceOf(Date);
          expect(cmd.lastUpdated.toISOString()).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
        });
        
        await fs.unlink(freshDbPath);
      });
    });
  });

  describe('personas', () => {
    beforeEach(async () => {
      await dbService.initialize();
    });

    describe('upsertPersona', () => {
      it('should insert new persona', async () => {
        const persona = mockPersonas[0];
        await dbService.upsertPersona(persona);
        
        const personas = await dbService.getAllPersonas();
        expect(personas).toHaveLength(1);
        expect(personas[0]).toMatchObject(persona);
      });

      it('should update existing persona', async () => {
        const persona = mockPersonas[0];
        await dbService.upsertPersona(persona);
        
        const updatedPersona = { ...persona, name: 'Updated Name' };
        await dbService.upsertPersona(updatedPersona);
        
        const personas = await dbService.getAllPersonas();
        expect(personas).toHaveLength(1);
        expect(personas[0].name).toBe('Updated Name');
      });

      it('should validate persona with Zod schema', async () => {
        const persona = createMockPersona();
        await dbService.upsertPersona(persona);
        
        const personas = await dbService.getAllPersonas();
        const result = PersonaModelSchema.safeParse(personas[0]);
        expect(result.success).toBe(true);
      });
    });

    describe('upsertPersonas', () => {
      it('should insert multiple personas', async () => {
        // Create fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-personas-multi-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        await freshDbService.upsertPersonas(mockPersonas);
        
        const personas = await freshDbService.getAllPersonas();
        expect(personas).toHaveLength(mockPersonas.length);
        
        await fs.unlink(freshDbPath);
      });
    });

    describe('getAllPersonas', () => {
      it('should return empty array when no personas exist', async () => {
        // Create a fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-empty-personas-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        const personas = await freshDbService.getAllPersonas();
        expect(personas).toEqual([]);
        
        await fs.unlink(freshDbPath);
      });
    });
  });

  describe('rules', () => {
    beforeEach(async () => {
      await dbService.initialize();
    });

    describe('upsertRules', () => {
      it('should insert new rules', async () => {
        await dbService.upsertRules(mockRules);
        
        const rules = await dbService.getRules();
        expect(rules).toMatchObject(mockRules);
      });

      it('should update existing rules', async () => {
        await dbService.upsertRules(mockRules);
        
        const updatedRules = {
          ...mockRules,
          rules: {
            rules: [
              { name: 'new-rule', content: 'New rule content' }
            ]
          }
        };
        
        await dbService.upsertRules(updatedRules);
        
        const rules = await dbService.getRules();
        expect(rules?.rules.rules).toHaveLength(1);
        expect(rules?.rules.rules[0].name).toBe('new-rule');
      });

      it('should validate rules with Zod schema', async () => {
        const rules = createMockRules();
        await dbService.upsertRules(rules);
        
        const storedRules = await dbService.getRules();
        const result = RulesModelSchema.safeParse(storedRules);
        expect(result.success).toBe(true);
      });
    });

    describe('getRules', () => {
      it('should return null when no rules exist', async () => {
        // Create a fresh database for this test
        const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-empty-rules-${Date.now()}.json`);
        const freshDbService = new DatabaseService(freshDbPath);
        await freshDbService.initialize();
        
        const rules = await freshDbService.getRules();
        expect(rules).toBeNull();
        
        await fs.unlink(freshDbPath);
      });

      it('should return first rules entry', async () => {
        await dbService.upsertRules(mockRules);
        const anotherRules = createMockRules({ id: 'another-rules' });
        await dbService.upsertRules(anotherRules);
        
        const rules = await dbService.getRules();
        expect(rules?.id).toBe('superclaude-rules');
      });
    });
  });

  describe('sync metadata', () => {
    beforeEach(async () => {
      await dbService.initialize();
    });

    describe('getLastSync', () => {
      it('should return epoch date initially', async () => {
        const lastSync = await dbService.getLastSync();
        expect(lastSync.getTime()).toBe(0);
      });
    });

    describe('updateSyncMetadata', () => {
      it('should update sync metadata with success status', async () => {
        await dbService.updateSyncMetadata('success');
        
        const lastSync = await dbService.getLastSync();
        expect(lastSync.getTime()).toBeGreaterThan(0);
        expect(lastSync).toBeInstanceOf(Date);
      });

      it('should update sync metadata with failed status and error message', async () => {
        const errorMessage = 'Network error';
        await dbService.updateSyncMetadata('failed', errorMessage);
        
        const dbContent = JSON.parse(await fs.readFile(testDbPath, 'utf-8'));
        expect(dbContent.syncMetadata.syncStatus).toBe('failed');
        expect(dbContent.syncMetadata.errorMessage).toBe(errorMessage);
      });
    });
  });

  describe('clearAll', () => {
    it('should clear all data', async () => {
      // Create fresh database for this test
      const freshDbPath = path.join(process.cwd(), 'tests', 'fixtures', `test-db-clear-${Date.now()}.json`);
      const freshDbService = new DatabaseService(freshDbPath);
      await freshDbService.initialize();
      
      await freshDbService.upsertCommands(mockCommands);
      await freshDbService.upsertPersonas(mockPersonas);
      await freshDbService.upsertRules(mockRules);
      
      await freshDbService.clearAll();
      
      const commands = await freshDbService.getAllCommands();
      const personas = await freshDbService.getAllPersonas();
      const rules = await freshDbService.getRules();
      
      expect(commands).toEqual([]);
      expect(personas).toEqual([]);
      expect(rules).toBeNull();
      
      await fs.unlink(freshDbPath);
    });
  });

  describe('error handling', () => {
    it('should throw error when not initialized', async () => {
      const uninitializedService = new DatabaseService(testDbPath);
      
      await expect(() => uninitializedService.getAllCommands()).rejects.toThrow('Database not initialized');
    });

    it('should handle file system errors gracefully', async () => {
      const invalidPath = '/invalid/path/db.json';
      const service = new DatabaseService(invalidPath);
      
      await expect(service.initialize()).rejects.toThrow();
    });
  });
});