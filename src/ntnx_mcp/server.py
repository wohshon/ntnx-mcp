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
    
    # We grab BOTH the server and the executor here
    server, executor = create_server(settings)
    
    # Pre-format the tools so they are ready for the NAI handshake
    from ntnx_mcp.tools.registry import get_all_tools
    raw_tools = get_all_tools()
    formatted_tools = [
        {
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t["inputSchema"]
        } for t in raw_tools
    ]

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
                        resp = JSONResponse({"jsonrpc": "2.0"})
                        return await resp(scope, receive, send)
                        
                    # 3. THE TOOL DISCOVERY (FIXED)
                    elif method == "tools/list":
                        print(f"-> Serving {len(formatted_tools)} tools to NAI!", file=sys.stderr)
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {"tools": formatted_tools}
                        }
                        resp = JSONResponse(response_data)
                        return await resp(scope, receive, send)
                    
                    # 4. TOOL EXECUTION (NEW: Actually run the tools!)
                    elif method == "tools/call":
                        params = payload.get("params", {})
                        tool_name = params.get("name")
                        tool_args = params.get("arguments", {})
                        print(f"-> NAI CALLING TOOL: {tool_name} with args: {tool_args}", file=sys.stderr)
                        
                        try:
                            # Pass the request to your Nutanix executor
                            result = await executor.execute(tool_name, tool_args)
                            
                            # Format the response back to NAI
                            if "error" in result:
                                error_text = f"Error: {result['error'].get('message', 'Unknown')}"
                                mcp_content = [{"type": "text", "text": error_text}]
                                is_error = True
                            else:
                                mcp_content = [{"type": "text", "text": json.dumps(result, indent=2)}]
                                is_error = False

                            response_data = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "result": {
                                    "content": mcp_content,
                                    "isError": is_error
                                }
                            }
                        except Exception as e:
                            print(f"-> Tool Execution Exception: {e}", file=sys.stderr)
                            response_data = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "error": {"code": -32603, "message": str(e)}
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
