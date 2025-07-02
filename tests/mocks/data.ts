import { faker } from '@faker-js/faker';
import { CommandModel, PersonaModel, RulesModel, DatabaseSchema, SyncMetadata } from '../../src/database.js';

export function createMockCommand(overrides?: Partial<CommandModel>): CommandModel {
  return {
    id: faker.string.uuid(),
    name: faker.hacker.verb() + '-' + faker.hacker.noun(),
    description: faker.lorem.sentence(),
    prompt: faker.lorem.paragraph(),
    messages: Math.random() > 0.5 ? [{
      role: 'user',
      content: faker.lorem.sentence()
    }] : undefined,
    arguments: Math.random() > 0.5 ? [{
      name: faker.hacker.noun(),
      description: faker.lorem.sentence(),
      required: faker.datatype.boolean()
    }] : undefined,
    lastUpdated: faker.date.recent(),
    hash: faker.string.alphanumeric(64),
    ...overrides
  };
}

export function createMockPersona(overrides?: Partial<PersonaModel>): PersonaModel {
  return {
    id: faker.string.uuid(),
    name: faker.person.jobTitle(),
    description: faker.lorem.sentence(),
    instructions: faker.lorem.paragraphs(2),
    lastUpdated: faker.date.recent(),
    hash: faker.string.alphanumeric(64),
    ...overrides
  };
}

export function createMockRules(overrides?: Partial<RulesModel>): RulesModel {
  return {
    id: 'superclaude-rules',
    rules: {
      rules: Array.from({ length: faker.number.int({ min: 2, max: 5 }) }, () => ({
        name: faker.hacker.noun(),
        content: faker.lorem.paragraph()
      }))
    },
    lastUpdated: faker.date.recent(),
    hash: faker.string.alphanumeric(64),
    ...overrides
  };
}

export function createMockSyncMetadata(overrides?: Partial<SyncMetadata>): SyncMetadata {
  return {
    lastSync: faker.date.recent(),
    syncStatus: faker.helpers.arrayElement(['success', 'failed'] as const),
    errorMessage: Math.random() > 0.5 ? faker.lorem.sentence() : undefined,
    ...overrides
  };
}

export function createMockDatabase(overrides?: Partial<DatabaseSchema>): DatabaseSchema {
  return {
    commands: Array.from({ length: 5 }, () => createMockCommand()),
    personas: Array.from({ length: 3 }, () => createMockPersona()),
    rules: [createMockRules()],
    syncMetadata: createMockSyncMetadata({ syncStatus: 'success' }),
    ...overrides
  };
}

export const mockCommands = [
  createMockCommand({
    id: 'test-command-1',
    name: 'test-command',
    description: 'A test command',
    prompt: 'This is a test prompt with $ARGUMENT',
    arguments: [{
      name: 'ARGUMENT',
      description: 'Test argument',
      required: true
    }]
  }),
  createMockCommand({
    id: 'simple-command',
    name: 'simple',
    description: 'A simple command',
    prompt: 'Simple prompt without arguments'
  })
];

export const mockPersonas = [
  createMockPersona({
    id: 'developer',
    name: 'Developer',
    description: 'A helpful developer persona',
    instructions: 'You are a helpful developer who writes clean code.'
  }),
  createMockPersona({
    id: 'architect',
    name: 'Software Architect',
    description: 'System design expert',
    instructions: 'You focus on high-level system design and architecture patterns.'
  })
];

export const mockRules = createMockRules({
  id: 'superclaude-rules',
  rules: {
    rules: [
      { name: 'safety', content: 'Always prioritize safety and security' },
      { name: 'clarity', content: 'Be clear and concise in communication' }
    ]
  }
});