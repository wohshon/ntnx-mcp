"""MCP Server implementation for Nutanix Prism Central."""

import sys
import asyncio
import uvicorn
from typing import Any
from starlette.applications import Starlette
from starlette.routing import Route

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool

from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.config import Settings, get_settings
from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.tools.registry import get_all_tools

# Add your existing create_server function here if it's in this file

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


async def run_server() -> None:
    settings = get_settings()
    # Ensure create_server is defined or imported
    server, _ = create_server(settings) 
    
    # Initialize transport
    sse = SseServerTransport("/messages")
    
    # Define app manually using confirmed methods
    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=sse.connect_sse),
            Route("/messages", endpoint=sse.handle_post_message, methods=["POST"]),
        ],
    )

    print(f"Starting Nutanix MCP server on port 8080", file=sys.stderr)
    
    # Start server
    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    await uvicorn.Server(config).serve()



def main() -> None:
    """Entry point for the MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
