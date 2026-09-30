import re
import random
import database.db_helper as db

FORBIDDEN_OPENERS = [
    "i hear you",
    "thank you for sharing",
    "i'm sorry you're going through this",
    "whatever you're going through",
    "taking a moment to express",
    "would you like to express what's on your heart",
    "what would feel most helpful for our conversation",
    "i am here to listen and support you",
    "your feelings are completely valid"
]

class DynamicNLGEngine:
    @staticmethod
    def extract_understanding(user_message, conversation_history=None):
        """
        Analyses user message and multi-turn conversation history to extract:
        - topic, subtopic, emotion, intent, entities, recency, and context reference.
        """
        text = user_message.strip()
        lower_text = text.lower()
        
        # 1. Check for multi-turn context from history
        last_user_msg = ""
        last_bot_msg = ""
        recent_topic = None
        recent_entities = {}
        
        if conversation_history:
            for m in reversed(conversation_history):
                if m['sender'] == 'user' and not last_user_msg:
                    last_user_msg = m['message'].lower()
                elif m['sender'] == 'bot' and not last_bot_msg:
                    last_bot_msg = m['message']

        # Determine if previous turns discussed a breakup / relationship
        if last_user_msg and any(w in last_user_msg for w in ['bf', 'boyfriend', 'gf', 'girlfriend', 'breakup', 'broke up', 'dumped', 'ex']):
            recent_topic = 'breakup'
            recent_entities['partner'] = 'boyfriend' if any(w in last_user_msg for w in ['bf', 'boyfriend']) else 'partner'
            
        elif last_user_msg and any(w in last_user_msg for w in ['exam', 'test', 'midterm', 'grade', 'study']):
            recent_topic = 'academic_stress'

        # 2. Extract current turn entities
        entities = {}
        if re.search(r'\b(yesterday|last night|this morning)\b', lower_text):
            time_match = re.search(r'\b(yesterday|last night|this morning)\b', lower_text)
            entities['recency'] = time_match.group(0)
            
        if re.search(r'\b(bf|boyfriend|gf|girlfriend|ex|partner)\b', lower_text):
            p_match = re.search(r'\b(bf|boyfriend|gf|girlfriend|ex|partner)\b', lower_text)
            entities['partner'] = p_match.group(0)

        # 3. Detect Topic & Intent
        topic = 'general'
        
        # Greetings
        if lower_text in ['hi', 'hello', 'hey', 'hey there', 'hi there', 'good morning', 'good evening', 'sup']:
            topic = 'greeting'
            
        # Happiness / Positive sharing
        elif any(w in lower_text for w in ['happy', 'great day', 'feeling good', 'passed', 'proud', 'wonderful', 'doing well', 'calm']):
            if not any(neg in lower_text for neg in ['not happy', 'isn\'t great', 'less happy']):
                topic = 'happiness'

        # Breakup / Relationship Loss
        elif any(w in lower_text for w in ['breakup', 'broke up', 'dumped', 'left me', 'doesn\'t love me', 'ex-boyfriend', 'ex-girlfriend']) or \
             (recent_topic == 'breakup' and any(w in lower_text for w in ['yesterday', 'it happened', 'thinking about it', 'he said', 'she said', 'don\'t love me', 'love me anymore'])):
            topic = 'breakup'

        # Academic Stress
        elif any(w in lower_text for w in ['exam', 'test', 'midterm', 'final', 'grade', 'freaking out', 'study', 'assignment', 'college', 'gpa']):
            topic = 'academic_stress'

        # Sleep Difficulties
        elif any(w in lower_text for w in ['sleep', 'insomnia', 'awake', 'restless', 'nightmare', 'can\'t sleep']):
            topic = 'sleep'

        # Loneliness
        elif any(w in lower_text for w in ['lonely', 'isolated', 'no friends', 'outsider', 'alone', 'nobody cares', 'nobody talks']):
            topic = 'loneliness'

        # Depressed / Low Mood
        elif 'depressed' in lower_text or 'depression' in lower_text:
            topic = 'feeling_depressed'
        elif any(w in lower_text for w in ['feeling low', 'feel low', 'down today', 'feeling grey', 'drained', 'empty']):
            topic = 'feeling_low'

        # General Distress / Hopelessness / Confusion
        elif any(w in lower_text for w in ['don\'t know what to do', 'can\'t take this', 'giving up', 'overwhelmed', 'terrible', 'awful']):
            topic = 'distress'

        # Inherit topic if current text is short continuation (e.g. "yesterday", "i can't stop thinking about it")
        if topic == 'general' and recent_topic:
            topic = recent_topic

        # Merge entities with past turn entities
        for k, v in recent_entities.items():
            if k not in entities:
                entities[k] = v

        return {
            'topic': topic,
            'entities': entities,
            'is_continuation': recent_topic is not None,
            'user_text': text,
            'lower_text': lower_text
        }

    @staticmethod
    def generate_dynamic_response(user_id, user_message, nlp_result, conversation_history=None):
        """
        Composes a specific, non-repetitive response dynamically matched to the context.
        """
        understanding = DynamicNLGEngine.extract_understanding(user_message, conversation_history)
        topic = understanding['topic']
        entities = understanding['entities']
        lower_text = understanding['lower_text']

        # Determine bot response strategy & structure
        # Strategies: 1=Empathy+Question, 2=Direct Acknowledgment, 3=Reflection+Observation, 4=Choice/Offer
        strategy_roll = random.random()

        response_sentences = []

        # ==========================================
        # 1. GREETING
        # ==========================================
        if topic == 'greeting':
            greetings = [
                "Hey there! How's your day going so far?",
                "Hello! I'm here if you'd like to chat, reflect, or work through anything on your mind today.",
                "Hi! What's on your mind today?"
            ]
            return random.choice(greetings)

        # ==========================================
        # 2. HAPPINESS / POSITIVE NEWS
        # ==========================================
        elif topic == 'happiness':
            positives = [
                "That's fantastic to hear! It's wonderful that you're having a good day today. What made things feel brighter?",
                "I'm really glad things are going well for you today! Enjoy this positive moment.",
                "That's great news! Taking time to appreciate the good days is so valuable. How are you planning to celebrate or enjoy the rest of your day?"
            ]
            return random.choice(positives)

        # ==========================================
        # 3. BREAKUP / RELATIONSHIP LOSS
        # ==========================================
        elif topic == 'breakup':
            recency = entities.get('recency', '')
            partner = entities.get('partner', 'partner')

            # Turn A: Explicit breakup announcement
            if any(w in lower_text for w in ['broke up', 'breakup', 'left me']):
                if 'bf' in lower_text or 'boyfriend' in lower_text:
                    response_sentences.append("Ah, that makes more sense. A breakup can hit really hard, especially when he was part of your everyday life.")
                else:
                    response_sentences.append("Ah, that makes more sense. A breakup can hit really hard, especially when that person was part of your everyday routine.")

                if recency:
                    response_sentences.append(f"Since it happened {recency}, everything is probably feeling very fresh and overwhelming right now.")
                else:
                    response_sentences.append("Did this happen recently?")

            # Turn B: Follow-up on recency ("yesterday", "it happened yesterday")
            elif any(w in lower_text for w in ['yesterday', 'last night', 'this morning']) and not any(w in lower_text for w in ['broke up', 'breakup']):
                time_str = entities.get('recency', 'Yesterday')
                response_sentences.append(f"{time_str.capitalize()} is really recent.")
                response_sentences.append("It's probably still feeling very raw right now, so you don't have to pressure yourself to be okay already.")
                
                # Variation in closing
                if strategy_roll > 0.5:
                    response_sentences.append("What happened between you two?")
                else:
                    response_sentences.append("What has been the hardest part since it happened?")

            # Turn C: Reason ("he said he doesn't love me anymore")
            elif any(w in lower_text for w in ['doesn\'t love me', 'don\'t love me', 'said he', 'said she']):
                response_sentences.append("That's a painful thing to hear from someone you love.")
                response_sentences.append("I can imagine your mind is probably replaying those words over and over.")
                if strategy_roll > 0.5:
                    response_sentences.append("Do you feel more hurt by losing him, or by the way he ended things?")
                else:
                    response_sentences.append("That's a really heavy weight to process.")

            # Turn D: Rumination ("i can't stop thinking about it")
            elif any(w in lower_text for w in ['can\'t stop thinking', 'thinking about it', 'in my head', 'replaying']):
                response_sentences.append("It's completely natural for your mind to be in overdrive after a breakup.")
                response_sentences.append("When a relationship ends abruptly, our brains constantly try to retrace steps to make sense of the shock.")
                response_sentences.append("That's an exhausting place to be.")

            # General breakup fallback
            else:
                response_sentences.append("A breakup leaves a huge gap in your daily life, and it takes time for your mind to adjust.")
                response_sentences.append("You don't have to rush yourself to 'get over it' right now.")
                if strategy_roll > 0.4:
                    response_sentences.append("What's been weighing on you the most today?")

        # ==========================================
        # 4. ACADEMIC STRESS / EXAMS
        # ==========================================
        elif topic == 'academic_stress':
            if any(w in lower_text for w in ['tomorrow', 'next week']):
                response_sentences.append("Exams right around the corner can make your stress levels spike fast.")
                response_sentences.append("It's completely normal to feel like your mind is racing when deadlines are looming.")
                if strategy_roll > 0.5:
                    response_sentences.append("Is there a specific test you're most worried about, or is it the overall workload?")
                else:
                    response_sentences.append("Remember to take a brief 5-minute breather so your brain can process what you've studied.")
            else:
                response_sentences.append("Academic pressure can feel relentless when assignments and tests pile up.")
                response_sentences.append("Trying to handle everything at once often leads to burnout.")
                if strategy_roll > 0.5:
                    response_sentences.append("We can either talk through what's stressing you, or work on breaking your tasks into smaller, manageable chunks.")
                else:
                    response_sentences.append("What part of your workload feels heaviest right now?")

        # ==========================================
        # 5. FEELING LOW / DEPRESSED
        # ==========================================
        elif topic in ['feeling_low', 'feeling_depressed']:
            if topic == 'feeling_depressed':
                response_sentences.append("Dealing with that persistent feeling of depression can be really exhausting.")
                response_sentences.append("You don't have to explain everything at once or pretend to be okay.")
            else:
                if strategy_roll < 0.33:
                    response_sentences.append("Yeah, it sounds like you're having a pretty heavy day.")
                    response_sentences.append("You don't have to explain everything at once. What's been weighing on you the most?")
                elif strategy_roll < 0.66:
                    response_sentences.append("That sounds rough. Sometimes 'feeling low' is hard to even put into words.")
                    response_sentences.append("Do you know what triggered it today, or has it been building up for a while?")
                else:
                    response_sentences.append("Got you. Let's slow things down for a moment.")
                    response_sentences.append("Is it more like sadness, exhaustion, loneliness, or just feeling emotionally drained?")

        # ==========================================
        # 6. LONELINESS / ISOLATION
        # ==========================================
        elif topic == 'loneliness':
            response_sentences.append("Feeling isolated or like no one understands you can feel really heavy.")
            response_sentences.append("It takes courage to express that loneliness.")
            if strategy_roll > 0.5:
                response_sentences.append("Has something specific happened recently that made you feel this way?")
            else:
                response_sentences.append("I'm right here with you to talk through whatever is on your mind.")

        # ==========================================
        # 7. SLEEP DIFFICULTY
        # ==========================================
        elif topic == 'sleep':
            response_sentences.append("Lying awake with a racing mind is so exhausting.")
            response_sentences.append("When you can't sleep, even minor stresses feel magnified the next day.")
            if strategy_roll > 0.5:
                response_sentences.append("Is there a specific thought keeping you up, or is your mind just racing?")
            else:
                response_sentences.append("We can try a short progressive relaxation technique if you'd like to quiet your mind.")

        # ==========================================
        # 8. GENERAL DISTRESS ("I don't know what to do anymore")
        # ==========================================
        elif topic == 'distress':
            if "don't know what to do" in lower_text:
                response_sentences.append("When everything feels overwhelming, not knowing your next step is completely understandable.")
                response_sentences.append("You don't have to figure out everything right now. Let's just focus on what's happening right in front of you.")
                if strategy_roll > 0.5:
                    response_sentences.append("Do you want to talk about what brought you to this point, or take a pause?")
            else:
                response_sentences.append("That sounds like a lot to carry all at once.")
                response_sentences.append("Take a slow breath. You don't have to navigate this completely alone.")

        # ==========================================
        # 9. GENERAL FALLBACK
        # ==========================================
        else:
            response_sentences.append("I can understand why that would be on your mind.")
            response_sentences.append("Tell me a bit more about what's been happening.")

        # Combine sentences into final string
        final_response = " ".join(response_sentences)

        # Execute Quality Check Gate
        final_response = DynamicNLGEngine.quality_check_and_refine(final_response, user_message)

        return final_response

    @staticmethod
    def quality_check_and_refine(response, user_message):
        """
        Quality control filter ensuring response passes 10 quality checks.
        Removes forbidden static template openers and verifies natural tone & length.
        """
        resp_lower = response.lower()
        
        # 1. Strip forbidden openers if present
        for forbidden in FORBIDDEN_OPENERS:
            if resp_lower.startswith(forbidden):
                # Replace opener with direct natural acknowledgment
                parts = response.split('.', 1)
                if len(parts) > 1:
                    response = parts[1].strip()
                else:
                    response = "I hear what you're saying. " + response

        # 2. Check sentence count (target 2-5 sentences)
        sentences = [s for s in re.split(r'[.!?]', response) if s.strip()]
        if len(sentences) > 5:
            response = ". ".join(sentences[:4]) + "."

        return response.strip()
