# ADO MCP

Azure DevOps MCP server with two transports:
- **HTTP REST wrapper** (existing behavior)
- **MCP stdio transport** (Phase 1)

## Overview

This is a read-only V1 implementation that provides:
- List work items by WIQL query
- Get a work item by ID
- List repositories
- List pull requests by repository
- List builds
- Health endpoint
- Tools manifest endpoint

## Requirements

- Python 3.12+
- Docker (optional)

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Azure DevOps organization URL (include https://)
ADO_ORG=https://dev.azure.com/yourorg
ADO_PROJECT=YourProjectName

# Personal Access Token (keep secret)
ADO_PAT=YOUR_PAT_HERE

# Optional
ADO_API_VERSION=7.1-preview.3
PORT=8080
LOG_LEVEL=INFO
ADO_ALLOW_WRITES=false
ADO_ALLOWED_WORK_ITEM_TYPES=Task,Bug,User Story
```

## Running with Docker

```bash
# Build and run
docker compose up

# Or build manually
docker build -t ado-mcp:local .
docker run -p 8080:8080 --env-file .env ado-mcp:local
```

## Compose Variants

### Test runner compose

Runs the test suite inside a container:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test
```

### GHCR pull compose

Pulls and runs the prebuilt image from GitHub Container Registry:

```bash
docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

## Running in MCP stdio mode (Claude/Cline)

Set `MCP_TRANSPORT=stdio` to run JSON-RPC over stdin/stdout:

```bash
MCP_TRANSPORT=stdio python -m app.main
```

### Example MCP client config

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "python",
      "args": ["-m", "app.main"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "ADO_ORG": "https://dev.azure.com/yourorg",
        "ADO_PROJECT": "YourProject",
        "ADO_PAT": "YOUR_PAT_HERE",
        "ADO_API_VERSION": "7.1-preview.3"
      }
    }
  }
}
```

Phase 1 MCP methods implemented:
- `initialize`
- `tools/list`
- `tools/call`

## API Endpoints

### Health Check
```bash
curl -s http://localhost:8080/health | jq
```

### Tools Manifest
```bash
curl -s http://localhost:8080/tools | jq
```

### Search Work Items
```bash
curl -s -X POST http://localhost:8080/tool/ado.search_work_items \
  -H 'Content-Type: application/json' \
  -d '{
    "wiql": "SELECT [System.Id],[System.Title] FROM WorkItems WHERE [System.TeamProject]=@project ORDER BY [System.ChangedDate] DESC",
    "top": 25
  }' | jq
```

### Get Work Item
```bash
curl -s http://localhost:8080/tool/ado.get_work_item/12345 | jq
```

### List Repositories
```bash
curl -s http://localhost:8080/tool/ado.list_repositories | jq
```

### List Pull Requests
```bash
curl -s "http://localhost:8080/tool/ado.list_pull_requests?repository_id=<repo-id>&status=active&top=25" | jq
```

### List Builds
```bash
curl -s "http://localhost:8080/tool/ado.list_builds?top=25" | jq
```

### Create Work Item (guarded write)
```bash
curl -s -X POST http://localhost:8080/tool/ado.create_work_item \
  -H 'Content-Type: application/json' \
  -d '{
    "work_item_type": "Task",
    "fields": {
      "System.Title": "Created from ADO MCP",
      "System.Description": "Write path test"
    }
  }' | jq
```

### Update Work Item (guarded write)
```bash
curl -s -X POST http://localhost:8080/tool/ado.update_work_item \
  -H 'Content-Type: application/json' \
  -d '{
    "id": 12345,
    "fields": {
      "System.State": "Active"
    }
  }' | jq
```

### Add PR Comment (guarded write)
```bash
curl -s -X POST http://localhost:8080/tool/ado.add_pr_comment \
  -H 'Content-Type: application/json' \
  -d '{
    "repository_id": "<repo-id>",
    "pull_request_id": 123,
    "content": "Looks good from MCP"
  }' | jq
```

> Write tools are disabled by default. Set `ADO_ALLOW_WRITES=true` to enable.

## Phase 4 Hardening

- Structured error mapping:
  - Validation errors -> HTTP 400 / MCP `-32602`
  - Auth/authz errors from Azure DevOps -> HTTP 401 / mapped MCP server error
  - Upstream Azure errors -> HTTP 502 / mapped MCP server error
- Secret redaction in logs for common token patterns (`ADO_PAT=...`, bearer tokens, `token=...`).
- Stricter validation:
  - bounded `top` values (1..1000)
  - PR status allowlist (`active|abandoned|completed|all`)
  - guarded write content size checks

## WIQL Examples

### Get all active user stories
```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] IN ('User Story','Task','Bug')
  AND [System.State] <> 'Done'
ORDER BY [System.ChangedDate] DESC
```

## Testing

```bash
# Run tests
pytest -q
```

## License

MIT
