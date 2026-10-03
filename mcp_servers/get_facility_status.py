from mcp.server.fastmcp import FastMCP

from db.facility_db import get_all_facilities


mcp = FastMCP("Database_Status_Server", port=8003)


@mcp.tool()
def get_facility_status() -> dict[str, str]:
    """查詢所有樂園設施目前的營運狀態。"""
    facilities = get_all_facilities()

    return {
        facility["設施名稱"]: facility["設施狀態"]
        for facility in facilities
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
