from report_processor.medication_extractor import MedicationExtractor

class ReportSummarizer:
    @staticmethod
    def summarize(extracted_text, filename):
        if not extracted_text or len(extracted_text.strip()) < 10:
            return {
                'document_name': filename,
                'summary_text': 'Report uploaded successfully, but minimal readable text was detected.',
                'key_findings': ['Document uploaded for records.'],
                'important_observations': ['No specific clinical observations identified.'],
                'recommendations_mentioned': ['Follow-up with qualified mental health professional.'],
                'medication_info': MedicationExtractor.extract_medications(extracted_text),
                'disclaimer': 'This is an AI-generated summary of the uploaded document and is NOT a medical diagnosis.'
            }
            
        lower_text = extracted_text.lower()
        
        # Extract Key Findings
        findings = []
        if any(w in lower_text for w in ['anxiety', 'anxious', 'panic', 'worry']):
            findings.append("Elevated anxiety symptoms mentioned in clinical notes.")
        if any(w in lower_text for w in ['sleep', 'insomnia', 'restless', 'fatigue']):
            findings.append("Sleep-related disturbance or fatigue observations recorded.")
        if any(w in lower_text for w in ['stress', 'overwhelmed', 'pressure', 'burnout']):
            findings.append("Stress-related indicators and high workload pressure noted.")
        if any(w in lower_text for w in ['mood', 'depress', 'sadness', 'affect']):
            findings.append("Low mood or depressive symptom indicators documented.")
            
        if not findings:
            findings.append("General psychological or wellness review recorded in document.")

        # Extract Observations
        observations = []
        if 'worry' in lower_text or 'anxious' in lower_text:
            observations.append("Persistent worry or tension mentioned.")
        if 'focus' in lower_text or 'concentrat' in lower_text:
            observations.append("Difficulty concentrating or mental fatigue reported.")
        if 'sleep' in lower_text:
            observations.append("Altered sleep routine or insomnia noted.")
            
        if not observations:
            observations.append("Standard self-reported or clinician observations.")

        # Extract Recommendations
        recs = []
        if 'therapy' in lower_text or 'cbt' in lower_text or 'counseling' in lower_text:
            recs.append("Cognitive Behavioral Therapy (CBT) or counseling suggested.")
        if 'follow' in lower_text or 'visit' in lower_text or 'check' in lower_text:
            recs.append("Follow-up evaluation with treating doctor recommended.")
        if 'mindful' in lower_text or 'relaxation' in lower_text or 'lifestyle' in lower_text:
            recs.append("Mindfulness, stress management, and lifestyle adjustments.")
            
        if not recs:
            recs.append("Follow-up with your healthcare provider to review findings.")

        # Extract Medication Info
        med_info = MedicationExtractor.extract_medications(extracted_text)

        summary_data = {
            'document_name': filename,
            'summary_text': f"Summary of {filename}: Key psychological observations include {', '.join(findings[:2]) if findings else 'general health evaluation'}.",
            'key_findings': findings,
            'important_observations': observations,
            'recommendations_mentioned': recs,
            'medication_info': med_info,
            'disclaimer': 'This is an AI-generated summary of the uploaded document and is NOT a medical diagnosis.'
        }
        
        return summary_data
