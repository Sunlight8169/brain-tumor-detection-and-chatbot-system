"""
Authentication System for Brain Tumor Medical Assistant
Email OTP-based Registration & Forgot Password
"""
import sqlite3
import hashlib
import random
import time
from datetime import datetime, timedelta, timezone
import jwt
import smtplib
from email.message import EmailMessage
import re

# ================= EMAIL CONFIG =================
SMTP_EMAIL = "surajvish254@gmail.com"          
SMTP_APP_PASSWORD = "outjmiyejpubnuaw"     

# ================= AUTH SYSTEM =================
class AuthenticationSystem:

    def __init__(self, db_path="users.db", secret_key="brain-tumor-secret-key"):
        self.db_path = db_path
        self.secret_key = secret_key
        self.email_otp_storage = {}
        self.init_database()
        print("✅ Email OTP Authentication System Ready")

    # ================= DATABASE =================
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'patient',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            patient_name TEXT,
            patient_age TEXT,
            patient_gender TEXT,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        conn.commit()
        conn.close()

    # ================= HELPERS =================
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def validate_email(self, email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    # ================= EMAIL OTP =================
    def send_email_otp(self, email, purpose):
        """
        purpose = 'register' | 'reset'
        """
        email = email.strip().lower()

        if not self.validate_email(email):
            return {"success": False, "message": "Invalid email format"}

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        user_exists = cur.fetchone()
        conn.close()

        if purpose == "register" and user_exists:
            return {"success": False, "message": "Email already registered"}

        if purpose == "reset" and not user_exists:
            return {"success": False, "message": "Email not registered"}

        otp = self.generate_otp()

        self.email_otp_storage[email] = {
            "otp": otp,
            "purpose": purpose,
            "verified": False,
            "expires": time.time() + 300,
            "attempts": 0
        }

        try:
            msg = EmailMessage()
            msg["Subject"] = "Brain Tumor Medical Assistant - OTP Verification"
            msg["From"] = SMTP_EMAIL
            msg["To"] = email
            msg.set_content(f"""
Your One-Time Password (OTP) is:

🔢 {otp}

Purpose: {purpose.upper()}
Validity: 5 minutes

If you did not request this, please ignore this email.
""")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
                server.send_message(msg)

            return {"success": True, "message": "OTP sent to email"}

        except Exception as e:
            return {"success": False, "message": str(e)}

    def verify_email_otp(self, email, otp, purpose="register"):
        email = email.strip().lower()
        data = self.email_otp_storage.get(email)

        if not data:
            return {"success": False, "message": "OTP not found"}

        if data["purpose"] != purpose:
            return {"success": False, "message": "Invalid OTP purpose"}

        if time.time() > data["expires"]:
            del self.email_otp_storage[email]
            return {"success": False, "message": "OTP expired"}

        if data["attempts"] >= 3:
            del self.email_otp_storage[email]
            return {"success": False, "message": "Too many wrong attempts"}

        if data["otp"] == otp:
            data["verified"] = True
            return {"success": True, "message": "OTP verified successfully"}

        data["attempts"] += 1
        return {"success": False, "message": "Invalid OTP"}
    

    # ================= REGISTRATION =================


    def register_user(self, name, email, password, role="patient"):
        email = email.strip().lower()
        name = name.strip()
        
        print(f"📝 Registration attempt:")
        print(f"   Name: {name}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        
        if not name or not email or not password:
            return {"success": False, "message": "All fields are required"}
        
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return {"success": False, "message": "Invalid email format"}
        
        otp_data = self.email_otp_storage.get(email)
        if not otp_data:
            return {"success": False, "message": "OTP not found. Please verify email first"}
        
        if otp_data.get("purpose") != "register":
            return {"success": False, "message": "Invalid OTP purpose"}
        
        if not otp_data.get("verified"):
            return {"success": False, "message": "Email OTP not verified"}
        
        password_hash = self.hash_password(password)
        print(f"🔐 Password hash: {password_hash[:20]}...")
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                return {"success": False, "message": "Email already registered"}
            
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (name, email, password_hash, role))
            
            conn.commit()
            
            user_id = cur.lastrowid
            if user_id:
                print(f"✅ User registered successfully: {email} (ID: {user_id})")
                
                cur.execute("SELECT email, password_hash FROM users WHERE id = ?", (user_id,))
                check = cur.fetchone()
                print(f"✅ Verification - Email stored: {check[0]}")
                print(f"✅ Verification - Hash stored: {check[1][:20]}...")
            else:
                return {"success": False, "message": "Failed to create user"}
            
        except sqlite3.IntegrityError as e:
            print(f"❌ IntegrityError: {e}")
            return {"success": False, "message": "Email already exists"}
        
        except Exception as e:
            print(f"❌ Database error: {e}")
            return {"success": False, "message": f"Database error: {str(e)}"}
        
        finally:
            if conn:
                conn.close()
        
        try:
            del self.email_otp_storage[email]
            print(f"✅ OTP cleared for {email}")
        except KeyError:
            pass
        
        return {"success": True, "message": "Account created successfully"}
    


    # ================= LOGIN =================

    
    def login_user(self, email, password):
        email = email.strip().lower()
        
        print(f"🔍 Login attempt for: {email}")
        
        password_hash = self.hash_password(password)
        print(f"🔐 Password hash: {password_hash[:20]}...")

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("SELECT id, name, role, password_hash FROM users WHERE email=?", (email,))
            user = cur.fetchone()
            
            if not user:
                print(f"❌ User not found: {email}")
                return {"success": False, "message": "Invalid email or password"}
            
            user_id, name, role, stored_hash = user
            print(f"✅ User found: {name} (ID: {user_id})")
            print(f"🔐 Stored hash: {stored_hash[:20]}...")
            
            if stored_hash != password_hash:
                print(f"❌ Password mismatch for: {email}")
                return {"success": False, "message": "Invalid email or password"}
            
            print(f"✅ Login successful: {email}")
            
            token = self.create_jwt(user_id, name, email, role)

            return {
                "success": True,
                "token": token,
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "role": role
                }
            }
        except Exception as e:
            print(f"❌ Login error: {e}")
            return {"success": False, "message": f"Login error: {str(e)}"}
        
        finally:
            if conn:
                conn.close()


    # ================= FORGOT PASSWORD =================


    def reset_password(self, email, new_password):
        email = email.strip().lower()
        
        if len(new_password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}

        otp_data = self.email_otp_storage.get(email)
        if not otp_data or not otp_data["verified"] or otp_data["purpose"] != "reset":
            return {"success": False, "message": "Email OTP verification required"}

        password_hash = self.hash_password(new_password)

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
            UPDATE users SET password_hash=?
            WHERE email=?
            """, (password_hash, email))
            conn.commit()
            
            if cur.rowcount == 0:
                return {"success": False, "message": "Email not found"}
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return {"success": False, "message": f"Database error: {str(e)}"}
        
        finally:
            if conn:
                conn.close()

        del self.email_otp_storage[email]
        return {"success": True, "message": "Password reset successful"}

    # ================= JWT =================
    def create_jwt(self, user_id, name, email, role):
        payload = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ================= USER PROFILE =================

    def get_user_profile(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        SELECT id, name, email, role, created_at FROM users
        WHERE id=?
        """, (user_id,))
        user = cur.fetchone()
        conn.close()

        if not user:
            return None

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "created_at": user[4]
        }

    # ================= SCAN HISTORY =================
    def save_scan_history(self, user_id, prediction, confidence, patient_name="", patient_age="", patient_gender=""):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO scan_history (user_id, prediction, confidence, patient_name, patient_age, patient_gender)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, prediction, confidence, patient_name, patient_age, patient_gender))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Scan saved successfully"}

    def get_scan_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        SELECT id, prediction, confidence, patient_name, patient_age, patient_gender, scan_date
        FROM scan_history
        WHERE user_id=?
        ORDER BY scan_date DESC
        LIMIT ?
        """, (user_id, limit))
        scans = cur.fetchall()
        conn.close()

        return [
            {
                "id": scan[0],
                "prediction": scan[1],
                "confidence": scan[2],
                "patient_name": scan[3],
                "patient_age": scan[4],
                "patient_gender": scan[5],
                "scan_date": scan[6]
            }
            for scan in scans
        ]