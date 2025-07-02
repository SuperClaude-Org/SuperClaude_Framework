export interface CommandArgument {
  name: string;
  description: string;
  required: boolean;
}

export interface SuperClaudeCommand {
  name: string;
  description: string;
  prompt: string;
  messages?: Array<{
    role: string;
    content: string;
  }>;
  arguments?: CommandArgument[];
}

export interface Persona {
  name: string;
  description: string;
  instructions: string;
}

export interface SuperClaudeRules {
  rules: Array<{
    name: string;
    content: string;
  }>;
}
