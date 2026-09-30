import os
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
import database.db_helper as db
from auth.auth_service import AuthService
from nlp.nlp_pipeline import NLPPipeline
from report_processor.document_extractor import DocumentExtractor
from report_processor.report_summarizer import ReportSummarizer
from screening.questionnaires import Questionnaires
from engine.wellbeing_tracker import WellbeingTracker
from engine.recommendation_engine import RecommendationEngine
from engine.emotional_support import EmotionalSupport
from evaluation.evaluate_models import evaluate

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# Ensure required directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

# Initialize Database Schema
db.init_db()

# Initialize NLP Pipeline Singleton
nlp_pipeline = NLPPipeline()

def get_current_user_id():
    return session.get('user_id')

# --- MAIN ROUTE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- AUTHENTICATION ENDPOINTS (Requirement 2) ---
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    success, result = AuthService.register_user(name, email, password)
    if success:
        session['user_id'] = result['user_id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        return jsonify({'success': True, 'user': result})
    return jsonify({'success': False, 'message': result}), 400

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    success, result = AuthService.login_user(email, password)
    if success:
        session['user_id'] = result['user_id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        return jsonify({'success': True, 'user': result})
    return jsonify({'success': False, 'message': result}), 400

@app.route('/api/auth/google', methods=['POST'])
def api_google_auth():
    data = request.json or {}
    google_id = data.get('google_id')
    name = data.get('name')
    email = data.get('email')
    
    success, result = AuthService.social_login_google(google_id, name, email)
    if success:
        session['user_id'] = result['user_id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        return jsonify({'success': True, 'user': result})
    return jsonify({'success': False, 'message': result}), 400

@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    data = request.json or {}
    email = data.get('email')
    new_password = data.get('new_password')
    
    success, result = AuthService.reset_password(email, new_password)
    if success:
        session['user_id'] = result['user_id']
        session['user_name'] = result['name']
        session['user_email'] = result['email']
        return jsonify({'success': True, 'user': result})
    return jsonify({'success': False, 'message': result}), 400

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    user_id = get_current_user_id()
    if user_id:
        user = db.get_user_by_id(user_id)
        if user:
            return jsonify({'authenticated': True, 'user': user})
    return jsonify({'authenticated': False})

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# --- DASHBOARD ENDPOINT (Requirement 3 & 19) ---
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    wellbeing = WellbeingTracker.get_current_wellbeing(user_id)
    recs = RecommendationEngine.generate_recommendations(user_id)
    
    # Get active conversation and recent messages
    conv = db.get_or_create_active_conversation(user_id)
    messages = db.get_conversation_history(conv['conversation_id'])
    
    recent_activity = []
    for m in messages[-4:]:
        recent_activity.append({
            'title': f"Chat Message ({m['intent']})",
            'subtitle': f"Emotion detected: {m['emotion']}",
            'date': m['timestamp']
        })
        
    reports = db.get_user_reports(user_id)
    for r in reports[:2]:
        recent_activity.append({
            'title': f"Report Uploaded: {r['filename']}",
            'subtitle': r['summary'][:50] + '...',
            'date': r['uploaded_at']
        })

    return jsonify({
        'success': True,
        'wellbeing': wellbeing,
        'recommendations': recs,
        'recent_activity': recent_activity
    })

# --- CONVERSATIONAL AI ENDPOINTS (Requirement 4, 5, 6, 7, 8, 14, 17, 18) ---
@app.route('/api/chat', methods=['POST'])
def api_chat():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json or {}
    user_msg = data.get('message', '').strip()
    if not user_msg:
        return jsonify({'success': False, 'message': 'Message is empty'}), 400
        
    # Get active user conversation
    conv = db.get_or_create_active_conversation(user_id)
    conv_id = conv['conversation_id']
    
    # 1. Run Complete NLP Pipeline
    nlp_res = nlp_pipeline.process(user_msg)
    
    # 2. Save User Message to Database
    db.save_message(
        conv_id, 'user', user_msg, 
        emotion=nlp_res['emotion'], 
        intent=nlp_res['intent'], 
        sentiment=nlp_res['sentiment'], 
        risk_level=nlp_res['risk_level']
    )
    
    # 3. Generate Empathetic Support Response (With Memory Retrieval & Safety Check)
    bot_res = EmotionalSupport.generate_response(user_id, user_msg, nlp_res)
    
    # 4. Save Bot Response to Database
    db.save_message(
        conv_id, 'bot', bot_res['response'], 
        emotion='Neutral', 
        intent='Support Response', 
        sentiment='Positive', 
        risk_level=nlp_res['risk_level']
    )
    
    # 5. Log Longitudinal Well-being Data
    stress_map = {'High Concern': 8, 'Concern': 6, 'Normal': 4}
    stress_val = 9 if nlp_res['is_critical'] else stress_map.get(nlp_res['risk_code'], 4)
    db.log_wellbeing_trend(user_id, nlp_res['emotion'], stress_val, stress_val - 1, 6)
    
    return jsonify({
        'success': True,
        'bot_response': bot_res['response'],
        'nlp_analysis': nlp_res,
        'context_memory': bot_res.get('memory_context_used', [])
    })

@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    conv = db.get_or_create_active_conversation(user_id)
    messages = db.get_conversation_history(conv['conversation_id'])
    return jsonify({'success': True, 'messages': messages})

# --- REPORT UPLOAD ENDPOINT (Requirement 9 & 10) ---
@app.route('/api/reports/upload', methods=['POST'])
def api_report_upload():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    if 'report_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in request'}), 400
        
    file = request.files['report_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    filename = secure_filename(file.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, f"{user_id}_{filename}")
    file.save(file_path)
    
    try:
        # Extract text from PDF, DOCX, or Image
        extracted_text = DocumentExtractor.extract_text(file_path)
        
        # Summarize & Extract Medications with strict disclaimers
        summary_data = ReportSummarizer.summarize(extracted_text, filename)
        
        # Save to database
        db.save_report(user_id, filename, extracted_text, summary_data['summary_text'])
        
        return jsonify({
            'success': True,
            'summary_data': summary_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reports/history', methods=['GET'])
def api_reports_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    reports = db.get_user_reports(user_id)
    return jsonify({'success': True, 'reports': reports})

# --- SCREENING ASSESSMENTS ENDPOINT (Requirement 12) ---
@app.route('/api/assessments/submit', methods=['POST'])
def api_assessment_submit():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.json or {}
    quiz_type = data.get('type', 'PHQ-9')
    scores = data.get('scores', [])
    
    if quiz_type == 'PHQ-9':
        result = Questionnaires.score_phq9(scores)
    else:
        result = Questionnaires.score_gad7(scores)
        
    db.save_assessment(user_id, quiz_type, result['score'], result['interpretation'])
    
    # Log well-being impact
    stress_impact = min(10, max(2, int(result['score'] / 2)))
    db.log_wellbeing_trend(user_id, 'Assessment', stress_impact, stress_impact, 10 - stress_impact)
    
    return jsonify({'success': True, 'result': result})

@app.route('/api/assessments/history', methods=['GET'])
def api_assessment_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    assessments = db.get_user_assessments(user_id)
    return jsonify({'success': True, 'assessments': assessments})

# --- WELL-BEING TRENDS ENDPOINT (Requirement 13) ---
@app.route('/api/trends/history', methods=['GET'])
def api_trends_history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    trends = db.get_user_wellbeing_trends(user_id, limit=30)
    return jsonify({'success': True, 'trends': trends})

# --- RECOMMENDATIONS ENDPOINT (Requirement 15 & 16) ---
@app.route('/api/recommendations', methods=['GET'])
def api_recommendations():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    recs = RecommendationEngine.generate_recommendations(user_id)
    return jsonify({'success': True, 'recommendations': recs})

# --- RESEARCH EVALUATION ENDPOINT (Requirement 26 & 28) ---
@app.route('/api/evaluation/metrics', methods=['GET'])
def api_evaluation_metrics():
    eval_results = evaluate()
    return jsonify({'success': True, 'results': eval_results})

# --- GROUNDWORK DAILY HABIT LOG ENDPOINTS ---
@app.route('/api/habits', methods=['GET'])
def api_get_habits():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    month = request.args.get('month', '2026-09')
    data = db.get_monthly_habit_data(user_id, month)
    return jsonify({'success': True, 'data': data})

@app.route('/api/habits', methods=['POST'])
def api_create_habit():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    req_data = request.json or {}
    name = req_data.get('name', '').strip()
    icon = req_data.get('icon', '📌').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Habit name is required'}), 400
        
    habit = db.create_habit(user_id, name, icon)
    return jsonify({'success': True, 'habit': habit})

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def api_delete_habit(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    db.delete_habit(habit_id, user_id)
    return jsonify({'success': True, 'message': 'Habit deleted'})

@app.route('/api/habits/log', methods=['POST'])
def api_toggle_habit_log():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    req_data = request.json or {}
    habit_id = req_data.get('habit_id')
    date_str = req_data.get('date')
    
    if not habit_id or not date_str:
        return jsonify({'success': False, 'message': 'habit_id and date are required'}), 400
        
    status = db.toggle_habit_log(user_id, habit_id, date_str)
    return jsonify({'success': True, 'completed': status})

@app.route('/api/habits/analysis', methods=['GET'])
def api_habit_analysis():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    timeframe = request.args.get('filter', 'month')
    year_month = request.args.get('month', '2026-09')
    analysis = db.get_habit_analysis(user_id, timeframe, year_month)
    return jsonify({'success': True, 'analysis': analysis})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

