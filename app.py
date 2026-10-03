import chainlit as cl
from ai.agent import create_my_agent
from langchain_core.messages import AIMessageChunk, ToolMessage

@cl.on_chat_start
async def on_chat_start():
    agent = await create_my_agent()
    thread_config = {
        "configurable": {
            "thread_id": cl.user_session.get("id")
        }
    }

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_config", thread_config)

    welcome_message = """**歡迎使用朝陽樂園營運決策助手**
您可以查詢天氣、設施狀態與營運規則，取得目前營運建議；確認後也可明確要求發送 LINE 通知。完整步驟請參考本介面的 **右上角說明頁** 。
試著輸入：
- 「現在霧峰的天氣如何？」
- 「目前有哪些設施維修中？」
- 「如果下大雨，依營運手冊應如何處理？」
- 「根據目前天氣與設施狀態，給我營運建議。」
要發布公告，請開啟[公告管理頁](http://127.0.0.1:5000/admin/announcements)。營運建議不會自動變更設施狀態或發送通知；發布公告也不會自動推播 LINE。"""

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):

    agent = cl.user_session.get("agent")
    thread_config = cl.user_session.get("thread_config")

    ui_msg = cl.Message(content="思考中...")
    await ui_msg.send()

    final_text = ""

    async for msg, _metadata in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message.content
                }
            ]
        },
        config=thread_config,
        stream_mode="messages",
    ):
        if isinstance(msg, ToolMessage):
            tool_name = msg.name or "未知工具"
            ui_msg.content = f"呼叫工具中：{tool_name}..."
            await ui_msg.update()
        elif isinstance(msg, AIMessageChunk):
            text = msg.text
            if text:
                final_text += text
                ui_msg.content = "回覆內容如下:\n\n" + final_text
                await ui_msg.update()
                    
    ui_msg.content = final_text or "模型未產生文字回覆。"
    await ui_msg.update()
