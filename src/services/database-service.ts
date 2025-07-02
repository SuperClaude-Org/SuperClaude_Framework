import { Low } from "lowdb";
import { JSONFile } from "lowdb/node";
import path from "path";
import { DatabaseSchema, DEFAULT_DATABASE_SCHEMA, CommandModel, PersonaModel, RulesModel } from "../database.js";
import logger from "../logger.js";

export class DatabaseService {
  private db: Low<DatabaseSchema>;
  private initialized: boolean = false;

  constructor(private readonly dbPath: string = path.join(process.cwd(), 'data', 'superclaude.json')) {}

  async initialize(): Promise<void> {
    if (this.initialized) return;

    try {
      const adapter = new JSONFile<DatabaseSchema>(this.dbPath);
      this.db = new Low(adapter, DEFAULT_DATABASE_SCHEMA);
      
      await this.db.read();
      
      // LowDB sets data to the default if file doesn't exist
      // Always write to ensure file is created
      await this.db.write();
      
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

  async upsertRules(rules: RulesModel): Promise<void> {
    this.ensureInitialized();
    
    const index = this.db.data!.rules.findIndex(r => r.id === rules.id);
    if (index >= 0) {
      this.db.data!.rules[index] = rules;
    } else {
      this.db.data!.rules.push(rules);
    }
    
    await this.db.write();
    logger.debug({ rulesId: rules.id }, "Rules upserted");
  }

  async getAllCommands(): Promise<CommandModel[]> {
    this.ensureInitialized();
    await this.db.read();
    return (this.db.data!.commands || []).map(cmd => ({
      ...cmd,
      lastUpdated: new Date(cmd.lastUpdated)
    }));
  }

  async getAllPersonas(): Promise<PersonaModel[]> {
    this.ensureInitialized();
    await this.db.read();
    return (this.db.data!.personas || []).map(persona => ({
      ...persona,
      lastUpdated: new Date(persona.lastUpdated)
    }));
  }

  async getRules(): Promise<RulesModel | null> {
    this.ensureInitialized();
    await this.db.read();
    const rules = this.db.data!.rules || [];
    if (rules.length > 0) {
      return {
        ...rules[0],
        lastUpdated: new Date(rules[0].lastUpdated)
      };
    }
    return null;
  }

  async getLastSync(): Promise<Date> {
    this.ensureInitialized();
    await this.db.read();
    return new Date(this.db.data!.syncMetadata.lastSync);
  }

  async updateSyncMetadata(status: 'success' | 'failed', errorMessage?: string): Promise<void> {
    this.ensureInitialized();
    
    this.db.data!.syncMetadata = {
      lastSync: new Date(),
      syncStatus: status,
      errorMessage
    };
    
    await this.db.write();
    logger.info({ status, errorMessage }, "Sync metadata updated");
  }

  async clearAll(): Promise<void> {
    this.ensureInitialized();
    
    this.db.data = DEFAULT_DATABASE_SCHEMA;
    await this.db.write();
    logger.info("Database cleared");
  }
}