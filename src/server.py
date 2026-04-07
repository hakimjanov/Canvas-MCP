from fastmcp import FastMCP
from .auth import CanvasOAuthProvider
from .config import Config
from .tools import courses, content, assignments, social

def create_server():
    auth = CanvasOAuthProvider(base_url=Config.MCP_BASE_URL)

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
