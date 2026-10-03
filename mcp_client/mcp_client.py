from langchain_mcp_adapters.client import MultiServerMCPClient


def get_mcp_client():
    return MultiServerMCPClient(
        {
            "LINE_Notify": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8001/mcp",
            },
            "Weather": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8002/mcp",
            },
            "Get_Facility_status":{
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8003/mcp",
            }
        }
    )
