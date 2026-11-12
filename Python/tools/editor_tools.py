"""
Editor Tools for Unreal MCP.

This module provides tools for controlling the Unreal Editor viewport and other editor functionality.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_editor_tools(mcp: FastMCP):
    """Register editor tools with the MCP server."""
    
    @mcp.tool()
    def get_render_memory_diagnostics(
        ctx: Context,
        top_texture_count: int = 30,
        top_mesh_count: int = 30,
        include_detailed_dumps: bool = True,
    ) -> Dict[str, Any]:
        """Inspect live Unreal rendering memory without modifying the scene.

        Returns RHI video-memory budget/usage, texture-streaming pool pressure,
        scene-referenced virtual and non-virtual texture summaries, top texture
        assets, skeletal-mesh/Nanite resident-resource details, selected memory-
        related console variables, and optional engine diagnostic dumps.

        Args:
            top_texture_count: Number of largest scene textures to include per list (1-100).
            top_mesh_count: Number of heaviest scene skeletal meshes to include (1-100).
            include_detailed_dumps: Include rhi.DumpMemory and VT physical-pool diagnostics.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command(
                "get_render_memory_diagnostics",
                {
                    "top_texture_count": max(1, min(int(top_texture_count), 100)),
                    "top_mesh_count": max(1, min(int(top_mesh_count), 100)),
                    "include_detailed_dumps": bool(include_detailed_dumps),
                },
            )
            return response or {}
        except Exception as e:
            logger.error(f"Error getting render memory diagnostics: {e}")
            return {"success": False, "message": str(e)}

    # @mcp.tool() commented out because it's buggy
    def focus_viewport(
        ctx: Context,
        target: str = None,
        location: List[float] = None,
        distance: float = 1000.0,
        orientation: List[float] = None
    ) -> Dict[str, Any]:
        """
        Focus the viewport on a specific actor or location.
        
        Args:
            target: Name of the actor to focus on (if provided, location is ignored)
            location: [X, Y, Z] coordinates to focus on (used if target is None)
            distance: Distance from the target/location
            orientation: Optional [Pitch, Yaw, Roll] for the viewport camera
            
        Returns:
            Response from Unreal Engine
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            params = {}
            if target:
                params["target"] = target
            elif location:
                params["location"] = location
            
            if distance:
                params["distance"] = distance
                
            if orientation:
                params["orientation"] = orientation
                
            response = unreal.send_command("focus_viewport", params)
            return response or {}
            
        except Exception as e:
            logger.error(f"Error focusing viewport: {e}")
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    def inspect_level_sequence(
        ctx: Context,
        sequence_path: str,
    ) -> Dict[str, Any]:
        """Audit a Level Sequence's rates, playback range, camera cuts, bindings, and markers."""
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            return unreal.send_command(
                "inspect_level_sequence",
                {"sequence_path": sequence_path},
            ) or {}
        except Exception as e:
            logger.error(f"Error inspecting Level Sequence: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def organize_level_sequence_camera_cuts(
        ctx: Context,
        sequence_path: str,
        marker_prefix: str = "CAMCUT_",
        apply: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """Number Camera Cut sections with managed Sequencer markers.

        Existing camera sections, bindings, transforms, lenses, and keys are preserved.
        Only markers matching ``marker_prefix + NNN + ' | '`` are replaced. The
        default is a dry run; set ``apply`` to true to modify the sequence.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            return unreal.send_command(
                "organize_level_sequence_camera_cuts",
                {
                    "sequence_path": sequence_path,
                    "marker_prefix": marker_prefix,
                    "apply": bool(apply),
                    "save": bool(save),
                },
            ) or {}
        except Exception as e:
            logger.error(f"Error organizing Level Sequence camera cuts: {e}")
            return {"success": False, "message": str(e)}

    logger.info("Editor tools registered successfully")
