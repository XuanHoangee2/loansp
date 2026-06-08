from mcp.server.fastmcp import FastMCP

from tools.recommend import recommend_loan, compare_products

mcp = FastMCP("product")

mcp.add_tool(recommend_loan)
mcp.add_tool(compare_products)

if __name__ == "__main__":
    mcp.run(transport="sse")
