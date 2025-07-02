#!/usr/bin/env node

import { DatabaseService } from "@services/database-service.js";
import { SyncReportGenerator } from "@utils/sync-report.js";
import { program } from "commander";
import chalk from "chalk";
import path from "path";

program
  .name("sync-report")
  .description("Generate a report of SuperClaude MCP sync status")
  .option("-d, --detailed", "Generate detailed report with full validation")
  .option(
    "-p, --path <path>",
    "Custom database path",
    path.join(process.cwd(), "data", "superclaude.json")
  )
  .option("--no-color", "Disable colored output")
  .parse(process.argv);

const options = program.opts();

if (options.noColor) {
  chalk.level = 0;
}

async function main() {
  try {
    const databaseService = new DatabaseService(options.path);
    const reportGenerator = new SyncReportGenerator(databaseService);

    const report = options.detailed
      ? await reportGenerator.generateDetailedReport()
      : await reportGenerator.generateReport();

    console.log(report);
  } catch (error) {
    console.error(chalk.red("Error generating report:"), error);
    process.exit(1);
  }
}

main();
