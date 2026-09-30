import re
from nlp.preprocessing import clean_text

# High-risk crisis pattern expressions
CRISIS_PATTERNS = [
    r'end (my|this) life',
    r'kill my\s?self',
    r'suicide',
    r'suicidal',
    r'don\'t want to live',
    r'want to die',
    r'hurt my\s?self',
    r'self[\s-]harm',
    r'better off dead',
    r'no reason to live',
    r'ending it all'
]

HIGH_CONCERN_PATTERNS = [
    r'can\'t take this pain',
    r'give up on everything',
    r'can\'t go on',
    r'escape forever',
    r'feeling worthless',
    r'nobody would miss me',
    r'completely hopeless'
]

CONCERN_PATTERNS = [
    r'overwhelmed',
    r'depressed for weeks',
    r'panic attack',
    r'can\'t sleep for days',
    r'crying every day',
    r'so lonely'
]

class RiskDetector:
    @staticmethod
    def detect_risk(text, emotion='Neutral', intent='General Support'):
        cleaned = clean_text(text)
        
        # 1. Crisis Check
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, cleaned):
                return {
                    'level': '🔴 Crisis / Immediate Support',
                    'code': 'CRISIS',
                    'is_critical': True,
                    'reason': 'Explicit safety-critical keyword or self-harm expression detected.'
                }
                
        # 2. High Concern Check
        for pattern in HIGH_CONCERN_PATTERNS:
            if re.search(pattern, cleaned):
                return {
                    'level': '🟠 High Concern',
                    'code': 'HIGH_CONCERN',
                    'is_critical': False,
                    'reason': 'High emotional distress or severe hopelessness indicator detected.'
                }
                
        if emotion in ['Sadness', 'Anxiety'] and intent in ['Sadness Support', 'Anxiety Concern']:
            if any(w in cleaned for w in ['hopeless', 'giving up', 'cannot cope', 'terrified']):
                return {
                    'level': '🟠 High Concern',
                    'code': 'HIGH_CONCERN',
                    'is_critical': False,
                    'reason': 'Combination of severe negative emotion and distress cues.'
                }

        # 3. Concern Check
        for pattern in CONCERN_PATTERNS:
            if re.search(pattern, cleaned):
                return {
                    'level': '🟡 Concern',
                    'code': 'CONCERN',
                    'is_critical': False,
                    'reason': 'Moderate stress or persistent emotional concern detected.'
                }
                
        if emotion in ['Anxiety', 'Sadness', 'Stress', 'Loneliness', 'Fear', 'Anger', 'Frustration']:
            return {
                'level': '🟡 Concern',
                'code': 'CONCERN',
                'is_critical': False,
                'reason': 'Self-reported non-neutral emotional state.'
            }

        # 4. Normal Level
        return {
            'level': '🟢 Normal',
            'code': 'NORMAL',
            'is_critical': False,
            'reason': 'Standard conversational tone with normal risk baseline.'
        }
