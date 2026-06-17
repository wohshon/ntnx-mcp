"""MCP Server implementation for Nutanix Prism Central."""
import json
import sys
from typing import Any
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.config import Settings, get_settings
from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.tools.registry import get_all_tools

def get_app():
    settings = get_settings()
    client = PrismCentralClient(settings)
    executor = ToolExecutor(client)
    
    # 1. Fetch the raw tools from your registry
    raw_tools = get_all_tools()
    
    # 2. CRITICAL FIX: Actually register the tools into the ToolExecutor runtime dictionary
    for tool in raw_tools:
        executor.register_tool(tool)
    
    # 3. Format tools for the schema lookup/discovery
    formatted_tools = [
        {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]} 
        for t in raw_tools
    ]

    async def mcp_endpoint(request: Request):
        body = await request.body()
        print(f"-> RECEIVED REQUEST: {request.method} {request.url.path}", file=sys.stderr)
        if body:
            print(f"-> BODY: {body.decode('utf-8')}", file=sys.stderr)

        if request.method == "GET":
            return JSONResponse({"status": "healthy"})

        if request.method == "POST":
            payload = await request.json()
            method = payload.get("method")
            msg_id = payload.get("id")
            
            if method == "initialize":
                client_version = payload.get("params", {}).get("protocolVersion", "2024-11-05")
                return JSONResponse({
                    "jsonrpc": "2.0", 
                    "id": msg_id, 
                    "result": {
                        "protocolVersion": client_version,
                        "capabilities": {"tools": {}, "resources": {}, "prompts": {}}, 
                        "serverInfo": {"name": "ntnx_mcp", "version": "1.0.0"}
                    }
                })

            elif method == "notifications/initialized":
                return JSONResponse({"jsonrpc": "2.0", "result": {}})
            
            elif method == "tools/list":
                return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": formatted_tools}})

            elif method == "tools/call":
                params = payload.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                # Now that tools are registered, this will map safely down to your client!
                result = await executor.execute(tool_name, tool_args)
                
                return JSONResponse({
                    "jsonrpc": "2.0", 
                    "id": msg_id, 
                    "result": {
                        "content": [
                            {
                                "type": "text", 
                                "text": json.dumps(result)
                            }
                        ]
                    }
                })

            return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": {}})

        if request.method == "DELETE":
            return Response(status_code=202)
            
        return JSONResponse({"error": "Method not allowed"}, status_code=405)

    return Starlette(debug=True, routes=[Route("/mcp", mcp_endpoint, methods=["POST", "DELETE", "GET"])])

def main() -> None:
    """Entry point: Start Uvicorn directly."""
    app = get_app()
    print("Starting Starlette-based MCP server on port 8080", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()



