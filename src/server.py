from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import random
from ntnx_mcp.tools.registry import ToolRegistry
from ntnx_mcp.client import PrismCentralClient
from ntnx_mcp.executor import ToolExecutor
from ntnx_mcp.config import get_settings

#
# Create MCP server
#
mcp = FastMCP(
    name="Demo MCP Server"
)
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

for tool_def in ToolRegistry.vmm_tools():
    executor.register_tool(tool_def)
    tool_name = tool_def["name"]
    tool_desc = tool_def.get("description", "Nutanix Tool")
    properties = tool_def.get("input_schema", {}).get("properties", {})
    required = tool_def.get("input_schema", {}).get("required", [])

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
    return await executor.execute("{tool_name}", locals())
"""
    local_namespace = {"executor": executor}
    exec(func_source, local_namespace)
    mcp.tool()(local_namespace[tool_name])


#
# Create the ASGI app with Streamable HTTP and CORS
#
app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    stateless_http=True,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id"],
        )
    ],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
      app,
      host="0.0.0.0",
      port=8000,
      log_level="debug",
    )
