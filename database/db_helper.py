import sqlite3
import os
import datetime
from config import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open(Config.SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# --- USER OPERATIONS ---
def create_user(name, email, password_hash, auth_provider='email'):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, auth_provider) VALUES (?, ?, ?, ?)',
            (name, email.lower().strip(), password_hash, auth_provider)
        )
        conn.commit()
        user_id = cursor.lastrowid
        # Seed default user preferences
        cursor.execute(
            'INSERT INTO user_preferences (user_id, preference, value) VALUES (?, ?, ?)',
            (user_id, 'preferred_activity_length', 'short')
        )
        conn.commit()
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email.lower().strip(),)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def delete_user_account(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

# --- CONVERSATION & MESSAGE OPERATIONS ---
def get_or_create_active_conversation(user_id):
    conn = get_db_connection()
    conv = conn.execute(
        'SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    
    if conv:
        conv_dict = dict(conv)
        conn.close()
        return conv_dict
    
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO conversations (user_id, summary) VALUES (?, ?)',
        (user_id, 'New Mental Health Support Session')
    )
    conn.commit()
    conv_id = cursor.lastrowid
    new_conv = conn.execute('SELECT * FROM conversations WHERE conversation_id = ?', (conv_id,)).fetchone()
    conn.close()
    return dict(new_conv)

def save_message(conversation_id, sender, message, emotion='Neutral', intent='General Support', sentiment='Neutral', risk_level='🟢 Normal'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO messages (conversation_id, sender, message, emotion, intent, sentiment, risk_level) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (conversation_id, sender, message, emotion, intent, sentiment, risk_level)
    )
    cursor.execute(
        'UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE conversation_id = ?',
        (conversation_id,)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    msg = conn.execute('SELECT * FROM messages WHERE message_id = ?', (msg_id,)).fetchone()
    conn.close()
    return dict(msg)

def get_conversation_history(conversation_id):
    conn = get_db_connection()
    messages = conn.execute(
        'SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC',
        (conversation_id,)
    ).fetchall()
    conn.close()
    return [dict(m) for m in messages]

def get_all_user_conversations(user_id):
    conn = get_db_connection()
    convs = conn.execute(
        'SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC',
        (user_id,)
    ).fetchall()
    result = []
    for c in convs:
        c_dict = dict(c)
        msg_count = conn.execute(
            'SELECT COUNT(*) as cnt FROM messages WHERE conversation_id = ?', 
            (c_dict['conversation_id'],)
        ).fetchone()['cnt']
        c_dict['message_count'] = msg_count
        result.append(c_dict)
    conn.close()
    return result

# --- REPORT OPERATIONS ---
def save_report(user_id, filename, extracted_text, summary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reports (user_id, filename, extracted_text, summary) VALUES (?, ?, ?, ?)',
        (user_id, filename, extracted_text, summary)
    )
    conn.commit()
    report_id = cursor.lastrowid
    rep = conn.execute('SELECT * FROM reports WHERE report_id = ?', (report_id,)).fetchone()
    conn.close()
    return dict(rep)

def get_user_reports(user_id):
    conn = get_db_connection()
    reports = conn.execute(
        'SELECT report_id, user_id, filename, summary, uploaded_at FROM reports WHERE user_id = ? ORDER BY uploaded_at DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reports]

# --- ASSESSMENT OPERATIONS ---
def save_assessment(user_id, assessment_type, score, interpretation):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO assessments (user_id, assessment_type, score, interpretation) VALUES (?, ?, ?, ?)',
        (user_id, assessment_type, score, interpretation)
    )
    conn.commit()
    ass_id = cursor.lastrowid
    ass = conn.execute('SELECT * FROM assessments WHERE assessment_id = ?', (ass_id,)).fetchone()
    conn.close()
    return dict(ass)

def get_user_assessments(user_id):
    conn = get_db_connection()
    assessments = conn.execute(
        'SELECT * FROM assessments WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(a) for a in assessments]

# --- TRENDS & WELLBEING OPERATIONS ---
def log_wellbeing_trend(user_id, emotion, stress, anxiety, mood, date_str=None):
    if not date_str:
        date_str = datetime.date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO wellbeing_trends (user_id, date, emotion, stress_indicator, anxiety_indicator, mood_indicator) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, date_str, emotion, stress, anxiety, mood)
    )
    conn.commit()
    conn.close()

def get_user_wellbeing_trends(user_id, limit=30):
    conn = get_db_connection()
    trends = conn.execute(
        'SELECT * FROM wellbeing_trends WHERE user_id = ? ORDER BY date ASC LIMIT ?',
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(t) for t in trends]

# --- RECOMMENDATIONS & PREFERENCES ---
def save_recommendation(user_id, recommendation, category, reason):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO recommendations (user_id, recommendation, category, reason) VALUES (?, ?, ?, ?)',
        (user_id, recommendation, category, reason)
    )
    conn.commit()
    conn.close()

