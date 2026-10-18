# 🎡 朝陽樂園營運輔助 AI Agent

結合雲端 Gemini 與本機 Ollama／Gemma，協助朝陽樂園處理**遊客問答、營運判斷與設施資訊管理**。

遊客在 LINE 詢問園區資訊；經理透過對話查詢天氣、設施與營運規則，取得建議；維修人員則在網頁更新設施狀態。遊客與經理使用各自獨立的知識手冊，讓對外客服與內部營運分工清楚。

**本機首頁：[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

## ✨ 功能介紹

| 使用端            | 功能                                                                           |
| ----------------- | ------------------------------------------------------------------------------ |
| 遊客端｜LINE 客服 | 查看營運時間、優惠、交通與聯絡資訊；詢問票務及入園規則；查詢設施目前是否開放。 |
| 經理端｜AI 對話   | 查詢霧峰天氣、設施狀態與營運手冊；取得當下營運建議、經理待辦及未來七日規劃。   |
| 經理端｜指定通知  | 明確指定後，透過本機通知 Sub-agent 發送固定類型的遊客通知或維修通知。          |
| 維修端｜設施管理  | 查看園內設施，更新為「正常開放」「暫停開放」或「設施維修中」。                 |
| 公告管理          | 新增、查看及刪除公告；發布時嘗試同步廣播 LINE 文字訊息。                       |

### 💬 遊客端

- 使用 LINE 選單快速查看園區資訊，固定選單直接回覆預先設定的 Flex Message。
- 一般問題由 Gemini 參考遊客專用手冊回答，需要設施現況時可查詢設施狀態工具。
- 資料不足時，依提示詞引導遊客查看公告、聯絡園方或尋求現場協助。

### 🧭 經理端

- 透過 Chainlit 對話整合天氣、設施現況與營運規則，輔助經理判斷。
- 天氣觀測用於當下建議，一週預報與紫外線資料用於人力、活動及物資規劃。
- 支援晴天、雨天、大雨、強風、颱風、促銷及維修通知；通知使用固定模板。
- 營運建議不會自動修改設施狀態。聊天中的通知須由經理明確要求發送。

### 🛠️ 維修與公告

維修人員儲存設施狀態後，遊客與經理的後續查詢可取得更新資料，儲存本身不會發送通知。

公告管理使用獨立網頁。**按下「發布公告」會先保存公告，再嘗試向遊客 LINE 帳號廣播文字訊息**；目前支援刪除、不支援直接編輯，刪除也不會撤回已發送的 LINE 訊息。

## 🧩 系統架構

![朝陽樂園營運輔助 AI Agent 系統架構圖](docs/diagrams/system-architecture.png)

| 文件                             | 內容                                                     |
| -------------------------------- | -------------------------------------------------------- |
| ![系統架構圖](系統架構圖.md)     | 三端入口、Agent、MCP、知識庫與外部服務的連線。           |
| ![系統區塊圖](系統區塊圖.md)     | 輸入、處理、資料與輸出的功能分工。                       |
| ![專案工作流程](專案工作流程.md) | 遊客問答、經理對話與通知、維修更新、公告發布的操作流程。 |

## 🔧 使用技術

| 技術                             | 在本專案的用途                                                   |
| -------------------------------- | ---------------------------------------------------------------- |
| Python 3.12、Flask               | LINE Webhook、介紹首頁、設施管理及公告頁面。                     |
| Chainlit                         | 經理端 AI 對話介面與串流回答。                                   |
| LangChain、LangGraph             | 串接模型、檢索與工具；管理經理對話的短期上下文。                 |
| Gemini API                       | 雲端遊客問答與經理營運分析，使用不同的 Agent 配置。              |
| Ollama／Gemma                    | 本機執行 LINE 通知 Sub-agent，協助選擇發送工具。                 |
| MCP、FastMCP                     | 將天氣、設施狀態與 LINE 通知包裝成獨立工具服務。                 |
| RAG、BGE、Sentence Transformers  | 從兩份獨立手冊檢索相關內容；向量模型為 `BAAI/bge-base-zh-v1.5`。 |
| SQLite                           | 儲存設施狀態與公告。                                             |
| LINE Messaging API、Flex Message | 客服回覆、遊客廣播及指定維修人員通知。                           |
| 中央氣象署開放資料 API           | 提供預報、紫外線、雨量、氣溫、風速及颱風警報資料。               |
| HTML、CSS、JavaScript、Anime.js  | 響應式介紹頁、管理頁面與動畫效果。                               |

## 🚀 安裝與環境設定

以下以 **Windows PowerShell** 為例，指令請在專案根目錄執行。

### 1. 準備軟體與服務

- [Python 3.12](https://www.python.org/downloads/) 與 Git。
- [Ollama](https://ollama.com/download/windows) 與通知 Sub-agent 使用的本機模型。
- Google Gemini API Key、中央氣象署開放資料 API Key。
- 遊客 LINE 官方帳號，以及維修通知使用的 LINE 頻道與收件人 ID。

### 2. 下載專案並安裝套件

```powershell
git clone https://github.com/AJI0417/CYUT_PARK_AGENT.git
cd CYUT_PARK_AGENT

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

若電腦未提供 `py` 指令，可先確認 `python --version` 為 3.12，再使用 `python -m venv .venv`。若 PowerShell 無法執行啟用腳本，也可直接用 `.\.venv\Scripts\python.exe` 執行 Python 指令。

### 3. 建立 `.env`

在專案根目錄建立 `.env`，依 `config.py` 使用的名稱填入：

```env
GOOGLE_API_KEY=your_google_api_key
Weather_API_KEY=your_cwa_api_key

CHANNEL_ACCESS_TOKEN=your_visitor_channel_access_token

WORKER_LINE_USER_ID=your_worker_line_user_id
WORKER_CHANNEL_ACCESS_TOKEN=your_worker_channel_access_token
```

`Weather_API_KEY` 的大小寫須保持一致。`.env` 已被 Git 忽略，請勿將真實金鑰或 Token 寫入公開文件。

### 4. 準備本機模型

先使用 `ollama list` 查看模型。`ai/sub.py` 目前設定為 `gemma4:e2b`；請準備可用的同名模型，或將程式中的名稱改成實際使用的模型。

```powershell
ollama list
ollama pull gemma4:e2b
```

若使用自訂模型名稱，須先在本機建立對應模型。雲端模型名稱則分別設定於 `ai/agent.py` 與 `ai/line_qa_agent.py`，須與你的 Gemini API 可用模型一致。

### 5. 啟動完整系統

**每個持續執行的服務使用一個終端機**；各 Python 終端機先切到專案目錄並啟用 `.venv`。

| 順序 | 指令                                        | 用途                                            |
| ---- | ------------------------------------------- | ----------------------------------------------- |
| 1    | `ollama serve`                              | 啟動本機模型服務；Ollama 已在背景執行時可略過。 |
| 2    | `python server.py`                          | 啟動 Flask，初始化設施與公告資料表。            |
| 3    | `python -m mcp_servers.get_facility_status` | 提供設施狀態查詢。                              |
| 4    | `python -m mcp_servers.line_notify`         | 提供遊客與維修通知工具。                        |
| 5    | `python -m mcp_servers.weather`             | 提供天氣資料工具。                              |
| 6    | `python -m chainlit run app.py`             | 啟動經理對話介面。                              |

首次啟動可能需要下載 BGE 模型。經理開始對話前，三個 MCP 服務須已就緒；目前遊客一般問答也需要設施狀態 MCP。

### 6. 連接 LINE

將 Flask 的 **5000 埠**透過 ngrok 等方式提供公開 HTTPS 入口，再將「公開網址加上 `/webhook`」設為 LINE Developers 的 Webhook URL，並啟用 Webhook。

`127.0.0.1` 僅供本機瀏覽，LINE 平台與遊客手機無法用它連進你的電腦。正式提供手機操作前，也要將 Flex 模板中的公告及維修頁連結換成可存取的公開網址。[LINE Webhook 設定說明](https://developers.line.biz/en/docs/messaging-api/receiving-messages/)

## 🌐 入口與使用方式

以 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 作為本機網站入口：

| 頁面／端點       | 網址                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------- |
| 專案介紹首頁     | [http://127.0.0.1:5000/](http://127.0.0.1:5000/)                                       |
| 維修人員設施管理 | [http://127.0.0.1:5000/worker](http://127.0.0.1:5000/worker)                           |
| 經理公告管理     | [http://127.0.0.1:5000/admin/announcements](http://127.0.0.1:5000/admin/announcements) |
| 遊客公告列表     | [http://127.0.0.1:5000/announcements](http://127.0.0.1:5000/announcements)             |
| LINE Webhook     | `POST http://127.0.0.1:5000/webhook`，由 LINE 平台呼叫。                               |

經理對話由 Chainlit 獨立提供，請另開 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)，目前沒有掛在 Flask 的 5000 路由下。

可從以下情境開始：

- **遊客問答：** 在 LINE 輸入「票價是多少？」或「急流泛舟目前有開放嗎？」。
- **經理分析：** 在 Chainlit 輸入「根據目前天氣與設施狀態，給我營運建議。」。
- **指定通知：** 確認後輸入完整指令，例如「發送晴天通知與維修通知」，並分別核對工具回覆及 LINE 結果。
- **維修更新：** 在設施管理頁選擇狀態並儲存，再從客服或經理端查詢。
- **公告發布：** 在公告管理頁填寫標題與內容，確認後發布，再核對公告頁與 LINE。

完整經理操作教學見 [chainlit.md](chainlit.md)。AI 回答與營運建議供人員參考；當日開園、停駛及恢復仍以園方確認與現場公告為準。

## 📁 專案結構

```text
CYUT_PARK_AGENT/
├─ ai/                         # 經理、遊客與通知 Agent，以及工具和提示詞
├─ db/                         # SQLite 初始化、設施與公告資料存取
├─ docs/diagrams/               # 架構、區塊與流程圖的圖片及 Mermaid 原始檔
├─ Line_template/               # LINE 固定選單與通知 Flex 模板
├─ mcp_client/                  # MCP 用戶端連線設定
├─ mcp_servers/                 # 天氣、設施狀態、LINE 通知工具服務
├─ rag/                         # 營運與遊客兩份知識庫的檢索處理
├─ routes/                      # Flask Webhook、設施與公告路由
├─ services/                    # LINE 回覆、載入動畫與文字廣播
├─ static/                      # CSS、JavaScript 與圖片
├─ templates/                   # 首頁、維修及公告 HTML 頁面
├─ app.py                       # Chainlit 經理對話入口
├─ server.py                    # Flask 網站入口
├─ config.py                    # 環境變數與共用設定
├─ requirements.txt             # Python 套件版本
├─ chainlit.md                  # 經理操作教學
├─ 系統架構圖.md                 # 系統連線與部署分工
├─ 系統區塊圖.md                 # 功能區塊與資料流
├─ 專案工作流程.md               # 三端及公告操作流程
├─ 樂園營運手冊.md               # 經理使用的內部知識來源
└─ 朝陽樂園遊客知識庫手冊.md     # 遊客客服使用的知識來源
```
