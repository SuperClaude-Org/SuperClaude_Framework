import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListResourceTemplatesRequestSchema
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import logger from "./logger.js";
import { GitHubLoader } from "./github-loader.js";
import { DatabaseService } from "./services/database-service.js";
import { SyncService } from "./services/sync-service.js";
import { SuperClaudeCommand, Persona } from "./types.js";
import { CommandModel, PersonaModel } from "./database.js";

class SuperClaudeMCPServer {
  private githubLoader = new GitHubLoader();
  private databaseService = new DatabaseService();
  private syncService: SyncService;
  private currentPersona: string | null = null;
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
      
      if (dbData.commands.length === 0 && dbData.personas && Object.keys(dbData.personas).length === 0) {
        // Database is empty, do initial sync
        logger.info("Database empty, performing initial sync from GitHub");
        await this.syncService.syncFromGitHub();
        await this.loadFromDatabase();
      } else {
        // Load from database
        await this.loadFromDatabase();
        
        // Check if we need to sync (if last sync was more than 30 minutes ago and auto sync is enabled)
        const autoSyncEnabled = process.env.SC_AUTO_SYNC_ENABLED === 'true';
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
      const autoSyncEnabled = process.env.SC_AUTO_SYNC_ENABLED === 'true';
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

  private async loadFromDatabase() {
    try {
      const { commands, personas, rules } = await this.syncService.loadFromDatabase();
      
      // Convert CommandModel[] to SuperClaudeCommand[]
      this.commands = commands.map(cmd => ({
        name: cmd.name,
        description: cmd.description,
        prompt: cmd.prompt,
        messages: cmd.messages,
        arguments: cmd.arguments
      }));
      
      // Convert PersonaModel record to Persona record
      this.personas = {};
      for (const [id, personaModel] of Object.entries(personas)) {
        this.personas[id] = {
          name: personaModel.name,
          description: personaModel.description,
          instructions: personaModel.instructions
        };
      }
      
      this.rules = rules?.rules || {};
      
      logger.info({
        commandsCount: this.commands.length,
        personasCount: Object.keys(this.personas).length,
        hasRules: !!rules
      }, "Successfully loaded data from database");
    } catch (error) {
      logger.error({ error }, "Failed to load data from database");
    }
  }

  createInstance() {
    const server = new McpServer({
      name: "superclaude-mcp",
      version: "1.0.0",
      description: "MCP server exposing SuperClaude commands as prompts",
    }, {
      capabilities: {
        prompts: {},
        tools: {},
        resources: {}
      }
    });

    // Register tool for switching persona
    server.tool(
      "assume-persona",
      "Switch the current SuperClaude persona",
      {
        persona: z.string().describe("The name of the persona to assume"),
      },
      async ({ persona }) => {
        logger.info({ persona, previous: this.currentPersona }, "Switching persona");
        
        if (!this.personas[persona]) {
          return {
            content: [{
              type: "text",
              text: JSON.stringify({
                success: false,
                error: `Persona '${persona}' not found. Available personas: ${Object.keys(this.personas).join(", ")}`
              })
            }]
          };
        }

        this.currentPersona = persona;
        
        if ('notification' in server && typeof server.notification === 'function') {
          server.notification({
          method: "superclaude/personaChanged",
          params: {
            persona,
            details: this.personas[persona]
          }
          });
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              success: true,
              persona,
              details: this.personas[persona]
            })
          }]
        };
      }
    );

    // Get the low-level server instance for registering handlers
    const lowLevelServer = server.server;

    // List available prompts
    lowLevelServer.setRequestHandler(ListPromptsRequestSchema, async () => {
      return {
        prompts: this.commands.map(cmd => ({
          name: cmd.name,
          description: cmd.description,
          arguments: cmd.arguments
        }))
      };
    });

    // Get specific prompt by name
    lowLevelServer.setRequestHandler(GetPromptRequestSchema, async (request) => {
      const commandName = request.params.name;
      const args = request.params.arguments as Record<string, string> | undefined;
      const command = this.commands.find(cmd => cmd.name === commandName);
      
      if (!command) {
        throw new Error(`Prompt not found: ${commandName}`);
      }

      let content = command.prompt;
      
      // Process @include directives
      const includeMatches = content.match(/@include\s+[\w\-\/\.]+/g);
      if (includeMatches) {
        const includeContents = await this.githubLoader.loadSharedIncludes(includeMatches);
        for (const match of includeMatches) {
          content = content.replace(match, includeContents);
        }
      }
      
      // Replace argument placeholders
      if (command.arguments && args) {
        for (const arg of command.arguments) {
          const argValue = args[arg.name];
          if (argValue) {
            content = content.replace(new RegExp(`\\$${arg.name}`, 'g'), argValue);
          }
        }
      }

      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: content
          }
        }]
      };
    });

    lowLevelServer.setRequestHandler(ListResourceTemplatesRequestSchema, async () => {
      return {
        resourceTemplates: [
          {
            uriTemplate: "superclaude://personas/{personaId}",
            name: "SuperClaude Persona",
            description: "Access a specific SuperClaude persona by ID",
            mimeType: "application/json"
          },
          {
            uriTemplate: "superclaude://rules/{ruleId}",
            name: "SuperClaude Rule",
            description: "Access a specific SuperClaude rule by name",
            mimeType: "application/json"
          }
        ]
      };
    });

    // List available resources
    lowLevelServer.setRequestHandler(ListResourcesRequestSchema, async () => {
      const resources = [];
      
      // Add individual rule resources
      if (this.rules && this.rules.rules) {
        const rulesList = Array.isArray(this.rules.rules) ? this.rules.rules : 
                         (this.rules.rules.rules || []);
        
        for (const rule of rulesList) {
          resources.push({
            uri: `superclaude://rules/${encodeURIComponent(rule.name)}`,
            name: rule.name,
            description: rule.content.substring(0, 100) + (rule.content.length > 100 ? '...' : ''),
            mimeType: "application/json"
          });
        }
      }
      
      // Add persona resources
      for (const [personaId, persona] of Object.entries(this.personas)) {
        resources.push({
          uri: `superclaude://personas/${personaId}`,
          name: persona.name,
          description: persona.description,
          mimeType: "application/json"
        });
      }
      
      return { resources };
    });

    // Read specific resource
    lowLevelServer.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const uri = request.params.uri;
      
      // Handle individual rule resources
      const ruleMatch = uri.match(/^superclaude:\/\/rules\/(.+)$/);
      if (ruleMatch) {
        const ruleId = decodeURIComponent(ruleMatch[1]);
        
        if (!this.rules || !this.rules.rules) {
          throw new Error("Rules not loaded");
        }
        
        const rulesList = Array.isArray(this.rules.rules) ? this.rules.rules : 
                         (this.rules.rules.rules || []);
        const rule = rulesList.find((r: {name: string; content: string}) => r.name === ruleId);
        
        if (!rule) {
          throw new Error(`Rule resource not found: ${ruleId}`);
        }
        
        return {
          contents: [{
            uri,
            mimeType: "application/json",
            text: JSON.stringify({
              name: rule.name,
              content: rule.content
            }, null, 2)
          }]
        };
      }
      
      // Handle persona resources
      const personaMatch = uri.match(/^superclaude:\/\/personas\/(.+)$/);
      if (personaMatch) {
        const personaId = personaMatch[1];
        const persona = this.personas[personaId];
        
        if (!persona) {
          throw new Error(`Persona resource not found: ${personaId}`);
        }
        
        return {
          contents: [{
            uri,
            mimeType: "application/json",
            text: JSON.stringify({
              id: personaId,
              ...persona
            }, null, 2)
          }]
        };
      }
      
      throw new Error(`Resource not found: ${uri}`);
    });

    return server;
  }
}

const serverInstance = new SuperClaudeMCPServer();
export default serverInstance;