from mcp.server.fastmcp import FastMCP

from tools.dti_calc import calculate_dti
from tools.ltv_calc import calculate_ltv
from tools.payment_calc import estimate_payment

mcp = FastMCP("loan_calc")

mcp.add_tool(calculate_dti)
mcp.add_tool(calculate_ltv)
mcp.add_tool(estimate_payment)

if __name__ == "__main__":
    mcp.run(transport="sse")
