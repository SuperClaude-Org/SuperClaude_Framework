import { GitHubLoader } from "@/github-loader.js";
import { DatabaseService } from "@services/database-service.js";
import { SyncService } from "@services/sync-service.js";
import logger from "@logger";

async function testPersonas() {
  const loader = new GitHubLoader();
  const db = new DatabaseService();
  const sync = new SyncService(loader, db);

  console.log("Testing persona loading...");
  const personas = await loader.loadPersonas();
  console.log("Loaded personas from GitHub:", Object.keys(personas));
  console.log("Persona count:", Object.keys(personas).length);

  if (Object.keys(personas).length > 0) {
    const firstKey = Object.keys(personas)[0];
    console.log(`First persona (${firstKey}):`, personas[firstKey]);
  }

  console.log("\nInitializing database...");
  await db.initialize();

  console.log("\nPerforming sync...");
  await sync.syncFromGitHub();

  console.log("\nLoading from database...");
  const data = await sync.loadFromDatabase();
  console.log("Database personas:", Object.keys(data.personas));
  console.log("Database persona count:", Object.keys(data.personas).length);

  // Check the raw database
  console.log("\nChecking raw database personas...");
  const allPersonas = await db.getAllPersonas();
  console.log("Raw getAllPersonas() result:", allPersonas);
  console.log("Raw getAllPersonas() count:", allPersonas.length);
}

testPersonas().catch(error => {
  logger.error({ error }, "Test failed");
  console.error(error);
  process.exit(1);
});
