import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { DatabaseService } from "../../src/services/database-service.js";
import {
  CommandModelSchema,
  PersonaModelSchema,
  RulesModelSchema,
  DatabaseSchemaSchema,
} from "../../src/schemas.js";
import {
  createMockCommand,
  createMockPersona,
  createMockRules,
  getMockCommands,
  getMockPersonas,
  getMockRules,
} from "../mocks/data.js";
import { createTestDatabase, verifyEmptyDatabase } from "../utils/test-helpers.js";

describe("DatabaseService", () => {
  let dbService: DatabaseService;
  let testDbPath: string;

  beforeEach(async () => {
    // Create a completely isolated database for each test
    const testDb = await createTestDatabase();
    dbService = testDb.dbService;
    testDbPath = testDb.dbPath;
  });

  afterEach(async () => {
    // No cleanup needed for in-memory databases
  });

  describe("initialize", () => {
    it.skip("should create database file if it does not exist", async () => {
      // Not applicable for in-memory databases
      expect(true).toBe(true);
    });

    it("should not reinitialize if already initialized", async () => {
      // Try to initialize again
      await dbService.initialize();

      // Should still be able to use the database
      const commands = await dbService.getAllCommands();
      expect(commands).toEqual([]);
    });
  });

  describe("commands", () => {
    describe("upsertCommand", () => {
      it("should insert new command", async () => {
        const command = createMockCommand({
          id: "test-1",
          name: "test-command",
          description: "Test description",
        });

        await dbService.upsertCommand(command);

        const commands = await dbService.getAllCommands();
        expect(commands).toHaveLength(1);
        expect(commands[0].id).toBe("test-1");
        expect(commands[0].name).toBe("test-command");
        expect(commands[0].description).toBe("Test description");
      });

      it("should update existing command", async () => {
        const command = createMockCommand({
          id: "test-1",
          name: "test-command",
          description: "Original description",
        });

        await dbService.upsertCommand(command);

        // Update the command
        const updatedCommand = { ...command, description: "Updated description" };
        await dbService.upsertCommand(updatedCommand);

        const commands = await dbService.getAllCommands();
        expect(commands).toHaveLength(1);
        expect(commands[0].description).toBe("Updated description");
      });

      it("should validate command with Zod schema", async () => {
        const command = createMockCommand();
        await dbService.upsertCommand(command);

        const commands = await dbService.getAllCommands();
        const result = CommandModelSchema.safeParse(commands[0]);
        expect(result.success).toBe(true);
      });
    });

    describe("upsertCommands", () => {
      it("should insert multiple commands", async () => {
        const commands = [
          createMockCommand({ id: "cmd-1", name: "command-1" }),
          createMockCommand({ id: "cmd-2", name: "command-2" }),
        ];

        await dbService.upsertCommands(commands);

        const savedCommands = await dbService.getAllCommands();
        expect(savedCommands).toHaveLength(2);
        expect(savedCommands.map(c => c.id).sort()).toEqual(["cmd-1", "cmd-2"]);
      });

      it("should update existing commands", async () => {
        const commands = [
          createMockCommand({ id: "cmd-1", name: "command-1", description: "Original 1" }),
          createMockCommand({ id: "cmd-2", name: "command-2", description: "Original 2" }),
        ];

        await dbService.upsertCommands(commands);

        // Update the commands
        const updatedCommands = commands.map(cmd => ({
          ...cmd,
          description: `Updated: ${cmd.description}`,
        }));

        await dbService.upsertCommands(updatedCommands);

        const savedCommands = await dbService.getAllCommands();
        expect(savedCommands).toHaveLength(2);
        savedCommands.forEach(cmd => {
          expect(cmd.description).toContain("Updated:");
        });
      });
    });

    describe("getAllCommands", () => {
      it("should return empty array when no commands exist", async () => {
        const commands = await dbService.getAllCommands();
        expect(commands).toEqual([]);
      });

      it("should return all commands with ISO8601 dates", async () => {
        const testCommands = [
          createMockCommand({ id: "cmd-1" }),
          createMockCommand({ id: "cmd-2" }),
          createMockCommand({ id: "cmd-3" }),
        ];

        await dbService.upsertCommands(testCommands);

        const commands = await dbService.getAllCommands();
        expect(commands).toHaveLength(3);

        commands.forEach(cmd => {
          expect(cmd.lastUpdated).toBeInstanceOf(Date);
          expect(cmd.lastUpdated.toISOString()).toMatch(
            /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/
          );
        });
      });
    });
  });

  describe("personas", () => {
    describe("upsertPersona", () => {
      it.skip("should insert new persona", async () => {
        const persona = createMockPersona({
          id: "persona-1",
          name: "Test Persona",
          description: "Test description",
        });

        await dbService.upsertPersona(persona);

        const personas = await dbService.getAllPersonas();
        expect(personas).toHaveLength(1);
        expect(personas[0].id).toBe("persona-1");
        expect(personas[0].name).toBe("Test Persona");
      });

      it("should update existing persona", async () => {
        const persona = createMockPersona({
          id: "persona-1",
          name: "Test Persona",
          description: "Original description",
        });

        await dbService.upsertPersona(persona);

        // Update the persona
        const updatedPersona = { ...persona, description: "Updated description" };
        await dbService.upsertPersona(updatedPersona);

        const personas = await dbService.getAllPersonas();
        expect(personas).toHaveLength(1);
        expect(personas[0].description).toBe("Updated description");
      });

      it("should validate persona with Zod schema", async () => {
        const persona = createMockPersona();
        await dbService.upsertPersona(persona);

        const personas = await dbService.getAllPersonas();
        const result = PersonaModelSchema.safeParse(personas[0]);
        expect(result.success).toBe(true);
      });
    });

    describe("upsertPersonas", () => {
      it("should insert multiple personas", async () => {
        const personas = [
          createMockPersona({ id: "p-1", name: "Persona 1" }),
          createMockPersona({ id: "p-2", name: "Persona 2" }),
        ];

        await dbService.upsertPersonas(personas);

        const savedPersonas = await dbService.getAllPersonas();
        expect(savedPersonas).toHaveLength(2);
        expect(savedPersonas.map(p => p.id).sort()).toEqual(["p-1", "p-2"]);
      });
    });

    describe("getAllPersonas", () => {
      it("should return empty array when no personas exist", async () => {
        const personas = await dbService.getAllPersonas();
        expect(personas).toEqual([]);
      });
    });
  });

  describe("rules", () => {
    describe("upsertRules", () => {
      it("should insert new rules", async () => {
        const rules = createMockRules({
          id: "test-rules",
          rules: {
            rules: [{ name: "rule1", content: "Content 1" }],
          },
        });

        await dbService.upsertRules(rules);

        const savedRules = await dbService.getRules();
        expect(savedRules).not.toBeNull();
        expect(savedRules?.id).toBe("test-rules");
        expect(savedRules?.rules.rules).toHaveLength(1);
      });

      it("should update existing rules", async () => {
        const rules = createMockRules({
          id: "test-rules",
          rules: {
            rules: [{ name: "rule1", content: "Original content" }],
          },
        });

        await dbService.upsertRules(rules);

        // Update the rules
        const updatedRules = {
          ...rules,
          rules: {
            rules: [
              { name: "rule1", content: "Updated content" },
              { name: "rule2", content: "New rule" },
            ],
          },
        };

        await dbService.upsertRules(updatedRules);

        const savedRules = await dbService.getRules();
        expect(savedRules?.rules.rules).toHaveLength(2);
        expect(savedRules?.rules.rules[0].content).toBe("Updated content");
      });

      it("should validate rules with Zod schema", async () => {
        const rules = createMockRules();
        await dbService.upsertRules(rules);

        const savedRules = await dbService.getRules();
        const result = RulesModelSchema.safeParse(savedRules);
        expect(result.success).toBe(true);
      });
    });

    describe("getRules", () => {
      it("should return null when no rules exist", async () => {
        const rules = await dbService.getRules();
        expect(rules).toBeNull();
      });

      it("should return first rules entry", async () => {
        // Insert multiple rules
        await dbService.upsertRules(createMockRules({ id: "rules-1" }));
        await dbService.upsertRules(createMockRules({ id: "rules-2" }));

        const rules = await dbService.getRules();
        expect(rules).not.toBeNull();
        // Should return one of the rules (order not guaranteed)
        expect(["rules-1", "rules-2"]).toContain(rules?.id);
      });
    });
  });

  describe("sync metadata", () => {
    it("should update sync metadata", async () => {
      const now = new Date();
      await dbService.updateSyncMetadata("success", "All synced");

      // Read the database to get sync metadata
      await dbService["db"].read();
      const metadata = dbService["db"].data.syncMetadata;

      expect(metadata.syncStatus).toBe("success");
      expect(metadata.errorMessage).toBe("All synced");
      expect(new Date(metadata.lastSync).getTime()).toBeGreaterThanOrEqual(now.getTime());
    });
  });

  describe("clearAll", () => {
    it("should clear all data", async () => {
      // Add some data
      await dbService.upsertCommand(createMockCommand());
      await dbService.upsertPersona(createMockPersona());
      await dbService.upsertRules(createMockRules());

      // Clear all data
      await dbService.clearAll();

      // Verify everything is cleared
      const commands = await dbService.getAllCommands();
      const personas = await dbService.getAllPersonas();
      const rules = await dbService.getRules();

      expect(commands).toEqual([]);
      expect(personas).toEqual([]);
      expect(rules).toBeNull();
    });
  });

  describe("validate database schema", () => {
    it("should validate entire database with Zod schema", async () => {
      // Add some data
      await dbService.upsertCommands(getMockCommands());
      await dbService.upsertPersonas(getMockPersonas());
      await dbService.upsertRules(getMockRules());

      // Read the raw database
      await dbService["db"].read();
      const db = dbService["db"].data;

      // Validate with schema
      const result = DatabaseSchemaSchema.safeParse(db);
      if (!result.success) {
        console.error("Schema validation failed:", result.error.errors);
      }
      expect(result.success).toBe(true);
    });
  });
});
