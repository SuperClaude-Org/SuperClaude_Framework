#!/usr/bin/env node

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Command } from "commander";
import express from "express";
import serverInstance from "@/http-server.js";
import app from "@/app.js";
import logger, { configureLogger } from "@logger";
import { DatabaseService } from "@services/database-service.js";
import { SyncReportGenerator } from "@utils/sync-report.js";
import { GitHubSourceLoader } from "@/sources/index.js";
import { SyncService } from "@services/sync-service.js";
import chalk from "chalk";
import path from "path";
import fs from "fs";

async function launchMcpStdioServer() {
  const server = serverInstance.createInstance();
  await server.connect(new StdioServerTransport());
  logger.info("SuperClaude MCP server started on stdio");
  return server;
}

async function launchHttpServer() {
  const PORT = process.env.PORT || 8080;

  const server = express()
    .use(app)
    .listen(PORT, () => {
      logger.info({ port: PORT }, "SuperClaude HTTP server started");
    });

  return server;
}

async function runServer(transport: string) {
  // Configure logger based on transport type as early as possible
  configureLogger(transport);

  if (!["stdio", "http"].includes(transport)) {
    logger.error(`Invalid transport type: ${transport}. Must be 'stdio' or 'http'`);
    process.exit(1);
  }

  try {
    let server;

    if (transport === "http") {
      server = await launchHttpServer();
    } else {
      server = await launchMcpStdioServer();
    }

    // Handle graceful shutdown
    const handleShutdown = async (signal: string) => {
      logger.info(`Received ${signal}, shutting down gracefully`);
      try {
        if (transport === "express") {
          // Express server shutdown
          await new Promise<void>(resolve => {
            (server as any).close(() => {
              logger.info("Express server closed");
              resolve();
            });
          });
        } else {
          // MCP server shutdown
          await (server as any).close();
          logger.info("MCP server closed");
        }
        process.exit(0);
      } catch (error) {
        logger.error({ error }, "Error during shutdown");
        process.exit(1);
      }
    };

    process.on("SIGINT", () => handleShutdown("SIGINT"));
    process.on("SIGTERM", () => handleShutdown("SIGTERM"));
  } catch (error) {
    logger.error({ error }, "Failed to start server");
    process.exit(1);
  }
}

async function runSyncAndReport(options: {
  detailed?: boolean;
  path?: string;
  color?: boolean;
  syncEnabled: boolean;
}) {
  // Configure logger for non-server usage
  configureLogger("http");

  if (options.color === false) {
    chalk.level = 0;
  }

  try {
    const dbPath = options.path || path.join(process.cwd(), "data", "superclaude.json");
    const databaseService = new DatabaseService(dbPath);

    // Perform sync if enabled
    if (options.syncEnabled) {
      console.log(chalk.blue("Starting GitHub sync..."));

      const githubLoader = new GitHubSourceLoader();
      const syncService = new SyncService(githubLoader, databaseService);

      // Only initialize database if it doesn't exist
      const dbExists = fs.existsSync(dbPath);
      if (!dbExists) {
        console.log(chalk.blue("Database doesn't exist, initializing..."));
        await databaseService.initialize();
      }

      try {
        await syncService.syncFromGitHub();
        console.log(chalk.green("Sync completed successfully"));
      } catch (error) {
        console.error(chalk.yellow("Warning: Sync failed, but will still generate report:"), error);
        // Continue to report generation even if sync fails
      }
    }

    // Generate report
    const reportGenerator = new SyncReportGenerator(databaseService);

    const report = options.detailed
      ? await reportGenerator.generateDetailedReport()
      : await reportGenerator.generateReport();

    console.log(report);
  } catch (error) {
    console.error(chalk.red("Error:"), error);
    process.exit(1);
  }
}

async function runReport(options: { detailed?: boolean; path?: string; color?: boolean }) {
  await runSyncAndReport({ ...options, syncEnabled: false });
}

async function runSync(options: { detailed?: boolean; path?: string; color?: boolean }) {
  await runSyncAndReport({ ...options, syncEnabled: true });
}

async function main() {
  const program = new Command();

  program.name("superclaude-mcp").description("SuperClaude MCP server").version("1.0.0");

  // Server command (default)
  program
    .command("server", { isDefault: true })
    .description("Start the SuperClaude MCP server")
    .option("-t, --transport <type>", "transport type (stdio or http)", "stdio")
    .action(async options => {
      await runServer(options.transport);
    });

  // Report command
  program
    .command("report")
    .description("Generate a report of recently synced data")
    .option("-d, --detailed", "Detailed report with full schema validation")
    .option(
      "-p, --path <path>",
      "Custom database path",
      path.join(process.cwd(), "data", "superclaude.json")
    )
    .option("--no-color", "Disable colored output")
    .action(async options => {
      await runReport(options);
    });

  // Sync command
  program
    .command("sync")
    .description("Sync data from GitHub and generate a report")
    .option("-d, --detailed", "Detailed report with full schema validation")
    .option(
      "-p, --path <path>",
      "Custom database path",
      path.join(process.cwd(), "data", "superclaude.json")
    )
    .option("--no-color", "Disable colored output")
    .action(async options => {
      await runSync(options);
    });

  await program.parseAsync();
}

main().catch(error => {
  logger.error({ error }, "Unhandled error in main");
  process.exit(1);
});
