"""Tool registry - defines a limited subset of available tools."""

from typing import Any

# Only import what we are actually using to avoid errors
from ntnx_mcp.tools.base import (
    ODATA_PARAMS,  # Kept in case other files import it from here
    create_get_tool,
    create_list_tool,
)


class ToolRegistry:
    """Registry of a curated subset of MCP tools mapped to Prism Central API operations."""

    @staticmethod
    def curated_tools() -> list[dict[str, Any]]:
        """Returns exactly 5 core management tools."""
        return [
            # 1. Your requested tool
            create_list_tool(
                "vmm_list",
                "vmm",
                "ahv/config/vms",
                "List virtual machines in Prism Central",
            ),
            # 2. VM Details Lookup
            create_get_tool(
                "vmm_get",
                "vmm",
                "ahv/config/vms",
                "Get virtual machine details by ID",
                id_param="vm_id",
                id_description="Virtual machine ID (UUID)",
            ),
            # 3. Cluster Lookup
            create_list_tool(
                "clustermgmt_clusters_list",
                "clustermgmt",
                "config/clusters",
                "List clusters managed by Prism Central",
            ),
            # 4. Network Lookup
            create_list_tool(
                "networking_subnets_list",
                "networking",
                "config/subnets",
                "List subnets/networks",
            ),
            # 5. Storage Lookup
            create_list_tool(
                "storage_containers_list",
                "clustermgmt",
                "config/storage-containers",
                "List storage containers",
            ),
        ]


def get_all_tools() -> list[dict[str, Any]]:
    """Get exactly 5 curated tool definitions."""
    return ToolRegistry.curated_tools()
