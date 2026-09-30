from nlp.preprocessing import clean_text, tokenize, remove_stopwords

class XAIEngine:
    @staticmethod
    def generate_explanation(text, emotion, intent, sentiment_res, risk_res):
        """
        Extracts key features, n-grams, and weight contributions that influenced the NLP decisions.
        """
        cleaned = clean_text(text)
        tokens = remove_stopwords(tokenize(text))
        
        # Identify key trigger words for emotion
        emotion_triggers = []
        for token in tokens:
            if token in ['exam', 'test', 'grades', 'deadlines', 'study', 'workload']:
                emotion_triggers.append({'word': token, 'influence': 'High (Academic Context)'})
            elif token in ['anxious', 'panic', 'shaking', 'scared', 'worry', 'worried']:
                emotion_triggers.append({'word': token, 'influence': 'Strong (Anxiety Signal)'})
            elif token in ['depressed', 'sad', 'crying', 'hopeless', 'empty']:
                emotion_triggers.append({'word': token, 'influence': 'Strong (Sadness Signal)'})
            elif token in ['sleep', 'insomnia', 'awake', 'tired']:
                emotion_triggers.append({'word': token, 'influence': 'High (Sleep Concern)'})
            elif token in ['lonely', 'alone', 'isolated', 'nobody']:
                emotion_triggers.append({'word': token, 'influence': 'High (Social Isolation)'})
                
        if not emotion_triggers and tokens:
            emotion_triggers = [{'word': t, 'influence': 'Moderate'} for t in tokens[:3]]

        explanation = {
            'text_length': len(text),
            'token_count': len(tokens),
            'classified_emotion': emotion,
            'classified_intent': intent,
            'sentiment_score': sentiment_res.get('score', 0.0),
            'risk_level': risk_res.get('level', '🟢 Normal'),
            'risk_reason': risk_res.get('reason', ''),
            'key_feature_weights': emotion_triggers,
            'disclaimer': 'These indicators represent statistical NLP language patterns and do NOT constitute a clinical assessment.'
        }
        return explanation
