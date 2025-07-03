import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import logger from "@logger";
import { GitHubLoader } from "@/github-loader.js";
import { DatabaseService } from "@services/database-service.js";
import { SyncService } from "@services/sync-service.js";
import { SuperClaudeCommand, Persona } from "@types";
import { CommandModel, PersonaModel } from "@database";
import { createMCPServer } from "@/mcp.js";

class SuperClaudeMCPServer {
  private githubLoader = new GitHubLoader();
  private databaseService = new DatabaseService();
  private syncService: SyncService;
  private personas: Record<string, Persona> = {};
  private commands: SuperClaudeCommand[] = [];
  private rules: any = {};

  constructor() {
    this.syncService = new SyncService(this.githubLoader, this.databaseService);
    this.initialize();
  }

  private async initialize() {
    try {
      // Initialize database
      await this.databaseService.initialize();

      // Try to load from database first
      const dbData = await this.syncService.loadFromDatabase();

      if (
        dbData.commands.length === 0 &&
        dbData.personas &&
        Object.keys(dbData.personas).length === 0
      ) {
        // Database is empty, do initial sync
        logger.info("Database empty, performing initial sync from GitHub");
        await this.syncService.syncFromGitHub();
        await this.loadFromDatabase();
      } else {
        // Load from database
        await this.loadFromDatabase();

        // Check if we need to sync (if last sync was more than 30 minutes ago and auto sync is enabled)
        const autoSyncEnabled = process.env.SC_AUTO_SYNC_ENABLED === "true";
        if (autoSyncEnabled) {
          const lastSync = await this.databaseService.getLastSync();
          const timeSinceLastSync = Date.now() - lastSync.getTime();
          if (timeSinceLastSync > 30 * 60 * 1000) {
            logger.info("Last sync was more than 30 minutes ago, syncing from GitHub");
            this.syncService.syncFromGitHub().catch(error => {
              logger.error({ error }, "Background sync failed");
            });
          }
        }
      }

      // Start periodic sync if enabled
      const autoSyncEnabled = process.env.SC_AUTO_SYNC_ENABLED === "true";
      if (autoSyncEnabled) {
        logger.info("Auto sync is enabled, starting periodic sync");
        this.syncService.startPeriodicSync();
      } else {
        logger.info("Auto sync is disabled (set SC_AUTO_SYNC_ENABLED=true to enable)");
      }
    } catch (error) {
      logger.error({ error }, "Failed to initialize server");
    }
  }

  async triggerSync(): Promise<void> {
    await this.syncService.syncFromGitHub();
    await this.loadFromDatabase();
  }

  private async loadFromDatabase() {
    try {
      const { commands, personas, rules } = await this.syncService.loadFromDatabase();

      // Convert CommandModel[] to SuperClaudeCommand[]
      this.commands = commands.map(cmd => ({
        name: cmd.name,
        description: cmd.description,
        prompt: cmd.prompt,
        messages: cmd.messages,
        arguments: cmd.arguments,
      }));

      // Convert PersonaModel record to Persona record
      this.personas = {};
      for (const [id, personaModel] of Object.entries(personas)) {
        this.personas[id] = {
          name: personaModel.name,
          description: personaModel.description,
          instructions: personaModel.instructions,
        };
      }

      this.rules = rules?.rules || {};

      // Count rules
      let rulesCount = 0;
      if (rules?.rules?.rules) {
        rulesCount = rules.rules.rules.length;
      }

      logger.info(
        {
          commandsCount: this.commands.length,
          personasCount: Object.keys(this.personas).length,
          rulesCount,
        },
        "Successfully loaded data from database"
      );
    } catch (error) {
      logger.error({ error }, "Failed to load data from database");
    }
  }

  createInstance(): McpServer {
    return createMCPServer(
      this.commands,
      this.personas,
      this.rules,
      this.githubLoader,
      this.triggerSync.bind(this)
    );
  }
}

const serverInstance = new SuperClaudeMCPServer();
export default serverInstance;
