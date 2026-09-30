import database.db_helper as db

class ContextMemory:
    @staticmethod
    def get_relevant_context(user_id, current_intent, current_emotion):
        """
        Retrieves relevant historical conversation summaries and recent message history
        for multi-turn context awareness.
        """
        conn = db.get_db_connection()
        
        # Fetch active conversation for user
        conv = conn.execute(
            'SELECT conversation_id FROM conversations WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
            (user_id,)
        ).fetchone()
        
        recent_history = []
        if conv:
            msgs = conn.execute(
                '''SELECT sender, message, emotion, intent, timestamp 
                   FROM messages WHERE conversation_id = ? 
                   ORDER BY timestamp DESC LIMIT 10''',
                (conv['conversation_id'],)
            ).fetchall()
            recent_history = [dict(m) for m in reversed(msgs)]

        # Fetch past user messages across conversations for summary topics
        past_user_msgs = conn.execute(
            '''SELECT m.message, m.intent, m.emotion, m.timestamp 
               FROM messages m 
               JOIN conversations c ON m.conversation_id = c.conversation_id 
               WHERE c.user_id = ? AND m.sender = 'user' 
               ORDER BY m.timestamp DESC LIMIT 20''',
            (user_id,)
        ).fetchall()
        conn.close()
        
        relevant_topics = []
        frequent_intents = set()
        
        for msg in past_user_msgs:
            m_dict = dict(msg)
            frequent_intents.add(m_dict['intent'])
            
            if current_intent in ['Academic Stress', 'Stress Management'] and m_dict['intent'] == 'Academic Stress':
                relevant_topics.append("Previously discussed academic workload and exam pressure.")
            elif current_intent == 'Sleep Difficulty' and m_dict['intent'] == 'Sleep Difficulty':
                relevant_topics.append("Has an ongoing history of sleep concerns and restless nights.")
            elif current_intent == 'Loneliness' and m_dict['intent'] == 'Loneliness':
                relevant_topics.append("Has previously expressed feelings of social isolation.")
            elif current_intent == 'Relationship Concern' and m_dict['intent'] == 'Relationship Concern':
                relevant_topics.append("Mentioned past relationship or family communication friction.")

        unique_topics = list(set(relevant_topics))
        
        return {
            'has_history': len(past_user_msgs) > 0,
            'recent_history': recent_history,
            'frequent_intents': list(frequent_intents),
            'relevant_topics': unique_topics[:3],
            'summary_prompt': "; ".join(unique_topics[:3]) if unique_topics else "No previous matching topic context."
        }
