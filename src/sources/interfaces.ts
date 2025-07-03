import { Command, Persona } from "@/schemas.js";
import { SuperClaudeRules } from "@types";

export interface ISourceLoader {
  loadCommands(): Promise<Command[]>;
  loadPersonas(): Promise<Persona[]>;
  loadRules(): Promise<SuperClaudeRules>;
  clearCache(): void;
  loadSharedIncludes?(includes: string[]): Promise<string>;
}
