import werkzeug.security as security
import database.db_helper as db

class AuthService:
    @staticmethod
    def register_user(name, email, password):
        if not name or not email or not password:
            return False, "All fields (name, email, password) are required."
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        
        existing = db.get_user_by_email(email)
        if existing:
            return False, "An account with this email already exists."
        
        password_hash = security.generate_password_hash(password)
        user = db.create_user(name, email, password_hash, auth_provider='email')
        if not user:
            return False, "Failed to create user account."
        
        # Seed initial sample trends so user has data on day 1
        db.log_wellbeing_trend(user['user_id'], 'Stress', 6, 5, 6, date_str='2026-09-01')
        db.log_wellbeing_trend(user['user_id'], 'Anxiety', 7, 7, 5, date_str='2026-09-04')
        db.log_wellbeing_trend(user['user_id'], 'Neutral', 5, 4, 7, date_str='2026-09-08')
        db.log_wellbeing_trend(user['user_id'], 'Stress', 6, 6, 6, date_str='2026-09-11')
        
        return True, user

    @staticmethod
    def login_user(email, password):
        if not email or not password:
            return False, "Email and password are required."
        
        user = db.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password."
        
        if user['auth_provider'] == 'google' and not user['password_hash']:
            return False, "This account uses Google Social Sign-In. Please click 'Continue with Google'."
            
        if not security.check_password_hash(user['password_hash'], password):
            return False, "Invalid email or password."
        
        return True, user

    @staticmethod
    def social_login_google(google_id, name, email):
        """
        Secure Google OAuth/OpenID Connect handler.
        Never stores social media passwords. Stores only minimum identity info.
        """
        if not email or not name:
            return False, "Invalid Google OAuth payload."
            
        user = db.get_user_by_email(email)
        if not user:
            # Create user without password for social auth
            random_placeholder_hash = security.generate_password_hash(f"google_oauth_{google_id}_no_pass")
            user = db.create_user(name, email, random_placeholder_hash, auth_provider='google')
            
            # Seed initial sample trends
            db.log_wellbeing_trend(user['user_id'], 'Neutral', 4, 4, 7, date_str='2026-09-01')
            db.log_wellbeing_trend(user['user_id'], 'Stress', 5, 5, 6, date_str='2026-09-06')
            db.log_wellbeing_trend(user['user_id'], 'Happiness', 3, 3, 8, date_str='2026-09-11')
            
        return True, user

    @staticmethod
    def reset_password(email, new_password):
        if not email or not new_password:
            return False, "Email and new password are required."
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters long."
            
        user = db.get_user_by_email(email)
        if not user:
            return False, "No registered user account found with this email."
            
        new_hash = security.generate_password_hash(new_password)
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE user_id = ?', (new_hash, user['user_id']))
        conn.commit()
        conn.close()
        
        updated_user = db.get_user_by_id(user['user_id'])
        return True, updated_user

