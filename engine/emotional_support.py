from config import Config
from memory.context_memory import ContextMemory
from engine.dynamic_nlg import DynamicNLGEngine

SAFETY_CRISIS_RESPONSE = """I am so sorry you're carrying such overwhelming pain, and I want you to know that your safety and life are deeply important. 

Because I am an AI supportive tool and not a human crisis counselor or medical provider, I cannot give you the direct clinical help you deserve right now.

If you are thinking of hurting yourself or feel in immediate danger, please reach out to dedicated crisis specialists immediately:

🆘 **Immediate Emergency Resources:**
- 📞 **US & International Suicide & Crisis Lifeline**: Call or Text **988** (Free, confidential, 24/7)
- 💬 **Crisis Text Line**: Text **HOME** to **741741**
- 🇮🇳 **India Tele-MANAS Helpline**: Call **14416** or **1800 891 4416**
- 🇬🇧 **UK Samaritans**: Call **116 123**
- 🚑 Or contact your local emergency services (911 / 112) or go to the nearest emergency department.

Please consider reaching out to a trusted family member, friend, or professional right now and staying with someone you trust."""

class EmotionalSupport:
    @staticmethod
    def generate_response(user_id, user_message, nlp_result):
        # 1. Safety Critical Crisis Override (Requirement 17)
        if nlp_result['is_critical'] or nlp_result['risk_code'] == 'CRISIS':
            return {
                'response': SAFETY_CRISIS_RESPONSE,
                'is_safety_override': True,
                'resources': Config.CRISIS_RESOURCES
            }
            
        intent = nlp_result['intent']
        emotion = nlp_result['emotion']
        
        # 2. Retrieve Conversation Context & Recent Message Stream
        context_data = ContextMemory.get_relevant_context(user_id, intent, emotion)
        
        # 3. Generate Dynamic Context-Aware Response
        response_text = DynamicNLGEngine.generate_dynamic_response(
            user_id=user_id,
            user_message=user_message,
            nlp_result=nlp_result,
            conversation_history=context_data.get('recent_history', [])
        )
        
        return {
            'response': response_text,
            'is_safety_override': False,
            'memory_context_used': context_data.get('relevant_topics', [])
        }
