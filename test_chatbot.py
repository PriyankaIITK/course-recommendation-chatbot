import unittest

from app import app
from chatbot_ml import load_or_train, predict_intent


class ChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, SECRET_KEY="test")
        cls.client = app.test_client()
        cls.model = load_or_train()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_data_scientist_prediction(self):
        intent, confidence = predict_intent(self.model, "I want a career as a data scientist")
        self.assertEqual(intent, "Data_Scientist")
        self.assertGreater(confidence, 0.3)

    def test_chat_returns_courses(self):
        response = self.client.post("/api/chat", json={"message": "Teach me Python"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["intent"], "Python")
        self.assertGreaterEqual(len(response.json["courses"]), 1)

    def test_empty_message_is_rejected(self):
        response = self.client.post("/api/chat", json={"message": "  "})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
