import unittest
import os
import sys

# Ensure parent directory is in import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
import database.db_helper as db
from auth.auth_service import AuthService
from nlp.nlp_pipeline import NLPPipeline
from engine.emotional_support import EmotionalSupport

class TestConversationScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Config.DATABASE_PATH = os.path.join(Config.BASE_DIR, 'database', 'test_conv_scenarios.db')
        db.init_db()
        _, cls.user = AuthService.register_user('Test Conversation User', 'conv.user@example.com', 'pass12345')
        cls.nlp = NLPPipeline()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(Config.DATABASE_PATH):
            os.remove(Config.DATABASE_PATH)

    def _send_msg(self, msg_text):
        conv = db.get_or_create_active_conversation(self.user['user_id'])
        conv_id = conv['conversation_id']
        nlp_res = self.nlp.process(msg_text)
        
        db.save_message(conv_id, 'user', msg_text, nlp_res['emotion'], nlp_res['intent'], nlp_res['sentiment'], nlp_res['risk_level'])
        bot_res = EmotionalSupport.generate_response(self.user['user_id'], msg_text, nlp_res)
        db.save_message(conv_id, 'bot', bot_res['response'], 'Neutral', 'Support Response', 'Positive', nlp_res['risk_level'])
        
        return bot_res['response']

    def test_01_casual_greeting(self):
        resp = self._send_msg("hi")
        self.assertFalse(any(b in resp.lower() for b in ["i hear you", "whatever you're going through", "take a moment"]))
        self.assertTrue(any(g in resp.lower() for g in ["hey", "hello", "hi", "how's your day", "on your mind"]))

    def test_02_feeling_low(self):
        resp = self._send_msg("i am feeling low")
        self.assertFalse(resp.lower().startswith("i hear you"))
        self.assertTrue(any(w in resp.lower() for w in ["heavy", "low", "rough", "drained", "weighing"]))

    def test_03_feeling_depressed(self):
        resp = self._send_msg("i am feeling depressed")
        self.assertNotIn("you have depression", resp.lower())
        self.assertTrue(any(w in resp.lower() for w in ["depression", "depressed", "heavy", "exhausting"]))

    def test_04_breakup_announcement(self):
        resp = self._send_msg("my boyfriend broke up with me")
        self.assertTrue(any(w in resp.lower() for w in ["breakup", "broke up", "hit really hard", "routine"]))
        self.assertNotIn("whatever you're going through", resp.lower())

    def test_05_multi_turn_recency(self):
        resp = self._send_msg("it happened yesterday")
        self.assertTrue(any(w in resp.lower() for w in ["yesterday", "recent", "raw"]))

    def test_06_multi_turn_rumination(self):
        resp = self._send_msg("i can't stop thinking about it")
        self.assertTrue(any(w in resp.lower() for w in ["mind", "overdrive", "retrace", "natural", "thinking"]))

    def test_07_academic_stress(self):
        resp = self._send_msg("my exams are tomorrow and i'm freaking out")
        self.assertTrue(any(w in resp.lower() for w in ["exam", "test", "deadline", "racing"]))

    def test_08_happy_sharing(self):
        resp = self._send_msg("i'm actually feeling happy today")
        self.assertTrue(any(w in resp.lower() for w in ["fantastic", "great", "wonderful", "glad", "bright"]))
        self.assertNotIn("mental health assessment", resp.lower())

    def test_09_general_distress(self):
        resp = self._send_msg("i don't know what to do anymore")
        self.assertTrue(any(w in resp.lower() for w in ["overwhelming", "step", "focus", "carry"]))

    def test_10_crisis_override(self):
        resp = self._send_msg("I want to kill myself.")
        self.assertIn("Immediate Emergency Resources", resp)
        self.assertIn("988", resp)

if __name__ == '__main__':
    unittest.main()
