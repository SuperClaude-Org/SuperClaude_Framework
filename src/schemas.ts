import { z } from 'zod';

export const SuperClaudeCommandSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  prompt: z.string().min(1),
  messages: z.array(z.object({
    role: z.string(),
    content: z.string()
  })).optional(),
  arguments: z.array(z.object({
    name: z.string(),
    description: z.string(),
    required: z.boolean()
  })).optional()
});

export const PersonaSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  instructions: z.string().min(1)
});

export const SuperClaudeRulesSchema = z.object({
  rules: z.array(z.object({
    name: z.string(),
    content: z.string()
  }))
});

export const CommandModelSchema = SuperClaudeCommandSchema.extend({
  id: z.string().min(1),
  lastUpdated: z.date(),
  hash: z.string().min(1)
});

export const PersonaModelSchema = PersonaSchema.extend({
  id: z.string().min(1),
  lastUpdated: z.date(),
  hash: z.string().min(1)
});

export const RulesModelSchema = z.object({
  id: z.string().min(1),
  rules: SuperClaudeRulesSchema,
  lastUpdated: z.date(),
  hash: z.string().min(1)
});

export const SyncMetadataSchema = z.object({
  lastSync: z.date(),
  syncStatus: z.enum(['success', 'failed']),
  errorMessage: z.string().optional()
});

export const DatabaseSchemaSchema = z.object({
  commands: z.array(CommandModelSchema),
  personas: z.array(PersonaModelSchema),
  rules: z.array(RulesModelSchema),
  syncMetadata: SyncMetadataSchema
});