import { z } from "zod";
import { CommandModelSchema } from "./command.model.js";
import { PersonaModelSchema } from "./persona.model.js";
import { RuleModelSchema } from "./rules.model.js";
import { SyncMetadataSchema } from "./sync.model.js";

export const DatabaseSchemaSchema = z.object({
  commands: z.array(CommandModelSchema),
  personas: z.array(PersonaModelSchema),
  rules: z.array(RuleModelSchema), // Store individual rules like personas
  syncMetadata: SyncMetadataSchema,
});

export type DatabaseSchema = z.infer<typeof DatabaseSchemaSchema>;
