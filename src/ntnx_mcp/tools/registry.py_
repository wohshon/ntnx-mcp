"""Tool registry - defines all available tools for each namespace."""

from typing import Any

from ntnx_mcp.tools.base import (
    ODATA_PARAMS,
    create_action_tool,
    create_delete_tool,
    create_get_tool,
    create_list_tool,
)


class ToolRegistry:
    """Registry of all MCP tools mapped to Prism Central API operations."""

    @staticmethod
    def vmm_tools() -> list[dict[str, Any]]:
        """Virtual Machine Management tools."""
        return [
            {
                "name": "v3_vms_list",
                "description": "List virtual machines using v3 API (use this for older Prism Central or when v4 fails)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Filter expression (e.g., 'vm_name==db.*' for VMs starting with 'db')",
                        },
                        "length": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 100)",
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset for pagination (default: 0)",
                        },
                    },
                },
                "metadata": {
                    "namespace": "v3",
                    "entity": "vms",
                    "operation": "v3_list",
                    "kind": "vm",
                },
            },
            create_list_tool(
                "vmm_list",
                "vmm",
                "ahv/config/vms",
                "List virtual machines in Prism Central",
            ),
            create_get_tool(
                "vmm_get",
                "vmm",
                "ahv/config/vms",
                "Get virtual machine details by ID",
                id_param="vm_id",
                id_description="Virtual machine ID (UUID)",
            ),
            {
                "name": "vmm_create",
                "description": "Create a new virtual machine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "VM name"},
                        "num_vcpus": {"type": "integer", "description": "Number of vCPUs"},
                        "memory_gb": {"type": "number", "description": "Memory in GB"},
                        "cluster_id": {"type": "string", "description": "Cluster ID to deploy on"},
                        "subnet_id": {"type": "string", "description": "Subnet ID for NIC"},
                        "disk_size_gb": {"type": "number", "description": "Boot disk size in GB"},
                        "image_id": {"type": "string", "description": "Image ID for boot disk"},
                    },
                    "required": ["name", "cluster_id"],
                },
                "metadata": {"namespace": "vmm", "entity": "ahv/config/vms", "operation": "create"},
            },
            create_delete_tool(
                "vmm_delete",
                "vmm",
                "ahv/config/vms",
                "Delete a virtual machine",
                id_param="vm_id",
                id_description="Virtual machine ID (UUID)",
            ),
            {
                "name": "vmm_power_on",
                "description": "Power on a virtual machine",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vm_id": {"type": "string", "description": "Virtual machine ID (UUID)"},
                    },
                    "required": ["vm_id"],
                },
                "metadata": {
                    "namespace": "vmm",
                    "entity": "ahv/config/vms",
                    "operation": "power_state",
                    "target_power_state": "ON",
                    "id_param": "vm_id",
                },
            },
            {
                "name": "vmm_power_off",
                "description": "Power off a virtual machine (hard power off)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vm_id": {"type": "string", "description": "Virtual machine ID (UUID)"},
                    },
                    "required": ["vm_id"],
                },
                "metadata": {
                    "namespace": "vmm",
                    "entity": "ahv/config/vms",
                    "operation": "power_state",
                    "target_power_state": "OFF",
                    "id_param": "vm_id",
                },
            },
            {
                "name": "vmm_guest_shutdown",
                "description": "Gracefully shutdown a VM (ACPI signal)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vm_id": {"type": "string", "description": "Virtual machine ID (UUID)"},
                    },
                    "required": ["vm_id"],
                },
                "metadata": {
                    "namespace": "vmm",
                    "entity": "ahv/config/vms",
                    "operation": "power_state",
                    "target_power_state": "OFF",
                    "id_param": "vm_id",
                },
            },
            {
                "name": "vmm_reset",
                "description": "Reset (hard reboot) a virtual machine by powering off then on",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vm_id": {"type": "string", "description": "Virtual machine ID (UUID)"},
                    },
                    "required": ["vm_id"],
                },
                "metadata": {
                    "namespace": "vmm",
                    "entity": "ahv/config/vms",
                    "operation": "power_state",
                    "target_power_state": "OFF",
                    "id_param": "vm_id",
                    "then_power_on": True,
                },
            },
            {
                "name": "vmm_guest_reboot",
                "description": "Reboot a VM by gracefully shutting down then powering on",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vm_id": {"type": "string", "description": "Virtual machine ID (UUID)"},
                    },
                    "required": ["vm_id"],
                },
                "metadata": {
                    "namespace": "vmm",
                    "entity": "ahv/config/vms",
                    "operation": "power_state",
                    "target_power_state": "OFF",
                    "id_param": "vm_id",
                    "then_power_on": True,
                },
            },
            create_list_tool(
                "vmm_images_list",
                "vmm",
                "content/images",
                "List disk images in Prism Central",
            ),
            create_get_tool(
                "vmm_image_get",
                "vmm",
                "content/images",
                "Get image details by ID",
                id_param="image_id",
                id_description="Image ID (UUID)",
            ),
        ]

    @staticmethod
    def clustermgmt_tools() -> list[dict[str, Any]]:
        """Cluster Management tools."""
        return [
            create_list_tool(
                "clustermgmt_clusters_list",
                "clustermgmt",
                "config/clusters",
                "List clusters managed by Prism Central",
            ),
            create_get_tool(
                "clustermgmt_cluster_get",
                "clustermgmt",
                "config/clusters",
                "Get cluster details by ID",
                id_param="cluster_id",
                id_description="Cluster ID (UUID)",
            ),
            create_list_tool(
                "clustermgmt_hosts_list",
                "clustermgmt",
                "config/hosts",
                "List hosts across all clusters",
            ),
            create_get_tool(
                "clustermgmt_host_get",
                "clustermgmt",
                "config/hosts",
                "Get host details by ID",
                id_param="host_id",
                id_description="Host ID (UUID)",
            ),
        ]

    @staticmethod
    def networking_tools() -> list[dict[str, Any]]:
        """Networking tools."""
        return [
            create_list_tool(
                "networking_subnets_list",
                "networking",
                "config/subnets",
                "List subnets/networks",
            ),
            create_get_tool(
                "networking_subnet_get",
                "networking",
                "config/subnets",
                "Get subnet details by ID",
                id_param="subnet_id",
                id_description="Subnet ID (UUID)",
            ),
            {
                "name": "networking_subnet_create",
                "description": "Create a new subnet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Subnet name"},
                        "subnet_type": {"type": "string", "description": "VLAN or OVERLAY"},
                        "cluster_id": {"type": "string", "description": "Cluster ID"},
                        "vlan_id": {"type": "integer", "description": "VLAN ID (for VLAN type)"},
                        "network_ip": {
                            "type": "string",
                            "description": "Network IP (e.g., 10.0.0.0)",
                        },
                        "prefix_length": {
                            "type": "integer",
                            "description": "Prefix length (e.g., 24)",
                        },
                        "gateway_ip": {"type": "string", "description": "Default gateway IP"},
                    },
                    "required": ["name", "subnet_type", "cluster_id"],
                },
                "metadata": {
                    "namespace": "networking",
                    "entity": "config/subnets",
                    "operation": "create",
                },
            },
            create_delete_tool(
                "networking_subnet_delete",
                "networking",
                "config/subnets",
                "Delete a subnet",
                id_param="subnet_id",
                id_description="Subnet ID (UUID)",
            ),
            create_list_tool(
                "networking_vpcs_list",
                "networking",
                "config/vpcs",
                "List Virtual Private Clouds",
            ),
            create_list_tool(
                "networking_floating_ips_list",
                "networking",
                "config/floating-ips",
                "List floating IPs",
            ),
        ]

    @staticmethod
    def storage_tools() -> list[dict[str, Any]]:
        """Storage tools (under clustermgmt namespace in v4)."""
        return [
            create_list_tool(
                "storage_containers_list",
                "clustermgmt",
                "config/storage-containers",
                "List storage containers",
            ),
            create_get_tool(
                "storage_container_get",
                "clustermgmt",
                "config/storage-containers",
                "Get storage container details by ID",
                id_param="container_id",
                id_description="Storage container ID (UUID)",
            ),
        ]

    @staticmethod
    def volumes_tools() -> list[dict[str, Any]]:
        """Volumes tools."""
        return [
            create_list_tool(
                "volumes_groups_list",
                "volumes",
                "config/volume-groups",
                "List volume groups",
            ),
            create_get_tool(
                "volumes_group_get",
                "volumes",
                "config/volume-groups",
                "Get volume group details by ID",
                id_param="volume_group_id",
                id_description="Volume group ID (UUID)",
            ),
            {
                "name": "volumes_group_create",
                "description": "Create a new volume group",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Volume group name"},
                        "cluster_id": {"type": "string", "description": "Cluster ID"},
                        "description": {"type": "string", "description": "Description"},
                    },
                    "required": ["name", "cluster_id"],
                },
                "metadata": {
                    "namespace": "volumes",
                    "entity": "config/volume-groups",
                    "operation": "create",
                },
            },
            create_delete_tool(
                "volumes_group_delete",
                "volumes",
                "config/volume-groups",
                "Delete a volume group",
                id_param="volume_group_id",
                id_description="Volume group ID (UUID)",
            ),
        ]

    @staticmethod
    def monitoring_tools() -> list[dict[str, Any]]:
        """Monitoring tools (v4 uses serviceability/ sub-path, not config/)."""
        return [
            create_list_tool(
                "monitoring_alerts_list",
                "monitoring",
                "serviceability/alerts",
                "List alerts",
            ),
            create_get_tool(
                "monitoring_alert_get",
                "monitoring",
                "serviceability/alerts",
                "Get alert details by ID",
                id_param="alert_id",
                id_description="Alert ID (UUID)",
            ),
            create_action_tool(
                "monitoring_alert_acknowledge",
                "monitoring",
                "serviceability/alerts",
                "acknowledge",
                "Acknowledge an alert",
                id_param="alert_id",
                id_description="Alert ID (UUID)",
            ),
            create_action_tool(
                "monitoring_alert_resolve",
                "monitoring",
                "serviceability/alerts",
                "resolve",
                "Resolve an alert",
                id_param="alert_id",
                id_description="Alert ID (UUID)",
            ),
            create_list_tool(
                "monitoring_events_list",
                "monitoring",
                "serviceability/events",
                "List events",
            ),
            create_list_tool(
                "monitoring_audits_list",
                "monitoring",
                "serviceability/audits",
                "List audit logs",
            ),
        ]

    @staticmethod
    def dataprotection_tools() -> list[dict[str, Any]]:
        """Data Protection tools."""
        return [
            {
                "name": "v3_protection_rules_list",
                "description": "List protection rules/policies (v3 fallback -- not available in v4 on this PC build)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Filter expression",
                        },
                        "length": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 100)",
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset for pagination (default: 0)",
                        },
                    },
                },
                "metadata": {
                    "namespace": "v3",
                    "entity": "protection_rules",
                    "operation": "v3_list",
                    "kind": "protection_rule",
                },
            },
            create_list_tool(
                "dataprotection_recovery_points_list",
                "dataprotection",
                "config/recovery-points",
                "List recovery points (snapshots)",
            ),
            create_get_tool(
                "dataprotection_recovery_point_get",
                "dataprotection",
                "config/recovery-points",
                "Get recovery point details by ID",
                id_param="recovery_point_id",
                id_description="Recovery point ID (UUID)",
            ),
            create_list_tool(
                "dataprotection_consistency_groups_list",
                "dataprotection",
                "config/consistency-groups",
                "List consistency groups",
            ),
        ]

    @staticmethod
    def iam_tools() -> list[dict[str, Any]]:
        """Identity and Access Management tools."""
        return [
            create_list_tool(
                "iam_users_list",
                "iam",
                "authn/users",
                "List users",
            ),
            create_get_tool(
                "iam_user_get",
                "iam",
                "authn/users",
                "Get user details by ID",
                id_param="user_id",
                id_description="User ID (UUID)",
            ),
            create_list_tool(
                "iam_roles_list",
                "iam",
                "authz/roles",
                "List roles",
            ),
            create_get_tool(
                "iam_role_get",
                "iam",
                "authz/roles",
                "Get role details by ID",
                id_param="role_id",
                id_description="Role ID (UUID)",
            ),
            create_list_tool(
                "iam_directory_services_list",
                "iam",
                "authn/directory-services",
                "List directory services (AD, LDAP)",
            ),
        ]

    @staticmethod
    def microseg_tools() -> list[dict[str, Any]]:
        """Flow Management (microsegmentation) tools."""
        return [
            create_list_tool(
                "microseg_policies_list",
                "microseg",
                "config/policies",
                "List network security policies",
            ),
            create_get_tool(
                "microseg_policy_get",
                "microseg",
                "config/policies",
                "Get security policy details by ID",
                id_param="policy_id",
                id_description="Security policy ID (UUID)",
            ),
            create_list_tool(
                "microseg_address_groups_list",
                "microseg",
                "config/address-groups",
                "List address groups",
            ),
            create_list_tool(
                "microseg_service_groups_list",
                "microseg",
                "config/service-groups",
                "List service groups",
            ),
        ]

    @staticmethod
    def lifecycle_tools() -> list[dict[str, Any]]:
        """Lifecycle Management tools."""
        return [
            create_list_tool(
                "lifecycle_entities_list",
                "lifecycle",
                "resources/entities",
                "List LCM entities (software/firmware)",
            ),
            {
                "name": "lifecycle_recommendations_get",
                "description": "Get update recommendations",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
                "metadata": {
                    "namespace": "lifecycle",
                    "entity": "resources/recommendations",
                    "operation": "list",
                },
            },
        ]

    @staticmethod
    def prism_tools() -> list[dict[str, Any]]:
        """Prism Central management tools."""
        return [
            create_list_tool(
                "prism_tasks_list",
                "prism",
                "config/tasks",
                "List tasks",
            ),
            create_get_tool(
                "prism_task_get",
                "prism",
                "config/tasks",
                "Get task status by ID",
                id_param="task_id",
                id_description="Task ID (UUID)",
            ),
            create_list_tool(
                "prism_categories_list",
                "prism",
                "config/categories",
                "List categories",
            ),
            create_get_tool(
                "prism_category_get",
                "prism",
                "config/categories",
                "Get category details by key",
                id_param="category_key",
                id_description="Category key (e.g., 'Environment')",
            ),
        ]

    @staticmethod
    def aiops_tools() -> list[dict[str, Any]]:
        """AI Operations tools."""
        return [
            create_list_tool(
                "aiops_scenarios_list",
                "aiops",
                "config/scenarios",
                "List what-if scenarios",
            ),
        ]

    @staticmethod
    def files_tools() -> list[dict[str, Any]]:
        """Files tools."""
        return [
            create_list_tool(
                "files_servers_list",
                "files",
                "config/file-servers",
                "List file servers",
            ),
            create_get_tool(
                "files_server_get",
                "files",
                "config/file-servers",
                "Get file server details by ID",
                id_param="file_server_id",
                id_description="File server ID (UUID)",
            ),
            create_list_tool(
                "files_shares_list",
                "files",
                "config/mount-targets",
                "List file shares/mount targets",
            ),
        ]

    @staticmethod
    def objects_tools() -> list[dict[str, Any]]:
        """Objects Storage tools."""
        return [
            create_list_tool(
                "objects_stores_list",
                "objects",
                "config/object-stores",
                "List object stores",
            ),
            create_get_tool(
                "objects_store_get",
                "objects",
                "config/object-stores",
                "Get object store details by ID",
                id_param="object_store_id",
                id_description="Object store ID (UUID)",
            ),
        ]

    @staticmethod
    def licensing_tools() -> list[dict[str, Any]]:
        """Licensing tools."""
        return [
            {
                "name": "licensing_summary_get",
                "description": "Get licensing summary and compliance status",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
                "metadata": {
                    "namespace": "licensing",
                    "entity": "config/license-summary",
                    "operation": "get_single",
                },
            },
            create_list_tool(
                "licensing_allowances_list",
                "licensing",
                "config/allowances",
                "List license allowances/entitlements",
            ),
        ]

    @staticmethod
    def security_tools() -> list[dict[str, Any]]:
        """Security tools (security_config_get removed -- not available in v4 on this PC build)."""
        return []

    @staticmethod
    def datapolicies_tools() -> list[dict[str, Any]]:
        """Data Policies tools."""
        return [
            create_list_tool(
                "datapolicies_storage_policies_list",
                "datapolicies",
                "config/storage-policies",
                "List storage policies",
            ),
        ]

    @staticmethod
    def opsmgmt_tools() -> list[dict[str, Any]]:
        """NCM Operations Management tools."""
        return [
            create_list_tool(
                "opsmgmt_reports_list",
                "opsmgmt",
                "config/reports",
                "List reports",
            ),
            create_get_tool(
                "opsmgmt_report_get",
                "opsmgmt",
                "config/reports",
                "Get report details by ID",
                id_param="report_id",
                id_description="Report ID (UUID)",
            ),
        ]


def get_all_tools() -> list[dict[str, Any]]:
    """Get all tool definitions from all namespaces."""
    tools: list[dict[str, Any]] = []
    tools.extend(ToolRegistry.vmm_tools())
    tools.extend(ToolRegistry.clustermgmt_tools())
    tools.extend(ToolRegistry.networking_tools())
    tools.extend(ToolRegistry.storage_tools())
    tools.extend(ToolRegistry.volumes_tools())
    tools.extend(ToolRegistry.monitoring_tools())
    tools.extend(ToolRegistry.dataprotection_tools())
    tools.extend(ToolRegistry.iam_tools())
    tools.extend(ToolRegistry.microseg_tools())
    tools.extend(ToolRegistry.lifecycle_tools())
    tools.extend(ToolRegistry.prism_tools())
    tools.extend(ToolRegistry.aiops_tools())
    tools.extend(ToolRegistry.files_tools())
    tools.extend(ToolRegistry.objects_tools())
    tools.extend(ToolRegistry.licensing_tools())
    tools.extend(ToolRegistry.security_tools())
    tools.extend(ToolRegistry.datapolicies_tools())
    tools.extend(ToolRegistry.opsmgmt_tools())
    return tools
