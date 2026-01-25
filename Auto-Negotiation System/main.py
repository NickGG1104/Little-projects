import re
import time
import json
import requests
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定 Ollama
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3-tw" 

class MeetingRequest(BaseModel):
    topic: str
    duration_minutes: float
    agent_a_name: str
    agent_a_role: str
    agent_b_name: str
    agent_b_role: str

def query_ollama(messages, model=MODEL_NAME, max_tokens=150):
    """
    max_tokens 放寬到 150，防止物理截斷。
    主要靠 Prompt 控制長度。
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.8, #稍微調高讓對話多變一點
            "num_predict": max_tokens, 
            # 設定停止詞，防止它自己在那邊 User: ... System: ...
            "stop": ["\nUser:", "\nSystem:", "User:", "System:"] 
        }
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

def meeting_generator(request: MeetingRequest):
    start_time = time.time()
    duration_seconds = request.duration_minutes * 60
    
    raw_history = [] 
    
    # --- 防線 1: Prompt 優化 ---
    # 明確禁止輸出名字標籤
    base_rules = (
        "規則：\n"
        "1. 限制在 30 字以內，極度簡短。\n"
        "2. 只能回應「一句話」。\n"
        "3. **絕對不要**在開頭加上你的名字、角色名或『[回答]:』之類的標籤。\n"
        "4. **直接開始說話**，就像真人對話一樣。\n"
        "5. 口語化、自然。"
    )

    yield f"data: {json.dumps({'type': 'info', 'content': '🚀 會議啟動...'})}\n\n"

    turn = 0
    while (time.time() - start_time) < duration_seconds:
        is_a_turn = (turn % 2 == 0)
        current_name = request.agent_a_name if is_a_turn else request.agent_b_name
        current_role_desc = request.agent_a_role if is_a_turn else request.agent_b_role
        other_name = request.agent_b_name if is_a_turn else request.agent_a_name
        
        messages = []
        
        # System Prompt
        messages.append({
            "role": "system",
            "content": (
                f"現在進行會議：『{request.topic}』。\n"
                f"你是 {current_name} ({current_role_desc})。\n"
                f"現在輪到你發言。你的對手是 {other_name}。\n"
                f"{base_rules}"
            )
        })

        # History
        recent_history = raw_history[-6:] 
        for h in recent_history:
            if h["speaker"] == current_name:
                messages.append({"role": "assistant", "content": h["content"]})
            else:
                # 這裡保持標記，讓 AI 知道是誰說的，但 Prompt 已經禁止它模仿
                messages.append({"role": "user", "content": f"[{h['speaker']}]: {h['content']}"})

        if len(messages) == 1:
            messages.append({"role": "user", "content": f"會議開始，請 {current_name} 先發言。"})

        # 呼叫 AI
        content = query_ollama(messages, max_tokens=150)
        
        # --- 防線 3: Python 強制清洗 (最關鍵的一步) ---
        # 使用正則表達式移除所有類似 "[xxx]:" 或 "xxx:" 的開頭
        content = clean_content(content, current_name)

        # 確保有標點符號 (視覺優化)
        if content and content[-1] not in ["。", "！", "？", ".", "!", "?"]:
            content += "。"

        raw_history.append({"speaker": current_name, "content": content})
        
        output_data = {
            "type": "chat",
            "speaker": current_name,
            "content": content
        }
        yield f"data: {json.dumps(output_data)}\n\n"
        
        turn += 1
        # 不需 Sleep，全速運轉

    # 總結
    yield f"data: {json.dumps({'type': 'info', 'content': '✨ 時間到，生成總結...'})}\n\n"
    
    # 總結時，把 raw_history 轉成文字串
    history_text = "\n".join([f"{h['speaker']}: {h['content']}" for h in raw_history])
    
    summary_prompt = [
        {"role": "system", "content": "你是一位精簡的會議記錄員。"},
        {"role": "user", "content": f"請用 3 個 bullet points (條列式) 總結以下會議，繁體中文，只講結論：\n\n{history_text}"}
    ]
    summary = query_ollama(summary_prompt, max_tokens=300)
    
    yield f"data: {json.dumps({'type': 'summary', 'content': summary})}\n\n"
    yield f"data: [DONE]\n\n"

def clean_content(text, speaker_name):
    """
    清洗 AI 回傳的內容，移除自我稱呼的標籤
    """
    if not text: return ""
    
    # 1. 移除類似 [我 回答]: [Steve]: (name): 的模式
    # 正則解釋：
    # ^\s* : 開頭可能的空白
    # \[?        : 可選的左中括號 [
    # (?:我|回答|{speaker_name}|[^\]]+) : 內容可能是 '我'、'回答'、'角色名' 或其他文字
    # \]?        : 可選的右中括號 ]
    # \s*[:：]\s* : 冒號 (全形或半形) 與前後空白
    
    # 簡單暴力版：移除開頭的 "[任何文字]:" 模式
    text = re.sub(r'^\s*\[.*?\]\s*[:：]\s*', '', text)
    
    # 移除開頭的 "名字:" 模式 (例如 "Steve: 哈囉")
    text = re.sub(f'^\s*{speaker_name}\s*[:：]\s*', '', text, flags=re.IGNORECASE)
    
    # 移除 "我回答：" 這種怪異模式
    text = re.sub(r'^\s*(我|回答)\s*[:：]\s*', '', text)
    text = re.sub(r'^\s*(主管)\s*[:：]\s*', '', text)

    # 移除引號 (有些 AI 喜歡把話包在引號裡)
    text = text.strip('"').strip("'").strip('「').strip('」')
    
    return text.strip()

@app.post("/start-meeting")
async def start_meeting(request: MeetingRequest):
    return StreamingResponse(meeting_generator(request), media_type="text/event-stream")

@app.get("/")
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)