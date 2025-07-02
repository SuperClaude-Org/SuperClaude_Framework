import serverInstance from "@/server.js";
import logger from "@logger";

async function testRulesResources() {
  console.log('Testing rules resource changes...\n');
  
  // Wait for server initialization
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Get the server instance
  const server = serverInstance.createInstance();
  const lowLevelServer = (server as any).server;
  
  // Test ListResourceTemplates
  console.log('1. Testing ListResourceTemplates:');
  const templates = await lowLevelServer.requestHandlers.get('resources/templates')();
  console.log('Resource Templates:', JSON.stringify(templates, null, 2));
  
  // Test ListResources
  console.log('\n2. Testing ListResources:');
  const resources = await lowLevelServer.requestHandlers.get('resources/list')();
  console.log('Total resources:', resources.resources.length);
  console.log('\nRules resources:');
  resources.resources
    .filter((r: any) => r.uri.startsWith('superclaude://rules/'))
    .forEach((r: any) => {
      console.log(`- ${r.uri}`);
      console.log(`  Name: ${r.name}`);
      console.log(`  Description: ${r.description.substring(0, 50)}...`);
    });
  
  // Test ReadResource for a specific rule
  console.log('\n3. Testing ReadResource for a specific rule:');
  try {
    const ruleUri = 'superclaude://rules/Design_Principles';
    const result = await lowLevelServer.requestHandlers.get('resources/read')({
      params: { uri: ruleUri }
    });
    console.log(`Content for ${ruleUri}:`);
    console.log(JSON.parse(result.contents[0].text));
  } catch (error) {
    console.error('Error reading rule:', error);
  }
  
  // Test with encoded URI
  console.log('\n4. Testing with URL-encoded rule name:');
  try {
    const ruleUri = 'superclaude://rules/Files_Code_Management';
    const result = await lowLevelServer.requestHandlers.get('resources/read')({
      params: { uri: ruleUri }
    });
    console.log(`Content for ${ruleUri}:`);
    const content = JSON.parse(result.contents[0].text);
    console.log(`Name: ${content.name}`);
    console.log(`Content preview: ${content.content.substring(0, 100)}...`);
  } catch (error) {
    console.error('Error reading rule:', error);
  }
}

testRulesResources().catch(error => {
  logger.error({ error }, "Test failed");
  console.error(error);
  process.exit(1);
});