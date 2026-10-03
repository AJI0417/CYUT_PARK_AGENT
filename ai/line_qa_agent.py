from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
import config
from ai.qa_tool import search_visitor_knowledge_base
from ai.prompt.line_qa_prompt import SYSTEM_PROMPT
from mcp_client.mcp_client import get_mcp_client


async def create_my_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        api_key=config.GOOGLE_API_KEY,
        temperature=1.0,
    )

    client =  get_mcp_client()
    Get_Facility_status_tools = await client.get_tools(
        server_name = "Get_Facility_status"
    )

    main_tools = [
        search_visitor_knowledge_base,
        *Get_Facility_status_tools
    ]

    return create_agent(
        model=llm,
        tools=main_tools,
        system_prompt=SYSTEM_PROMPT,
    )


async def answer_line_question(user_text: str) -> str:
    """將 LINE 使用者的問題交給遊客 Agent，回傳文字答案。"""
    agent = await create_my_agent()

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_text,
                }
            ]
        }
    )

    # Agent 回傳訊息列表；最後一則是產生的回答。
    answer = result["messages"][-1].text.strip()
    return answer
