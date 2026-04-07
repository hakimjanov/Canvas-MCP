import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
    CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")

    @classmethod
    def validate(cls):
        if not cls.CANVAS_BASE_URL or not cls.CANVAS_TOKEN:
            raise ValueError("Missing CANVAS_BASE_URL or CANVAS_TOKEN environment variables.")

        # Ensure base URL doesn't have trailing slash
        if cls.CANVAS_BASE_URL.endswith("/"):
            cls.CANVAS_BASE_URL = cls.CANVAS_BASE_URL.rstrip("/")

    # MCP Server Token for Authentication (legacy static token for existing clients)
    MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN", "test-token")

    # Public base URL where this MCP server is hosted (used for OAuth discovery)
    MCP_BASE_URL = os.getenv("MCP_BASE_URL", "https://textdonna.com")
