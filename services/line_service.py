import requests

import config


def show_loading_animation(user_id: str) -> None:
    """在一對一聊天室顯示 LINE 載入動畫。"""
    url = f"{config.LINE_API_BASE}/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "chatId": user_id,
        "loadingSeconds": 60,
    }

    requests.post(url,headers=headers,json=data,timeout=5)


def reply_add_friend_message(reply_token):
    """使用 LINE Reply API 傳送 Flex Message。"""
    url = f"{config.LINE_API_BASE}/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text":
                (
                    "歡迎加入朝陽主題樂園官方客服帳號！🎡\n"
                    "想了解停車、票價或園區設施等資訊嗎？\n"
                    "直接輸入您的問題，我們會為您解答。\n"
                    "也可以點選下方選單，快速查看常見問題👇\n"
                    "祝您在朝陽主題樂園度過愉快的一天！✨"
                )
            }
        ],
    }

    requests.post(url, headers=headers, json=data)



def reply_message(reply_token, flex_content, alt_text):
    """使用 LINE Reply API 傳送 Flex Message。"""
    url = f"{config.LINE_API_BASE}/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "flex",
                "altText": alt_text,
                "contents": flex_content,
            }
        ],
    }

    requests.post(url, headers=headers, json=data)


def reply_text_message(reply_token: str, text: str) -> None:
    """透過 LINE Reply API 回覆純文字。"""
    url = f"{config.LINE_API_BASE}/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    requests.post(url,headers=headers,json=data,)


