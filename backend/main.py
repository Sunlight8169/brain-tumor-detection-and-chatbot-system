"""
Flask Backend with Authentication
File: backend/main.py

Features:
- Email OTP Registration
- Email OTP Password Reset
- JWT Authentication
- MRI Prediction (Protected)
- Scan History
"""

from flask import Flask, request, jsonify
from flask_cors import CORS  # type: ignore
import tensorflow as tf  # type: ignore
import numpy as np
from PIL import Image
from functools import wraps
from auth_system import AuthenticationSystem

# ================= APP SETUP =================

app = Flask(__name__)
CORS(app)

auth = AuthenticationSystem(
    db_path='users.db',
    secret_key='brain-tumor-detection-2024-secret'
)

# ================= MODEL =================

MODEL_PATH = r"C:\Users\Suraj Vishwakarma\Desktop\FinalYearProject2025\backend\saved_model.h5"

try:
    print("🔄 Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

CLASSES = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

# ================= JWT DECORATOR =================

def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token missing'}), 401

        payload = auth.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return f(current_user=payload, *args, **kwargs)
    return decorated

# ================= PUBLIC ROUTES =================

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'status': 'running',
        'message': '🧠 Brain Tumor Detection API',
        'auth': 'Email OTP',
        'version': 'Final'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'database': 'connected'
    })

# ================= AUTHENTICATION ROUTES =================

@app.route('/auth/send-email-otp', methods=['POST'])
def send_email_otp():
    """Send OTP to email for registration or password reset"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    purpose = data.get('purpose', '').strip()  # 'register' or 'reset'

    if not email or purpose not in ['register', 'reset']:
        return jsonify({'success': False, 'message': 'Email and purpose required'}), 400

    result = auth.send_email_otp(email, purpose)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/auth/verify-email-otp', methods=['POST'])
def verify_email_otp():
    """Verify OTP sent to email"""
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()
    purpose = data.get('purpose', 'register')

    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP required'}), 400

    result = auth.verify_email_otp(email, otp, purpose)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/auth/register-user', methods=['POST'])
def register_user():
    """Register new user account"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        role = data.get('role', 'patient')
        
        if not all([name, email, password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        result = auth.register_user(
            name=name,
            email=email,
            password=password,
            role=role
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/auth/login-user', methods=['POST'])
def login_user():
    """Login user and return JWT token"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password required'
            }), 400

        result = auth.login_user(email=email, password=password)
        return jsonify(result), 200 if result['success'] else 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user password after OTP verification"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        email = data.get('email', '').strip().lower()
        new_password = data.get('new_password', '').strip()

        if not email or not new_password:
            return jsonify({
                'success': False,
                'message': 'Email and new password required'
            }), 400

        result = auth.reset_password(email=email, new_password=new_password)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client-side token removal)"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

# ================= PROTECTED ROUTES =================

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile information"""
    profile = auth.get_user_profile(current_user['user_id'])
    
    if not profile:
        return jsonify({
            'success': False,
            'message': 'Profile not found'
        }), 404
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200


@app.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    """Predict brain tumor from MRI scan"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        img = Image.open(file).resize((224, 224)).convert('RGB')
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

        preds = model.predict(img_array)
        idx = int(np.argmax(preds[0]))

        auth.save_scan_history(
            user_id=current_user['user_id'],
            prediction=CLASSES[idx],
            confidence=float(preds[0][idx] * 100),
            patient_name=request.form.get('patient_name', ''),
            patient_age=request.form.get('patient_age', ''),
            patient_gender=request.form.get('patient_gender', '')
        )

        return jsonify({
            'success': True,
            'prediction': CLASSES[idx],
            'confidence': round(float(preds[0][idx]) * 100, 2),
            'all_predictions': {
                CLASSES[i]: round(float(preds[0][i]) * 100, 2)
                for i in range(len(CLASSES))
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500


@app.route('/scan-history', methods=['GET'])
@token_required
def scan_history(current_user):
    """Get user's scan history"""
    try:
        user_id = current_user['user_id']
        limit = request.args.get('limit', 10, type=int)
        
        history = auth.get_scan_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error retrieving history: {str(e)}'
        }), 500


# ================= ADMIN ROUTES =================

@app.route('/admin/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({'message': 'Admin endpoint - implement as needed'}), 200


# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ================= START SERVER ===============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 Brain Tumor Detection API with Authentication")
    print("="*60)
    print("✅ Authentication System: Active")
    print("✅ JWT Tokens: Enabled")
    print("✅ Database: SQLite")
    print("🌐 Server: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)

