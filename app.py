"""Flask web application for the NLP course recommendation chatbot."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session

from chatbot_ml import load_or_train, predict_intent


ROOT = Path(__file__).resolve().parent
CONFIDENCE_THRESHOLD = 0.34

app = Flask(__name__)
app.secret_key = os.environ.get("CHATBOT_SECRET", "local-development-secret-change-me")

model = load_or_train()
with (ROOT / "data" / "courses.json").open(encoding="utf-8") as file:
    COURSE_CATALOG = json.load(file)

POSITIVE_WORDS = {"love", "like", "enjoy", "great", "good", "excited", "happy", "awesome", "interesting"}
NEGATIVE_WORDS = {"hate", "dislike", "bad", "confused", "difficult", "hard", "boring", "frustrated", "unsure"}


def sentiment(message: str) -> str:
    words = {word.strip(".,!?;:").lower() for word in message.split()}
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"


def response_for(intent: str) -> tuple[str, list[dict]]:
    if intent == "Greeting":
        return "Hello! Tell me what you enjoy learning or which career you want to pursue.", []
    if intent == "Goodbye":
        return "Goodbye! Your next skill is waiting whenever you are ready.", []
    if intent == "Thanks":
        return "You’re welcome! Ask me about another skill or career whenever you like.", []
    if intent == "Recommendation":
        return (
            "I can help. Tell me a goal such as ‘I want to analyze business data,’ "
            "‘I enjoy building websites,’ or ‘I want to protect computer systems.’",
            [],
        )
    courses = COURSE_CATALOG.get(intent, [])
    readable = intent.replace("_", " ")
    return f"Based on your message, the {readable} path looks like a strong fit. Here are my top recommendations:", courses


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if len(message) > 500:
        return jsonify({"error": "Please keep your message under 500 characters."}), 400

    intent, confidence = predict_intent(model, message)
    tone = sentiment(message)
    if confidence < CONFIDENCE_THRESHOLD:
        reply, courses = (
            "I’m not confident I understood that. Could you rephrase it and mention a skill or career goal?",
            [],
        )
        shown_intent = "Unknown"
    else:
        reply, courses = response_for(intent)
        shown_intent = intent

    history = session.get("history", [])
    history.append({"user": message, "intent": shown_intent, "confidence": round(confidence, 3)})
    session["history"] = history[-10:]

    return jsonify(
        {
            "reply": reply,
            "intent": shown_intent,
            "confidence": round(confidence, 3),
            "sentiment": tone,
            "courses": courses,
            "history_count": len(session["history"]),
        }
    )


@app.post("/api/reset")
def reset():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model": "TF-IDF + Logistic Regression"})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
