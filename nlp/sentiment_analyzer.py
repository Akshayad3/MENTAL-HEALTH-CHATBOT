from nlp.preprocessing import clean_text

POSITIVE_WORDS = {
    'good', 'great', 'happy', 'calm', 'peaceful', 'relaxed', 'better', 'improvement',
    'improving', 'hope', 'proud', 'love', 'enjoy', 'wonderful', 'passed', 'successful',
    'grateful', 'thankful', 'relief', 'relieved', 'optimistic', 'comfort', 'supported'
}

NEGATIVE_WORDS = {
    'sad', 'anxious', 'scared', 'terrified', 'fear', 'afraid', 'stressed', 'overwhelmed',
    'depressed', 'lonely', 'isolated', 'hopeless', 'helpless', 'angry', 'furious',
    'exhausted', 'tired', 'insomnia', 'panic', 'pain', 'fail', 'failing', 'hate',
    'hurt', 'useless', 'worthless', 'ruining', 'suffering', 'crying', 'tearful'
}

class SentimentAnalyzer:
    @staticmethod
    def analyze(text):
        cleaned = clean_text(text)
        if not cleaned:
            return {'label': 'Neutral', 'score': 0.0}
        
        words = cleaned.split()
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        
        total = pos_count + neg_count
        if total == 0:
            return {'label': 'Neutral', 'score': 0.0}
        
        compound_score = round((pos_count - neg_count) / max(len(words), 1), 2)
        
        if pos_count > neg_count:
            label = 'Positive'
        elif neg_count > pos_count:
            label = 'Negative'
        else:
            label = 'Neutral'
            
        return {
            'label': label,
            'score': compound_score,
            'pos_words': [w for w in words if w in POSITIVE_WORDS],
            'neg_words': [w for w in words if w in NEGATIVE_WORDS]
        }
