from nlp.preprocessing import clean_text
from nlp.emotion_classifier import EmotionClassifier
from nlp.intent_classifier import IntentClassifier
from nlp.sentiment_analyzer import SentimentAnalyzer
from nlp.risk_detector import RiskDetector
from explainability.xai_engine import XAIEngine

class NLPPipeline:
    def __init__(self):
        self.emotion_classifier = EmotionClassifier()
        self.intent_classifier = IntentClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()

    def process(self, user_message):
        cleaned = clean_text(user_message)
        
        # 1. Emotion Classification
        emotion, emotion_conf = self.emotion_classifier.predict(cleaned)
        
        # 2. Intent Classification
        intent, intent_conf = self.intent_classifier.predict(cleaned)
        
        # 3. Sentiment Analysis
        sentiment_res = self.sentiment_analyzer.analyze(cleaned)
        
        # 4. Risk / Urgency Detection
        risk_res = RiskDetector.detect_risk(cleaned, emotion, intent)
        
        # 5. Explainable AI Insights
        xai_res = XAIEngine.generate_explanation(user_message, emotion, intent, sentiment_res, risk_res)
        
        return {
            'cleaned_text': cleaned,
            'emotion': emotion,
            'emotion_confidence': emotion_conf,
            'intent': intent,
            'intent_confidence': intent_conf,
            'sentiment': sentiment_res['label'],
            'sentiment_score': sentiment_res['score'],
            'risk_level': risk_res['level'],
            'risk_code': risk_res['code'],
            'risk_reason': risk_res['reason'],
            'is_critical': risk_res['is_critical'],
            'xai': xai_res
        }
