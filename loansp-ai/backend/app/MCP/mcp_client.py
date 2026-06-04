import json
from typing import Any, Dict

from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack

from app.core.logging.log import logger


class MCPClient:
    """Quản lý kết nối đến nhiều MCP servers qua SSE."""

    def __init__(self, server_configs: Dict[str, str]):
        """
        server_configs: {"loan_mcp": "http://localhost:8001/sse", "knowledge_mcp": "http://localhost:8002/sse"}
        """
        self.server_configs = server_configs
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        for name, url in self.server_configs.items():
            try:
                transport = await self.exit_stack.enter_async_context(sse_client(url))
                read, write = transport
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.sessions[name] = session
                logger.info(f"MCP server '{name}' connected")
            except Exception as e:
                logger.warning(f"MCP server '{name}' unavailable: {e}")

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        if server_name not in self.sessions:
            raise RuntimeError(f"MCP server '{server_name}' not connected")
        return await self.sessions[server_name].call_tool(tool_name, arguments=arguments)

    async def disconnect(self):
        """Đóng tất cả kết nối."""
        await self.exit_stack.aclose()
        self.sessions.clear()
        logger.info("All MCP connections closed")