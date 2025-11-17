from flask import jsonify, request


def chat():
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()
    if not msg:
        return jsonify({'answer': 'Please type a question.'})
    # Minimal stub answer; hook to real AI provider later
    if 'ram' in msg.lower():
        return jsonify({'answer': 'RAM (Random Access Memory) is temporary memory used by the CPU to store working data.'})
    return jsonify({'answer': f"You asked: {msg}. I will improve with real AI soon."})

