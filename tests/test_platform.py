import unittest
import os
import sys

# Ensure parent directory is in import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
import database.db_helper as db
from auth.auth_service import AuthService
from nlp.emotion_classifier import EmotionClassifier
from nlp.intent_classifier import IntentClassifier
from nlp.sentiment_analyzer import SentimentAnalyzer
from nlp.risk_detector import RiskDetector
from screening.questionnaires import Questionnaires
from report_processor.medication_extractor import MedicationExtractor
from report_processor.report_summarizer import ReportSummarizer

class TestMentalHealthPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize test database
        Config.DATABASE_PATH = os.path.join(Config.BASE_DIR, 'database', 'test_mental_health.db')
        db.init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(Config.DATABASE_PATH):
            os.remove(Config.DATABASE_PATH)

    def test_01_authentication_service(self):
        # Registration
        success, user = AuthService.register_user('Test User', 'test.user@example.com', 'securepass123')
        self.assertTrue(success)
        self.assertEqual(user['email'], 'test.user@example.com')

        # Login success
        login_ok, login_user = AuthService.login_user('test.user@example.com', 'securepass123')
        self.assertTrue(login_ok)

        # Login failure
        fail_ok, _ = AuthService.login_user('test.user@example.com', 'wrongpassword')
        self.assertFalse(fail_ok)

    def test_02_nlp_emotion_classification(self):
        clf = EmotionClassifier()
        emotion, conf = clf.predict("I feel so anxious and panicked about my exam next week.")
        self.assertIn(emotion, ['Anxiety', 'Stress', 'Fear'])
        self.assertGreater(conf, 0.4)

    def test_03_nlp_intent_classification(self):
        clf = IntentClassifier()
        intent, conf = clf.predict("I haven't slept for three nights because of overthinking.")
        self.assertIn(intent, ['Sleep Difficulty', 'Anxiety Concern'])

    def test_04_sentiment_analysis(self):
        res = SentimentAnalyzer.analyze("I am feeling great and very happy today!")
        self.assertEqual(res['label'], 'Positive')
        self.assertGreater(res['score'], 0.0)

    def test_05_risk_detection(self):
        # Crisis input
        crisis_res = RiskDetector.detect_risk("I want to end my life right now")
        self.assertEqual(crisis_res['code'], 'CRISIS')
        self.assertTrue(crisis_res['is_critical'])

        # Normal input
        normal_res = RiskDetector.detect_risk("I'm looking for a short breathing exercise.")
        self.assertEqual(normal_res['code'], 'NORMAL')
        self.assertFalse(normal_res['is_critical'])

    def test_06_screening_questionnaires(self):
        phq_res = Questionnaires.score_phq9([2, 2, 3, 2, 1, 2, 1, 0, 0])
        self.assertEqual(phq_res['score'], 13)
        self.assertEqual(phq_res['severity'], 'Moderate')

        gad_res = Questionnaires.score_gad7([3, 3, 3, 3, 2, 2, 2])
        self.assertEqual(gad_res['score'], 18)
        self.assertEqual(gad_res['severity'], 'Severe')

    def test_07_medication_extraction(self):
        sample_report = "Patient currently takes Sertraline 50mg daily for anxiety management."
        res = MedicationExtractor.extract_medications(sample_report)
        self.assertTrue(res['found'])
        self.assertEqual(res['medications'][0]['name'], 'Sertraline')
        self.assertIn('Do not start, stop or change medication', res['disclaimer'])

    def test_08_groundwork_habit_tracker(self):
        user = db.get_user_by_email('test.user@example.com')
        uid = user['user_id']
        
        # Test habit retrieval and seeding
        habits = db.get_user_habits(uid)
        self.assertGreaterEqual(len(habits), 6)
        
        # Add habit
        new_h = db.create_habit(uid, 'Read 20 pages', '📚')
        self.assertEqual(new_h['name'], 'Read 20 pages')
        
        # Toggle log
        status = db.toggle_habit_log(uid, new_h['habit_id'], '2026-09-24')
        self.assertEqual(status, 1)
        
        # Monthly data
        m_data = db.get_monthly_habit_data(uid, '2026-09')
        self.assertIn(new_h['habit_id'], m_data['logs'])
        self.assertEqual(m_data['logs'][new_h['habit_id']]['2026-09-24'], 1)
        
        # Analysis
        analysis = db.get_habit_analysis(uid, 'month', '2026-09')
        self.assertGreaterEqual(analysis['habits_tracked'], 7)
        self.assertGreaterEqual(analysis['habit_days_logged'], 1)

if __name__ == '__main__':
    unittest.main()

