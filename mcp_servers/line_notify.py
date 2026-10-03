import json
import requests
from mcp.server.fastmcp import FastMCP

import config
from line_notification_types import WeatherNotificationType


mcp = FastMCP("LINE_Message_Server", port=8001)




def load_flex_messages():
    """讀取存放 Flex Message 的 JSON 檔案。"""
    with open(config.MCP_TOOL_FLEX_LINE_MESSAGES_PATH, "r", encoding="utf-8") as file:
        flex_data = json.load(file)

    return flex_data

FLEX_MESSAGES = load_flex_messages()


# =========== 單一推播工具 ==========
@mcp.tool()
def push_weather_message(
    notification_type: WeatherNotificationType,
) -> dict:
    """
    向所有遊客廣播指定的天氣通知。只有經理明確要求發送通知時才能使用。
    notification_type 必須選擇已存在的通知模板。
    """

    flex_message = {
        "type": "flex",
        "altText": notification_type,
        "contents": FLEX_MESSAGES[notification_type],
    }

    response = requests.post(
        f"{config.LINE_API_BASE}/message/broadcast",
        headers={
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {config.CHANNEL_ACCESS_TOKEN}"
            ),
        },
        json={
            "messages": [
                flex_message
            ]
        },
        timeout=15,
    )

    if response.ok:
        return {
            "status": "success",
            "status_code": response.status_code,
            "notification_type": notification_type,
        }
    else:
        return {
            "status": "error",
            "status_code": response.status_code,
            "notification_type": notification_type,
            "body": response.text,
        }

# 發送維修通知給工人
@mcp.tool()
def push_worker_message() -> dict:
    """
    向指定維修工人發送固定的「維修通知」Flex Message。
    只有經理明確要求通知維修人員時才能使用。
    """

    notification_type = "維修通知"

    flex_message = {
        "type": "flex",
        "altText": notification_type,
        "contents": FLEX_MESSAGES[notification_type],
    }

    response = requests.post(
        f"{config.LINE_API_BASE}/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {config.WORKER_CHANNEL_ACCESS_TOKEN}"
            ),
        },
        json={
            "to": config.WORKER_LINE_USER_ID,
            "messages": [
                flex_message
            ],
        },
        timeout=15,
    )

    if response.ok:
        return {
            "status": "success",
            "status_code": response.status_code,
            "notification_type": notification_type,
            "recipient": "維修工人",
        }

    return {
        "status": "error",
        "status_code": response.status_code,
        "notification_type": notification_type,
        "recipient": "維修工人",
        "body": response.text,
    }







if __name__ == "__main__":
    mcp.run(transport="streamable-http")
