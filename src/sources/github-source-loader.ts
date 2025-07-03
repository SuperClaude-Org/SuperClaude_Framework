import axios from "axios";
import yaml from "js-yaml";
import logger from "@/logger.js";
import { Command, Persona } from "@/schemas.js";
import { SuperClaudeRules } from "@types";
import { ISourceLoader } from "./interfaces.js";

const GITHUB_BASE_URL = "https://raw.githubusercontent.com/NomenAK/SuperClaude/master";

/**
 * Sanitizes error objects to remove large buffer content while preserving useful debug info
 */
function sanitizeError(error: any) {
  if (!error) return error;

  // For YAML parsing errors, extract only essential information
  if (error.name === "YAMLException" || error.reason) {
    return {
      name: error.name,
      reason: error.reason,
      message: error.message,
      line: error.mark?.line,
      column: error.mark?.column,
      snippet: error.mark?.snippet,
    };
  }

  // For other errors, just return name and message
  return {
    name: error.name,
    message: error.message,
    code: error.code,
    status: error.status,
  };
}

export class GitHubSourceLoader implements ISourceLoader {
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
          Accept: "text/plain",
        },
      });

      this.cache.set(cacheKey, { data: response.data, timestamp: Date.now() });
      return response.data;
    } catch (error) {
      logger.error({ error: sanitizeError(error), path }, "Failed to fetch from GitHub");
      throw error;
    }
  }

  async loadCommands(): Promise<Command[]> {
    try {
      const commandsListUrl =
        "https://api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands";
      const response = await axios.get(commandsListUrl, {
        headers: {
          Accept: "application/vnd.github.v3+json",
        },
      });

      const commands: Command[] = [];

      for (const file of response.data) {
        if (file.name.endsWith(".md") && file.type === "file") {
          try {
            const content = await this.fetchFromGitHub(`/.claude/commands/${file.name}`);
            const name = file.name.replace(".md", "");

            // Extract description from Purpose line
            const purposeMatch = content.match(/\*\*Purpose\*\*:\s*(.+)/);
            const description = purposeMatch ? purposeMatch[1].trim() : `Command: ${name}`;

            // The entire content is the prompt
            const prompt = content;

            // Parse arguments from content (look for $ARGUMENTS or specific argument patterns)
            const argumentMatches = content.match(/\$([A-Z_]+)/g);
            const uniqueArgNames = argumentMatches
              ? [...new Set(argumentMatches.map(arg => arg.replace("$", "")))]
              : [];

            const commandArguments =
              uniqueArgNames.length > 0
                ? uniqueArgNames.map(argName => ({
                    name: argName,
                    description: `Argument: $${argName}`,
                    required: true,
                  }))
                : undefined;

            commands.push({
              name,
              description,
              prompt,
              arguments: commandArguments,
            });
          } catch (error) {
            logger.error(
              { error: sanitizeError(error), file: file.name },
              "Failed to load command"
            );
          }
        }
      }

      logger.info({ count: commands.length }, "Loaded SuperClaude commands");
      return commands;
    } catch (error) {
      logger.error({ error: sanitizeError(error) }, "Failed to load commands list");
      return [];
    }
  }

  async loadPersonas(): Promise<Persona[]> {
    try {
      const content = await this.fetchFromGitHub("/.claude/shared/superclaude-personas.yml");

      // Use safe loader with duplicate key handling
      const data = yaml.load(content, {
        schema: yaml.JSON_SCHEMA,
        onWarning: warning => {
          logger.warn({ warning: warning.toString() }, "YAML warning while loading personas");
        },
      }) as any;

      const personas: Persona[] = [];

      // Look for All_Personas section
      const personasData = data?.All_Personas || data?.personas || data;

      if (personasData && typeof personasData === "object") {
        for (const [key, value] of Object.entries(personasData)) {
          if (typeof value === "object" && value !== null) {
            const persona = value as any;
            personas.push({
              name: persona.Identity || key,
              description: persona.Core_Belief || `${key} persona`,
              instructions: [
                persona.Identity || "",
                persona.Core_Belief || "",
                persona.Problem_Solving || "",
                persona.Focus || "",
              ]
                .filter(Boolean)
                .join(". "),
            });
          }
        }
      }

      logger.info({ count: personas.length }, "Loaded personas");
      return personas;
    } catch (error) {
      logger.error({ error: sanitizeError(error) }, "Failed to load personas");

      // If YAML parsing fails due to duplicate keys, try a simple regex approach
      try {
        const content = await this.fetchFromGitHub("/.claude/shared/superclaude-personas.yml");
        return this.parsePersonasManually(content);
      } catch (fallbackError) {
        logger.error(
          { error: sanitizeError(fallbackError) },
          "Fallback persona parsing also failed"
        );
        return [];
      }
    }
  }

  private parsePersonasManually(content: string): Persona[] {
    const personas: Persona[] = [];

    // Simple regex to extract persona blocks
    const personaBlocks = content.match(/^[a-zA-Z_]+:\s*\n(?:  .+\n)+/gm);

    if (personaBlocks) {
      for (const block of personaBlocks) {
        const lines = block.split("\n").filter(line => line.trim());
        const personaKey = lines[0].replace(":", "").trim();

        let identity = "";
        let coreBelief = "";
        let problemSolving = "";
        let focus = "";

        for (const line of lines.slice(1)) {
          if (line.includes("Identity:")) {
            identity = line.split("Identity:")[1].trim().replace(/"/g, "");
          } else if (line.includes("Core_Belief:")) {
            coreBelief = line.split("Core_Belief:")[1].trim().replace(/"/g, "");
          } else if (line.includes("Problem_Solving:")) {
            problemSolving = line.split("Problem_Solving:")[1].trim().replace(/"/g, "");
          } else if (line.includes("Focus:")) {
            focus = line.split("Focus:")[1].trim().replace(/"/g, "");
          }
        }

        if (identity || coreBelief) {
          personas.push({
            name: identity || personaKey,
            description: coreBelief || `${personaKey} persona`,
            instructions: [identity, coreBelief, problemSolving, focus].filter(Boolean).join(". "),
          });
        }
      }
    }

    logger.info({ count: personas.length }, "Loaded personas using manual parsing");
    return personas;
  }

  async loadRules(): Promise<SuperClaudeRules> {
    try {
      const content = await this.fetchFromGitHub("/.claude/shared/superclaude-rules.yml");

      // Use safe loader with duplicate key handling
      const data = yaml.load(content, {
        schema: yaml.JSON_SCHEMA,
        onWarning: warning => {
          logger.warn({ warning: warning.toString() }, "YAML warning while loading rules");
        },
      }) as any;

      // Convert the YAML structure to our expected format
      const rules: Array<{ name: string; content: string }> = [];

      // Recursively extract rules from the YAML structure
      const extractRules = (obj: any, prefix = ""): void => {
        if (typeof obj === "string") {
          rules.push({
            name: prefix,
            content: obj,
          });
        } else if (typeof obj === "object" && obj !== null) {
          for (const [key, value] of Object.entries(obj)) {
            const newPrefix = prefix ? `${prefix}.${key}` : key;
            extractRules(value, newPrefix);
          }
        }
      };

      extractRules(data);

      logger.info({ count: rules.length }, "Loaded SuperClaude rules");
      return { rules };
    } catch (error) {
      logger.error({ error: sanitizeError(error) }, "Failed to load rules");

      // If YAML parsing fails, try a simple approach
      try {
        const content = await this.fetchFromGitHub("/.claude/shared/superclaude-rules.yml");
        return this.parseRulesManually(content);
      } catch (fallbackError) {
        logger.error({ error: sanitizeError(fallbackError) }, "Fallback rules parsing also failed");
        return { rules: [] };
      }
    }
  }

  private parseRulesManually(content: string): SuperClaudeRules {
    const rules: Array<{ name: string; content: string }> = [];

    // Split by sections (lines that start with no indentation and end with ':')
    const lines = content.split("\n");
    let currentSection = "";
    let currentContent: string[] = [];

    for (const line of lines) {
      // Skip comments and empty lines
      if (line.trim().startsWith("#") || !line.trim()) continue;

      // Check if this is a new section (no leading spaces and ends with ':')
      if (line.match(/^[A-Za-z_]+.*:/) && !line.startsWith(" ")) {
        // Save previous section if exists
        if (currentSection && currentContent.length > 0) {
          rules.push({
            name: currentSection,
            content: currentContent.join(" ").trim(),
          });
        }

        currentSection = line.replace(":", "").trim();
        currentContent = [];
      } else if (currentSection && line.trim()) {
        // Add content to current section
        currentContent.push(line.trim());
      }
    }

    // Don't forget the last section
    if (currentSection && currentContent.length > 0) {
      rules.push({
        name: currentSection,
        content: currentContent.join(" ").trim(),
      });
    }

    logger.info({ count: rules.length }, "Loaded rules using manual parsing");
    return { rules };
  }

  clearCache(): void {
    this.cache.clear();
    logger.debug("GitHub loader cache cleared");
  }

  async loadSharedIncludes(includes: string[]): Promise<string> {
    const contents: string[] = [];

    for (const include of includes) {
      try {
        const path = include.startsWith("@include")
          ? include.replace("@include ", "").trim()
          : include;

        const fullPath = path.startsWith("/") ? path : `/.claude/commands/shared/${path}`;
        const content = await this.fetchFromGitHub(fullPath);
        contents.push(content);
      } catch (error) {
        logger.warn({ error, include }, "Failed to load include");
      }
    }

    return contents.join("\n\n");
  }
}
