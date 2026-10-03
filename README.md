# 朝陽主題樂園營運輔助 Agent

本專案把**遊客 LINE 客服、經理營運決策與維修人員設施管理**串接在同一套樂園流程中。遊客與經理各自使用獨立手冊做 RAG 檢索；Gemini 負責問答與分析，本機 Ollama／Gemma 參與經理指定的 LINE 通知。

## 功能一覽

| 使用者   | 入口              | 目前功能                                                                             |
| -------- | ----------------- | ------------------------------------------------------------------------------------ |
| 遊客     | LINE 官方帳號     | 固定選單、遊客手冊問答、查詢設施現況；提示詞要求無可靠答案時依問題類型轉介。         |
| 樂園經理 | Chainlit 對話介面 | 查詢霧峰天氣、設施狀態及營運手冊，取得營運建議；明確要求後發送固定類型的 LINE 通知。 |
| 維修人員 | Flask `/worker`   | 查看設施清單，將狀態更新為正常開放、暫停開放或設施維修中。                           |
| 樂園經理 | Flask 公告管理頁  | 新增、查看及刪除公告；目前沒有編輯公告功能。                                         |

維修更新後，遊客與經理的**後續查詢**才會讀到新狀態。營運建議不會自動更改設施，公告發布也不會自動推播 LINE。

## 模型配置

| 用途                      | 目前程式設定            | 執行位置          |
| ------------------------- | ----------------------- | ----------------- |
| 經理營運 Agent            | `gemini-3.8-flash`      | Google Gemini API |
| 遊客 LINE 問答 Agent      | `gemini-3.7-flash`      | Google Gemini API |
| 經理通知用 LINE Sub-agent | `gemma4:e2b`            | 本機 Ollama       |
| 兩份 RAG 的向量模型       | `BAAI/bge-base-zh-v1.5` | CPU               |

以上依目前原始碼記錄；修改模型名稱時，請同步確認 Google API 或 Ollama 端可使用該模型。

## 目前開發環境

- 作業系統：Windows 11
- CPU：Intel Core i5-12600K
- GPU：NVIDIA GeForce RTX 4060 Ti 8 GB
- RAM：32 GB
- Python：3.12

這是目前使用的主機配置，不是最低硬體需求；兩份 RAG 的 BGE 向量模型在程式中指定使用 CPU。

## 安裝方式

以下以 Windows PowerShell 為例，所有指令都必須在專案根目錄執行。專案依賴版本固定於 `requirements.txt`，預期使用 Python 3.12。

### 1. 安裝必要軟體

請依使用的功能安裝：

