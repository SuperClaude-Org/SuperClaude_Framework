#!/usr/bin/env node
import serverInstance from "./server.js";
import logger from "./logger.js";

async function main() {
  try {
    const server = serverInstance.createInstance();

    // Connect to stdio transport
    await server.connect({
      stdio: {
        stdin: process.stdin,
        stdout: process.stdout,
      },
    });

    logger.info("SuperClaude MCP server started on stdio");

    // Handle graceful shutdown
    process.on("SIGINT", async () => {
      logger.info("Received SIGINT, shutting down gracefully");
      await server.close();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      logger.info("Received SIGTERM, shutting down gracefully");
      await server.close();
      process.exit(0);
    });
  } catch (error) {
    logger.error({ error }, "Failed to start MCP server");
    process.exit(1);
  }
}

main().catch(error => {
  logger.error({ error }, "Unhandled error in main");
  process.exit(1);
});
