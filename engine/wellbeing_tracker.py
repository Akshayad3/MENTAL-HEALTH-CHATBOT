import database.db_helper as db

class WellbeingTracker:
    @staticmethod
    def get_current_wellbeing(user_id):
        """
        Calculates non-diagnostic current well-being status based on past messages,
        assessments, and logged trends.
        """
        trends = db.get_user_wellbeing_trends(user_id, limit=14)
        assessments = db.get_user_assessments(user_id)
        
        # Default baseline values
        stress_level = 5
        anxiety_level = 5
        sadness_level = 4
        overall_status = "🟢 Stable"
        status_code = "STABLE"
        
        if trends:
            stress_level = round(sum(t['stress_indicator'] for t in trends) / len(trends), 1)
            anxiety_level = round(sum(t['anxiety_indicator'] for t in trends) / len(trends), 1)
            sadness_level = round(sum(10 - t['mood_indicator'] for t in trends) / len(trends), 1)

        # Check latest screening assessment
        latest_assessment = assessments[0] if assessments else None
        if latest_assessment:
            if latest_assessment['score'] > 14 or stress_level >= 8 or anxiety_level >= 8:
                overall_status = "🔴 Immediate Support Recommended"
                status_code = "IMMEDIATE_SUPPORT"
            elif latest_assessment['score'] >= 9 or stress_level >= 6 or anxiety_level >= 6:
                overall_status = "🟡 Needs Attention"
                status_code = "NEEDS_ATTENTION"

        # Determine trend direction
        stress_trend = "Stable"
        if len(trends) >= 2:
            first_half = sum(t['stress_indicator'] for t in trends[:len(trends)//2]) / (len(trends)//2)
            second_half = sum(t['stress_indicator'] for t in trends[len(trends)//2:]) / (len(trends) - len(trends)//2)
            if second_half > first_half + 0.5:
                stress_trend = "Increasing ↑"
            elif second_half < first_half - 0.5:
                stress_trend = "Decreasing ↓"

        mood_trend = "Improving ↑" if sadness_level < 5 else "Stable"

        return {
            'overall_status': overall_status,
            'status_code': status_code,
            'indicators': {
                'stress': int(stress_level * 10),     # Percentage 0-100 for UI bar
                'anxiety': int(anxiety_level * 10),
                'sadness': int(sadness_level * 10)
            },
            'raw_scores': {
                'stress': stress_level,
                'anxiety': anxiety_level,
                'sadness': sadness_level
            },
            'trends': {
                'stress': stress_trend,
                'anxiety': 'Stable',
                'mood': mood_trend
            },
            'latest_assessment': latest_assessment,
            'disclaimer': 'These indicators are AI-generated and self-reported wellness estimates and are NOT medical diagnoses.'
        }
