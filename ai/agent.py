from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

import config
from ai.tools import search_knowledge_base
from ai.prompt.main_agent_prompt import SYSTEM_PROMPT
from ai.sub import create_line_subagent_tool
from mcp_client.mcp_client import get_mcp_client


async def create_my_agent():
    # llm = ChatOllama(
    #     model="gemma4:e4b",
    #     temperature=1.0,
    #     num_ctx=8192,
    #     reasoning=True,
    # )
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        api_key=config.GOOGLE_API_KEY,
        temperature=1.0,
    )

    client =  get_mcp_client()

    # 主 Agent 只載入 Weather MCP
    weather_tools = await client.get_tools(
        server_name="Weather"
    )

    Get_Facility_status_tools = await client.get_tools(
        server_name = "Get_Facility_status"
    )
    

    # 建立已經掛載 LINE MCP 的 Subagent 工具
    send_line_message = await create_line_subagent_tool()

    main_tools = [
        *weather_tools,
        search_knowledge_base,
        send_line_message,
        *Get_Facility_status_tools
    ]

    return create_agent(
        model=llm,
        tools=main_tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer = InMemorySaver()
    )
