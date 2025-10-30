from flask import Flask, request, render_template, jsonify
from openai import OpenAI
import os
import sqlite3
from datetime import datetime
import json
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# ===== 設定 =====
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("請在 .env 檔案中設定 OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
ASSISTANT_ID = 'asst_zoSqB9QQT7hufLJLimrl7p3L'
DATABASE = 'conversations.db'

app = Flask(__name__)

# ===== 資料庫初始化 =====
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # 對話表
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT UNIQUE NOT NULL,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 訊息表
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ===== 資料庫操作函式 =====
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_conversation(thread_id, title=None):
    """建立新對話"""
    db = get_db()
    if not title:
        title = f"對話 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    db.execute('INSERT INTO conversations (thread_id, title) VALUES (?, ?)', (thread_id, title))
    db.commit()
    conv_id = db.execute('SELECT id FROM conversations WHERE thread_id = ?', (thread_id,)).fetchone()['id']
    db.close()
    return conv_id

def get_conversation_by_thread_id(thread_id):
    """透過 thread_id 取得對話"""
    db = get_db()
    conv = db.execute('SELECT * FROM conversations WHERE thread_id = ?', (thread_id,)).fetchone()
    db.close()
    return dict(conv) if conv else None

def save_message(conversation_id, role, content):
    """儲存訊息"""
    db = get_db()
    db.execute('INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)', 
               (conversation_id, role, content))
    db.execute('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (conversation_id,))
    db.commit()
    db.close()

def get_messages(conversation_id):
    """取得對話的所有訊息"""
    db = get_db()
    messages = db.execute('SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp', 
                          (conversation_id,)).fetchall()
    db.close()
    return [dict(m) for m in messages]

def get_all_conversations():
    """取得所有對話列表"""
    db = get_db()
    convs = db.execute('SELECT * FROM conversations ORDER BY updated_at DESC').fetchall()
    db.close()
    return [dict(c) for c in convs]

def delete_conversation(conversation_id):
    """刪除對話"""
    db = get_db()
    db.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    db.commit()
    db.close()

def generate_title_from_message(message):
    """從第一個訊息生成標題"""
    title = message[:50] + "..." if len(message) > 50 else message
    return title

# ===== OpenAI 互動 =====
def call_openai_assistant(thread_id, user_message):
    """呼叫 OpenAI Assistant API"""
    try:
        # 新訊息
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # 執行 run
        client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            model="gpt-4o-mini",
            temperature=0.2,
            instructions="請只提供簡潔回答"
        )
        
        # 取得回覆
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
        if messages.data and messages.data[0].role == "assistant":
            return messages.data[0].content[0].text.value
        return "（沒有找到 AI 回覆）"
    except Exception as e:
        return f"Error: {str(e)}"

# ===== API 路由 =====
@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/conversations', methods=['GET'])
def api_get_conversations():
    """取得所有對話列表"""
    conversations = get_all_conversations()
    return jsonify(conversations)

@app.route('/api/conversation/<int:conv_id>', methods=['GET'])
def api_get_conversation(conv_id):
    """取得特定對話的訊息"""
    messages = get_messages(conv_id)
    return jsonify(messages)

@app.route('/api/conversation', methods=['POST'])
def api_create_conversation():
    """建立新對話"""
    thread = client.beta.threads.create()
    thread_id = thread.id
    conv_id = create_conversation(thread_id, "新對話")
    return jsonify({'conversation_id': conv_id, 'thread_id': thread_id})

@app.route('/api/conversation/<int:conv_id>/message', methods=['POST'])
def api_send_message(conv_id):
    """在對話中發送訊息"""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': '訊息不能為空'}), 400
    
    # 取得對話資訊
    db = get_db()
    conv = db.execute('SELECT * FROM conversations WHERE id = ?', (conv_id,)).fetchone()
    db.close()
    
    if not conv:
        return jsonify({'error': '對話不存在'}), 404
    
    thread_id = conv['thread_id']
    
    # 儲存使用者訊息
    save_message(conv_id, 'user', user_message)
    
    # 如果是第一條訊息，自動生成標題
    messages = get_messages(conv_id)
    if len(messages) == 1:
        title = generate_title_from_message(user_message)
        db = get_db()
        db.execute('UPDATE conversations SET title = ? WHERE id = ?', (title, conv_id))
        db.commit()
        db.close()
    
    # 呼叫 OpenAI
    ai_response = call_openai_assistant(thread_id, user_message)
    
    # 儲存 AI 回覆
    save_message(conv_id, 'assistant', ai_response)
    
    return jsonify({
        'user_message': user_message,
        'ai_response': ai_response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/conversation/<int:conv_id>', methods=['DELETE'])
def api_delete_conversation(conv_id):
    """刪除對話"""
    delete_conversation(conv_id)
    return jsonify({'message': '對話已刪除'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
