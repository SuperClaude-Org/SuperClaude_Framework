import { Low, Memory } from "lowdb";
import { JSONFile } from "lowdb/node";
import path from "path";
import fs from "fs/promises";
import {
  DatabaseSchema,
  DEFAULT_DATABASE_SCHEMA,
  CommandModel,
  PersonaModel,
  RuleModel,
} from "@database";
import logger from "@logger";

export class DatabaseService {
  private db: Low<DatabaseSchema>;
  private initialized: boolean = false;

  constructor(
    private readonly dbPath: string = path.join(process.cwd(), "data", "superclaude.json"),
    private readonly adapter?: JSONFile<DatabaseSchema> | Memory<DatabaseSchema>
  ) {}

  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      let adapterToUse: JSONFile<DatabaseSchema> | Memory<DatabaseSchema>;

      if (this.adapter) {
        // Use provided adapter (e.g., for testing)
        adapterToUse = this.adapter;
      } else {
        // Use file adapter for production
        // Ensure the directory exists
        const dbDir = path.dirname(this.dbPath);
        try {
          await fs.access(dbDir);
        } catch (error) {
          // If using default path, create the directory
          if (this.dbPath === path.join(process.cwd(), "data", "superclaude.json")) {
            await fs.mkdir(dbDir, { recursive: true });
            logger.info({ dbDir }, "Created database directory");
          } else {
            // For custom paths (like tests), create the directory too
            await fs.mkdir(dbDir, { recursive: true });
            logger.debug({ dbDir }, "Created test database directory");
          }
        }
        adapterToUse = new JSONFile<DatabaseSchema>(this.dbPath);
      }

      this.db = new Low(adapterToUse, DEFAULT_DATABASE_SCHEMA());

      await this.db.read();

      // LowDB sets data to the default if file doesn't exist
      // Always write to ensure file is created (only for file adapters)
      if (!this.adapter) {
        await this.db.write();
      }

      this.initialized = true;
      logger.info({ dbPath: this.dbPath }, "Database initialized");
    } catch (error) {
      logger.error({ error, dbPath: this.dbPath }, "Failed to initialize database");
      throw error;
    }
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Error("Database not initialized. Call initialize() first.");
    }
  }

  async upsertCommand(command: CommandModel): Promise<void> {
    this.ensureInitialized();

    const index = this.db.data!.commands.findIndex(c => c.id === command.id);
    if (index >= 0) {
      this.db.data!.commands[index] = command;
    } else {
      this.db.data!.commands.push(command);
    }

    await this.db.write();
    logger.debug({ commandId: command.id }, "Command upserted");
  }

  async upsertCommands(commands: CommandModel[]): Promise<void> {
    this.ensureInitialized();

    // Read latest data before modifying
    await this.db.read();

    for (const command of commands) {
      const index = this.db.data!.commands.findIndex(c => c.id === command.id);
      if (index >= 0) {
        this.db.data!.commands[index] = command;
      } else {
        this.db.data!.commands.push(command);
      }
    }

    await this.db.write();
    logger.debug({ count: commands.length }, "Commands upserted");
  }

  async upsertPersona(persona: PersonaModel): Promise<void> {
    this.ensureInitialized();

    const index = this.db.data!.personas.findIndex(p => p.id === persona.id);
    if (index >= 0) {
      this.db.data!.personas[index] = persona;
    } else {
      this.db.data!.personas.push(persona);
    }

    await this.db.write();
    logger.debug({ personaId: persona.id }, "Persona upserted");
  }

  async upsertPersonas(personas: PersonaModel[]): Promise<void> {
    this.ensureInitialized();

    // Read latest data before modifying
    await this.db.read();

    for (const persona of personas) {
      const index = this.db.data!.personas.findIndex(p => p.id === persona.id);
      if (index >= 0) {
        this.db.data!.personas[index] = persona;
      } else {
        this.db.data!.personas.push(persona);
      }
    }

    await this.db.write();
    logger.debug({ count: personas.length }, "Personas upserted");
  }

  async upsertRule(rule: RuleModel): Promise<void> {
    this.ensureInitialized();

    // Read latest data before modifying
    await this.db.read();

    const index = this.db.data!.rules.findIndex(r => r.id === rule.id);
    if (index >= 0) {
      this.db.data!.rules[index] = rule;
    } else {
      this.db.data!.rules.push(rule);
    }

    await this.db.write();
    logger.debug({ ruleId: rule.id }, "Rule upserted");
  }

  async upsertRules(rules: RuleModel[]): Promise<void> {
    this.ensureInitialized();

    // Read latest data before modifying
    await this.db.read();

    for (const rule of rules) {
      const index = this.db.data!.rules.findIndex(r => r.id === rule.id);
      if (index >= 0) {
        this.db.data!.rules[index] = rule;
      } else {
        this.db.data!.rules.push(rule);
      }
    }

    await this.db.write();
    logger.debug({ count: rules.length }, "Rules upserted");
  }

  async getAllCommands(): Promise<CommandModel[]> {
    this.ensureInitialized();
    await this.db.read();
    return (this.db.data!.commands || []).map(cmd => ({
      ...cmd,
      lastUpdated: new Date(cmd.lastUpdated),
    }));
  }

  async getAllPersonas(): Promise<PersonaModel[]> {
    this.ensureInitialized();
    await this.db.read();
    return (this.db.data!.personas || []).map(persona => ({
      ...persona,
      lastUpdated: new Date(persona.lastUpdated),
    }));
  }

  async getAllRules(): Promise<RuleModel[]> {
    this.ensureInitialized();
    await this.db.read();
    return (this.db.data!.rules || []).map(rule => ({
      ...rule,
      lastUpdated: new Date(rule.lastUpdated),
    }));
  }

  async getLastSync(): Promise<Date> {
    this.ensureInitialized();
    await this.db.read();
    return new Date(this.db.data!.syncMetadata.lastSync);
  }

  async updateSyncMetadata(status: "success" | "failed", errorMessage?: string): Promise<void> {
    this.ensureInitialized();

    this.db.data!.syncMetadata = {
      lastSync: new Date(),
      syncStatus: status,
      errorMessage,
    };

    await this.db.write();
    logger.info({ status, errorMessage }, "Sync metadata updated");
  }

  async clearAll(): Promise<void> {
    this.ensureInitialized();

    this.db.data = DEFAULT_DATABASE_SCHEMA();
    await this.db.write();
    logger.info("Database cleared");
  }

  async close(): Promise<void> {
    if (this.initialized && this.db) {
      // Ensure all pending writes are completed
      await this.db.write();
      this.initialized = false;
      logger.debug("Database connection closed");
    }
  }
}
