import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nlp_mental_health_secret_key_2026_secure_hash')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'mental_health.db')
    SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}
    
    # NLP Model Parameters
    EMOTION_CLASSES = [
        'Anxiety', 'Sadness', 'Fear', 'Anger', 
        'Frustration', 'Stress', 'Loneliness', 'Happiness', 'Neutral'
    ]
    
    INTENT_CLASSES = [
        'Academic Stress', 'Anxiety Concern', 'Sleep Difficulty', 
        'Loneliness', 'Relationship Concern', 'Sadness Support', 
        'General Emotional Support', 'Stress Management', 
        'Mental Health Information', 'Coping Support'
    ]
    
    # Risk Levels
    RISK_LEVELS = {
        'NORMAL': '🟢 Normal',
        'CONCERN': '🟡 Concern',
        'HIGH_CONCERN': '🟠 High Concern',
        'CRISIS': '🔴 Crisis / Immediate Support'
    }
    
    # Crisis Emergency Hotlines & Support Resources
    CRISIS_RESOURCES = [
        {
            'region': 'International / US',
            'name': 'Suicide & Crisis Lifeline',
            'contact': '988 (Call or Text)',
            'website': 'https://988lifeline.org'
        },
        {
            'region': 'Crisis Text Line',
            'name': 'Free 24/7 Text Support',
            'contact': 'Text HOME to 741741',
            'website': 'https://www.crisistextline.org'
        },
        {
            'region': 'India',
            'name': 'Tele-MANAS Mental Health Helpline',
            'contact': '14416 / 1800 891 4416',
            'website': 'https://telemanas.mohfw.gov.in'
        },
        {
            'region': 'UK',
            'name': 'Samaritans Helpline',
            'contact': '116 123',
            'website': 'https://www.samaritans.org'
        }
    ]
