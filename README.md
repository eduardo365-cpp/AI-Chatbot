# 🤖 AI 聊天系統

基於 Flask + OpenAI Assistant API 的現代化聊天介面

## 📋 功能特色

✅ **SQLite 資料庫管理** - 永久儲存對話記錄  
✅ **對話列表** - 左側邊欄顯示所有歷史對話  
✅ **即時互動** - ChatGPT 風格的聊天介面  
✅ **Enter 送出** - Enter 傳送，Shift+Enter 換行  
✅ **自動標題** - 根據第一條訊息生成對話標題  
✅ **刪除功能** - 快速刪除不需要的對話  
✅ **深色主題** - 護眼的現代化設計  

## 🚀 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

**✅ 已經幫你設定好了！**

`.env` 檔案已經包含你的 API Key，可以直接使用。

如果未來需要更換 API Key，只需要編輯 `.env` 檔案：

```
OPENAI_API_KEY=你的新API金鑰
```

### 3. （可選）遷移舊資料

如果你有舊的 `threads_*.txt` 檔案，可以執行：

```bash
python migrate_to_db.py
```

### 4. 啟動應用

```bash
python app.py
```

### 5. 開始使用

在瀏覽器中訪問：**http://localhost:5000**

## 📁 檔案說明

```
ai/
├── app.py                  # Flask 後端主程式
├── templates/
│   └── index.html         # 前端介面
├── .env                   # 環境變數（包含 API Key）⚠️ 不要分享此檔案
├── .env.example           # 環境變數範本
├── requirements.txt       # Python 相依套件
├── migrate_to_db.py       # 資料遷移工具
└── conversations.db       # SQLite 資料庫（自動產生）
```

## 🎮 使用方式

### 建立新對話
點擊左上角的「➕ 新對話」按鈕

### 發送訊息
1. 在底部輸入框輸入訊息
2. 按 **Enter** 送出
3. 按 **Shift + Enter** 換行

### 查看歷史對話
點擊左側邊欄中的任一對話，即可載入完整內容

### 刪除對話
將滑鼠移到對話上，點擊出現的「刪除」按鈕

## 🔧 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/conversations` | 取得所有對話列表 |
| GET | `/api/conversation/<id>` | 取得特定對話訊息 |
| POST | `/api/conversation` | 建立新對話 |
| POST | `/api/conversation/<id>/message` | 發送訊息 |
| DELETE | `/api/conversation/<id>` | 刪除對話 |

## 💡 技術架構

- **後端**: Flask + SQLite
- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **API**: OpenAI Assistant API (gpt-4o-mini)
- **特效**: CSS 動畫 + 漸層設計

## ⚠️ 注意事項

1. **不要將 `.env` 檔案上傳到 Git**（已包含 API Key）
2. `.env.example` 是範本，可以分享
3. `conversations.db` 會自動建立，包含所有對話記錄
4. 首次運行會自動初始化資料庫

## 🆘 常見問題

**Q: 出現 "請在 .env 檔案中設定 OPENAI_API_KEY" 錯誤？**  
A: 確認 `.env` 檔案存在且包含正確的 API Key

**Q: 如何更換 Assistant ID？**  
A: 在 `app.py` 中修改 `ASSISTANT_ID` 變數

**Q: 可以自訂 AI 回覆風格嗎？**  
A: 可以在 `call_openai_assistant()` 函數中修改 `instructions` 參數

## 🎨 自訂化

### 修改顏色主題
編輯 `templates/index.html` 中的 CSS 變數

### 調整 AI 參數
在 `app.py` 的 `call_openai_assistant()` 中修改：
- `temperature`: 控制創意度（0-2）
- `model`: 選擇模型（gpt-4o-mini, gpt-4o 等）
- `instructions`: 設定 AI 行為指示

---

**享受你的 AI 聊天體驗！** 🚀
