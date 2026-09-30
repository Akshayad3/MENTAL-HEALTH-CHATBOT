class Questionnaires:
    PHQ9_QUESTIONS = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling or staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself — or that you are a failure?",
        "Trouble concentrating on things, such as reading or watching TV?",
        "Moving or speaking so slowly that other people could have noticed?",
        "Thoughts that you would be better off dead, or of hurting yourself?"
    ]

    GAD7_QUESTIONS = [
        "Feeling nervous, anxious, or on edge?",
        "Not being able to stop or control worrying?",
        "Worrying too much about different things?",
        "Trouble relaxing?",
        "Being so restless that it is hard to sit still?",
        "Becoming easily annoyed or irritable?",
        "Feeling afraid as if something awful might happen?"
    ]

    OPTION_LABELS = [
        {"text": "Not at all", "score": 0},
        {"text": "Several days", "score": 1},
        {"text": "More than half the days", "score": 2},
        {"text": "Nearly every day", "score": 3}
    ]

    @staticmethod
    def score_phq9(scores):
        total = sum(scores)
        if total <= 4:
            interpretation = "Minimal or no depressive symptoms indicated."
            severity = "Minimal"
        elif total <= 9:
            interpretation = "Mild depressive symptom range."
            severity = "Mild"
        elif total <= 14:
            interpretation = "Moderate depressive symptom range."
            severity = "Moderate"
        elif total <= 19:
            interpretation = "Moderately severe depressive symptom range."
            severity = "Moderately Severe"
        else:
            interpretation = "Severe depressive symptom range."
            severity = "Severe"

        return {
            'type': 'PHQ-9',
            'score': total,
            'max_score': 27,
            'severity': severity,
            'interpretation': f"Your PHQ-9 questionnaire score is {total}/27 ({severity}). {interpretation}",
            'disclaimer': 'This questionnaire is a validated screening tool and does NOT establish a clinical diagnosis. Consult a qualified professional for clinical evaluation.'
        }

    @staticmethod
    def score_gad7(scores):
        total = sum(scores)
        if total <= 4:
            interpretation = "Minimal or no anxiety symptoms indicated."
            severity = "Minimal"
        elif total <= 9:
            interpretation = "Mild anxiety symptom range."
            severity = "Mild"
        elif total <= 14:
            interpretation = "Moderate anxiety symptom range."
            severity = "Moderate"
        else:
            interpretation = "Severe anxiety symptom range."
            severity = "Severe"

        return {
            'type': 'GAD-7',
            'score': total,
            'max_score': 21,
            'severity': severity,
            'interpretation': f"Your GAD-7 questionnaire score is {total}/21 ({severity}). {interpretation}",
            'disclaimer': 'This questionnaire is a validated screening tool and does NOT establish a clinical diagnosis. Consult a qualified professional for clinical evaluation.'
        }
