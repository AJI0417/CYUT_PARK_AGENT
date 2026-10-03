from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama

from ai.prompt.sub_agent_prompt import LINE_SUBAGENT_PROMPT
from line_notification_types import LineNotificationType
from mcp_client.mcp_client import get_mcp_client

async def create_line_subagent_tool():
    # Subagent 取得 MCP Client
    client = get_mcp_client()

    # 只載入 LINE_Notify Server 的工具
    line_tools = await client.get_tools(
        server_name="LINE_Notify"
    )

    subagent_model = ChatOllama(
        model="gemma4:e2b",
        temperature=1.0,
        num_ctx=8192,
    )

    # LINE 工具直接掛載在 Subagent
    line_sub_agent = create_agent(
        model=subagent_model,
        tools=line_tools,
        system_prompt=LINE_SUBAGENT_PROMPT,
    )

    # 將整個 Subagent 包裝成主 Agent 的一個工具
    @tool(
        "send_line_message",
        description=(
            "只有經理明確要求發送 LINE 通知時才能使用。"
            "notification_type 必須選擇工具列出的正式通知類型；"
            "單純分析、建議或通知類型不明時不得使用。"
        ),
    )
    async def send_line_message(
        notification_type: LineNotificationType,
    ) -> str:
        if notification_type == "維修通知":
            instruction = (
                "上游已確認經理明確要求發送維修通知。"
                "請只呼叫一次 push_worker_message，不要傳入任何參數，"
                "並依工具真實結果回覆。"
            )
        else:
            instruction = (
                "上游已確認經理明確要求發送遊客天氣通知。"
                "請只呼叫一次 push_weather_message，"
                f"notification_type 必須精確使用「{notification_type}」，"
                "並依工具真實結果回覆。"
            )

        result = await line_sub_agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": instruction,
                }
            ]
        })

        return result["messages"][-1].content

    return send_line_message
