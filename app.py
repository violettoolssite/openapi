# -*- coding: utf-8 -*-
from flask import Flask, request, Response, render_template_string
import requests
import os

# 加载环境变量
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
for line in open(env_path):
    if "=" in line: k, v = line.strip().split("=", 1); os.environ[k] = v

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
API_URL = "https://opencode.ai/zen/v1/chat/completions"

HTML = r'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GLM Chat</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a1a2e; color: #eee; height: 100vh; display: flex; flex-direction: column; }
        .header { padding: 16px; background: #16213e; text-align: center; border-bottom: 1px solid #0f3460; }
        .header h1 { font-size: 20px; color: #e94560; }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; }
        .message { max-width: 80%; margin: 10px 0; padding: 12px 16px; border-radius: 12px; line-height: 1.5; white-space: pre-wrap; }
        .user { background: #0f3460; margin-left: auto; }
        .assistant { background: #16213e; border: 1px solid #0f3460; }
        .input-area { padding: 16px; background: #16213e; border-top: 1px solid #0f3460; display: flex; gap: 10px; }
        #input { flex: 1; padding: 12px; border: 1px solid #0f3460; border-radius: 8px; background: #1a1a2e; color: #eee; font-size: 14px; }
        #input:focus { outline: none; border-color: #e94560; }
        button { padding: 12px 24px; background: #e94560; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
        button:hover { background: #ff6b6b; }
        button:disabled { background: #555; cursor: not-allowed; }
        pre { background: #0d1117; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
        code { font-family: "Fira Code", monospace; }
        .typing::after { content: "▊"; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        .thinking { color: #888; font-style: italic; }
        .thinking::before { content: "🤔 "; }
        @keyframes dots { 0%,20% {content: ".";} 40% {content: "..";} 60%,100% {content: "...";} }
        .thinking::after { content: "..."; animation: dots 1.5s infinite; }
    </style>
</head>
<body>
    <div class="header"><h1>GLM-4.7 Free Chat (流式输出)</h1></div>
    <div class="chat-container" id="chat"></div>
    <div class="input-area">
        <input type="text" id="input" placeholder="输入消息..." onkeypress="if(event.key==='Enter')send()">
        <button onclick="send()" id="btn">发送</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const btn = document.getElementById('btn');
        let messages = [];

        async function send() {
            const text = input.value.trim();
            if (!text) return;
            
            input.value = '';
            btn.disabled = true;
            
            messages.push({role: 'user', content: text});
            chat.innerHTML += '<div class="message user">' + escapeHtml(text) + '</div>';
            
            const assistantDiv = document.createElement('div');
            assistantDiv.className = 'message assistant thinking';
            assistantDiv.textContent = '思考中';
            chat.appendChild(assistantDiv);
            chat.scrollTop = chat.scrollHeight;
            
            let fullContent = '';
            let reasoningContent = '';
            let answerContent = '';
            let firstToken = true;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({messages: messages})
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value, {stream: true});
                    const lines = text.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.substring(6);
                            if (data === '[DONE]') continue;
                            try {
                                const json = JSON.parse(data);
                                const delta = json.choices?.[0]?.delta || {};
                                const content = delta.content || '';
                                const reasoning = delta.reasoning_content || '';
                                
                                if (reasoning || content) {
                                    if (firstToken) {
                                        assistantDiv.classList.remove('thinking');
                                        assistantDiv.classList.add('typing');
                                        assistantDiv.innerHTML = '';
                                        firstToken = false;
                                    }
                                    
                                    if (reasoning) {
                                        reasoningContent += reasoning;
                                        assistantDiv.innerHTML = '<div style="color:#888;font-size:12px;border-left:2px solid #444;padding-left:8px;margin-bottom:8px;">💭 ' + escapeHtml(reasoningContent) + '</div>' + escapeHtml(answerContent);
                                    }
                                    if (content) {
                                        answerContent += content;
                                        assistantDiv.innerHTML = (reasoningContent ? '<div style="color:#888;font-size:12px;border-left:2px solid #444;padding-left:8px;margin-bottom:8px;">💭 ' + escapeHtml(reasoningContent) + '</div>' : '') + escapeHtml(answerContent);
                                    }
                                    chat.scrollTop = chat.scrollHeight;
                                }
                            } catch (e) {}
                        }
                    }
                }
                
                assistantDiv.classList.remove('typing');
                fullContent = answerContent || reasoningContent;
                messages.push({role: 'assistant', content: fullContent});
                
            } catch (e) {
                assistantDiv.textContent = '错误: ' + e.message;
                assistantDiv.classList.remove('typing');
            }
            
            btn.disabled = false;
            input.focus();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    messages = request.json.get('messages', [])
    
    def generate():
        resp = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": "kimi-k2.5-free", "messages": messages, "stream": True},
            stream=True)
        
        for line in resp.iter_lines():
            if line:
                yield line.decode('utf-8') + '\n'
    
    return Response(
        generate(), 
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
