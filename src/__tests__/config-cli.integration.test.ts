import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { spawn } from "child_process";
import path from "path";
import fs from "fs/promises";
import os from "os";

// Mock fs/promises and os for controlled testing
vi.mock("fs/promises");
vi.mock("os");

describe.skip("Configuration CLI Integration Tests", () => {
  const mockHomeDir = "/mock/home";
  const mockConfigPath = path.join(mockHomeDir, ".superclaude", "config.json");
  const cliPath = path.join(process.cwd(), "dist", "main.js");

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(os.homedir).mockReturnValue(mockHomeDir);
    
    // Default mock implementations
    vi.mocked(fs.access).mockRejectedValue(new Error("File not found"));
    vi.mocked(fs.mkdir).mockResolvedValue(undefined);
    vi.mocked(fs.writeFile).mockResolvedValue(undefined);
    vi.mocked(fs.readFile).mockRejectedValue(new Error("File not found"));
    vi.mocked(fs.unlink).mockResolvedValue(undefined);
    vi.mocked(fs.stat).mockRejectedValue(new Error("File not found"));
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  // Helper function to run CLI commands
  function runCommand(args: string[]): Promise<{ stdout: string; stderr: string; code: number }> {
    return new Promise((resolve) => {
      const proc = spawn("node", [cliPath, ...args], {
        env: { ...process.env, NODE_ENV: "test" },
      });

      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("close", (code) => {
        resolve({ stdout, stderr, code: code || 0 });
      });
    });
  }

  describe("config init", () => {
    it("should initialize configuration file", async () => {
      const result = await runCommand(["config", "init"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration initialized at:");
      expect(result.stdout).toContain(mockConfigPath);
      
      expect(vi.mocked(fs.mkdir)).toHaveBeenCalledWith(
        path.dirname(mockConfigPath),
        { recursive: true }
      );
      expect(vi.mocked(fs.writeFile)).toHaveBeenCalledWith(
        mockConfigPath,
        expect.any(String),
        "utf-8"
      );
    });

    it("should not overwrite existing configuration", async () => {
      vi.mocked(fs.access).mockResolvedValueOnce(undefined);

      const result = await runCommand(["config", "init"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration file already exists");
      expect(result.stdout).toContain("Use 'config reset' to reset to defaults");
      expect(vi.mocked(fs.writeFile)).not.toHaveBeenCalled();
    });
  });

  describe("config show", () => {
    it("should display current configuration", async () => {
      const mockConfig = {
        source: {
          type: "remote",
          remote: {
            url: "https://github.com/test/repo",
            branch: "main",
            cacheTTL: 60,
          },
          local: { path: "/data" },
        },
        database: { path: "./data/superclaude.json" },
        sync: {
          enabled: true,
          intervalMinutes: 30,
          onStartup: true,
        },
        server: {
          transport: "stdio",
          port: 8080,
          logLevel: "info",
        },
        persistence: {
          enabled: false,
          autoSave: false,
        },
      };

      vi.mocked(fs.access).mockResolvedValueOnce(undefined);
      vi.mocked(fs.readFile).mockResolvedValueOnce(JSON.stringify(mockConfig));

      const result = await runCommand(["config", "show"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Current Configuration:");
      expect(result.stdout).toContain(`Config file: ${mockConfigPath}`);
      expect(result.stdout).toContain('"type": "remote"');
      expect(result.stdout).toContain('"url": "https://github.com/test/repo"');
    });

    it("should show default configuration when no config file exists", async () => {
      const result = await runCommand(["config", "show"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Current Configuration:");
      expect(result.stdout).toContain('"type": "remote"');
      expect(result.stdout).toContain("superclaudeinc/superclaude-content");
    });
  });

  describe("config set", () => {
    it("should set configuration values", async () => {
      const result = await runCommand(["config", "set", "sync.enabled", "false"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration updated: sync.enabled = false");
      
      // Verify the configuration was saved
      expect(vi.mocked(fs.writeFile)).toHaveBeenCalledWith(
        mockConfigPath,
        expect.stringContaining('"enabled": false'),
        "utf-8"
      );
    });

    it("should handle nested configuration paths", async () => {
      const result = await runCommand([
        "config", 
        "set", 
        "source.remote.url", 
        "https://github.com/new/repo"
      ]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain(
        "Configuration updated: source.remote.url = https://github.com/new/repo"
      );
    });

    it("should parse boolean values", async () => {
      const result = await runCommand(["config", "set", "persistence.enabled", "true"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration updated: persistence.enabled = true");
      
      const savedConfig = JSON.parse(
        vi.mocked(fs.writeFile).mock.calls[0][1] as string
      );
      expect(savedConfig.persistence.enabled).toBe(true);
      expect(typeof savedConfig.persistence.enabled).toBe("boolean");
    });

    it("should parse numeric values", async () => {
      const result = await runCommand(["config", "set", "sync.intervalMinutes", "45"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration updated: sync.intervalMinutes = 45");
      
      const savedConfig = JSON.parse(
        vi.mocked(fs.writeFile).mock.calls[0][1] as string
      );
      expect(savedConfig.sync.intervalMinutes).toBe(45);
      expect(typeof savedConfig.sync.intervalMinutes).toBe("number");
    });
  });

  describe("config reset", () => {
    it("should reset configuration to defaults", async () => {
      const result = await runCommand(["config", "reset"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration reset to defaults");
      expect(vi.mocked(fs.unlink)).not.toHaveBeenCalled();
    });

    it("should delete config file with --delete flag", async () => {
      const result = await runCommand(["config", "reset", "--delete"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration reset to defaults and file deleted");
      expect(vi.mocked(fs.unlink)).toHaveBeenCalledWith(mockConfigPath);
    });

    it("should handle file deletion errors gracefully", async () => {
      vi.mocked(fs.unlink).mockRejectedValueOnce(new Error("File not found"));

      const result = await runCommand(["config", "reset", "--delete"]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Configuration reset to defaults and file deleted");
    });
  });

  describe("global options", () => {
    it("should apply source configuration options to server command", async () => {
      process.env.SC_SOURCE_TYPE = "";
      process.env.SC_SOURCE_PATH = "";
      
      const result = await runCommand([
        "--source-type", "local",
        "--source-path", "/custom/data",
        "server"
      ]);

      // The server command sets environment variables
      expect(process.env.SC_SOURCE_TYPE).toBe("local");
      expect(process.env.SC_SOURCE_PATH).toBe("/custom/data");
    });

    it("should persist configuration with --persist-config flag", async () => {
      process.env.SC_PERSIST_CONFIG = "";
      
      const result = await runCommand([
        "--source-url", "https://github.com/custom/repo",
        "--persist-config",
        "server"
      ]);

      expect(process.env.SC_PERSIST_CONFIG).toBe("true");
    });
  });

  describe("sync command with configuration", () => {
    it("should use custom source configuration", async () => {
      // Mock database doesn't exist
      vi.mocked(fs.existsSync).mockReturnValue(false);

      const result = await runCommand([
        "--source-type", "local",
        "--source-path", "/test/data",
        "sync"
      ]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Starting GitHub sync...");
      expect(result.stdout).toContain("Database doesn't exist, initializing...");
    });

    it("should respect remote source configuration", async () => {
      vi.mocked(fs.existsSync).mockReturnValue(false);

      const result = await runCommand([
        "--source-url", "https://github.com/test/repo",
        "--source-branch", "develop",
        "sync"
      ]);

      expect(result.code).toBe(0);
      expect(result.stdout).toContain("Starting GitHub sync...");
    });
  });

  describe("report command with configuration", () => {
    it("should generate report with custom database path", async () => {
      const customDbPath = "/custom/database.json";

      // Mock database exists and has data
      vi.mocked(fs.readFile).mockResolvedValueOnce(JSON.stringify({
        commands: [],
        personas: {},
        rules: [],
        sync: {
          lastSync: new Date().toISOString(),
          source: "test",
        },
      }));

      const result = await runCommand([
        "report",
        "--path", customDbPath
      ]);

      expect(result.code).toBe(0);
      expect(vi.mocked(fs.readFile)).toHaveBeenCalledWith(customDbPath, "utf-8");
    });
  });

  describe("error handling", () => {
    it("should handle invalid configuration gracefully", async () => {
      const result = await runCommand([
        "config", 
        "set", 
        "source.type", 
        "invalid"
      ]);

      expect(result.code).toBe(1);
      expect(result.stderr).toContain("Error setting configuration:");
    });

    it("should handle missing required arguments", async () => {
      const result = await runCommand(["config", "set", "key"]);

      expect(result.code).toBe(1);
      expect(result.stderr).toContain("error");
    });
  });
});