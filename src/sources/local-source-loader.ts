import fs from "fs/promises";
import path from "path";
import yaml from "js-yaml";
import logger from "@/logger.js";
import { Command, Persona } from "@/schemas.js";
import { SuperClaudeRules } from "@types";
import { ISourceLoader } from "./interfaces.js";

/**
 * LocalSourceLoader loads SuperClaude data from local file system
 * Expected directory structure:
 * - {basePath}/commands/
 * - {basePath}/personas/
 * - {basePath}/rules/rules.yaml
 */
export class LocalSourceLoader implements ISourceLoader {
  constructor(private readonly basePath: string) {}

  async loadCommands(): Promise<Command[]> {
    try {
      const commandsPath = path.join(this.basePath, "commands");
      const commands: Command[] = [];

      // Check if commands directory exists
      const commandsDirExists = await this.directoryExists(commandsPath);
      if (!commandsDirExists) {
        logger.debug({ path: commandsPath }, "Commands directory not found");
        return [];
      }

      // Read all YAML files in the commands directory
      const files = await fs.readdir(commandsPath);
      const yamlFiles = files.filter(file => file.endsWith(".yaml") || file.endsWith(".yml"));

      for (const file of yamlFiles) {
        try {
          const filePath = path.join(commandsPath, file);
          const content = await fs.readFile(filePath, "utf-8");
          const commandData = yaml.load(content) as Command;

          // Validate basic structure
          if (commandData && typeof commandData === "object" && commandData.name) {
            commands.push(commandData);
            logger.debug({ file, commandName: commandData.name }, "Loaded command from local file");
          } else {
            logger.warn({ file }, "Invalid command structure in file");
          }
        } catch (error) {
          logger.error({ error, file }, "Failed to load command file");
        }
      }

      logger.info(
        { count: commands.length, path: commandsPath },
        "Loaded commands from local directory"
      );
      return commands;
    } catch (error) {
      logger.error({ error, basePath: this.basePath }, "Failed to load commands from local source");
      throw new Error(
        `Failed to load commands: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  async loadPersonas(): Promise<Persona[]> {
    try {
      const personasPath = path.join(this.basePath, "personas");
      const personas: Persona[] = [];

      // Check if personas directory exists
      const personasDirExists = await this.directoryExists(personasPath);
      if (!personasDirExists) {
        logger.debug({ path: personasPath }, "Personas directory not found");
        return [];
      }

      // Read all YAML files in the personas directory
      const files = await fs.readdir(personasPath);
      const yamlFiles = files.filter(file => file.endsWith(".yaml") || file.endsWith(".yml"));

      for (const file of yamlFiles) {
        try {
          const filePath = path.join(personasPath, file);
          const content = await fs.readFile(filePath, "utf-8");
          const personaData = yaml.load(content) as Persona;

          // Validate basic structure
          if (personaData && typeof personaData === "object" && personaData.name) {
            personas.push(personaData);
            logger.debug({ file, personaName: personaData.name }, "Loaded persona from local file");
          } else {
            logger.warn({ file }, "Invalid persona structure in file");
          }
        } catch (error) {
          logger.error({ error, file }, "Failed to load persona file");
        }
      }

      logger.info(
        { count: personas.length, path: personasPath },
        "Loaded personas from local directory"
      );
      return personas;
    } catch (error) {
      logger.error({ error, basePath: this.basePath }, "Failed to load personas from local source");
      throw new Error(
        `Failed to load personas: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  async loadRules(): Promise<SuperClaudeRules> {
    try {
      const rulesPath = path.join(this.basePath, "rules", "rules.yaml");

      // Check if rules file exists
      const rulesFileExists = await this.fileExists(rulesPath);
      if (!rulesFileExists) {
        logger.debug({ path: rulesPath }, "Rules file not found");
        return { rules: [] };
      }

      const content = await fs.readFile(rulesPath, "utf-8");
      const rulesData = yaml.load(content) as SuperClaudeRules;

      // Validate basic structure
      if (rulesData && typeof rulesData === "object" && Array.isArray(rulesData.rules)) {
        logger.info(
          { count: rulesData.rules.length, path: rulesPath },
          "Loaded rules from local file"
        );
        return rulesData;
      } else {
        logger.warn({ path: rulesPath }, "Invalid rules structure in file");
        return { rules: [] };
      }
    } catch (error) {
      logger.error({ error, basePath: this.basePath }, "Failed to load rules from local source");
      throw new Error(
        `Failed to load rules: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  clearCache(): void {
    // Local source loader doesn't use caching, so this is a no-op
    logger.debug("Local source loader cache cleared (no-op)");
  }

  /**
   * Load shared includes (for command templates)
   */
  async loadSharedIncludes(includes: string[]): Promise<string> {
    const contents: string[] = [];

    for (const include of includes) {
      try {
        const includePath = include.startsWith("@include")
          ? include.replace("@include ", "").trim()
          : include;

        const fullPath = includePath.startsWith("/")
          ? path.join(this.basePath, includePath)
          : path.join(this.basePath, "commands", "shared", includePath);

        const content = await fs.readFile(fullPath, "utf-8");
        contents.push(content);
      } catch (error) {
        logger.warn({ error, include }, "Failed to load include from local source");
      }
    }

    return contents.join("\n\n");
  }

  /**
   * Check if a directory exists
   */
  private async directoryExists(dirPath: string): Promise<boolean> {
    try {
      const stat = await fs.stat(dirPath);
      return stat.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * Check if a file exists
   */
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      const stat = await fs.stat(filePath);
      return stat.isFile();
    } catch {
      return false;
    }
  }

  /**
   * Get information about the local source
   */
  getSourceInfo(): { type: "local"; basePath: string } {
    return {
      type: "local",
      basePath: this.basePath,
    };
  }
}
