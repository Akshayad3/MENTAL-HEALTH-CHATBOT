import os
import sys
import json
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.emotion_classifier import EmotionClassifier
from nlp.intent_classifier import IntentClassifier
from nlp.risk_detector import RiskDetector

def evaluate():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    if not os.path.exists(dataset_path):
        print("Dataset not found for evaluation.")
        return None

    with open(dataset_path, 'r') as f:
        data = json.load(f)

    texts = [item['text'] for item in data]
    true_emotions = [item['emotion'] for item in data]
    true_intents = [item['intent'] for item in data]
    true_risks = [item['risk'] for item in data]

    emotion_clf = EmotionClassifier()
    intent_clf = IntentClassifier()

    pred_emotions = [emotion_clf.predict(t)[0] for t in texts]
    pred_intents = [intent_clf.predict(t)[0] for t in texts]
    pred_risks = [RiskDetector.detect_risk(t)['level'] for t in texts]

    # --- EMOTION METRICS ---
    emotion_labels = sorted(list(set(true_emotions + pred_emotions)))
    acc_emotion = accuracy_score(true_emotions, pred_emotions)
    p_emo, r_emo, f1_emo, _ = precision_recall_fscore_support(true_emotions, pred_emotions, average='macro', zero_division=0)
    cm_emotion = confusion_matrix(true_emotions, pred_emotions, labels=emotion_labels).tolist()

    # --- INTENT METRICS ---
    intent_labels = sorted(list(set(true_intents + pred_intents)))
    acc_intent = accuracy_score(true_intents, pred_intents)
    p_int, r_int, f1_int, _ = precision_recall_fscore_support(true_intents, pred_intents, average='macro', zero_division=0)
    cm_intent = confusion_matrix(true_intents, pred_intents, labels=intent_labels).tolist()

    # --- RISK METRICS ---
    risk_labels = sorted(list(set(true_risks + pred_risks)))
    acc_risk = accuracy_score(true_risks, pred_risks)
    p_risk, r_risk, f1_risk, _ = precision_recall_fscore_support(true_risks, pred_risks, average='macro', zero_division=0)
    cm_risk = confusion_matrix(true_risks, pred_risks, labels=risk_labels).tolist()

    results = {
        'total_samples': len(data),
        'emotion_evaluation': {
            'accuracy': round(float(acc_emotion), 4),
            'precision': round(float(p_emo), 4),
            'recall': round(float(r_emo), 4),
            'macro_f1': round(float(f1_emo), 4),
            'labels': emotion_labels,
            'confusion_matrix': cm_emotion
        },
        'intent_evaluation': {
            'accuracy': round(float(acc_intent), 4),
            'precision': round(float(p_int), 4),
            'recall': round(float(r_int), 4),
            'macro_f1': round(float(f1_int), 4),
            'labels': intent_labels,
            'confusion_matrix': cm_intent
        },
        'risk_evaluation': {
            'accuracy': round(float(acc_risk), 4),
            'precision': round(float(p_risk), 4),
            'recall': round(float(r_risk), 4),
            'macro_f1': round(float(f1_risk), 4),
            'labels': risk_labels,
            'confusion_matrix': cm_risk
        }
    }
    
    return results

if __name__ == '__main__':
    res = evaluate()
    print(json.dumps(res, indent=2))
