import { Command, Persona, Rules } from "@/schemas.js";

export interface ISourceLoader {
  loadCommands(): Promise<Command[]>;
  loadPersonas(): Promise<Persona[]>;
  loadRules(): Promise<Rules>;
  clearCache(): void;
}
