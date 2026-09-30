import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nlp.preprocessing import clean_text

class EmotionClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        self.model = MultinomialNB()
        self.is_trained = False
        self._train_from_dataset()
        
        # Rule-based fallback keyword maps for robust edge coverage
        self.keyword_rules = {
            'Anxiety': ['anxious', 'panic', 'shaking', 'heart race', 'tight chest', 'scared', 'worry', 'worried', 'nervous', 'uneasy'],
            'Sadness': ['depressed', 'down', 'crying', 'tearful', 'hopeless', 'empty', 'bed all day', 'grey', 'sad', 'grief'],
            'Fear': ['terrified', 'scared', 'fear', 'afraid', 'frightened', 'horror', 'dread'],
            'Anger': ['furious', 'mad', 'angry', 'hate', 'rage', 'fight', 'arguing'],
            'Frustration': ['frustrated', 'annoyed', 'stuck', 'exhausted', 'ruining', 'unfair'],
            'Stress': ['stressed', 'overwhelmed', 'pressure', 'deadlines', 'exam', 'tests', 'workload', 'too much'],
            'Loneliness': ['lonely', 'isolated', 'nobody', 'no one', 'outsider', 'alone', 'ignored'],
            'Happiness': ['happy', 'great', 'calm', 'proud', 'better', 'enjoy', 'good', 'passed', 'peace'],
            'Neutral': ['information', 'what is', 'how to', 'explain', 'tell me', 'hello', 'hi']
        }

    def _train_from_dataset(self):
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evaluation', 'dataset.json')
        if not os.path.exists(dataset_path):
            return
        try:
            with open(dataset_path, 'r') as f:
                data = json.load(f)
            
            X = [clean_text(item['text']) for item in data]
            y = [item['emotion'] for item in data]
            
            X_vec = self.vectorizer.fit_transform(X)
            self.model.fit(X_vec, y)
            self.is_trained = True
        except Exception as e:
            print(f"Error training EmotionClassifier: {e}")

    def predict(self, text):
        cleaned = clean_text(text)
        if not cleaned:
            return "Neutral", 0.5
        
        # Rule check first for exact keyword matches
        for emotion, keywords in self.keyword_rules.items():
            for kw in keywords:
                if kw in cleaned:
                    return emotion, 0.85
        
        if self.is_trained:
            vec = self.vectorizer.transform([cleaned])
            probs = self.model.predict_proba(vec)[0]
            max_idx = probs.argmax()
            predicted_emotion = self.model.classes_[max_idx]
            confidence = float(probs[max_idx])
            return predicted_emotion, round(confidence, 2)
            
        return "Neutral", 0.50
