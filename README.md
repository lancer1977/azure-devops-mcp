# ADO MCP

Azure DevOps MCP Wrapper - A Flask-based API service that wraps Azure DevOps REST APIs behind an MCP-style tool surface.

## Overview

This is a read-only V1 implementation that provides:
- List work items by WIQL query
- Get a work item by ID
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
```

## Running with Docker

```bash
# Build and run
docker compose up

# Or build manually
docker build -t ado-mcp:local .
docker run -p 8080:8080 --env-file .env ado-mcp:local
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
```

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
