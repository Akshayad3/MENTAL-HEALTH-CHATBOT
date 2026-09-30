import database.db_helper as db

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(user_id, current_emotion='Neutral', current_intent='General Support'):
        prefs = db.get_user_preferences(user_id)
        pref_length = prefs.get('preferred_activity_length', 'short')
        
        recs = []
        
        if current_intent == 'Academic Stress' or current_emotion in ['Stress', 'Anxiety']:
            recs.append({
                'title': '5-Minute Box Breathing Exercise',
                'category': 'Breathing & Relaxation',
                'duration': '5 mins',
                'reason': 'Tailored to calm your immediate physical response to exam & workload stress.',
                'description': 'Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold for 4 seconds. Repeat 4 cycles.',
                'action_type': 'breathing_timer'
            })
            recs.append({
                'title': 'Micro-Break Task Chunking',
                'category': 'Study Planning',
                'duration': '10 mins',
                'reason': 'Reduces overwhelming academic pressure by breaking study goals into 25-minute Pomodoro sessions.',
                'description': 'Select 1 specific section to focus on. Set a timer for 25 mins, then take a mandatory 5-min screen-free break.',
                'action_type': 'guide'
            })
            
        elif current_intent == 'Sleep Difficulty':
            recs.append({
                'title': 'Bedtime Progressive Muscle Relaxation',
                'category': 'Sleep Hygiene',
                'duration': '7 mins',
                'reason': 'Helps release physical tension before sleep.',
                'description': 'Tense each muscle group (feet, legs, shoulders, jaw) for 5 seconds, then release slowly.',
                'action_type': 'guide'
            })
            recs.append({
                'title': 'Digital Sunset & Sleep Environment',
                'category': 'Sleep Hygiene',
                'duration': 'Ongoing',
                'reason': 'Minimizes blue-light stimulation interfering with melatonin.',
                'description': 'Dim overhead lights and park all mobile screens 30 minutes before lying down.',
                'action_type': 'guide'
            })

        elif current_emotion == 'Loneliness' or current_intent == 'Loneliness':
            recs.append({
                'title': 'Low-Pressure Connection Outreach',
                'category': 'Social Support',
                'duration': '5 mins',
                'reason': 'Eases social isolation through small, low-stress interactions.',
                'description': 'Send a brief text message or voice note to a friend, colleague, or family member to check in.',
                'action_type': 'guide'
            })
            recs.append({
                'title': 'Expressive Journaling Prompt',
                'category': 'Journaling',
                'duration': '10 mins',
                'reason': 'Helps process complex unspoken emotions safely.',
                'description': 'Write down: "What is 1 thing I wish someone understood about my situation right now?"',
                'action_type': 'guide'
            })

        # Default fallback grounding recommendation
        recs.append({
            'title': '5-4-3-2-1 Sensory Grounding Technique',
            'category': 'Grounding Exercise',
            'duration': '3 mins',
            'reason': 'Instantly anchors your focus when thoughts feel racing or overwhelming.',
            'description': 'Acknowledge: 5 things you see, 4 things you feel, 3 things you hear, 2 things you smell, and 1 thing you taste.',
            'action_type': 'grounding_tool'
        })
        
        recs.append({
            'title': 'Professional Consultation Support',
            'category': 'Professional Care',
            'duration': 'Information',
            'reason': 'Recommended if emotional distress or anxiety persists over consecutive weeks.',
            'description': 'Connect with campus counseling, a licensed therapist, or your healthcare clinic.',
            'action_type': 'resources'
        })

        # Save generated recommendations to database
        for r in recs:
            db.save_recommendation(user_id, r['title'], r['category'], r['reason'])

        return recs
