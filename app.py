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

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    messages = data.get('messages', [])
    model = data.get('model', 'kimi-k2.5-free')
    stream = data.get('stream', True)
    
    if stream:
        def generate():
            resp = requests.post(API_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "stream": True},
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
    else:
        resp = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "stream": False})
        return Response(resp.text, status=resp.status_code, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
