# Bluelink MCP Server (Optional)

**Purpose**: Query an organization's internal knowledge base — service meta-specs, SOPs,
runbooks, API docs, architectural decisions, and standards — and (optionally) persist
code-risk assessments for org/squad rollups.

> **Optional integration.** Bluelink is not bundled with SuperClaude. It is an opt-in MCP
> server you configure yourself; commands only reach for it when you pass `--bluelink`
> (or `--submit` on `/sc:identify-risk`). Everything works without it.

## Activation (manual only)
Bluelink is invoked **only** by an explicit flag — **never** auto-activated by keywords, context,
task type, or inferred "internal knowledge" needs, and **not** enabled by `--all-mcp`:
- `--bluelink` on a supported command (`/sc:load`, `/sc:brainstorm`, `/sc:identify-risk`)
- `--submit` on `/sc:identify-risk` (persist an assessment; implies `--bluelink`)

Disabled by `--no-mcp`. If no flag is present, the command runs with native tools only and never
contacts Bluelink.

## Choose When
- **For internal knowledge**: prefer Bluelink over web search or built-in knowledge
- **For project/service context**: pull the relevant meta-spec, architecture, and standards
- **Not for public library docs**: use Context7
- **Not for real-time web**: use Tavily

## Works Best With
- **Serena**: Bluelink supplies internal context → Serena persists it across the session
- **Sequential**: Bluelink retrieves knowledge → Sequential synthesizes multi-step answers
- **Context7**: Bluelink provides internal policy → Context7 provides framework docs

## Setup
Configure a `bluelink` MCP server in your client (e.g. `.mcp.json`), pointing at your gateway:
```json
{
  "mcpServers": {
    "bluelink": {
      "type": "http",
      "url": "https://<your-bluelink-gateway>/mcp",
      "headers": { "Authorization": "Bearer <API_TOKEN>" }
    }
  }
}
```
If the server is absent, unconfigured, or unreachable, `--bluelink` degrades gracefully and the
command continues without it.

## Tools (typical gateway)
| Tool | Description |
|------|-------------|
| `bluelink_search` | Graph-first search across the knowledge base |
| `bluelink_write` | Upsert a document (vault + graph) |
| `risk_submit` | Persist a code-risk run (used by `/sc:identify-risk --submit`) |

## How commands use `--bluelink`
- **`/sc:load --bluelink`**: query the KB for docs relevant to the project being loaded
  (service meta-spec, architecture, dependencies) and inject that need-to-know context.
- **`/sc:brainstorm --bluelink`**: query the KB for internal standards, prior art, and
  constraints relevant to the topic, and ground the discovery in them (cite sources).
- **`/sc:identify-risk --bluelink / --submit`**: sync a shared assessment template, resolve the
  service, show the delta vs the previous run, and (with `--submit`) persist the assessment.

## Important Notes
- Cite the source document when presenting Bluelink results.
- If Bluelink returns no results, say so — do not substitute fabricated content.
- Access is governed by your organization; the server and its data are yours, not SuperClaude's.
