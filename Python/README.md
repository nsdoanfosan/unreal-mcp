# Unreal MCP

Python bridge for interacting with Unreal Engine 5.5 using the Model Context Protocol (MCP).

## Setup

1. Make sure Python 3.10+ is installed
2. Install `uv` if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```
4. Install dependencies:
   ```bash
   uv pip install -e .
   ```

At this point, you can configure your MCP Client (Claude Desktop, Cursor, Windsurf) to use the Unreal MCP Server as per the [Configuring your MCP Client](README.md#configuring-your-mcp-client).

## Testing Scripts

There are several scripts in the [scripts](./scripts) folder. They are useful for testing the tools and the Unreal Bridge via a direct connection. This means that you do not need to have an MCP Server running.

You should make sure you have installed dependencies and/or are running in the `uv` virtual environment in order for the scripts to work.


## Troubleshooting

- Make sure Unreal Engine editor is loaded loaded and running before running the server.
- Check logs in `unreal_mcp.log` for detailed error information

The command client connects only for an actual tool request and closes the socket
after its response. Do not add a startup connection or a null-byte health check:
the editor's TCP bridge handles one client at a time, so an idle startup socket
can fill the accept backlog and make other chats fail with WinError 10061.
Concurrent calls in one Python process are serialized. A failed mutation is never
automatically replayed. Transport regressions run with
`python -m unittest discover -s tests -p test_startup_transport.py`.

## Development

To add new tools, modify the `UnrealMCPBridge.py` file to add new command handlers, and update the `unreal_mcp_server.py` file to expose them through the HTTP API. 