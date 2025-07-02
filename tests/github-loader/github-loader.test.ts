import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { GitHubLoader } from '../../src/github-loader.js';
import { SuperClaudeCommandSchema, PersonaSchema, SuperClaudeRulesSchema } from '../../src/schemas.js';
import axios from 'axios';
import { mockCommands } from '../mocks/data.js';

vi.mock('axios', () => ({
  default: {
    get: vi.fn()
  }
}));

describe('GitHubLoader', () => {
  let githubLoader: GitHubLoader;

  beforeEach(() => {
    vi.resetAllMocks();
    vi.clearAllMocks();
    githubLoader = new GitHubLoader();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.resetAllMocks();
    vi.useRealTimers();
  });

  describe('loadCommands', () => {
    const mockCommandFiles = [
      { name: 'test-command.md', path: '.claude/commands/test-command.md', type: 'file' },
      { name: 'another-command.md', path: '.claude/commands/another-command.md', type: 'file' }
    ];

    const mockCommandContent = `**Purpose**: A test command

This is the prompt content with $ARGUMENT

Some more content here.`;

    it('should load and parse commands from GitHub', async () => {
      vi.clearAllMocks(); // Ensure clean state
      (axios.get as any).mockImplementation((url: string) => {
        if (url.includes('api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands')) {
          return Promise.resolve({ data: mockCommandFiles });
        }
        if (url.includes('raw.githubusercontent.com') && url.includes('/test-command.md')) {
          return Promise.resolve({ data: mockCommandContent });
        }
        if (url.includes('raw.githubusercontent.com') && url.includes('/another-command.md')) {
          return Promise.resolve({ data: mockCommandContent.replace('test-command', 'another-command') });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      const commands = await githubLoader.loadCommands();

      expect(commands).toHaveLength(2);
      expect(commands[0].name).toBe('test-command');
      expect(commands[0].description).toBe('A test command');
      expect(commands[0].prompt).toBe(mockCommandContent);
      expect(commands[0].arguments).toHaveLength(1);
      expect(commands[0].arguments?.[0].name).toBe('ARGUMENT');
    });

    it('should validate commands with Zod schema', async () => {
      (axios.get as any).mockImplementation((url: string) => {
        if (url.includes('api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands')) {
          return Promise.resolve({ data: mockCommandFiles });
        }
        return Promise.resolve({ data: mockCommandContent });
      });

      const commands = await githubLoader.loadCommands();

      commands.forEach(command => {
        const result = SuperClaudeCommandSchema.safeParse(command);
        expect(result.success).toBe(true);
      });
    });

    it('should use cache for subsequent calls within TTL', async () => {
      (axios.get as any).mockImplementation((url: string) => {
        if (url.includes('api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands')) {
          return Promise.resolve({ data: mockCommandFiles });
        }
        if (url.includes('raw.githubusercontent.com')) {
          return Promise.resolve({ data: mockCommandContent });
        }
        return Promise.reject(new Error('Unexpected URL: ' + url));
      });

      // First call
      await githubLoader.loadCommands();
      const firstCallCount = (axios.get as any).mock.calls.length;
      expect(firstCallCount).toBe(3); // Exactly 1 for list + 2 for files

      // Second call within TTL (should use cache for file contents)
      await githubLoader.loadCommands();
      const secondCallCount = (axios.get as any).mock.calls.length;
      // Second call makes 1 more API call (for the file list)
      expect(secondCallCount).toBe(firstCallCount + 1);

      // Advance time past TTL (5 minutes)
      await vi.advanceTimersByTimeAsync(6 * 60 * 1000);

      // Third call after TTL
      await githubLoader.loadCommands();
      const thirdCallCount = (axios.get as any).mock.calls.length;
      expect(thirdCallCount).toBeGreaterThan(secondCallCount); // More calls after cache expires
    });

    it('should handle GitHub API errors', async () => {
      (axios.get as any).mockRejectedValue(new Error('GitHub API error'));

      const commands = await githubLoader.loadCommands();
      expect(commands).toEqual([]);
    });

    it('should skip non-markdown files', async () => {
      const mixedFiles = [
        { name: 'test-command.md', path: '.claude/commands/test-command.md', type: 'file' },
        { name: 'README.txt', path: '.claude/commands/README.txt', type: 'file' },
        { name: '.DS_Store', path: '.claude/commands/.DS_Store', type: 'file' }
      ];

      (axios.get as any).mockImplementation((url: string) => {
        if (url.includes('api.github.com/repos/NomenAK/SuperClaude/contents/.claude/commands')) {
          return Promise.resolve({ data: mixedFiles });
        }
        if (url.includes('raw.githubusercontent.com') && url.includes('/test-command.md')) {
          return Promise.resolve({ data: mockCommandContent });
        }
        return Promise.reject(new Error('Should not fetch non-markdown files'));
      });

      const commands = await githubLoader.loadCommands();

      expect(commands).toHaveLength(1);
      expect(axios.get).toHaveBeenCalledTimes(2); // 1 for list + 1 for markdown file
    });
  });

  describe('loadPersonas', () => {
    const mockPersonasYaml = `
developer:
  Identity: Developer identity
  Core_Belief: Developer core belief
  Problem_Solving: Developer problem solving
  Focus: Developer focus

architect:
  Identity: Architect identity
  Core_Belief: Architect core belief
  Problem_Solving: Architect problem solving
  Focus: Architect focus
`;

    it('should load and parse personas from GitHub', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockPersonasYaml
      });

      const personas = await githubLoader.loadPersonas();

      expect(Object.keys(personas)).toHaveLength(2);
      expect(personas.developer.name).toBe('Developer identity');
      expect(personas.architect.name).toBe('Architect identity');
      expect(personas.developer.description).toBe('Developer core belief');
      expect(personas.architect.description).toBe('Architect core belief');
      expect(personas.developer.instructions).toContain('Developer identity');
      expect(personas.developer.instructions).toContain('Developer core belief');
    });

    it('should validate personas with Zod schema', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockPersonasYaml
      });

      const personas = await githubLoader.loadPersonas();

      Object.values(personas).forEach(persona => {
        const result = PersonaSchema.safeParse(persona);
        expect(result.success).toBe(true);
      });
    });

    it('should handle invalid YAML gracefully', async () => {
      const invalidYaml = `
invalid: yaml: content
  - this is not valid
`;

      (axios.get as any).mockResolvedValue({
        data: invalidYaml
      });

      const personas = await githubLoader.loadPersonas();
      expect(personas).toEqual({});
    });

    it('should use cache for personas', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockPersonasYaml
      });

      await githubLoader.loadPersonas();
      expect(axios.get).toHaveBeenCalledTimes(1);

      await githubLoader.loadPersonas();
      expect(axios.get).toHaveBeenCalledTimes(1);

      await vi.advanceTimersByTimeAsync(6 * 60 * 1000);

      await githubLoader.loadPersonas();
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('loadRules', () => {
    const mockRulesYaml = `
rules:
  - name: safety
    content: Always prioritize safety and security
  - name: clarity
    content: Be clear and concise in communication
`;

    it('should load and parse rules from GitHub', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockRulesYaml
      });

      const rules = await githubLoader.loadRules();

      expect(rules.rules.length).toBeGreaterThan(0);
      // The extractRules function creates flattened entries, so check for the actual structure
      const ruleNames = rules.rules.map(r => r.name);
      const ruleContents = rules.rules.map(r => r.content).join(' ');
      expect(ruleContents).toContain('safety');
      expect(ruleContents).toContain('clarity');
    });

    it('should validate rules with Zod schema', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockRulesYaml
      });

      const rules = await githubLoader.loadRules();

      const result = SuperClaudeRulesSchema.safeParse(rules);
      expect(result.success).toBe(true);
    });

    it('should handle missing rules file', async () => {
      (axios.get as any).mockRejectedValue({ response: { status: 404 } });

      const rules = await githubLoader.loadRules();
      expect(rules).toEqual({ rules: [] });
    });

    it('should use cache for rules', async () => {
      (axios.get as any).mockResolvedValue({
        data: mockRulesYaml
      });

      await githubLoader.loadRules();
      expect(axios.get).toHaveBeenCalledTimes(1);

      await githubLoader.loadRules();
      expect(axios.get).toHaveBeenCalledTimes(1);

      await vi.advanceTimersByTimeAsync(6 * 60 * 1000);

      await githubLoader.loadRules();
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      (axios.get as any).mockRejectedValue(new Error('Network error'));

      const commands = await githubLoader.loadCommands();
      const personas = await githubLoader.loadPersonas();
      const rules = await githubLoader.loadRules();
      
      expect(commands).toEqual([]);
      expect(personas).toEqual({});
      expect(rules).toEqual({ rules: [] });
    });

    it('should handle rate limiting', async () => {
      (axios.get as any).mockRejectedValue({
        response: {
          status: 403,
          headers: { 'x-ratelimit-remaining': '0' }
        }
      });

      const commands = await githubLoader.loadCommands();
      expect(commands).toEqual([]);
    });

    it('should handle malformed base64 content', async () => {
      (axios.get as any).mockResolvedValue({
        data: 'invalid yaml content {{'
      });

      const personas = await githubLoader.loadPersonas();
      expect(personas).toEqual({});
    });
  });
});