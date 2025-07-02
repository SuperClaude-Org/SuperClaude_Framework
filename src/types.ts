export interface SuperClaudeCommand {
  name: string;
  content: string;
  arguments?: string[];
}

export interface Persona {
  name: string;
  description?: string;
  settings?: Record<string, any>;
}

export interface SuperClaudeRules {
  [key: string]: any;
}