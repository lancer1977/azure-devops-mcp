# ADO-MCP (Flask) – Cline Build Guide (Docker-first)

Christopher, this is a **Cline-friendly** implementation guide to build a repo that wraps **Azure DevOps REST APIs** behind an **MCP-style tool surface**.  
Goal: **read-only V1**, dockerized, env-var driven, easy to extend later.

> Assumptions  
> - Linux Mint (your default)  
> - You’ll run locally via Docker / docker compose  
> - Auth is **PAT** (Personal Access Token) in V1  
> - You want **strong enums/constants** instead of string soup

---

## 0) Repo name + intent

Suggested repo: `ado-mcp` (or `mcp-ado-wrapper`)

**V1 scope**
- List work items by WIQL query
- Get a work item by ID
- List recent builds (optional)
- Health endpoint
- Simple “tools manifest” endpoint describing available tools + JSON schemas

**V2 scope (later)**
- Update work items (write access)
- Sync to `features.json`
- Stream-safe task view projection for ChannelCheevos overlay

---

## 1) Cline “Plan Mode” prompt

Paste this into Cline (Plan Mode) and let it generate tasks + files:

```text
You are implementing a new repo called ado-mcp. Use Python + Flask. Create a Docker-first API service that wraps Azure DevOps REST APIs.

Requirements:
- Provide a REST API with endpoints:
  - GET /health
  - GET /tools  (returns a JSON manifest of tools, their descriptions, and input/output JSON schemas)
  - POST /tool/ado.search_work_items  (accepts query params; runs WIQL; returns work items)
  - GET /tool/ado.get_work_item/<id>  (returns full work item JSON)
- Use environment variables:
  - ADO_ORG (e.g. https://dev.azure.com/myorg)
  - ADO_PROJECT
  - ADO_PAT (PAT token)
  - ADO_API_VERSION (default 7.1-preview.3 or latest used in code)
  - PORT (default 8080)
  - LOG_LEVEL (default INFO)
- Implement a typed configuration module and validate required env vars at startup.
- Implement a small Azure DevOps client with requests, including retry/backoff for 429 and 5xx.
- Include constants/enums for common work item fields and states.
- Make it Docker friendly:
  - Dockerfile (multi-stage optional but fine if single stage)
  - docker-compose.yml
  - .env.example
- Include a README with run instructions and curl examples.
- Add basic unit tests (pytest) for config validation and tools manifest shape.
- Keep V1 read-only.
```

---

## 2) Repo structure (target)

```
ado-mcp/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    ado_client.py
    tools_manifest.py
    constants.py
    routes.py
  tests/
    test_config.py
    test_tools.py
  .env.example
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
  LICENSE
```

---

## 3) Environment variables

Create `.env.example`:

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

**Notes**
- Use PAT with basic auth: username can be anything, PAT is the password.
- Never commit `.env` or actual PAT.

---

## 4) Minimal Flask app design

### `app/config.py`
- Load env vars
- Validate required keys
- Expose `Settings` dataclass

### `app/ado_client.py`
- `AdoClient` with:
  - `wiql(query: str) -> dict`
  - `get_work_item(id: int) -> dict`
- Add retry/backoff for:
  - HTTP 429
  - HTTP 5xx

### Tool endpoints
You’re not implementing the MCP protocol itself in V1—just an **MCP-shaped surface** you can later adapt to a real MCP server runtime.

- `GET /tools` returns a JSON manifest with:
  - tool name
  - description
  - input schema
  - output schema

- `POST /tool/ado.search_work_items`
  - body: `{ "wiql": "SELECT ...", "top": 50 }`
  - output: `{ "workItems": [ { "id": 123, "url": "..." }, ... ], "count": 12 }`

- `GET /tool/ado.get_work_item/<id>`
  - output: raw work item JSON

---

## 5) WIQL examples you can ship in README

