import json
import asyncio

from flask import Blueprint, request

import config
from ai.line_qa_agent import answer_line_question
from services.line_service import (
    reply_message,
    reply_text_message,
    reply_add_friend_message,
    show_loading_animation
)


line_bp = Blueprint("line", __name__)


def load_flex_messages():
    """讀取 Flex Message 的 JSON 檔案。"""
    with open(config.RICH_MENU_FLEX_MESSAGES_PATH, "r", encoding="utf-8") as file:
        flex_data = json.load(file)

    return flex_data


@line_bp.route("/webhook", methods=["POST"])
def webhook():
    """接收 LINE Webhook 事件。"""
    body = request.get_json(silent=True) or {}
    events = body.get("events", [])

    for event in events:
        event_type = event.get("type")
        reply_token = event.get("replyToken")

        # 加好友事件：發送歡迎訊息。
        if event_type == "follow":
            if reply_token:
                reply_add_friend_message(reply_token)

            # 這個事件處理完畢，繼續看下一個事件。
            continue

        # 取消好友等事件不是訊息，不需要交給客服回答。
        if event_type != "message":
            continue

        message = event.get("message") or {}

        # 目前只處理文字訊息，圖片、貼圖等先略過。
        if message.get("type") != "text":
            continue

        # 沒有 replyToken 就無法使用 LINE Reply API。
        if not reply_token:
            continue

        user_text = message.get("text", "")
        if not user_text:
            continue

        print(f"實際收到的指令是：[{user_text}]")

        # 固定選單指令需要用到 Flex Message，這時才讀取檔案。
        if user_text == "查看今日營運時間":
            flex_data = load_flex_messages()
            reply_message(
                reply_token,
                flex_data["營運時間"],
                "查看今日營運時間",
            )

        elif user_text == "查看最新優惠活動":
            flex_data = load_flex_messages()
            reply_message(
                reply_token,
                flex_data["優惠活動"],
                "查看最新優惠活動",
            )

        elif user_text == "查看樂園資訊":
            flex_data = load_flex_messages()
            reply_message(
                reply_token,
                flex_data["樂園資訊"],
                "查看樂園資訊",
            )

        elif user_text == "查看完整交通資訊":
            flex_data = load_flex_messages()
            reply_message(
                reply_token,
                flex_data["交通資訊"],
                "選擇交通工具",
            )

        elif user_text == "聯絡我們":
            flex_data = load_flex_messages()
            reply_message(
                reply_token,
                flex_data["聯絡資訊"],
                "聯絡客服",
            )

        else: # 不是固定選單指令，就交給遊客問答 Agent。
            # 一般文字問題：先顯示載入動畫，再呼叫遊客問答 Agent。
            source = event.get("source") or {}
            # LINE 載入動畫只支援一對一聊天室。
            if source.get("type") == "user":
                user_id = source.get("userId")
                if user_id:
                    show_loading_animation(user_id)
            try:
                answer = asyncio.run(
                    answer_line_question(user_text)
                )
            except Exception:
                answer = "抱歉，目前無法查詢，請稍後再試。"

            reply_text_message(reply_token, answer)

    return "OK", 200