import crypto from "crypto";
import { GitHubLoader } from "../github-loader.js";
import { DatabaseService } from "./database-service.js";
import { CommandModel, PersonaModel, RulesModel } from "../database.js";
import logger from "../logger.js";

export class SyncService {
  private syncInterval: NodeJS.Timer | null = null;
  private isSyncing = false;

  constructor(
    private readonly githubLoader: GitHubLoader,
    private readonly databaseService: DatabaseService,
    private readonly syncIntervalMinutes: number = 30
  ) {}

  private generateHash(content: string): string {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  private async syncCommands(): Promise<number> {
    const commands = await this.githubLoader.loadCommands();
    const commandModels: CommandModel[] = [];
    let updatedCount = 0;

    for (const command of commands) {
      const id = command.name;
      const hash = this.generateHash(JSON.stringify(command));
      
      const existing = (await this.databaseService.getAllCommands()).find(c => c.id === id);
      
      if (!existing || existing.hash !== hash) {
        commandModels.push({
          ...command,
          id,
          hash,
          lastUpdated: new Date()
        });
        updatedCount++;
      }
    }

    if (commandModels.length > 0) {
      await this.databaseService.upsertCommands(commandModels);
    }

    return updatedCount;
  }

  private async syncPersonas(): Promise<number> {
    const personas = await this.githubLoader.loadPersonas();
    const personaModels: PersonaModel[] = [];
    let updatedCount = 0;

    for (const [key, persona] of Object.entries(personas)) {
      const id = key;
      const hash = this.generateHash(JSON.stringify(persona));
      
      const existing = (await this.databaseService.getAllPersonas()).find(p => p.id === id);
      
      if (!existing || existing.hash !== hash) {
        personaModels.push({
          ...persona,
          id,
          hash,
          lastUpdated: new Date()
        });
        updatedCount++;
      }
    }

    if (personaModels.length > 0) {
      await this.databaseService.upsertPersonas(personaModels);
    }

    return updatedCount;
  }

  private async syncRules(): Promise<boolean> {
    const rules = await this.githubLoader.loadRules();
    const id = 'superclaude-rules';
    const hash = this.generateHash(JSON.stringify(rules));
    
    const existing = await this.databaseService.getRules();
    
    if (!existing || existing.hash !== hash) {
      const rulesModel: RulesModel = {
        id,
        rules,
        hash,
        lastUpdated: new Date()
      };
      
      await this.databaseService.upsertRules(rulesModel);
      return true;
    }

    return false;
  }

  async syncFromGitHub(): Promise<void> {
    if (this.isSyncing) {
      logger.warn("Sync already in progress, skipping");
      return;
    }

    this.isSyncing = true;
    const startTime = Date.now();

    try {
      logger.info("Starting GitHub sync");

      const [commandsUpdated, personasUpdated, rulesUpdated] = await Promise.all([
        this.syncCommands(),
        this.syncPersonas(),
        this.syncRules()
      ]);

      await this.databaseService.updateSyncMetadata('success');

      const duration = Date.now() - startTime;
      logger.info({
        commandsUpdated,
        personasUpdated,
        rulesUpdated,
        durationMs: duration
      }, "GitHub sync completed successfully");

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      await this.databaseService.updateSyncMetadata('failed', errorMessage);
      
      logger.error({ error, durationMs: Date.now() - startTime }, "GitHub sync failed");
      throw error;
    } finally {
      this.isSyncing = false;
    }
  }

  async loadFromDatabase(): Promise<{
    commands: CommandModel[];
    personas: Record<string, PersonaModel>;
    rules: RulesModel | null;
  }> {
    const commands = await this.databaseService.getAllCommands();
    const personasList = await this.databaseService.getAllPersonas();
    const rules = await this.databaseService.getRules();

    const personas: Record<string, PersonaModel> = {};
    for (const persona of personasList) {
      personas[persona.id] = persona;
    }

    return { commands, personas, rules };
  }

  startPeriodicSync(): void {
    if (this.syncInterval) {
      logger.warn("Periodic sync already started");
      return;
    }

    const intervalMs = this.syncIntervalMinutes * 60 * 1000;
    
    this.syncInterval = setInterval(async () => {
      try {
        await this.syncFromGitHub();
      } catch (error) {
        logger.error({ error }, "Periodic sync failed");
      }
    }, intervalMs);

    logger.info({ intervalMinutes: this.syncIntervalMinutes }, "Started periodic GitHub sync");
  }

  stopPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
      logger.info("Stopped periodic GitHub sync");
    }
  }
}