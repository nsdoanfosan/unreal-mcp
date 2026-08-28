"""Chaos Cloth Dataflow inspection and editing tools for Unreal MCP."""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP


logger = logging.getLogger("UnrealMCP")


def _send(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    from unreal_mcp_server import get_unreal_connection

    unreal = get_unreal_connection()
    if not unreal:
        return {"success": False, "message": "Failed to connect to Unreal Engine"}
    response = unreal.send_command(command, params)
    return response or {"success": False, "message": "No response from Unreal Engine"}


def register_cloth_tools(mcp: FastMCP):
    """Register modern Chaos Cloth Dataflow graph tools."""

    @mcp.tool()
    def inspect_cloth_dataflow_graph(
        ctx: Context,
        asset_path: str,
    ) -> Dict[str, Any]:
        """Inspect a Dataflow-backed Chaos Cloth asset without changing it.

        Returns every existing node, reflected property, input/output pin, connection,
        terminal reachability, collection vertex-colour statistics, and weight-map state.
        ``asset_path`` may be a full Unreal object path or the exact name of one loaded asset.
        """
        try:
            return _send("inspect_cloth_dataflow_graph", {"asset_path": asset_path})
        except Exception as exc:
            logger.exception("Cloth Dataflow inspection failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def add_cloth_dataflow_node(
        ctx: Context,
        asset_path: str,
        node_type: str,
        node_name: str,
        position_x: float = 0.0,
        position_y: float = 0.0,
        property_edits: Optional[List[Dict[str, str]]] = None,
        apply_changes: bool = False,
        evaluate: bool = True,
        save: bool = False,
    ) -> Dict[str, Any]:
        """Create an approved built-in node in a Chaos Cloth Dataflow editor graph.

        The node is created through Unreal's Dataflow editor action, so both the runtime
        graph and the visible editor node are persisted. ``property_edits`` entries use
        ``property`` and Unreal ``value_text``. The current allow-list includes UE 5.8's
        ``FDataflowVertexColorToAttributeNode`` and the Chaos Cloth skeletal-mesh
        import node needed to build a non-destructive PHY colour source branch.
        Preview is the default.
        """
        try:
            return _send(
                "add_cloth_dataflow_node",
                {
                    "asset_path": asset_path,
                    "node_type": node_type,
                    "node_name": node_name,
                    "position_x": float(position_x),
                    "position_y": float(position_y),
                    "property_edits": property_edits or [],
                    "apply_changes": bool(apply_changes),
                    "evaluate": bool(evaluate),
                    "save": bool(save),
                },
            )
        except Exception as exc:
            logger.exception("Cloth Dataflow node creation failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def edit_cloth_dataflow_graph(
        ctx: Context,
        asset_path: str,
        connections: Optional[List[Dict[str, Any]]] = None,
        property_edits: Optional[List[Dict[str, str]]] = None,
        remove_node_names: Optional[List[str]] = None,
        remove_unreachable: bool = False,
        cleanup_orphan_editor_nodes: bool = False,
        apply_changes: bool = False,
        evaluate: bool = True,
        save: bool = False,
    ) -> Dict[str, Any]:
        """Rewire or clean an existing Chaos Cloth Dataflow graph; never creates nodes.

        Each connection uses ``from_node``, ``from_output``, ``to_node``, and ``to_input``;
        ``clear_existing_input`` defaults to true. Each property edit uses ``node``,
        ``property``, and Unreal ``value_text``. Nodes are removed only by exact name, unless
        ``remove_unreachable`` is explicitly enabled. Preview is the default; set
        ``apply_changes`` to mutate, and ``save`` to persist both Dataflow and Cloth packages.
        Do not combine automatic unreachable removal with rewiring: inspect after the rewire,
        then remove the exact unused nodes in a second call.
        """
        try:
            return _send(
                "edit_cloth_dataflow_graph",
                {
                    "asset_path": asset_path,
                    "connections": connections or [],
                    "property_edits": property_edits or [],
                    "remove_node_names": remove_node_names or [],
                    "remove_unreachable": bool(remove_unreachable),
                    "cleanup_orphan_editor_nodes": bool(cleanup_orphan_editor_nodes),
                    "apply_changes": bool(apply_changes),
                    "evaluate": bool(evaluate),
                    "save": bool(save),
                },
            )
        except Exception as exc:
            logger.exception("Cloth Dataflow edit failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def invoke_cloth_dataflow_node_function(
        ctx: Context,
        asset_path: str,
        node_name: str,
        function_property: str,
        apply_changes: bool = False,
        evaluate: bool = False,
        save: bool = False,
    ) -> Dict[str, Any]:
        """Invoke a reflected Dataflow node button/function such as WeightMap.Transfer.

        Preview validates the node and function property without invoking it. Set
        ``apply_changes`` to run it and ``save`` to persist the resulting node state.
        Full Cloth terminal evaluation is opt-in because it can trigger an expensive
        skeletal-mesh rebuild; the safe default only runs the requested node function.
        """
        try:
            return _send(
                "invoke_cloth_dataflow_node_function",
                {
                    "asset_path": asset_path,
                    "node_name": node_name,
                    "function_property": function_property,
                    "apply_changes": bool(apply_changes),
                    "evaluate": bool(evaluate),
                    "save": bool(save),
                },
            )
        except Exception as exc:
            logger.exception("Cloth Dataflow function invocation failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def analyze_cloth_vertex_colors(
        ctx: Context,
        skeletal_mesh_path: str,
        lod_index: int = 0,
    ) -> Dict[str, Any]:
        """Measure the authored R/G/B/A channels of a skeletal mesh imported LOD.

        Use this to select the actual painted channel on a PHY simulation mesh before
        connecting or baking it as a cloth weight map.
        """
        try:
            return _send(
                "analyze_cloth_vertex_colors",
                {"skeletal_mesh_path": skeletal_mesh_path, "lod_index": int(lod_index)},
            )
        except Exception as exc:
            logger.exception("Cloth vertex-colour analysis failed")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def bake_cloth_vertex_color_weight_map(
        ctx: Context,
        asset_path: str,
        source_mesh_path: str,
        weight_map_node_name: str,
        color_channel: str = "red",
        scaling_factor: float = 1.0,
        invert: bool = False,
        apply_changes: bool = False,
        save: bool = False,
    ) -> Dict[str, Any]:
        """Bake a PHY skeletal mesh vertex-colour channel into an existing WeightMap node.

        This is an explicit fallback for graphs that do not already contain a usable
        vertex-colour conversion path. It never creates a node and previews by default.
        """
        try:
            return _send(
                "bake_cloth_vertex_color_weight_map",
                {
                    "asset_path": asset_path,
                    "source_mesh_path": source_mesh_path,
                    "weight_map_node_name": weight_map_node_name,
                    "color_channel": color_channel,
                    "scaling_factor": float(scaling_factor),
                    "invert": bool(invert),
                    "apply_changes": bool(apply_changes),
                    "save": bool(save),
                },
            )
        except Exception as exc:
            logger.exception("Cloth vertex-colour weight-map bake failed")
            return {"success": False, "message": str(exc)}
