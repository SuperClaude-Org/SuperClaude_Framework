import { SuperClaudeCommand, Persona, SuperClaudeRules } from "./types.js";

export interface CommandModel extends SuperClaudeCommand {
  id: string;
  lastUpdated: Date;
  hash: string;
}

export interface PersonaModel extends Persona {
  id: string;
  lastUpdated: Date;
  hash: string;
}

export interface RulesModel {
  id: string;
  rules: SuperClaudeRules;
  lastUpdated: Date;
  hash: string;
}

export interface SyncMetadata {
  lastSync: Date;
  syncStatus: "success" | "failed";
  errorMessage?: string;
}

export interface DatabaseSchema {
  commands: CommandModel[];
  personas: PersonaModel[];
  rules: RulesModel[];
  syncMetadata: SyncMetadata;
}

export const DEFAULT_DATABASE_SCHEMA: DatabaseSchema = {
  commands: [],
  personas: [],
  rules: [],
  syncMetadata: {
    lastSync: new Date(0),
    syncStatus: "success",
  },
};
