import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nlp.preprocessing import clean_text

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        self.model = MultinomialNB()
        self.is_trained = False
        self._train_from_dataset()
        
        self.keyword_rules = {
            'Academic Stress': ['exam', 'test', 'midterm', 'grade', 'study', 'assignment', 'presentation', 'college', 'school', 'gpa'],
            'Anxiety Concern': ['panic', 'heart race', 'tight chest', 'anxiety attack', 'shaking', 'uneasy', 'terrified'],
            'Sleep Difficulty': ['sleep', 'insomnia', 'awake', 'night', 'tired', 'exhausted', 'bedtime', 'restless'],
            'Loneliness': ['lonely', 'isolated', 'no friends', 'outsider', 'alone', 'nobody cares'],
            'Relationship Concern': ['partner', 'parents', 'fight', 'arguing', 'roommate', 'relationship', 'breakup', 'family'],
            'Sadness Support': ['hopeless', 'depressed', 'tearful', 'crying', 'sad', 'giving up', 'empty'],
            'Coping Support': ['exercise', 'mindfulness', 'meditation', 'relaxation', 'calm down', 'breathing', 'tips'],
            'Stress Management': ['manage stress', 'workplace', 'workload', 'burnout', 'pressure'],
            'Mental Health Information': ['what is', 'how does', 'definition', 'cortisol', 'therapy', 'symptoms'],
            'General Emotional Support': ['hello', 'hi', 'listen', 'thank you', 'confide', 'talk']
        }

    def _train_from_dataset(self):
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evaluation', 'dataset.json')
        if not os.path.exists(dataset_path):
            return
        try:
            with open(dataset_path, 'r') as f:
                data = json.load(f)
            
            X = [clean_text(item['text']) for item in data]
            y = [item['intent'] for item in data]
            
            X_vec = self.vectorizer.fit_transform(X)
            self.model.fit(X_vec, y)
            self.is_trained = True
        except Exception as e:
            print(f"Error training IntentClassifier: {e}")

    def predict(self, text):
        cleaned = clean_text(text)
        if not cleaned:
            return "General Emotional Support", 0.5
        
        # Rule fallback check
        for intent, keywords in self.keyword_rules.items():
            for kw in keywords:
                if kw in cleaned:
                    return intent, 0.85
        
        if self.is_trained:
            vec = self.vectorizer.transform([cleaned])
            probs = self.model.predict_proba(vec)[0]
            max_idx = probs.argmax()
            predicted_intent = self.model.classes_[max_idx]
            confidence = float(probs[max_idx])
            return predicted_intent, round(confidence, 2)
            
        return "General Emotional Support", 0.50