- [Python 3.12](https://www.python.org/downloads/)
- [Ollama for Windows](https://ollama.com/download/windows)（僅經理通知用 LINE Sub-agent 需要）
- Git（如需使用 Git 下載專案）

安裝 Python 時，請勾選將 Python 加入 PATH；只有在使用經理營運 Agent 的 LINE 通知功能時才需要 Ollama。

### 2. 建立虛擬環境

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

若 PowerShell 不允許執行啟用腳本，可改用 CMD 的 `.venv\Scripts\activate.bat`，或直接呼叫 `.venv\Scripts\python.exe`。若既有 `.venv` 從其他路徑搬移而來，或原本的 Python 已被移除，請重建虛擬環境；虛擬環境不能視為可直接搬移的資料夾。

### 3. 準備 Ollama 模型

若要使用經理營運 Agent 的通知功能，確認 Ollama 已在背景執行，並準備 LINE Sub-agent 使用的模型：

```powershell
ollama pull gemma4:e2b
```

可使用下列指令確認模型是否存在：

```powershell
ollama list
```

若 Ollama 沒有自動啟動，可另外開啟一個終端機執行：

```powershell
ollama serve
```

### 4. 設定環境變數

在專案根目錄建立 `.env`，內容如下：

```env
# 經理營運 Agent 與遊客 LINE 問答 Agent 共用
GOOGLE_API_KEY=填入_Google_API_Key

# 中央氣象署開放資料平台
Weather_API_KEY=填入_CWA_API_Key

# 發送遊客通知及回覆 LINE Webhook
CHANNEL_ACCESS_TOKEN=填入_LINE_Channel_Access_Token

# 發送維修通知
WORKER_LINE_USER_ID=填入_維修人員_LINE_User_ID
WORKER_CHANNEL_ACCESS_TOKEN=填入_維修頻道_Channel_Access_Token
```

只使用遊客 LINE 客服時，至少需要 `GOOGLE_API_KEY` 與 `CHANNEL_ACCESS_TOKEN`；完整營運功能還需要天氣 API 金鑰與維修通知設定。變數名稱有大小寫之分，請保持與範例完全一致。`.env` 已列入 `.gitignore`，請勿將真實金鑰或 Token 提交到版本控制。

### 5. 確認兩份獨立的 RAG 手冊

既有經理 Agent 的 RAG 讀取專案根目錄中的營運手冊，索引存放於 `faiss_index/`：

```text
樂園營運手冊.md
```

遊客 RAG 獨立讀取 `朝陽樂園遊客知識庫手冊.md`，索引存放於 `faiss_visitor_index/`。兩者沿用 `BAAI/bge-base-zh-v1.5`，但不共用索引。遊客手冊只依 Markdown 的 `###` FAQ 標題切分，每題一個 chunk，不設定 token 上限或 overlap。

目前 `ai/tools.py` 與 `ai/qa_tool.py` 各自在**模組匯入時**載入自己的向量索引，而不是等到第一次提問。前者只載入營運索引，後者只載入遊客索引；啟動 Chainlit 或 Flask 時可能因此先花時間載入 BGE。首次沒有索引時，程式會建立索引，並可能下載向量模型。

營運索引不會在手冊修改後自動更新。要重建時，先停止 Chainlit，**刪除**舊的，再重新啟動 Chainlit；程式會依《樂園營運手冊.md》和 《朝陽樂園遊客知識庫手冊.md》建立新索引。營運手冊路徑與索引路徑使用相對路徑，因此營運流程必須從專案根目錄啟動。索引檔只應從自己信任的本機建置載入。

## 啟動服務

所有服務都從專案根目錄啟動，且各自佔用一個終端機。每個 PowerShell 視窗先執行 `.\.venv\Scripts\Activate.ps1`（或直接使用 `.venv\Scripts\python.exe` 取代下列 `python`）。

### 只啟動遊客 LINE 客服

依序啟動：

1. `python server.py`：Flask Webhook 與 SQLite 初始化，預設 port 5000。
2. `python -m mcp_servers.get_facility_status`：設施狀態 MCP，port 8003。

目前遊客 Agent 在處理**一般文字問題**時就會連接設施 MCP 取得工具，因此即使只問票務，也要先啟動 8003。固定選單與加入好友歡迎訊息不會建立遊客 Agent。這條流程不需要 Ollama、Weather MCP、LINE 通知 MCP 或 Chainlit。

### 啟動完整營運系統

除上述 Flask 與設施 MCP 外，另開終端機啟動下列服務；全部就緒後再開 Chainlit：

| 服務          | 指令                                | Port／用途               |
| ------------- | ----------------------------------- | ------------------------ |
| Ollama        | `ollama serve`（若尚未在背景執行）  | 經理通知用 Gemma 模型    |
| LINE 通知 MCP | `python -m mcp_servers.line_notify` | 8001；遊客廣播與維修通知 |
| Weather MCP   | `python -m mcp_servers.weather`     | 8002；中央氣象署資料     |
| Chainlit      | `python -m chainlit run app.py`     | 8000；經理營運對話       |

Chainlit 在對話開始時建立經理 Agent，會連接 8001、8002、8003 三個 MCP 服務。只開 Chainlit、不開 Flask 也可以進行營運對話，但請先確保 SQLite 資料表已由 `server.py` 初始化過。

## 服務網址

| 服務                | 本機網址                                    | 說明                       |
| ------------------- | ------------------------------------------- | -------------------------- |
| 介紹首頁            | `http://127.0.0.1:5000/`                    | 一頁式三端功能介紹         |
| Chainlit            | `http://127.0.0.1:8000`                     | 經理營運對話介面           |
| 設施管理            | `http://127.0.0.1:5000/worker`              | 查看及修改設施狀態         |
| 公告管理            | `http://127.0.0.1:5000/admin/announcements` | 建立與刪除公告             |
| 公告列表            | `http://127.0.0.1:5000/announcements`       | 查看已發布公告             |
| LINE Webhook        | `http://127.0.0.1:5000/webhook`             | 接收 LINE 事件的 POST 端點 |
| LINE 通知 MCP       | `http://127.0.0.1:8001/mcp`                 | 天氣廣播、維修通知         |
| Weather MCP         | `http://127.0.0.1:8002/mcp`                 | 天氣資料                   |
| Facility Status MCP | `http://127.0.0.1:8003/mcp`                 | SQLite 設施狀態            |

LINE 平台無法存取電腦上的 `127.0.0.1`。要接收真實 LINE Webhook，需透過 ngrok 等 HTTPS 通道公開 **Flask 的 port 5000**，並把公開網址加上 `/webhook` 設定到 LINE Developers Console。只在瀏覽器開啟本機網址，不會自行收到 LINE 訊息；專案內沒有提供 ngrok 設定檔。**公開 Webhook 不會自動改寫 Flex 訊息內的連結**，對外發送前須另外檢查那些連結是否可由手機開啟。

## 使用範例

遊客在 LINE 可輸入「票價是多少？」、「急流泛舟目前開放嗎？」或點選固定選單。固定選單的 Flex 回覆不經過遊客 Agent；一般文字問答才會使用 Gemini、遊客手冊與可用的設施工具。

經理在 Chainlit 可詢問：

- `現在天氣如何？`
- `目前有哪些設施維修中？`
- `如果下大雨，樂園應該怎麼處理？`
- `根據目前狀況提供營運建議。`
- `發送大雨通知。`
- `發送維修通知。`

經理端的完整操作說明見 [chainlit.md](chainlit.md)。要發布公告，請另開公告管理頁填寫標題與內容，送出後到公告列表核對；不能在對話中請 Agent 直接發布。維修人員則在 `/worker` 選擇各設施狀態並儲存。

## 基本驗證

安裝完成後，可先執行 `python -m pip check` 確認目前虛擬環境沒有套件相依衝突。啟動 Flask 後，依序查看首頁、`/worker` 和 `/admin/announcements` 是否能顯示；再啟動三個 MCP 與 Chainlit，分別測試手冊、天氣和設施問題。

## 專案目錄

```text
CYUT_PARK_AGENT\
├─ ai\                  # 經理 Agent、遊客 Agent、通知 Sub-agent、各自工具與提示詞
├─ db\                  # SQLite 初始化與資料存取；執行後產生 cyut_park.db
├─ Line_template\       # 固定選單與通知的 Flex Message JSON
├─ mcp_client\          # 三個 MCP 服務的連線設定
├─ mcp_servers\         # LINE 通知、天氣、設施狀態 MCP
├─ rag\                 # 兩份手冊的切分、Embedding 與 FAISS 載入
├─ routes\              # Flask Webhook、設施與公告路由
├─ services\            # LINE Reply API 呼叫
├─ static\              # Flask 頁面的 CSS、圖片與 JavaScript
├─ templates\           # Flask HTML 模板
├─ app.py                # Chainlit 經理介面
├─ server.py             # Flask 與資料庫初始化入口
├─ config.py             # 路徑、時區與環境變數
├─ requirements.txt      # 固定的 Python 依賴版本
├─ chainlit.md            # 經理端新手教學
├─ 專案工作流程.md        # 現有程式的詳細資料流
├─ 系統區塊圖.md          # 可修改的 Mermaid 系統圖
├─ 系統架構圖.png         # 系統圖圖片版
├─ 專案檢查報告.md        # 依賴檢查與待修問題
├─ 樂園營運手冊.md        # 經理 RAG 知識來源
└─ 朝陽樂園遊客知識庫手冊.md  # 遊客 RAG 知識來源
```

## 常見問題

### `ModuleNotFoundError: No module named 'config'`

請確認目前目錄是專案根目錄，並使用模組方式啟動 MCP Server：

```powershell
python -m mcp_servers.weather
```

不要先切換到 `mcp_servers` 後執行 `python weather.py`，否則 Python 可能找不到根目錄的 `config.py`。

### Chainlit 啟動或開始對話時顯示連線失敗

經理 Agent 在對話開始時會連接三個 MCP Server。請確認 8001、8002、8003 都已啟動，且 `mcp_client/mcp_client.py` 中的網址沒有被修改。遊客 LINE 問答目前則需要 8003。

### Flask 啟動時 BGE 模型載入訊息出現兩次

`server.py` 使用 Flask 開發模式的重新載入器，可能讓匯入階段的遊客向量模型載入兩次。若程式最後正常顯示 `Running on http://127.0.0.1:5000`，這通常不是啟動失敗；若要排查卡住或記憶體使用量，請先確認索引與模型載入是否完成。

### `ollama` 不是內部或外部命令

請安裝 Ollama，重新開啟終端機，再執行 `ollama --version`。若仍無法使用，請確認 Ollama 已加入系統 PATH。

### Ollama 顯示找不到 `gemma4:e2b`

```powershell
ollama pull gemma4:e2b
```

### Google API 回傳錯誤

確認 `.env` 的 `GOOGLE_API_KEY`、目前程式指定的 Gemini 模型 ID，以及 Gemini API 的錯誤碼與訊息。暫時性伺服器錯誤可稍後重試；不要只憑 HTTP 500 判定 API Key 有效或無效。

### 修改營運手冊後仍取得舊內容

營運索引來自 `樂園營運手冊.md`，遊客索引來自 `朝陽樂園遊客知識庫手冊.md`；修改 Markdown 不會自動更新已載入的 FAISS。請依上方「確認兩份獨立的 RAG 手冊」重建對應索引並重啟相應服務。
