
Add on notes:


---
# ntnx-mcp

An MCP (Model Context Protocol) server that connects AI assistants to the Nutanix Prism Central v4 API. This gives any MCP-compatible AI agent (Cursor, Claude Desktop, etc.) the ability to manage Nutanix infrastructure through natural language.

## What It Does

The server exposes 60+ tools covering the full Nutanix v4 API surface:

| Namespace | Tools | Examples |
|-----------|-------|----------|
| **Virtual Machines** (vmm) | list, get, create, delete, power on/off, shutdown, reset, reboot | "List all VMs on the cluster" |
| **Cluster Management** (clustermgmt) | clusters, hosts, storage containers | "Show me host utilization" |
| **Networking** (networking) | subnets, VPCs, floating IPs | "What subnets are available?" |
| **Monitoring** (monitoring) | alerts, events, audit logs | "Are there any critical alerts?" |
| **Data Protection** (dataprotection) | recovery points, consistency groups, protection rules | "List recent snapshots" |
| **IAM** (iam) | users, roles, directory services | "Who has admin access?" |
| **Microsegmentation** (microseg) | security policies, address groups, service groups | "Show network security policies" |
| **Lifecycle** (lifecycle) | LCM entities, update recommendations | "What firmware needs updating?" |
| **Prism** (prism) | tasks, categories | "Show running tasks" |
| **Storage** (volumes) | volume groups | "List all volume groups" |
| **Files** (files) | file servers, shares | "What file servers exist?" |
| **Objects** (objects) | object stores | "List object stores" |
| **AIOps** (aiops) | what-if scenarios | "Show capacity scenarios" |
| **Licensing** (licensing) | license summary, allowances | "Check license compliance" |
| **Data Policies** (datapolicies) | storage policies | "List storage policies" |
| **Operations** (opsmgmt) | reports | "Show available reports" |

## Quick Start

### Prerequisites

- Python 3.10+
- Access to a Nutanix Prism Central instance (PC 7.3+ for v4 API)
- Either username/password or an API key for authentication

### Install

```bash
git clone https://github.com/script-repo/ntnx-mcp.git
cd ntnx-mcp
pip install -e .
```

### Configure

Copy the example environment file and fill in your Prism Central details:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
PRISM_CENTRAL_HOST=your-pc-ip-or-fqdn

# Option 1: API key (recommended for service accounts)
PRISM_CENTRAL_API_KEY=your-api-key-here

# Option 2: Username/password
# PRISM_CENTRAL_USERNAME=admin
# PRISM_CENTRAL_PASSWORD=your-password

# Optional
# PRISM_CENTRAL_PORT=9440
# PRISM_CENTRAL_VERIFY_SSL=true
# PRISM_CENTRAL_TIMEOUT=30
```

### Run Standalone

```bash
python -m ntnx_mcp
```

The server communicates over stdio (MCP protocol), so it's meant to be launched by an AI client, not run interactively.

## Setting Up with AI Clients

### Cursor IDE

Add to your global MCP config at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "nutanix": {
      "command": "python",
      "args": ["-m", "ntnx_mcp"],
      "cwd": "/path/to/ntnx-mcp",
      "env": {
        "PRISM_CENTRAL_HOST": "your-pc-ip",
        "PRISM_CENTRAL_API_KEY": "your-api-key",
        "PRISM_CENTRAL_VERIFY_SSL": "false"
      }
    }
  }
}
```

Or if you installed the package globally:

```json
{
  "mcpServers": {
    "nutanix": {
      "command": "ntnx-mcp",
      "env": {
        "PRISM_CENTRAL_HOST": "your-pc-ip",
        "PRISM_CENTRAL_API_KEY": "your-api-key",
        "PRISM_CENTRAL_VERIFY_SSL": "false"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nutanix": {
      "command": "python",
      "args": ["-m", "ntnx_mcp"],
      "cwd": "/path/to/ntnx-mcp",
      "env": {
        "PRISM_CENTRAL_HOST": "your-pc-ip",
        "PRISM_CENTRAL_API_KEY": "your-api-key",
        "PRISM_CENTRAL_VERIFY_SSL": "false"
      }
    }
  }
}
```

### Docker

```bash
docker build -t ntnx-mcp .
docker run --rm \
  -e PRISM_CENTRAL_HOST=your-pc-ip \
  -e PRISM_CENTRAL_API_KEY=your-api-key \
  -e PRISM_CENTRAL_VERIFY_SSL=false \
  ntnx-mcp
```

## Authentication

The server supports two authentication methods:

### API Key (Recommended)

Create a service account in Prism Central under **Admin > IAM > Service Accounts**, generate an API key, and assign an authorization policy with the appropriate role and scope.

```env
PRISM_CENTRAL_API_KEY=your-api-key-here
```

The API key is sent via the `X-Ntnx-Api-Key` header. This is the recommended method for automated/agent use.

### Basic Auth

```env
PRISM_CENTRAL_USERNAME=admin
PRISM_CENTRAL_PASSWORD=your-password
```

