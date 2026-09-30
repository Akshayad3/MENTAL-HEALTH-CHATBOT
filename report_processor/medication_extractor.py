import re

COMMON_MEDICATIONS = [
    'sertraline', 'zoloft', 'fluoxetine', 'prozac', 'escitalopram', 'lexapro',
    'alprazolam', 'xanax', 'lorazepam', 'ativan', 'clonazepam', 'klonopin',
    'diazepam', 'valium', 'bupropion', 'wellbutrin', 'venlafaxine', 'effexor',
    'duloxetine', 'cymbalta', 'aripiprazole', 'abilify', 'quetiapine', 'seroquel',
    'risperidone', 'risperdal', 'melatonin', 'propranolol', 'buspirone'
]

class MedicationExtractor:
    @staticmethod
    def extract_medications(text):
        if not text:
            return {
                'found': False,
                'medications': [],
                'disclaimer': 'Do not start, stop or change medication based on this AI summary. Follow the instructions of your treating healthcare professional.'
            }
            
        lower_text = text.lower()
        extracted = []
        
        for med in COMMON_MEDICATIONS:
            if med in lower_text:
                # Find surrounding snippet to extract dosage/frequency
                pattern = rf'({med}[\w\s,.:\dmg-]{{0,60}})'
                match = re.search(pattern, lower_text)
                snippet = match.group(1).strip() if match else med
                
                # Extract dosage if present (e.g. 50mg, 10 mg)
                dosage_match = re.search(r'\b\d+\s?mg\b', snippet)
                dosage = dosage_match.group(0) if dosage_match else 'As stated in document'
                
                # Extract frequency if present (e.g. daily, twice a day, once daily)
                freq_match = re.search(r'\b(once daily|daily|twice a day|at bedtime|every morning|as needed)\b', snippet)
                frequency = freq_match.group(0) if freq_match else 'As prescribed by physician'
                
                extracted.append({
                    'name': med.capitalize(),
                    'dosage': dosage,
                    'frequency': frequency,
                    'purpose': 'Extracted directly from uploaded clinical report'
                })
                
        return {
            'found': len(extracted) > 0,
            'medications': extracted,
            'disclaimer': 'Do not start, stop or change medication based on this AI summary. Always follow the explicit instructions of your treating healthcare professional.'
        }
