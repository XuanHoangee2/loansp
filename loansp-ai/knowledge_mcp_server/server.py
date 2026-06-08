from mcp.server.fastmcp import FastMCP

from tools.faq_search import faq_search
from tools.policy_search import policy_search

mcp = FastMCP("knowledge")

mcp.add_tool(faq_search)
mcp.add_tool(policy_search)

if __name__ == "__main__":
    mcp.run(transport="sse")
