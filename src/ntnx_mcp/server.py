import asyncio
import json
import uuid
import sys
import urllib.parse

from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.config import get_settings
from ntnx_mcp.tools.registry import get_all_tools

# Initialize Backend Connections
settings = get_settings()
executor = ToolExecutor(PrismCentralClient(settings))

# FETCH AND REGISTER TOOLS INTO THE EXECUTOR CONTEXT
tools_list = get_all_tools()
for tool in tools_list:
    executor.register_tool(tool)

# Track active SSE stream connections in memory
active_sessions = {}

async def handle_list_tools() -> list:
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t.get("inputSchema", {"type": "object", "properties": {}})
        }
        for t in tools_list
    ]

async def handle_call_tool(name: str, arguments: dict) -> dict:
    try:
        res = await executor.execute(name, arguments)
        return {"content": [{"type": "text", "text": str(res)}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error: {str(e)}"}]}

async def process_rpc(payload: dict) -> dict:
    """Core JSON-RPC router matching standard MCP syntax specs"""
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {}) if isinstance(payload.get("params"), dict) else {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "Nutanix-MCP", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        tools = await handle_list_tools()
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
    
    elif method == "tools/call":
        t_name = params.get("name") or payload.get("name")
        t_args = params.get("arguments") or {}
        result = await handle_call_tool(t_name, t_args)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    
    elif method == "notifications/initialized":
        return None
        
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method {method} not found"}}

async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    path = scope["path"].rstrip("/")
    method = scope["method"]
    query = urllib.parse.parse_qs(scope.get("query_string", b"").decode("utf-8"))

    # Global CORS Headers
    cors_headers = [
        (b"access-control-allow-origin", b"*"),
        (b"access-control-allow-methods", b"GET, POST, OPTIONS, DELETE"),
        (b"access-control-allow-headers", b"content-type, authorization, mcp-session-id"),
        (b"access-control-expose-headers", b"mcp-session-id"),
    ]

    if method == "OPTIONS":
        await send({"type": "http.response.start", "status": 200, "headers": cors_headers})
        await send({"type": "http.response.body", "body": b""})
        return

    # Route: GET /mcp -> Open clean native SSE stream channel
    if path == "/mcp" and method == "GET":
        session_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        active_sessions[session_id] = queue

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": cors_headers + [
                (b"content-type", b"text/event-stream"),
                (b"cache-control", b"no-cache"),
                (b"connection", b"keep-alive"),
                (b"mcp-session-id", session_id.encode("utf-8"))
            ]
        })

        init_message = f"event: endpoint\ndata: /mcp?session_id={session_id}\n\n"
        await send({"type": "http.response.body", "body": init_message.encode("utf-8"), "more_body": True})

        try:
            while True:
                msg = await queue.get()
                frame = f"event: message\ndata: {json.dumps(msg)}\n\n"
                await send({"type": "http.response.body", "body": frame.encode("utf-8"), "more_body": True})
                queue.task_done()
        except asyncio.CancelledError:
            pass
        finally:
            active_sessions.pop(session_id, None)
        return

    # Route: POST /mcp -> Processes both SSE client frames and NAI raw payloads
    if path == "/mcp" and method == "POST":
        body = b""
        more_body = True
        while more_body:
            msg = await receive()
            body += msg.get("body", b"")
            more_body = msg.get("more_body", False)

        try:
            payload = json.loads(body.decode("utf-8"))
            response_rpc = await process_rpc(payload)

            url_session = query.get("session_id", [None])[0]
            if url_session and url_session in active_sessions:
                if response_rpc:
                    await active_sessions[url_session].put(response_rpc)
                
                await send({"type": "http.response.start", "status": 202, "headers": cors_headers})
                await send({"type": "http.response.body", "body": b"Accepted"})
            else:
                res_body = json.dumps(response_rpc if response_rpc else {}).encode("utf-8")
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": cors_headers + [(b"content-type", b"application/json")]
                })
                await send({"type": "http.response.body", "body": res_body})
        except Exception as e:
            err_frame = json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": cors_headers + [(b"content-type", b"application/json")]
            })
            await send({"type": "http.response.body", "body": err_frame})
        return

    # Route: DELETE /mcp
    if path == "/mcp" and method == "DELETE":
        await send({"type": "http.response.start", "status": 200, "headers": cors_headers})
        await send({"type": "http.response.body", "body": b""})
        return

    # Catch-all 404
    await send({"type": "http.response.start", "status": 404, "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"Not Found"})
