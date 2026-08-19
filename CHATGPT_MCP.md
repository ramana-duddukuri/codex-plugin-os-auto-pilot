# Connecting the Oniesoft MCP server to ChatGPT

The bundled server supports local stdio and Streamable HTTP. The plugin packages
the reusable test workflows; backend tools become available after deployment and
an MCP connection is added in ChatGPT developer mode.

```bash
export PLATFORM_API_KEY="your-oniesoft-api-key"
export PLATFORM_API_URL="https://your-platform.example"
export BACKEND_URL="https://your-execution-api.example"
uv run --with-requirements server/requirements.txt --python '>=3.10' \
  server/launch.py --transport streamable-http
```

The development server exposes MCP at `/mcp`. For public distribution, deploy
it behind HTTPS with per-user authentication, add its connection in ChatGPT,
then use the returned `plugin_asdk_app...` ID to create the plugin app mapping.
Do not commit that workspace-specific ID to source control.
