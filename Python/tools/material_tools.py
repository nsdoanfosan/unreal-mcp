"""Material graph and material-layer tools for Unreal MCP."""

import logging
from typing import Any, Dict

from mcp.server.fastmcp import Context, FastMCP


logger = logging.getLogger("UnrealMCP")


def _send(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    from unreal_mcp_server import get_unreal_connection

    unreal = get_unreal_connection()
    if not unreal:
        return {"success": False, "message": "Failed to connect to Unreal Engine"}
    response = unreal.send_command(command, params)
    return response or {"success": False, "message": "No response from Unreal Engine"}


def register_material_tools(mcp: FastMCP):
    """Register material inspection and editing tools."""

    @mcp.tool()
    def dump_material_expression_graph(
        ctx: Context,
        asset_path: str,
    ) -> Dict[str, Any]:
        """Dump nodes and connections for a material or material function.

        Args:
            asset_path: Unreal object path such as /Game/Materials/M_Master.
        """
        try:
            return _send("dump_material_expression_graph", {"asset_path": asset_path})
        except Exception as exc:
            logger.exception("Material graph dump failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def build_hair_pixel_depth_offset_vertex_mask(
        ctx: Context,
        material_path: str = "/Game/Material/HairTool/Master/M_HT_HairCards",
        apply_changes: bool = False,
    ) -> Dict[str, Any]:
        """Build or audit a switchable VertexColor.R mask on hair Pixel Depth Offset.

        The Unreal side preserves the material's existing Pixel Depth Offset expression,
        multiplies it by a static switch named ``Use Vertex Color PDO Mask``, and uses
        neutral one when the switch is disabled. The operation is idempotent, refuses a
        dirty or partially modified target graph, compiles before saving, and rolls back
        on failure. Preview is the default.

        Args:
            material_path: Hair master material object path.
            apply_changes: False audits only; True creates, compiles, and saves the nodes.
        """
        try:
            return _send(
                "build_hair_pixel_depth_offset_vertex_mask",
                {
                    "material_path": material_path,
                    "apply_changes": bool(apply_changes),
                },
            )
        except Exception as exc:
            logger.exception("Hair Pixel Depth Offset vertex-mask operation failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def inspect_material_layer_stack(
        ctx: Context,
        material_interface_path: str,
    ) -> Dict[str, Any]:
        """Inspect layers, blends, link states, and scalar overrides on a material interface.

        Args:
            material_interface_path: Material or material-instance object path.
        """
        try:
            return _send(
                "inspect_material_layer_stack",
                {"material_interface_path": material_interface_path},
            )
        except Exception as exc:
            logger.exception("Material layer-stack inspection failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def set_material_function_scalar_default(
        ctx: Context,
        material_function_path: str,
        parameter_name: str,
        value: float,
    ) -> Dict[str, Any]:
        """Set and save one scalar-parameter default in a material function.

        The Unreal side refuses the edit if the target package already has unsaved changes.

        Args:
            material_function_path: Material-function object path.
            parameter_name: Exact scalar parameter name.
            value: New default value.
        """
        try:
            return _send(
                "set_material_function_scalar_default",
                {
                    "material_function_path": material_function_path,
                    "parameter_name": parameter_name,
                    "value": float(value),
                },
            )
        except Exception as exc:
            logger.exception("Material-function scalar edit failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def set_material_instance_scalar_override(
        ctx: Context,
        material_instance_path: str,
        parameter_name: str,
        association: str,
        index: int,
        value: float,
    ) -> Dict[str, Any]:
        """Set and save an existing scalar override on a material instance.

        Args:
            material_instance_path: Material-instance object path.
            parameter_name: Exact scalar parameter name.
            association: global, layer, or blend.
            index: -1 for global; otherwise the layer/blend stack index.
            value: New override value.
        """
        try:
            return _send(
                "set_material_instance_scalar_override",
                {
                    "material_instance_path": material_instance_path,
                    "parameter_name": parameter_name,
                    "association": association,
                    "index": int(index),
                    "value": float(value),
                },
            )
        except Exception as exc:
            logger.exception("Material-instance scalar edit failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def set_material_instance_layer_blend(
        ctx: Context,
        material_instance_path: str,
        blend_index: int,
        blend_function_path: str,
    ) -> Dict[str, Any]:
        """Replace and save one material-layer blend slot on an instance.

        Args:
            material_instance_path: Material-instance object path.
            blend_index: Zero-based blend slot index.
            blend_function_path: Material Layer Blend function object path.
        """
        try:
            return _send(
                "set_material_instance_layer_blend",
                {
                    "material_instance_path": material_instance_path,
                    "blend_index": int(blend_index),
                    "blend_function_path": blend_function_path,
                },
            )
        except Exception as exc:
            logger.exception("Material-instance blend edit failed")
            return {"success": False, "message": str(exc)}

    logger.info("Material tools registered successfully")
