from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from .config import Config
from .tools import courses, content, assignments, social

def create_server():
    print(f"DEBUG: MCP_SERVER_TOKEN = '{Config.MCP_SERVER_TOKEN}'")
    # Initialize Auth Verifier
    auth = StaticTokenVerifier(tokens={
        Config.MCP_SERVER_TOKEN: {
            "client_id": "canvas-mcp-client",
            "scopes": ["read", "write"]
        }
    })
    
    mcp = FastMCP("canvas-mcp", auth=auth)
    
    # Register tools from modules
    courses.register_tools(mcp)
    content.register_tools(mcp)
    assignments.register_tools(mcp)
    social.register_tools(mcp)
    
    return mcp

mcp = create_server()

def main():
    mcp.run(transport="http", host="127.0.0.1", port=2222, stateless_http=True)

if __name__ == "__main__":
    main()
