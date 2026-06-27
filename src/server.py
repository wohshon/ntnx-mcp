import os
import inspect
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Nutanix business logic imports
from ntnx_mcp.tools.registry import ToolRegistry
from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.config import get_settings

port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("mcp_project")

# Initialize Nutanix components
settings = get_settings()
client = PrismCentralClient(settings)
executor = ToolExecutor(client)

type_mapping = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "list",
    "object": "dict"
}

# Register the modular tools dynamically with explicit keyword signatures
nutanix_tools = ToolRegistry.vmm_tools()

for tool_def in nutanix_tools:
    executor.register_tool(tool_def)
    tool_name = tool_def["name"]
    tool_desc = tool_def.get("description", "Nutanix Tool Execution")
    
    properties = tool_def.get("input_schema", {}).get("properties", {})
    required = tool_def.get("input_schema", {}).get("required", [])
    
    # Dynamically compile clean Python signatures so FastMCP inspects true arguments
    args = []
    for param_name, prop_info in properties.items():
        json_type = prop_info.get("type", "string")
        py_type = type_mapping.get(json_type, "str")
        if param_name in required:
            args.append(f"{param_name}: {py_type}")
        else:
            args.append(f"{param_name}: {py_type} = None")
            
    args.sort(key=lambda x: "= None" in x)
    args_str = ", ".join(args)
    
    func_source = f"""
async def {tool_name}({args_str}):
    \"\"\"{tool_desc}\"\"\"
    kwargs = locals()
    return await executor.execute("{tool_name}", kwargs)
"""
    local_namespace = {"executor": executor}
    exec(func_source, local_namespace)
    dynamic_func = local_namespace[tool_name]
    
    mcp.tool()(dynamic_func)

# 1. Extract the underlying Starlette ASGI app for Streamable HTTP
base_app = mcp.streamable_http_app()

# Find the internal application instance to completely bypass Starlette's Mount redirects
mcp_sub_app = base_app
for route in getattr(base_app.router, "routes", []):
    if hasattr(route, "path") and route.path.startswith("/mcp"):
        if hasattr(route, "app"):
            mcp_sub_app = route.app
            break

# 2. Top-level ASGI router to normalize paths and eliminate client/server slash-redirect loops
async def raw_app(scope, receive, send):
    if scope["type"] == "http":
        path = scope["path"]
        # Directly map both variations straight to the root of the transport app
        if path in ("/mcp", "/mcp/"):
            scope["path"] = "/"
            if "raw_path" in scope:
                scope["raw_path"] = b"/"
            await mcp_sub_app(scope, receive, send)
            return
        elif path.startswith("/mcp/"):
            scope["path"] = path[4:]  # Strip '/mcp' prefix
            if "raw_path" in scope:
                scope["raw_path"] = scope["path"].encode()
            await mcp_sub_app(scope, receive, send)
            return

    # Forward all other scopes (lifespan initialization, etc.) to the base app
    await base_app(scope, receive, send)

# 3. Wrap the raw application with CORS middleware at the absolute outer edge
app = CORSMiddleware(
    raw_app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"]  # Critical for maintaining session state
)

if __name__ == "__main__":
    print(f"Starting MCP Server on port {port} via Uvicorn with CORS and Path Unification enabled...")
    # 4. Run the app directly using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
