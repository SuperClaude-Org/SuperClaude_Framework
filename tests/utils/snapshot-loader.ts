import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { CommandModel, PersonaModel, RulesModel } from '../../src/database.js';
import { SuperClaudeCommand, Persona } from '../../src/types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface SnapshotData {
  commands: CommandModel[];
  personas: PersonaModel[];
  rules: Array<{
    id: string;
    rules: {
      rules: Array<{
        name: string;
        content: string;
      }>;
    };
    hash: string;
    lastUpdated: string;
  }>;
  syncMetadata: {
    lastSync: string;
    syncStatus: 'success' | 'failed';
  };
}

let cachedSnapshot: SnapshotData | null = null;

export function loadSnapshot(): SnapshotData {
  if (cachedSnapshot) {
    return cachedSnapshot;
  }

  const snapshotPath = join(__dirname, '..', 'data', 'superclaude.snapshot.json');
  const rawData = readFileSync(snapshotPath, 'utf-8');
  const snapshot = JSON.parse(rawData) as SnapshotData;
  
  // Convert date strings to Date objects for compatibility
  const processedSnapshot: SnapshotData = {
    ...snapshot,
    commands: snapshot.commands.map(cmd => ({
      ...cmd,
      lastUpdated: new Date(cmd.lastUpdated)
    })),
    personas: snapshot.personas.map(persona => ({
      ...persona,
      lastUpdated: new Date(persona.lastUpdated)
    })),
    rules: snapshot.rules
  };
  
  cachedSnapshot = processedSnapshot;
  return processedSnapshot;
}

export function getSnapshotCommands(): CommandModel[] {
  return loadSnapshot().commands;
}

export function getSnapshotPersonas(): PersonaModel[] {
  return loadSnapshot().personas;
}

export function getSnapshotRules(): RulesModel | null {
  const snapshot = loadSnapshot();
  const rules = snapshot.rules as any[];
  if (rules.length === 0) return null;
  
  const rule = rules[0];
  return {
    id: rule.id,
    rules: rule.rules,
    hash: rule.hash,
    lastUpdated: new Date()  // Use current date for tests
  };
}

export function getSnapshotPersonasAsRecord(): Record<string, PersonaModel> {
  const personas = getSnapshotPersonas();
  return personas.reduce((acc, persona) => {
    acc[persona.id] = persona;
    return acc;
  }, {} as Record<string, PersonaModel>);
}

export function getCommandByName(name: string): CommandModel | undefined {
  return getSnapshotCommands().find(cmd => cmd.name === name);
}

export function getPersonaById(id: string): PersonaModel | undefined {
  return getSnapshotPersonas().find(persona => persona.id === id);
}

// Convert PersonaModel to Persona type for GitHub loader tests
export function convertPersonaModelToPersona(personaModel: PersonaModel): Persona {
  return {
    name: personaModel.name,
    description: personaModel.description,
    instructions: personaModel.instructions
  };
}

// Convert CommandModel to SuperClaudeCommand type for GitHub loader tests
export function convertCommandModelToCommand(commandModel: CommandModel): SuperClaudeCommand {
  return {
    name: commandModel.name,
    description: commandModel.description,
    prompt: commandModel.prompt,
    messages: commandModel.messages,
    arguments: commandModel.arguments
  };
}

// Get raw YAML-like content for personas (for GitHub loader mock)
export function getPersonasYamlContent(): string {
  const personas = getSnapshotPersonas();
  let yaml = '';
  
  personas.forEach(persona => {
    yaml += `${persona.id}:\n`;
    yaml += `  Identity: ${persona.name}\n`;
    yaml += `  Core_Belief: ${persona.description}\n`;
    
    // Extract problem solving and focus from instructions
    const lines = persona.instructions.split('. ');
    yaml += `  Problem_Solving: ${lines[1] || 'Problem solving approach'}\n`;
    yaml += `  Focus: ${lines[3] || 'Focus areas'}\n\n`;
  });
  
  return yaml.trim();
}

// Get raw YAML-like content for rules (for GitHub loader mock)
export function getRulesYamlContent(): string {
  const rulesData = loadSnapshot().rules;
  if (!rulesData || rulesData.length === 0) return '';
  
  const rules = rulesData[0];
  let yaml = 'rules:\n';
  
  rules.rules.rules.forEach(rule => {
    yaml += `  - name: ${rule.name}\n`;
    yaml += `    content: ${rule.content}\n`;
  });
  
  return yaml.trim();
}