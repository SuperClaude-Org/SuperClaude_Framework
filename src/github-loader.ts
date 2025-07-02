import axios from "axios";
import yaml from "js-yaml";
import logger from "./logger.js";
import { SuperClaudeCommand, Persona, SuperClaudeRules } from "./types.js";

const GITHUB_BASE_URL = "https://raw.githubusercontent.com/NomenAK/SuperClaude/master";

export class GitHubLoader {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private cacheTTL = 5 * 60 * 1000; // 5 minutes

  private async fetchFromGitHub(path: string): Promise<string> {
    const cacheKey = path;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      logger.debug({ path }, "Using cached GitHub content");
      return cached.data;
    }

    try {
      const url = `${GITHUB_BASE_URL}${path}`;
      logger.debug({ url }, "Fetching from GitHub");
      const response = await axios.get(url, { 
        headers: {
          'Accept': 'text/plain'
        }
      });
      
      this.cache.set(cacheKey, { data: response.data, timestamp: Date.now() });
      return response.data;
    } catch (error) {
      logger.error({ error, path }, "Failed to fetch from GitHub");
      throw error;
    }
  }

  async loadCommands(): Promise<SuperClaudeCommand[]> {
    try {
      const commandsListUrl = "https://api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands";
      const response = await axios.get(commandsListUrl, {
        headers: {
          'Accept': 'application/vnd.github.v3+json'
        }
      });

      const commands: SuperClaudeCommand[] = [];
      
      for (const file of response.data) {
        if (file.name.endsWith('.md') && file.type === 'file') {
          try {
            const content = await this.fetchFromGitHub(`/.claude/commands/${file.name}`);
            const name = file.name.replace('.md', '');
            
            // Parse arguments from content (look for $ARGUMENTS)
            const argumentMatches = content.match(/\$ARGUMENTS/g);
            const commandArguments = argumentMatches ? ['arguments'] : undefined;
            
            commands.push({
              name,
              content,
              arguments: commandArguments
            });
          } catch (error) {
            logger.error({ error, file: file.name }, "Failed to load command");
          }
        }
      }

      logger.info({ count: commands.length }, "Loaded SuperClaude commands");
      return commands;
    } catch (error) {
      logger.error({ error }, "Failed to load commands list");
      return [];
    }
  }

  async loadPersonas(): Promise<Record<string, Persona>> {
    try {
      const content = await this.fetchFromGitHub("/.claude/shared/superclaude-personas.yml");
      const data = yaml.load(content) as any;
      
      const personas: Record<string, Persona> = {};
      
      if (data.personas) {
        for (const [key, value] of Object.entries(data.personas)) {
          personas[key] = {
            name: key,
            ...(value as any)
          };
        }
      }
      
      logger.info({ count: Object.keys(personas).length }, "Loaded personas");
      return personas;
    } catch (error) {
      logger.error({ error }, "Failed to load personas");
      return {};
    }
  }

  async loadRules(): Promise<SuperClaudeRules> {
    try {
      const content = await this.fetchFromGitHub("/.claude/shared/superclaude-rules.yml");
      const rules = yaml.load(content) as SuperClaudeRules;
      
      logger.info("Loaded SuperClaude rules");
      return rules;
    } catch (error) {
      logger.error({ error }, "Failed to load rules");
      return {};
    }
  }

  async loadSharedIncludes(includes: string[]): Promise<string> {
    const contents: string[] = [];
    
    for (const include of includes) {
      try {
        const path = include.startsWith('@include') 
          ? include.replace('@include ', '').trim()
          : include;
          
        const fullPath = path.startsWith('/') ? path : `/.claude/commands/shared/${path}`;
        const content = await this.fetchFromGitHub(fullPath);
        contents.push(content);
      } catch (error) {
        logger.warn({ error, include }, "Failed to load include");
      }
    }
    
    return contents.join('\n\n');
  }
}