If both are set, the API key takes precedence.

## Walk-Through: First Conversation

Once the MCP server is configured in your AI client, you can interact with Nutanix through natural language. Here's a typical first session:

**1. Check connectivity**

> "List the clusters managed by Prism Central"

The agent calls `clustermgmt_clusters_list` and returns cluster names, IDs, and node counts.

**2. Explore the environment**

> "How many VMs are running? Show me the top 10 by memory"

The agent calls `vmm_list` with OData parameters to filter and sort.

**3. Investigate alerts**

> "Are there any critical alerts I should look at?"

The agent calls `monitoring_alerts_list` with a severity filter.

**4. Take action**

> "Shut down the test VM named dev-scratch"

The agent calls `vmm_list` to find the VM by name, then `vmm_guest_shutdown` to power it down gracefully.

**5. Audit changes**

> "Show me the last 10 tasks"

The agent calls `prism_tasks_list` with `top=10` and `orderby=startedTime desc`.

## Example Prompts

### Infrastructure Overview

```
"Give me a summary of the cluster — how many hosts, VMs, storage containers, and what's the resource utilization?"

"List all hosts and their CPU/memory specs"

"Show all storage containers and their usage"
```

### VM Management

```
"List all powered-off VMs that have more than 8GB of memory allocated"

"Create a new VM called web-server-01 with 4 vCPUs and 8GB RAM on cluster <id>"

"Power off the VM with ID <uuid>, change its memory to 16GB, then start it back up"

"Find all VMs with 'test' in the name"
```

### Networking

```
"What subnets are available and which VLANs are they on?"

"Show me all VPCs"

"Create a new VLAN subnet called dev-net on VLAN 100"
```

### Security & Compliance

```
"List all network security policies"

"Who are the admin users?"

"Show me the IAM roles and how many operations each has"

"Check the licensing status — are we compliant?"
```

### Monitoring & Troubleshooting

```
"Show me all unresolved alerts from the last 24 hours"

"What events happened today?"

"Pull the last 50 audit log entries"

"Are there any LCM updates available?"
```

### Data Protection

```
"List all protection rules"

"How many recovery points exist?"

"Show consistency groups"
```

### Capacity Planning

```
"Run through the what-if scenarios in AIOps"

"Show the current storage policies"

"What reports are available?"
```

## OData Query Support

All list tools support OData query parameters for filtering, sorting, and pagination:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `filter` | OData filter expression | `name eq 'my-vm'` |
| `orderby` | Sort field and direction | `name asc` |
| `top` | Max results to return | `10` |
| `skip` | Results to skip (pagination) | `20` |
| `select` | Fields to include | `name,extId,powerState` |
| `expand` | Related entities to include | `cluster` |

The AI agent translates natural language into these parameters automatically.

## Architecture

```
AI Client (Cursor, Claude, etc.)
    │
    │  MCP Protocol (stdio)
    │
    ▼
┌─────────────────────────┐
│   ntnx-mcp server       │
│                         │
│  server.py   ─── MCP protocol handler
│  executor.py ─── tool dispatch + business logic
│  client.py   ─── HTTP client (httpx, async)
│  config.py   ─── env-based configuration
│  tools/      ─── tool definitions
│    base.py   ─── shared schemas (OData, CRUD helpers)
│    registry.py── all 60+ tool definitions
└─────────────────────────┘
    │
    │  HTTPS (v4 REST API)
    │
    ▼
┌─────────────────────────┐
│  Nutanix Prism Central  │
│  (v4 API on port 9440)  │
└─────────────────────────┘
```

### How It Works

1. The AI client launches `ntnx-mcp` as a subprocess
2. The server registers 60+ tools mapped to Prism Central API operations
3. When the AI decides to call a tool, the executor translates the call into an HTTP request
4. Results are returned as JSON through the MCP protocol
5. The AI interprets the results and presents them in natural language

### Key Design Decisions

- **v4 API first**: All tools target the Nutanix v4 API with v3 fallbacks only where v4 endpoints are unavailable
- **ETag-based updates**: VM power state changes use the v4 GET+PUT workflow with `If-Match` headers for optimistic concurrency
- **OData throughout**: Every list tool supports filtering, sorting, and pagination via OData query parameters
- **No SDK dependency**: Uses raw HTTP (httpx) for maximum compatibility and transparency

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ntnx_mcp

# Type check
mypy src/ntnx_mcp
```

## v4 API Compatibility

This server targets the Nutanix v4 API (GA). See the [Nutanix v4 API Reference](https://www.nutanix.dev/api-reference-v4/) for full documentation.

| Requirement | Minimum Version |
|-------------|----------------|
| Prism Central | PC 7.3+ |
| AOS | 7.3+ |
| Python | 3.10+ |

> **Note**: Nutanix legacy API versions (v0.8, v1, v2, v3) will be deprecated in Q4 2026. This server is built for v4 to ensure long-term compatibility.

## License

MIT
