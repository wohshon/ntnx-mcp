"""MCP Server implementation for Nutanix Prism Central."""

from starlette.requests import Request
from starlette.responses import Response
import sys
import json
import asyncio
import uvicorn
from typing import Any
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool

from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.config import Settings, get_settings
from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.tools.registry import get_all_tools

def create_server(settings: Settings) -> tuple[Server, ToolExecutor]:
    """Create and configure the MCP server."""
    server = Server("ntnx-mcp")
    client = PrismCentralClient(settings)
    executor = ToolExecutor(client)

    all_tools = get_all_tools()
    for tool in all_tools:
        executor.register_tool(tool)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return the list of available tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["inputSchema"],
            )
            for tool in all_tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool and return the result."""
        result = await executor.execute(name, arguments or {})

        if "error" in result:
            error = result["error"]
            error_text = f"Error: {error.get('message', 'Unknown error')}"
            if error.get("details"):
                error_text += f"\nDetails: {error['details']}"
            if error.get("status_code"):
                error_text += f"\nStatus: {error['status_code']}"
            return [TextContent(type="text", text=error_text)]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return server, executor


import json
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

async def run_server() -> None:
    settings = get_settings()
    server, _ = create_server(settings)
    
    # We NO LONGER use SseServerTransport because NAI is stateless.

    async def asgi_wrapper(scope, receive, send):
        if scope["type"] == "http":
            if scope["method"] == "POST":
                request = Request(scope, receive)
                body = await request.body()
                
                try:
                    payload = json.loads(body)
                    method = payload.get("method")
                    msg_id = payload.get("id")
                    
                    print(f"-> NAI Executing Method: {method}", file=sys.stderr)
                    
                    # 1. THE HANDSHAKE
                    if method == "initialize":
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "protocolVersion": "2024-11-05", 
                                "capabilities": {"tools": {}},
                                "serverInfo": {"name": "ntnx_mcp", "version": "1.0.0"}
                            }
                        }
                        resp = JSONResponse(response_data)
                        return await resp(scope, receive, send)
                        
                    # 2. THE ACKNOWLEDGEMENT
                    elif method == "notifications/initialized":
                        # Notifications don't require a result body
                        resp = JSONResponse({"jsonrpc": "2.0"})
                        return await resp(scope, receive, send)
                        
                    # 3. THE TOOL DISCOVERY
                    elif method == "tools/list":
                        print(f"-> NAI REQUESTED TOOLS!", file=sys.stderr)
                        # We return an empty tools list for now just to prove the connection works.
                        # Once this connects, we will map your actual Nutanix tools here.
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {"tools": []}
                        }
                        resp = JSONResponse(response_data)
                        return await resp(scope, receive, send)
                        
                    else:
                        print(f"-> UNHANDLED NAI METHOD: {method}", file=sys.stderr)
                        resp = JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": {}})
                        return await resp(scope, receive, send)
                        
                except Exception as e:
                    print(f"-> JSON Parse Error: {e}", file=sys.stderr)
                    resp = Response("Bad Request", status_code=400)
                    return await resp(scope, receive, send)
                    
            elif scope["method"] == "DELETE":
                resp = Response(status_code=202)
                return await resp(scope, receive, send)

        resp = Response("Not Found", status_code=404)
        return await resp(scope, receive, send)

    print("Starting Stateless JSON-RPC MCP server on port 8080", file=sys.stderr)
    config = uvicorn.Config(asgi_wrapper, host="0.0.0.0", port=8080)
    await uvicorn.Server(config).serve()


def main() -> None:
    """Entry point for the MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