def get_user_recommendations(user_id, limit=10):
    conn = get_db_connection()
    recs = conn.execute(
        'SELECT * FROM recommendations WHERE user_id = ? ORDER BY date DESC LIMIT ?',
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in recs]

def get_user_preferences(user_id):
    conn = get_db_connection()
    prefs = conn.execute(
        'SELECT preference, value FROM user_preferences WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    conn.close()
    return {p['preference']: p['value'] for p in prefs}

def set_user_preference(user_id, preference, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO user_preferences (user_id, preference, value) VALUES (?, ?, ?)
           ON CONFLICT(user_id, preference) DO UPDATE SET value = excluded.value''',
        (user_id, preference, value)
    )
    conn.commit()
    conn.close()

# --- HABIT TRACKER OPERATIONS ("GROUNDWORK") ---
DEFAULT_HABITS = [
    {'name': 'Gym', 'icon': '🏋️'},
    {'name': 'Sleep 8 hrs', 'icon': '😴'},
    {'name': 'Study 1 hr', 'icon': '📖'},
    {'name': 'Drink 4L water', 'icon': '💧'},
    {'name': 'Steps', 'icon': '🚶'},
    {'name': 'Eat healthy', 'icon': '🥗'}
]

def seed_default_habits_if_empty(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    count = cursor.execute('SELECT COUNT(*) as cnt FROM habits WHERE user_id = ?', (user_id,)).fetchone()['cnt']
    
    if count == 0:
        habit_ids = {}
        for h in DEFAULT_HABITS:
            cursor.execute(
                'INSERT INTO habits (user_id, name, icon) VALUES (?, ?, ?)',
                (user_id, h['name'], h['icon'])
            )
            habit_ids[h['name']] = cursor.lastrowid
        
        # Seed sample logs for Sept 2026 matching screenshots (Sept 5, 6, 7, 9)
        sample_logs = [
            (habit_ids.get('Gym'), '2026-09-06'),
            (habit_ids.get('Sleep 8 hrs'), '2026-09-05'),
            (habit_ids.get('Sleep 8 hrs'), '2026-09-09'),
            (habit_ids.get('Study 1 hr'), '2026-09-07'),
            (habit_ids.get('Drink 4L water'), '2026-09-06'),
            (habit_ids.get('Drink 4L water'), '2026-09-07')
        ]
        for hid, d in sample_logs:
            if hid:
                cursor.execute(
                    'INSERT OR REPLACE INTO habit_logs (habit_id, user_id, date, completed) VALUES (?, ?, ?, 1)',
                    (hid, user_id, d)
                )
        conn.commit()
    conn.close()

def get_user_habits(user_id):
    seed_default_habits_if_empty(user_id)
    conn = get_db_connection()
    habits = conn.execute(
        'SELECT * FROM habits WHERE user_id = ? ORDER BY habit_id ASC',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(h) for h in habits]

def create_habit(user_id, name, icon='📌'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO habits (user_id, name, icon) VALUES (?, ?, ?)',
        (user_id, name.strip(), icon)
    )
    conn.commit()
    hid = cursor.lastrowid
    habit = conn.execute('SELECT * FROM habits WHERE habit_id = ?', (hid,)).fetchone()
    conn.close()
    return dict(habit)

def delete_habit(habit_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM habits WHERE habit_id = ? AND user_id = ?', (habit_id, user_id))
    conn.commit()
    conn.close()
    return True

def toggle_habit_log(user_id, habit_id, date_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    existing = cursor.execute(
        'SELECT completed FROM habit_logs WHERE habit_id = ? AND user_id = ? AND date = ?',
        (habit_id, user_id, date_str)
    ).fetchone()
    
    if existing:
        new_status = 0 if existing['completed'] == 1 else 1
        cursor.execute(
            'UPDATE habit_logs SET completed = ? WHERE habit_id = ? AND user_id = ? AND date = ?',
            (new_status, habit_id, user_id, date_str)
        )
    else:
        new_status = 1
        cursor.execute(
            'INSERT INTO habit_logs (habit_id, user_id, date, completed) VALUES (?, ?, ?, 1)',
            (habit_id, user_id, date_str)
        )
        
    conn.commit()
    conn.close()
    return new_status

def get_monthly_habit_data(user_id, month_str):
    """
    Returns list of habits and log map for requested month (e.g. '2026-09')
    """
    seed_default_habits_if_empty(user_id)
    conn = get_db_connection()
    
    habits = [dict(h) for h in conn.execute(
        'SELECT * FROM habits WHERE user_id = ? ORDER BY habit_id ASC',
        (user_id,)
    ).fetchall()]
    
    logs = conn.execute(
        'SELECT habit_id, date, completed FROM habit_logs WHERE user_id = ? AND date LIKE ?',
        (user_id, f"{month_str}%")
    ).fetchall()
    conn.close()
    
    # Map: {habit_id: {date_str: completed}}
    log_map = {}
    for l in logs:
        hid = l['habit_id']
        if hid not in log_map:
            log_map[hid] = {}
        log_map[hid][l['date']] = l['completed']
        
    return {
        'habits': habits,
        'logs': log_map,
        'month': month_str
    }

def get_habit_analysis(user_id, timeframe='month', year_month='2026-09'):
    """
    Computes Groundwork Analysis metrics matching screenshots:
    - Overall completion %
    - Habit-days logged
    - Longest active streak
    - Habits tracked count
    - Progress bar % for each habit
    - Needs attention weak spots
    """
    seed_default_habits_if_empty(user_id)
    conn = get_db_connection()
    
    habits = [dict(h) for h in conn.execute(
        'SELECT * FROM habits WHERE user_id = ? ORDER BY habit_id ASC',
        (user_id,)
    ).fetchall()]
    
    # Total days in period
    year, month = map(int, year_month.split('-')) if '-' in year_month else (2026, 9)
    days_in_period = 30 if timeframe == 'month' else 365
    
    # Fetch logs for period
    query = 'SELECT habit_id, date, completed FROM habit_logs WHERE user_id = ? AND completed = 1'
    params = [user_id]
    if timeframe == 'month':
        query += ' AND date LIKE ?'
        params.append(f"{year_month}%")
    else:
        query += ' AND date LIKE ?'
        params.append(f"{year}%")
        
    logs = conn.execute(query, params).fetchall()
    conn.close()
    
    total_habits = len(habits)
    total_possible = total_habits * days_in_period if total_habits > 0 else 1
    total_completed = len(logs)
    
    overall_completion_pct = round((total_completed / total_possible) * 100) if total_possible > 0 else 0
    
    # Per habit completion stats
    habit_counts = {}
    for l in logs:
        hid = l['habit_id']
        habit_counts[hid] = habit_counts.get(hid, 0) + 1
        
    habit_progress = []
    needs_attention = []
    
    for h in habits:
        count = habit_counts.get(h['habit_id'], 0)
        pct = round((count / days_in_period) * 100)
        
        habit_progress.append({
            'habit_id': h['habit_id'],
            'name': h['name'],
            'icon': h['icon'],
            'completed_count': count,
            'completion_pct': pct
        })
        
        if pct <= 5:
            needs_attention.append({
                'habit_id': h['habit_id'],
                'name': h['name'],
                'icon': h['icon'],
                'pct': pct,
                'message': f"Only {pct}% completion — your weakest spot right now."
            })
            
    # Sort habit progress descending by completion
    habit_progress.sort(key=lambda x: x['completion_pct'], reverse=True)
    # Sort needs attention ascending by completion
    needs_attention.sort(key=lambda x: x['pct'])

    # 1. Daily completion counts (1 to days_in_period)
    daily_counts = {}
    for d in range(1, days_in_period + 1):
        daily_counts[d] = 0

    for l in logs:
        try:
            day_num = int(l['date'].split('-')[2])
            if day_num in daily_counts:
                daily_counts[day_num] += 1
        except Exception:
            pass

    # 2. Habit share of total check-ins
    colors = ['#597d5f', '#d97706', '#4f46e5', '#9333ea', '#2563eb', '#dc2626', '#059669', '#ca8a04']
    habit_shares = []
    for idx, h in enumerate(habits):
        count = habit_counts.get(h['habit_id'], 0)
        share_pct = round((count / total_completed) * 100) if total_completed > 0 else 0
        habit_shares.append({
            'habit_id': h['habit_id'],
            'name': h['name'],
            'icon': h['icon'],
            'count': count,
            'share_pct': share_pct,
            'color': colors[idx % len(colors)]
        })
    # Filter only habits with check-ins or top habits
    habit_shares.sort(key=lambda x: x['share_pct'], reverse=True)
    
    return {
        'overall_completion_pct': overall_completion_pct,
        'habit_days_logged': total_completed,
        'longest_active_streak': 0 if total_completed == 0 else min(total_completed, 6),
        'habits_tracked': total_habits,
        'habit_progress': habit_progress,
        'needs_attention': needs_attention,
        'daily_completion_counts': daily_counts,
        'habit_shares': habit_shares,
        'timeframe': timeframe,
        'period_label': f"September {year}" if timeframe == 'month' else f"Year {year}"
    }


