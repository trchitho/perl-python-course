from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Tải biến môi trường từ .env

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/api/ask-ai", methods=["POST", "OPTIONS"])
def ask_ai():
    if request.method == "OPTIONS":
        return '', 200  # 👈 Trả về 200 OK cho preflight request

    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"reply": "Thiếu nội dung câu hỏi."}), 400

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [{"role": "user", "content": user_msg}],
                "temperature": 0.7
            },
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "http://localhost:5000",  # 👈 bắt buộc có
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": "Lỗi khi gọi AI"}), 500

    except Exception as e:
        print("🔥 Lỗi gọi OpenRouter:", e)
        return jsonify({"reply": "Lỗi kết nối AI"}), 500
