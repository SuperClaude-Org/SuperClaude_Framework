// Re-export from models for backward compatibility
export {
  CommandSchema as SuperClaudeCommandSchema,
  CommandModelSchema,
  type Command,
  type CommandModel,
} from "./models/command.model.js";

export {
  PersonaSchema,
  PersonaModelSchema,
  type Persona,
  type PersonaModel,
} from "./models/persona.model.js";

export {
  RulesSchema as SuperClaudeRulesSchema,
  RuleModelSchema,
  RuleSchema,
  type Rules,
  type Rule,
  type RuleModel,
} from "./models/rules.model.js";

export { SyncMetadataSchema, type SyncMetadata } from "./models/sync.model.js";

export { DatabaseSchemaSchema, type DatabaseSchema } from "./models/database.model.js";