```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] IN ('User Story','Task','Bug')
  AND [System.State] <> 'Done'
ORDER BY [System.ChangedDate] DESC
```

You can allow clients to pass WIQL directly in V1 (read-only), and later add safe templates.

---

## 6) Docker-first setup

### `Dockerfile` (simple, production-ish)

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# default port
ENV PORT=8080
EXPOSE 8080

CMD ["python", "-m", "app.main"]
```

### `docker-compose.yml`

```yaml
services:
  ado-mcp:
    build: .
    ports:
      - "${PORT:-8080}:8080"
    env_file:
      - .env
    environment:
      - PORT=8080
    restart: unless-stopped
```

---

## 7) `requirements.txt`

Start minimal:

```txt
Flask==3.0.3
requests==2.32.3
python-dotenv==1.0.1
pydantic==2.8.2
pytest==8.3.2
```

(Version pins can be loosened later; V1 is about getting a stable wrapper.)

---

## 8) Strong constants/enums (avoid string soup)

Create `app/constants.py`:

- `WorkItemFields` constants:
  - `SYSTEM_ID = "System.Id"`
  - `SYSTEM_TITLE = "System.Title"`
  - `SYSTEM_STATE = "System.State"`
  - `SYSTEM_ASSIGNED_TO = "System.AssignedTo"`
  - etc.

- `WorkItemStates` (your org may differ; keep generic):
  - `NEW`, `ACTIVE`, `RESOLVED`, `CLOSED`, `DONE`

In V1 these are primarily for:
- building WIQL templates later
- normalizing results for the task overlay

---

## 9) Testing goals (lightweight)

### `tests/test_config.py`
- missing `ADO_ORG` fails validation
- missing `ADO_PROJECT` fails validation
- missing `ADO_PAT` fails validation

### `tests/test_tools.py`
- `GET /tools` returns JSON
- has required keys: `tools`, each tool has `name`, `description`, `input_schema`, `output_schema`

---

## 10) README content checklist

Include:
- What it is
- Env vars
- Docker run
- Local run
- Example curl calls

Example curl:

```bash
curl -s http://localhost:8080/health | jq

curl -s http://localhost:8080/tools | jq

curl -s -X POST http://localhost:8080/tool/ado.search_work_items \
  -H 'Content-Type: application/json' \
  -d '{
    "wiql": "SELECT [System.Id],[System.Title] FROM WorkItems WHERE [System.TeamProject]=@project ORDER BY [System.ChangedDate] DESC",
    "top": 25
  }' | jq

curl -s http://localhost:8080/tool/ado.get_work_item/12345 | jq
```

---

## 11) Next-step hooks (for future you)

Add TODOs (not implementation yet):
- `tool/ado.get_active_tasks(assigned_to?)`
- `tool/ado.get_sprint_state()`
- `tool/taskview.snapshot()` (stream-safe projection)
- `tool/docs.report_drift()` (compare features.json vs docs)

This is where you connect:
- **Task View MCP** + **ChannelCheevos overlay**
- “what I’m doing right now” on stream
- future goal / plan status dashboards

---

## 12) Definition of Done (V1)

- [ ] Docker build works
- [ ] `docker compose up` runs service
- [ ] `/health` returns ok
- [ ] `/tools` lists tools with schemas
- [ ] `ado.search_work_items` runs WIQL and returns IDs
- [ ] `ado.get_work_item/<id>` returns JSON
- [ ] Basic tests pass in CI/local

---

## 13) Optional: add a tiny Makefile (quality-of-life)

```makefile
.PHONY: run test docker

run:
	python -m app.main

test:
	pytest -q

docker:
	docker build -t ado-mcp:local .
```

---

## 14) If you want “real MCP protocol” later

Once this wrapper exists, you can:
- replace/augment Flask routes with an MCP server runtime
- keep the same internal client + tool functions
- expose them through MCP tool registration instead of REST endpoints

V1 gets you moving without a protocol rabbit hole.
