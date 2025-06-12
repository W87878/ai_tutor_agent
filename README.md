
# 🎓 EduQ Agent - 教育顧問 AI 助理

## 功能特色
- 🔍 回答招生、課程相關問題（RAG 搜尋）
- 🧠 多輪對話記憶（LangChain Memory）
- 📄 支援大型簡章 PDF 文件查詢
- ➗ 處理數學計算（MATH Agent）
- 🧾 複習對話總結（REVIEW Agent）
- 💬 WebSocket 串流回應（Streaming），即時呈現回覆內容，提高互動體驗

## 快速開始

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
建立 `.env` 檔案，內容如下：

```env
OPENAI_API_KEY=your_key_here
```

或直接在 CLI 中執行：
```bash
export OPENAI_API_KEY=your_key_here
```

### 3. 執行伺服器
```bash
python main.py
```

預設會啟動在 `ws://localhost:8000/ws`

### 4. 前端頁面
若你已建立 `frontend.html` 前端，可使用 VSCode 的 Live Server 外掛打開：

```bash
# 或手動開啟 HTML 檔案
open frontend.html
```

## 範例對話

```txt
一元二次方程式是什麼？       => PDF
請問 12 + 37 等於多少？                    => MATH
幫我整理剛剛問過的內容                     => REVIEW
```

## 資料來源
請將 PDF 檔案放到 `docs/` 資料夾中，會自動建立向量索引。

## 聯絡作者
Steve Wang | 2025
