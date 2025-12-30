"""
Brain Tumor Medical Assistant - Streamlit Frontend
File: streamlit_app.py

Complete fixed version with:
- All duplicate button errors fixed
- Beautiful PDF report generation
- Email OTP authentication
- Clean UI with proper styling
"""

import streamlit as st
import requests
import sys
import os
from PIL import Image
import io
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot_engine import ChatbotEngine
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.pagesizes import A4 # type: ignore
from reportlab.lib.colors import HexColor # type: ignore
from reportlab.lib.units import mm # type: ignore
from reportlab.platypus import Paragraph # type: ignore
from reportlab.lib.styles import getSampleStyleSheet # type: ignore

# API Configuration
API_BASE_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="Brain Tumor Medical Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    .auth-container {
        max-width: 500px;
        margin: 2rem auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .user-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 15%;
        border-left: 4px solid #2196F3;
        color: #1f2d3d;
    }
    .bot-message {
        background-color: #F5F5F5;
        margin-right: 15%;
        border-left: 4px solid #4CAF50;
        color: #1f2d3d;
    }
    .warning-box {
        background-color: #FFF3CD;
        border: 1px solid #FFC107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1f2d3d;
    }
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #28A745;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #000000;
    }

    /* ========== FORM INPUT STYLING ========== */
    .stTextInput input, 
    .stSelectbox select,
    .stNumberInput input,
    .stTextArea textarea {
        color: ##1f2d3d !important;
        background-color: #2c2c2c !important;
        border: 2px solid #444444 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus, 
    .stSelectbox select:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #1E88E5 !important;
        background-color: #1a1a1a !important;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.3) !important;
        outline: none !important;
    }
    
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }
    
    .stTextInput label, 
    .stSelectbox label, 
    .stNumberInput label,
    .stTextArea label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Focus state */
    .stTextInput input:focus, 
    .stSelectbox select:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #1E88E5 !important;
        background-color: #1a1a1a !important;  /* Focus pe thoda aur dark */
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.3) !important;
        outline: none !important;
    }

    /* Placeholder text */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #888888 !important;  /* Placeholder grey */
        opacity: 1 !important;
    }

    /* Labels white rahenge */
    .stTextInput label, 
    .stSelectbox label, 
    .stNumberInput label,
    .stTextArea label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    } 
                   
</style>
""", unsafe_allow_html=True)


# ============ SESSION STATE INITIALIZATION ============

def init_session_state():
    """Initialize all session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_reset' not in st.session_state:
        st.session_state.show_reset = False
    if 'reset_otp_sent' not in st.session_state:
        st.session_state.reset_otp_sent = False
    if 'reset_email' not in st.session_state:
        st.session_state.reset_email = ""
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'otp_verified' not in st.session_state:
        st.session_state.otp_verified = False
    if 'current_email' not in st.session_state:
        st.session_state.current_email = ""

    #  PRIMARY LANDING PAGE
    if 'page' not in st.session_state:
        st.session_state.page = "about"

    # 🔥 ADD THESE
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chatbot_loaded' not in st.session_state:
        st.session_state.chatbot_loaded = False

init_session_state()



# ============ API FUNCTIONS ============

def send_email_otp(email, purpose='register'):
    """Send OTP to email"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/send-email-otp",
            json={'email': email, 'purpose': purpose},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def verify_email_otp(email, otp, purpose='register'):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-email-otp",
            json={
                'email': email.strip().lower(),
                'otp': otp,
                'purpose': purpose
            },
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500



def register_user(name, email, password, role='patient'):
        """Register new user"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register-user",
                json={
                    'name': name,
                    'email': email,
                    'password': password,
                    'role': role
                },
                timeout=10
            )
            
            # ✅ FIX: Properly handle response
            if response.status_code in [200, 201]:
                return response.json(), response.status_code
            else:
                # Handle error responses
                try:
                    error_data = response.json()
                    return error_data, response.status_code
                except:
                    return {'error': 'Registration failed', 'success': False}, response.status_code
                    
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout', 'success': False}, 500
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to server', 'success': False}, 500
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}, 500
        

def login_user(email, password):
    """Login user with email and password"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login-user",
            json={'email': email, 'password': password},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def reset_password(email, new_password):
    """Reset user password"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/reset-password",
            json={'email': email, 'new_password': new_password},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def get_user_profile(token):
    """Get user profile information"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def predict_mri(token, image_file, patient_name='', patient_age='', patient_gender=''):
    """Send MRI image for prediction"""
    try:
        files = {'file': ('image.png', image_file, 'image/png')}
        data = {
            'patient_name': patient_name,
            'patient_age': patient_age,
            'patient_gender': patient_gender
        }
        response = requests.post(
            f"{API_BASE_URL}/predict",
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def get_scan_history(token, limit=10):
    """Get user's scan history"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/scan-history?limit={limit}",
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


# ============ BEAUTIFUL PDF GENERATION ============

def generate_pdf_report(patient_name, patient_age, patient_gender, tumor_type_raw, confidence):
    """
    Generate a beautiful, professional PDF report for brain MRI analysis
    with sky blue color theme and modern design
    """
    
    # Tumor information database
    tumor_details = {
        "glioma_tumor": {
            "display_name": "Glioma Tumor",
            "location": "Brain or spinal cord (originates from glial cells)",
            "severity": "High Risk",
            "severity_color": "#E53935",
            "description": "Glioma is a serious type of brain tumor that arises from glial cells. It can grow aggressively and may be malignant. Common symptoms include persistent headaches, seizures, cognitive changes, and neurological deficits. Early detection and treatment are crucial for better outcomes."
        },
        "meningioma_tumor": {
            "display_name": "Meningioma Tumor",
            "location": "Meninges (protective membranes around brain and spinal cord)",
            "severity": "Moderate Risk",
            "severity_color": "#FB8C00",
            "description": "Meningioma is typically a slow-growing tumor arising from the meninges. Most are benign but can cause symptoms based on size and location. Common effects include headaches, vision problems, hearing loss, and weakness. Regular monitoring and treatment are recommended."
        },
        "pituitary_tumor": {
            "display_name": "Pituitary Tumor",
            "location": "Pituitary gland (base of the brain)",
            "severity": "Low to Moderate Risk",
            "severity_color": "#FDD835",
            "description": "Pituitary tumors are usually benign growths affecting the pituitary gland. They can disrupt hormone production, leading to various symptoms including fatigue, weight changes, vision problems, and reproductive issues. Treatment depends on tumor size, type, and hormone activity."
        },
        "no_tumor": {
            "display_name": "No Tumor Detected",
            "location": "No abnormal growth identified",
            "severity": "Normal",
            "severity_color": "#43A047",
            "description": "The AI analysis did not detect any tumor-like abnormalities in the MRI scan. However, if you are experiencing symptoms or have clinical concerns, please consult with a qualified medical professional for a comprehensive evaluation."
        }
    }
    
    # Get tumor info or use default
    info = tumor_details.get(tumor_type_raw, {
        "display_name": tumor_type_raw.replace("_", " ").title() if tumor_type_raw else "Unknown",
        "location": "Information not available",
        "severity": "Unknown",
        "severity_color": "#757575",
        "description": "Detailed information not available for this classification."
    })
    
    # Create PDF buffer
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Define colors (Sky Blue theme)
    sky_blue = HexColor("#4FC3F7")  # Light sky blue
    dark_blue = HexColor("#01579B")  # Dark blue for headers
    text_black = HexColor("#212121")
    light_gray = HexColor("#F5F5F5")
    white = HexColor("#FFFFFF")
    
    margin = 20 * mm
    current_y = height - margin
    
    # ========== HEADER SECTION ==========
    header_height = 35 * mm
    c.setFillColor(sky_blue)
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    
    # Hospital/System Logo Area (decorative circle)
    c.setFillColor(white)
    c.circle(width / 2, height - 12 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(dark_blue)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 14 * mm, "🧠")
    
    # Main Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 24 * mm, "Brain MRI Analysis Report")
    
    # Subtitle
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 30 * mm, "AI-Assisted Medical Screening System")
    
    current_y = height - header_height - 10 * mm
    
    # ========== REPORT METADATA ==========
    c.setFillColor(text_black)
    c.setFont("Helvetica", 10)
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    c.drawString(margin, current_y, f"Report Generated: {report_date}")
    current_y -= 5 * mm
    
    # Horizontal line
    c.setStrokeColor(sky_blue)
    c.setLineWidth(1.5)
    c.line(margin, current_y, width - margin, current_y)
    current_y -= 12 * mm
    
    # ========== PATIENT INFORMATION BOX ==========
    box_height = 45 * mm
    c.setFillColor(light_gray)
    c.roundRect(margin, current_y - box_height, width - 2 * margin, box_height, 8, fill=1, stroke=0)
    
    # Section header
    c.setFillColor(dark_blue)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin + 8 * mm, current_y - 8 * mm, "📋 Patient Information")
    
    # Patient details
    c.setFillColor(text_black)
    c.setFont("Helvetica", 11)
    current_y -= 18 * mm
    c.drawString(margin + 10 * mm, current_y, f"Name: {patient_name or 'Not Provided'}")
    current_y -= 8 * mm
    c.drawString(margin + 10 * mm, current_y, f"Age: {patient_age or 'Not Provided'} years")
    current_y -= 8 * mm
    c.drawString(margin + 10 * mm, current_y, f"Gender: {patient_gender or 'Not Provided'}")
    
    current_y -= 18 * mm
    
    # ========== AI ANALYSIS RESULTS ==========
    c.setFillColor(dark_blue)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "🔬 AI Analysis Results")
    current_y -= 12 * mm
    
    # Result box
    result_box_height = 35 * mm
    c.setFillColor(light_gray)
    c.roundRect(margin, current_y - result_box_height, width - 2 * margin, result_box_height, 8, fill=1, stroke=0)
    
    c.setFillColor(text_black)
    c.setFont("Helvetica-Bold", 12)
    current_y -= 10 * mm
    c.drawString(margin + 8 * mm, current_y, f"Detected Condition: {info['display_name']}")
    
    c.setFont("Helvetica", 11)
    current_y -= 8 * mm
    c.drawString(margin + 8 * mm, current_y, f"Model Confidence: {confidence:.2f}%")
    
    current_y -= 8 * mm
    c.drawString(margin + 8 * mm, current_y, f"Risk Level: ")
    c.setFillColor(HexColor(info['severity_color']))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 8 * mm + 45, current_y, info['severity'])
    
    current_y -= 15 * mm
    
    # ========== CONDITION DETAILS ==========
    c.setFillColor(dark_blue)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, current_y, "📖 About The Detected Condition")
    current_y -= 10 * mm
    
    # Description box
    desc_box_height = 60 * mm
    c.setFillColor(light_gray)
    c.roundRect(margin, current_y - desc_box_height, width - 2 * margin, desc_box_height, 8, fill=1, stroke=0)
    
    # Typical location
    c.setFillColor(text_black)
    c.setFont("Helvetica-Bold", 10)
    current_y -= 8 * mm
    c.drawString(margin + 8 * mm, current_y, "Typical Location:")
    c.setFont("Helvetica", 10)
    current_y -= 6 * mm
    
    # Wrap location text
    location_text = info['location']
    words = location_text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if c.stringWidth(test_line, "Helvetica", 10) < (width - 2 * margin - 20 * mm):
            line = test_line
        else:
            c.drawString(margin + 10 * mm, current_y, line.strip())
            current_y -= 5 * mm
            line = word + " "
    if line:
        c.drawString(margin + 10 * mm, current_y, line.strip())
    
    current_y -= 8 * mm
    
    # Description
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 8 * mm, current_y, "Medical Description:")
    c.setFont("Helvetica", 10)
    current_y -= 6 * mm
    
    # Wrap description text
    desc_words = info['description'].split()
    line = ""
    for word in desc_words:
        test_line = line + word + " "
        if c.stringWidth(test_line, "Helvetica", 10) < (width - 2 * margin - 20 * mm):
            line = test_line
        else:
            c.drawString(margin + 10 * mm, current_y, line.strip())
            current_y -= 5 * mm
            line = word + " "
    if line:
        c.drawString(margin + 10 * mm, current_y, line.strip())
    
    current_y -= 15 * mm
    
    # ========== GENERATED BY SECTION ==========
    c.setFillColor(dark_blue)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, current_y, "👨‍💻 Report Generated By:")
    current_y -= 8 * mm
    
    c.setFillColor(text_black)
    c.setFont("Helvetica", 10)
    c.drawString(margin + 8 * mm, current_y, "• Suraj Vishwakarma")
    current_y -= 6 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(margin + 8 * mm, current_y, "  Academic Project: AI-Powered Brain Tumor Detection System")
    
    # ========== FOOTER - DISCLAIMER ==========
    footer_height = 32 * mm
    c.setFillColor(sky_blue)
    c.rect(0, 0, width, footer_height, fill=1, stroke=0)
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, footer_height - 8 * mm, "⚠️ IMPORTANT DISCLAIMER")
    
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, footer_height - 14 * mm, 
                        "This report is generated for EDUCATIONAL PURPOSES ONLY.")
    c.drawCentredString(width / 2, footer_height - 19 * mm,
                        "It should NOT be used for actual medical diagnosis, treatment decisions, or clinical practice.")
    c.drawCentredString(width / 2, footer_height - 24 * mm,
                        "Always consult with qualified healthcare professionals for medical advice and diagnosis.")
    
    # Page number and watermark
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 5 * mm, "Page 1 of 1")
    
    # Save PDF
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ============ PAGE: ABOUT BRAIN TUMOR ============
# # ============ ABOUT BRAIN TUMOR PAGE ============
def show_about_page():

    # Custom CSS - Properly Organized
    st.markdown("""
    <style>
        /* ========== GENERAL APP SETTINGS ========== */
        .stApp {
            background-color: #ffffff !important;
        }
        
        .main .block-container {
            background-color: #000000 !important;
            padding: 0 !important;
            max-width: 100% !important;
        }
        
        .main > div {
            padding: 0 !important;
            background-color: #000000 !important;
        }
        
        /* ========== ABOUT PAGE - HERO SECTION ========== */
        .hero-section {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
            color: #ffffff !important;
            padding: 100px 60px;
            text-align: center;
            border-radius: 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin: 0;
            width: 100%;
            animation: slideDown 0.8s ease;
        }
        
        .hero-title {
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            color: #ffffff !important;
            animation: fadeInDown 1s ease;
        }
        
        .hero-subtitle {
            font-size: 1.5rem !important;
            opacity: 0.95;
            margin-bottom: 30px;
            color: #ffffff !important;
            animation: fadeInUp 1s ease;
        }
        
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 30px;
        }
        
        .badge {
            background: rgba(255,255,255,0.2) !important;
            backdrop-filter: blur(10px);
            padding: 15px 35px;
            border-radius: 30px;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            color: #ffffff !important;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
            animation: fadeIn 1.2s ease;
        }
        
        .badge:hover {
            background: rgba(255,255,255,0.35) !important;
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        /* ========== FIX STREAMLIT DEFAULT TEXT COLORS ========== */
       /* Only headings white, not all text */
                
        .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
            color: #000000 !important;
        }
        
        
        .alt-bg {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
        }
        
        .section-title {
            font-size: 2.8rem !important;
            color: #000000 !important;
            margin-bottom: 50px;
            text-align: center;
            font-weight: 700 !important;
            animation: fadeInDown 0.8s ease;
        }
        
        .icon {
            font-size: 3.5rem !important;
            margin-right: 15px;
            vertical-align: middle;
        }
        
        /* ========== ABOUT PAGE - CONTENT CARDS ========== */
        .content-card {
            background: #ffffff !important;
            padding: 20px;
            width: 100%;
            max-width: 100%;
            border-radius: 20px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
                
        .content-card1 {
            background: #ffffff !important;
            padding: 20px;
            width: 100%;
            max-width: 100%;
            border-radius: 20px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        
        .content-card:hover {
            box-shadow: 0 10px 40px rgba(0,0,0,0.12);
            transform: translateY(-5px);
        }
        
        .content-card p,
        .content-card div, 
        .content-card span, 
        .content-card li {
            color: #2c3e50 !important;
            font-weight: bold !important;
        }
        
        .intro-text {
            font-size: 1.25rem !important;
            line-height: 1.9;
            color: #2c3e50 !important;
            margin-bottom: 30px;
            font-weight: 400 !important;
            
        }
        
        .card-subtitle {
            font-size: 1.8rem !important;
            color: #2980b9 !important;
            margin: 30px 0 20px 0;
            font-weight: 600 !important;
            border-left: 6px solid #3498db;
            padding-left: 20px;
            width: 100%;
        }
        
        /* ========== ABOUT PAGE - FEATURE LISTS ========== */
        .feature-list {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 20px;
            width: 100%;          /* 🔥 */
            max-width: 100%;     /* 🔥 */
            margin-top: 20px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            padding: 18px 20px;
            margin: 0;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
            border-radius: 15px;
            border-left: 5px solid #2196f3;
            transition: all 0.3s ease;
            animation: slideInLeft 0.6s ease;
            width: 100%;
            box-sizing: border-box
                
        }

        .feature-item span {
            color: #2c3e50 !important;
            font-size: 1.05rem !important;
        }
        
        .feature-item:hover {
            transform: translateX(-6px);
            background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%) !important;
            box-shadow: 0 5px 20px rgba(33,150,243,0.3);
        }
        
        .check-icon {
            color: #27ae60 !important;
            font-size: 1.8rem !important;
            font-weight: bold !important;
            margin-right: 20px;
            min-width: 35px;
        }
        /* ========== RESPONSIVE ========== */
        @media (max-width: 1200px) {
            .feature-list {
                grid-template-columns: repeat(2, 1fr);  /* tablet */
            }
        }

        @media (max-width: 768px) {
            .feature-list {
                grid-template-columns: 1fr;  /* mobile */
            }
        }
        
        /* ========== ABOUT PAGE - HIGHLIGHT BOXES ========== */
        .highlight-box {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%) !important;
            color: #ffffff !important;
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            font-size: 1.15rem !important;
            line-height: 1.8;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            animation: pulse 3s infinite;
            width: 100%;
            justify-content: center;   /* horizontal */
            align-items: center;       /* vertical */
        }
        .highlight-box1 {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%) !important;
            color: #ffffff !important;
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            font-size: 1.15rem !important;
            line-height: 1.8;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            animation: pulse 3s infinite;
            width: 90%;
            justify-content: center;   /* horizontal */
            align-items: center;       /* vertical */
        }
        
        .highlight-box strong, .highlight-box p, .highlight-box span {
            color: #ffffff !important;
        }
        
        .urgent-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%) !important;
            color: #ffffff !important;
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            line-height: 1.8;
            box-shadow: 0 8px 25px rgba(201,42,42,0.3);
        }
        
        .urgent-box strong, .urgent-box p {
            color: #ffffff !important;
        }
        
        /* ========== ABOUT PAGE - SYMPTOMS GRID ========== */
        .symptoms-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .symptom-card {
            background: #ffffff !important;
            padding: 30px 25px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 2px solid #e0e0e0;
            animation: fadeInUp 0.8s ease;
        }
        
        .symptom-card:hover {
            transform: translateY(-15px) scale(1.05);
            box-shadow: 0 15px 40px rgba(52,152,219,0.3);
            border-color: #3498db;
        }
        
        .symptom-card strong {
            color: #2c3e50 !important;
            font-size: 1.1rem !important;
        }
        
        .symptom-card p {
            color: #555555 !important;
            margin-top: 10px;
        }
        
        .symptom-icon {
            font-size: 3rem !important;
            display: block;
            margin-bottom: 15px;
        }
        
        /* ========== ABOUT PAGE - COMPARISON GRID ========== */
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 30px 0;
        }
        
        .comparison-item {
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            animation: fadeIn 0.8s ease;
        }
        
        .comparison-item.positive {
            background: linear-gradient(135deg, #d4edda 0%, #a8e6b8 100%) !important;
            border-left: 6px solid #28a745;
        }
        
        .comparison-item.positive strong {
            color: #155724 !important;
            font-size: 1.2rem !important;
        }
        
        .comparison-item.positive ul, .comparison-item.positive li {
            color: #2c3e50 !important;
        }
        
        .comparison-item.negative {
            background: linear-gradient(135deg, #f8d7da 0%, #f5b7b1 100%) !important;
            border-left: 6px solid #dc3545;
        }
        
        .comparison-item.negative strong {
            color: #721c24 !important;
            font-size: 1.2rem !important;
        }
        
        .comparison-item.negative ul, .comparison-item.negative li {
            color: #2c3e50 !important;
        }
        
        /* ========== ABOUT PAGE - STATS GRID ========== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: #ffffff !important;
            padding: 40px 25px;
            border-radius: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
            transition: all 0.3s ease;
            animation: bounceIn 0.8s ease;
        }
        
        .stat-box:hover {
            transform: translateY(-15px) scale(1.08);
            box-shadow: 0 20px 50px rgba(102,126,234,0.5);
        }
        
        .stat-number {
            font-size: 4rem !important;
            font-weight: 800 !important;
            margin-bottom: 15px;
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .stat-label {
            font-size: 1.2rem !important;
            opacity: 0.95;
            line-height: 1.6;
            color: #ffffff !important;
        }
        
        /* ========== ABOUT PAGE - VIDEO & IMAGE CONTAINERS (REDUCED SIZE) ========== */
        .video-container {
            position: relative;
            width: 100%;
            max-width: 600px;  /* ✅ VIDEO SIZE REDUCED */
            margin: 25px auto;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            animation: zoomIn 0.8s ease;
        }
        
        .video-container video {
            width: 100%;
            height: auto;
            display: block;
            border-radius: 20px;
        }
        
        .image-container {
            max-width: 250px;  /* ✅ IMAGE SIZE REDUCED */
            margin: 20px auto;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            animation: zoomIn 1s ease;
            width: 70%;
        }
        
        .image-container img {
            display: block;
            border-radius: 10px;
            object-fit: contain;
            max-width: 200px !important;
            width: 70%;
            height: auto;
        }
        
        /* ========== ABOUT PAGE - AWARENESS CARDS ========== */
        .awareness-card {
            background: #ffffff !important;
            padding: 30px;
            border-radius: 20px;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            border-left: 8px solid #e74c3c;
            transition: all 0.3s ease;
            animation: slideInRight 0.6s ease;
        }
        
        .awareness-card:hover {
            transform: translateX(15px);
            box-shadow: 0 12px 35px rgba(231,76,60,0.3);
            border-left-width: 12px;
        }
        
        .awareness-card strong {
            color: #e74c3c !important;
            font-size: 1.25rem !important;
        }
        
        .awareness-card p {
            color: #2c3e50 !important;
            margin-top: 10px;
            line-height: 1.7;
        }
        
        /* ========== ABOUT PAGE - FOOTER ========== */
        .footer-section {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
            color: #ffffff !important;
            padding: 80px 60px;
            text-align: center;
            margin: 0;
            width: 100%;
        }
        
        .footer-text {
            font-size: 2rem !important;
            font-weight: 600 !important;
            margin-bottom: 20px;
            color: #ffffff !important;
        }
        
        .footer-subtext {
            font-size: 1.3rem !important;
            opacity: 0.95;
            color: #ffffff !important;
        }
        
        .footer-section p {
            color: #ffffff !important;
        }
        
        /* ========== ANIMATIONS ========== */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes zoomIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes bounceIn {
            0% { opacity: 0; transform: scale(0.3); }
            50% { transform: scale(1.05); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.03); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        /* ========== RESPONSIVE DESIGN ========== */
        @media (max-width: 768px) {
            .hero-title { font-size: 2.5rem !important; }
            .section-title { font-size: 2rem !important; }
            .comparison-grid { grid-template-columns: 1fr; }
            .hero-section { padding: 60px 30px; }
            .section-container { padding: 40px 20px; }
            
            /* Mobile pe images aur video size */
            .video-container { max-width: 100%; }
            .image-container { max-width: 100%; }
            [data-testid="stImage"] { max-width: 100% !important; }
        }
                 
    </style>
    """, unsafe_allow_html=True)
    
    """Display the complete About Brain Tumor website"""
    
    st.markdown("<div>", unsafe_allow_html=True)
    
        # ---------- HERO SECTION ----------
    st.markdown("""
        <div class='hero-section'>
            <h1 class='hero-title'>🧠 Brain Health & Tumor Awareness</h1>
            <p class='hero-subtitle'>Empowering Lives Through Knowledge, Care & Advanced Technology</p>
            <div class='hero-badges'>
                <span class='badge'>Early Detection</span>
                <span class='badge'>Expert Care</span>
                <span class='badge'>Hope & Recovery</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------- SECTION 1: UNDERSTANDING YOUR BRAIN & MRI ----------
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🧠</span> Understanding Your Brain & MRI Technology</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
            <div class='content-card'>
                    <h3 class='card-subtitle'>Why MRI Matters ?</h3>
            </div>
                    
            <div class='content-card'>   
                <p class='intro-text'>
                    The human brain is your body's command center—a three-pound marvel that orchestrates 
                    every thought, emotion, and movement. Housing approximately 86 billion neurons, it processes 
                    information at incredible speeds, creating the essence of who you are.
                    Magnetic Resonance Imaging (MRI) is a revolutionary non-invasive technology that uses 
                    powerful magnets and radio waves to create detailed images of your brain's structure. 
                    Unlike X-rays, MRI doesn't use radiation, making it safer for repeated scans.
                </p>
            </div>
                
            <div class='feature-list'>
                <div class='feature-item'>
                    <span class='check-icon'>✓</span>
                    <span>Detects tumors as small as a few millimeters</span>
                </div>
                <div class='feature-item'>
                    <span class='check-icon'>✓</span>
                    <span>Identifies precise tumor location and boundaries</span>
                </div>
                <div class='feature-item'>
                    <span class='check-icon'>✓</span>
                    <span>Monitors treatment progress effectively</span>
                </div>
                <div class='feature-item'>
                    <span class='check-icon'>✓</span>
                    <span>Guides surgical planning with accuracy</span>
                </div>
            </div>
            
            <div class='highlight-box'>
                <strong>Critical Insight:</strong> Early detection through MRI can improve survival rates 
                by up to 90% for certain brain tumor types. Regular screening is vital for high-risk individuals.
            </div>

        """, unsafe_allow_html=True)

    with col2:
        try:
            st.image(
                "about/assets/images/img3.jpg",
                width=800
            )
        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 60px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.2rem;'>📷 Image: Brain MRI Scan</p>
                    <p style='color: #999; margin-top: 10px;'>Add image: about/assets/images/img3.jpg</p>
                </div>
            """, unsafe_allow_html=True)

    # ---------- SECTION 2: NEUROPLASTICITY ----------
    st.markdown("<div class='section-container alt-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🎯</span> Neuroplasticity: Your Brain's Superpower</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 5])

    with col1:
        try:
            st.image("about/assets/images/img5.jpg", width=800)
        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 60px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.2rem;'>🧠 Image: Neural Networks</p>
                    <p style='color: #999; margin-top: 10px;'>Add image: about/assets/images/img5.jpg</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='content-card'>
                    <h3 class='card-subtitle'>The Power of Positive Programming</h3>
            </div>
            <div class='content-card'>
                <p class='intro-text'>
                    Your brain possesses an extraordinary ability called neuroplasticity—the capacity to 
                    reorganize itself by forming new neural connections throughout life. Every experience, 
                    thought, and habit literally reshapes your brain's structure.
                </p>
                <div>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    Research shows that consistent positive thinking and healthy habits strengthen beneficial 
                    neural pathways, while negative patterns can create stress-inducing circuits. The brain 
                    doesn't distinguish between real and imagined experiences—what you focus on grows stronger.
                </p>
                </div>
            
            </div>
                
            <div class='comparison-grid'>
                <div class='comparison-item positive'>
                    <strong>Positive Inputs →</strong>
                    <ul style='margin-top: 15px; line-height: 1.8;'>
                        <li>Enhanced memory retention</li>
                        <li>Improved problem-solving</li>
                        <li>Reduced anxiety levels</li>
                        <li>Better emotional regulation</li>
                    </ul>
                </div>
                <div class='comparison-item negative'>
                    <strong>Negative Patterns →</strong>
                    <ul style='margin-top: 15px; line-height: 1.8;'>
                        <li>Chronic stress responses</li>
                        <li>Impaired decision-making</li>
                        <li>Weakened immune function</li>
                        <li>Cognitive decline risk</li>
                    </ul>
                </div>
            </div>
                
            <div class='highlight-box'>
                <strong>AI Parallel:</strong> Just as machine learning models improve with quality data, 
                your brain optimizes based on the quality of information and experiences you provide it. 
                Discipline and positive reinforcement are your training algorithms.
            </div>
        """, unsafe_allow_html=True)

    # ---------- SECTION 3: BRAIN TUMORS ----------
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🎥</span> Understanding Brain Tumors</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.2, 0.5])

    with col1:
        try:
            st.markdown(""" 
            <div style="margin-top: 15px;"> 
            """,unsafe_allow_html=True)

            st.video(
                "about/assets/video/patient1.mp4",
                autoplay=True,
                loop=True,
                muted=True
            )
            st.markdown("""
            </div>
                        

            <div class = 'content-card1'>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    <h3 class='card-subtitle'>Warning Signs to Watch </h3>
                </p>
            </div>  
                        
            """,unsafe_allow_html=True)
            

            st.markdown(""" 
            <div style="margin-top: 10px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img7.jpg",
                width=300
            )
            st.markdown("""
            </div>   
                """,unsafe_allow_html=True)

        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.5rem;'>🎥 Video: Brain Tumor Overview</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/patient1.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='content-card'>
                <h3 class='card-subtitle'>What Are Brain Tumors?</h3>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    A brain tumor is an abnormal growth of cells within the brain or skull. They can be 
                    benign (non-cancerous) or malignant (cancerous), and both types require medical attention 
                    as they can impact brain function due to pressure and location.
                </p>
            </div>
                    
            <div class='symptoms-grid'>
                <div class='symptom-card'>
                    <span class='symptom-icon'>🤕</span>
                    <strong>Persistent Headaches</strong>
                    <p>Especially severe in morning</p>
                </div>
                <div class='symptom-card'>
                    <span class='symptom-icon'>🧩</span>
                    <strong>Memory Issues</strong>
                    <p>Difficulty concentrating</p>
                </div>
                <div class='symptom-card'>
                    <span class='symptom-icon'>👁️</span>
                    <strong>Vision Problems</strong>
                    <p>Blurred or double vision</p>
                </div>
                <div class='symptom-card'>
                    <span class='symptom-icon'>⚡</span>
                    <strong>Seizures</strong>
                    <p>New onset in adults</p>
                </div>
            </div>
                
            <div class='urgent-box'>
                <strong>⚠️ Seek Immediate Medical Attention If:</strong>
                <p style='margin-top: 10px;'>You experience sudden severe headaches, loss of consciousness, 
                difficulty speaking, or weakness on one side of the body.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 4: BRAIN-HEART CONNECTION ----------
    st.markdown("<div class='section-container alt-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>❤️</span> The Brain-Heart Connection</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.5, 0.2])

    with col1:
        st.markdown("""
            <div class="blue-text">
                    <h3 class='card-subtitle'>The Science of Emotional Health</h3>
            </div>
            <div class='content-card'>
                <p class='intro-text'>
                    Your brain and heart communicate constantly through a sophisticated network of nerves, 
                    hormones, and biochemical signals. This bidirectional relationship means that what affects 
                    one inevitably influences the other.
                </p>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    Chronic stress triggers the release of cortisol and adrenaline, which can increase heart 
                    rate, blood pressure, and inflammation—all risk factors for cardiovascular disease. 
                    Conversely, practices like meditation and mindfulness can activate the parasympathetic 
                    nervous system, promoting healing and recovery.
                </p>
            </div>
                
            <div style='background: #e8f5e9; padding: 25px; border-radius: 15px; margin: 25px 0; border-left: 5px solid #4caf50;'>
                    <h4 style='color: #2e7d32; margin-bottom: 15px;'>Daily Practices for Brain-Heart Health:</h4>
                    <ul style='color: #2c3e50; line-height: 2;'>
                        <li>10 minutes of meditation or deep breathing</li>
                        <li>Regular physical activity (30 mins, 5x/week)</li>
                        <li>7-9 hours of quality sleep</li>
                        <li>Gratitude journaling</li>
                        <li>Social connection and meaningful relationships</li>
                    </ul>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        try:

            st.video("about/assets/video/brain+heart.mp4", autoplay=True, loop=True, muted=True)

            st.markdown(""" 
            <div style="margin-top: 40px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img8.jpg",
                width=400
            )
            st.markdown("""
                        
            </div>   
                """,unsafe_allow_html=True)

        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>❤️ Video: Brain-Heart Connection</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets//brain+heart.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 5: DOCTOR-PATIENT PARTNERSHIP ----------
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>👨‍⚕️</span> The Power of Partnership in Healthcare</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.2, 0.5])

    with col1:
        try:
            st.video("about/assets/video/doctor.mp4", autoplay=True, loop=True, muted=True)

            st.markdown(""" 
            <div style="margin-top: 25px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img9.jpg",
                width=350
            )
            st.markdown("""
                        
            </div>   
                        
            <div class='highlight-box'>
                <strong>Remember:</strong> You are an active participant in your healthcare journey. 
                Advocate for yourself and seek second opinions when needed.
            </div>
                        
                """,unsafe_allow_html=True)

        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>👨‍⚕️ Video: Doctor-Patient Partnership</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/doctor.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
                    
            <div class="blue-text">
                <h3 class='card-subtitle'>Building Effective Communication</h3>
            </div>
                    
            <div class='content-card'>
                <p class='intro-text'>
                    A strong doctor-patient relationship is the foundation of effective healthcare. Studies 
                    show that patients who trust their healthcare providers experience better outcomes, 
                    improved adherence to treatment, and faster recovery times.
                </p>
            </div>
            <div style='background: #fff3cd; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #ffc107;'>
                <strong style='color: #856404;'>Be Prepared:</strong>
                <p style='color: #856404; margin-top: 8px;'>Write down symptoms, questions, and concerns before appointments</p>
            </div>
            <div style='background: #d1ecf1; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #17a2b8;'>
                <strong style='color: #0c5460;'>Be Honest:</strong>
                <p style='color: #2c3e50; margin-top: 8px;'>Share complete information about your health history and lifestyle</p>
            </div>
            <div style='background: #d4edda; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #28a745;'>
                <strong style='color: #155724;'>Ask Questions:</strong>
                <p style='color: #2c3e50; margin-top: 8px;'>No question is too small when it comes to your health</p>
            </div>
            
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 6: DIAGNOSTIC TECHNOLOGY ----------
    st.markdown("<div class='section-container alt-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🧪</span> Cutting-Edge Diagnostic Technology</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.5, 0.2])

    with col1:
        st.markdown("""
            <div class='content-card'>
                <h3 class='card-subtitle'>Modern Imaging Technologies</h3>
            </div>
                
            <div style='background: #e3f2fd; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    <strong style='color: #1565c0; font-size: 1.2rem;'>MRI (Magnetic Resonance Imaging)</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        Uses magnetic fields to create detailed soft tissue images. Ideal for brain tumors, 
                        offering superior contrast and no radiation exposure.
                    </p>
            </div>
            
                
            <div style='background: #f3e5f5; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    <strong style='color: #6a1b9a; font-size: 1.2rem;'>CT Scan (Computed Tomography)</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        X-ray technology that creates cross-sectional images. Faster than MRI, excellent 
                        for emergency situations and bone imaging.
                    </p>
            </div>
                
            <div style='background: #fce4ec; padding: 20px; border-radius: 12px; margin: 20px 0;'>
                    <strong style='color: #c2185b; font-size: 1.2rem;'>PET Scan (Positron Emission Tomography)</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        Shows metabolic activity of tissues. Helps distinguish between tumor types and 
                        assess treatment effectiveness.
                    </p>
            </div>
            
        """, unsafe_allow_html=True)

    with col2:
        try:
            st.video("about/assets/video/scan.mp4", autoplay=True, loop=True, muted=True)

            st.markdown(""" 
            <div style="margin-top: 50px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img11.jpg",
                width=400
            )
            st.markdown("""
                        
            </div> 
            """, unsafe_allow_html=True)



        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>🧪 Video: MRI Scanning Process</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/scan.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 7: TUMOR GROWTH & DEVELOPMENT ----------
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🔬</span> How Brain Tumors Develop & Grow</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.5, 0.2])

    with col1:
        st.markdown("""
            <div class='content-card'>
                <h3 class='card-subtitle'>Understanding Tumor Development</h3>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    Brain tumors develop when cells in the brain begin to grow abnormally. This can happen 
                    due to genetic mutations, environmental factors, or radiation exposure. Understanding 
                    the growth patterns helps doctors plan effective treatment strategies.
                </p>
            </div>
                
            <div style="color: blue;">
                <h3 class='card-subtitle'>Types of Brain Tumors</h3>
            </div>

                
            <div style='background: #fff3e0; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 5px solid #ff9800;'>
                    <strong style='color: #e65100; font-size: 1.15rem;'>Primary Tumors</strong>
                    <p style='color: #000000; margin-top: 8px; line-height: 1.7;'>
                        Originate in the brain itself. Examples include gliomas, meningiomas, and pituitary adenomas.
                    </p>
            </div>
                
            <div style='background: #fce4ec; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 5px solid #e91e63;'>
                    <strong style='color: #880e4f; font-size: 1.15rem;'>Secondary (Metastatic) Tumors</strong>
                    <p style='color: #2c3e50; margin-top: 8px; line-height: 1.7;'>
                        Spread from other parts of the body (lungs, breast, kidney, etc.) to the brain.
                    </p>
            </div>
                
            <div style="color:#6A1B9A;">
                <h3 class='card-subtitle'>Growth Rate Factors</h3>
            </div>        
                
            <div class='feature-list'>
                    <div class='feature-item'>
                        <span class='check-icon'>•</span>
                        <span><strong>Tumor Grade:</strong> Low-grade tumors grow slowly; high-grade tumors grow rapidly</span>
                    </div>
                    <div class='feature-item'>
                        <span class='check-icon'>•</span>
                        <span><strong>Location:</strong> Affects surgical accessibility and treatment options</span>
                    </div>
                    <div class='feature-item'>
                        <span class='check-icon'>•</span>
                        <span><strong>Blood Supply:</strong> Tumors with rich blood supply tend to grow faster</span>
                    </div>
                    <div class='feature-item'>
                        <span class='check-icon'>•</span>
                        <span><strong>Patient Age:</strong> Younger patients often have better recovery outcomes</span>
                    </div>
            </div>
            
        """, unsafe_allow_html=True)

    with col2:
        try:
            st.video("about/assets/video/Cancer.mp4", autoplay=True, loop=True, muted=True)


            st.markdown(""" 
            <div style="margin-top: 70px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img11.jpg",
                width=400
            )
            st.markdown("""
                        
            </div> 
                        
            <div class='highlight-box'>
                    <strong>Treatment Evolution:</strong> Modern treatments like targeted therapy, immunotherapy, 
                    and proton beam radiation are revolutionizing brain tumor care with fewer side effects.
            </div>
                        
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>🔬 Video: Tumor Growth</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/Cancer.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 8: DIGITAL WELLNESS ----------
    st.markdown("<div class='section-container alt-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>📱</span> Digital Wellness & Brain Health in Modern Age</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.2, 0.5])

    with col1:
        try:

            st.video("about/assets/video/person+phone.mp4", autoplay=True, loop=True, muted=True)

            st.markdown(""" 
            <div style="margin-top: 2px;"> 
            """,unsafe_allow_html=True)

            st.image(
                "about/assets/images/img13.jpg",
                width=350
            )
            st.markdown("""
                        
            </div> 
            
            <div style="margin-top: 2px;" , class='highlight-box1'>
                    <strong>Balance is Key:</strong> Technology is a tool, not a lifestyle. Use it intentionally 
                    to enhance your life, not replace real-world connections and experiences.
                    <span class='check-icon'>✓</span>
                    <span><strong>Mindful Usage:   </strong> Set app limits and track screen time</span>
            </div>
                        
                        
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>📱 Video: Phone Usage Impact</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/person+phone.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
                    
            <div class='content-card'>
                    <h3 class='card-subtitle'>The Impact of Screen Time on Brain Health</h3>
            </div>

            <div class='content-card'>
                <p style='color: #2c3e50; font-size: 1.1rem; line-height: 1.8;'>
                    While technology enhances our lives, excessive screen time can affect brain health. 
                    Studies show prolonged exposure to blue light and constant digital stimulation can 
                    impact sleep quality, attention span, and mental well-being.
                </p>
            </div>
                    
            <div style='background: #ffebee; padding: 25px; border-radius: 15px; margin: 10px 0; border-left: 5px solid #f44336;'>
                    <h4 style='color: #c62828; margin-bottom: 12px;'>⚠️ Potential Risks of Excessive Use:</h4>
                    <ul style='color: #2c3e50; line-height: 1.9;'>
                        <li><strong>Digital Eye Strain:</strong> Headaches, blurred vision, dry eyes</li>
                        <li><strong>Sleep Disruption:</strong> Blue light suppresses melatonin production</li>
                        <li><strong>Attention Fragmentation:</strong> Reduced ability to focus deeply</li>
                        <li><strong>Mental Fatigue:</strong> Constant notifications increase stress</li>
                        <li><strong>Posture Problems:</strong> "Text neck" and spine issues</li>
                    </ul>
            </div>
                    
            <div class='content-card'>
                <h3 class='card-subtitle'>Healthy Digital Habits</h3>
            </div>

            <div style="margin-top: 8px;", class='feature-list'>
                <div class='feature-item'>
                        <span class='check-icon'>✓</span>
                        <span><strong>20-20-20 Rule:</strong> Every 20 minutes, look 20 feet away for 20 seconds</span>
                </div>
                <div class='feature-item'>
                        <span class='check-icon'>✓</span>
                        <span><strong>Screen-Free Hours:</strong> No devices 1 hour before sleep</span>
                </div>
                <div class='feature-item'>
                        <span class='check-icon'>✓</span>
                        <span><strong>Blue Light Filters:</strong> Use night mode or blue-light blocking glasses</span>
                </div>
                <div class='feature-item'>
                        <span class='check-icon'>✓</span>
                        <span><strong>Digital Detox:</strong> Take regular breaks from social media</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- SECTION 9: CANCER AWARENESS DAYS ----------
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>🎗️</span> Global Brain Tumor & Cancer Awareness</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.15, 0.5])

    with col1:
        try:
            st.video("about/assets/video/CancerDay.mp4", autoplay=True, loop=True, muted=True)

            st.markdown("""
                        
            </div> 
            
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin-top: 25px; text-align: center;'>
                    <strong style='font-size: 1.3rem;'>Join the Movement</strong>
                    <p style='margin-top: 12px; opacity: 0.95; line-height: 1.7;'>
                        Participate in awareness campaigns, wear colored ribbons, share information, 
                        and support research to make a difference.
                    </p>
            </div>
                                
            """, unsafe_allow_html=True)

        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 20px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>🎗️ Video: Cancer Awareness Days</p>
                    <p style='color: #999; margin-top: 10px;'>Add video: about/assets/video/CancerDay.mp4</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='content-card'>
                <h3 class='card-subtitle'>Important Awareness Days</h3>
                <p style='color: #2c3e50; font-size: 1.05rem; line-height: 1.7; margin-bottom: 20px;'>
                    These global observances raise awareness, support patients, and fund critical research 
                    for brain tumor and cancer prevention, detection, and treatment.
                </p>
            </div>
                
            <div class='awareness-card'>
                    <strong style='color: #e74c3c; font-size: 1.25rem;'>🧠 May 8 - World Brain Tumor Day</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        Dedicated to raising awareness about brain tumors and honoring patients, survivors, 
                        and caregivers worldwide.
                    </p>
            </div>
                
            <div class='awareness-card'>
                    <strong style='color: #e74c3c; font-size: 1.25rem;'>🎗️ February 4 - World Cancer Day</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        A global initiative to unite the world's population in the fight against cancer and 
                        reduce the global cancer burden.
                    </p>
            </div>
                
            <div class='awareness-card'>
                    <strong style='color: #e74c3c; font-size: 1.25rem;'>🧒 September (Childhood Cancer Awareness Month)</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        Focuses on pediatric cancers, including brain tumors, which are the leading cause of 
                        cancer deaths in children.
                    </p>
            </div>
                
            <div class='awareness-card'>
                    <strong style='color: #e74c3c; font-size: 1.25rem;'>💜 November (Lung Cancer Awareness Month)</strong>
                    <p style='color: #2c3e50; margin-top: 10px; line-height: 1.7;'>
                        Lung cancer is a common source of brain metastases, making this awareness month 
                        relevant for brain health.
                    </p>
            </div>
            
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------- FINAL SECTION: HOPE & STATISTICS ----------
    st.markdown("<div class='section-container alt-bg'>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-title'><span class='icon'>💪</span> Hope, Progress & the Road Ahead</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([0.5, 0.25])

    with col1:
        st.markdown("""
            <div class='content-card'>
                <h3 class='card-subtitle'>A Message of Hope</h3>
                <p style='color: #2c3e50; font-size: 1.2rem; line-height: 1.9; font-weight: 500;'>
                    Every day, researchers make breakthroughs in understanding and treating brain tumors. 
                    Survival rates are improving, treatments are becoming more targeted and less invasive, 
                    and quality of life during and after treatment continues to advance.
                </p>
            </div>
            <div style='background: linear-gradient(135deg, #52c234 0%, #0a8f08 100%); color: white; padding: 30px; border-radius: 20px; margin: 25px 0; text-align: center;'>
                    <h3 style='font-size: 2rem; margin-bottom: 15px;'>✨ You Are Not Alone ✨</h3>
                    <p style='font-size: 1.15rem; line-height: 1.8; opacity: 0.95;'>
                        Millions of survivors worldwide are living proof that brain tumors can be beaten. 
                        With early detection, expert care, and unwavering support, hope is always present.
                    </p>
                </div> 
                <h3 class='card-subtitle'>Progress in Numbers</h3>
                <div style='background: #e8f5e9; padding: 25px; border-radius: 15px; margin: 20px 0;'>
                    <ul style='color: #2c3e50; line-height: 2; font-size: 1.05rem;'>
                        <li><strong>5-Year Survival Rate:</strong> Improved by <span style='color: #2e7d32; font-weight: 700;'>35%</span> in the last 20 years</li>
                        <li><strong>Research Funding:</strong> Increased by <span style='color: #2e7d32; font-weight: 700;'>$500M+</span> annually</li>
                        <li><strong>Clinical Trials:</strong> Over <span style='color: #2e7d32; font-weight: 700;'>2,000</span> active trials worldwide</li>
                        <li><strong>Early Detection:</strong> Saves <span style='color: #2e7d32; font-weight: 700;'>thousands</span> of lives each year</li>
                    </ul>
            </div>
            <div style='background: #fff3cd; padding: 25px; border-radius: 15px; margin: 25px 0; border-left: 5px solid #ffc107;'>
                <strong style='color: #856404; font-size: 1.2rem;'>💡 Take Action Today:</strong>
                <ul style='color: #2c3e50; margin-top: 15px; line-height: 2;'>
                    <li>Schedule regular health check-ups</li>
                        <li>Know your family medical history</li>
                        <li>Maintain a brain-healthy lifestyle</li>
                        <li>Support research and awareness initiatives</li>
                        <li>Spread knowledge within your community</li>
                </ul>
            </div>
                
                
        """, unsafe_allow_html=True)

    with col2:
        try:
            st.image("about/assets/images/img6.jpg", width=300)

            st.markdown("""
            <div class='stats-grid' style='margin-top: 5px;'>
                <div style='margin-top: 5px;', class='stat-box'>
                    <div class='stat-number'>700K+</div>
                    <div class='stat-label'>People living with brain tumors in US</div>
                </div>
                <div style='margin-top: 5px;',  class='stat-box'>
                    <div class='stat-number'>90%</div>
                    <div class='stat-label'>Survival rate with early detection</div>
                </div>
                <div style='margin-top: 5px;', class='stat-box'>
                    <div class='stat-number'>150+</div>
                    <div class='stat-label'>Types of brain tumors identified</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='background: #e0e0e0; padding: 80px 40px; border-radius: 15px; text-align: center;'>
                    <p style='color: #666; font-size: 1.3rem;'>💪 Image: Hope & Progress</p>
                    <p style='color: #999; margin-top: 5px;'>Add image: about/assets/images/img6.jpg</p>
                </div>
            """, unsafe_allow_html=True)

    # ---------- FOOTER SECTION ----------
    st.markdown("""
                
        <div style="margin-top: 50px;", class='footer-section'>
            <h2 class='footer-text'>🧠 Knowledge Empowers. Early Detection Saves Lives. 🧠</h2>
            <p class='footer-subtext'>Together, we can make a difference in the fight against brain tumors.</p>
            <p style='margin-top: 40px; font-size: 1rem; opacity: 1;'>
                © 2024 Brain Tumor Medical Assistant | For Educational & Awareness Purposes
            </p>
        </div>
        
        <div>
                <p>
                </P>
                <p>
                </P>
        </div>
                
    """, unsafe_allow_html=True)


        # Back button
    if st.button("⬅️ Back to Login", key="back_btn"):
            st.session_state.page = "login"
            st.rerun()


def show_login_page():
    """Display login and registration page"""


# ABOUT BUTTON - TOP LEFT
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("📖 About Brain Tumor", key="about_btn", type="primary"):
            st.session_state.page = "about"
            st.rerun()



    st.markdown('<h1 class="main-header">🧠 Brain Tumor Medical Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Login Required</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])
        
        # ========== LOGIN TAB ==========
        with tab_login:
            st.subheader("Login to Your Account")
            
            login_email = st.text_input("📧 Email", key="login_email_input", placeholder="Enter registered email")
            login_password = st.text_input("🔒 Password", type="password", key="login_password_input")
            
            if st.button("🚀 Login", use_container_width=True, type="primary", key="login_submit_btn"):
                if not login_email or not login_password:
                    st.error("❌ Please enter email and password")
                else:
                    with st.spinner("🔄 Authenticating..."):
                        result, status = login_user(login_email, login_password)
                        
                        if status == 200 and result.get("success"):
                            st.session_state.authenticated = True
                            st.session_state.user = result.get("user", login_email)
                            st.session_state.token = result["token"]
                            # 🔥 ADD THESE LINES
                            st.session_state.page = "main"
                            st.session_state.chatbot_loaded = False   # optional but safe

                            st.success("✅ Login successful!")

                            st.write("PAGE:", st.session_state.page)
                            st.write("AUTH:", st.session_state.authenticated)
                            st.write("USER:", st.session_state.user)

                            st.rerun()
                        else:
                            st.error(result.get("message", "Login failed"))
            
            st.markdown("---")
            
            # Forgot Password button with unique key
            if st.button("🔑 Forgot Password?", key="show_reset_password_btn"):
                st.session_state.show_reset = True
                st.rerun()
            
            # Reset Password Section
            if st.session_state.show_reset:
                st.markdown("### 🔑 Reset Password")
                
                reset_email_input = st.text_input("📧 Registered Email", key="reset_email_field", 
                                                  value=st.session_state.reset_email)
                
                if not st.session_state.reset_otp_sent:
                    if st.button("📤 Send Reset OTP", use_container_width=True, key="send_reset_otp_btn"):
                        if not reset_email_input:
                            st.error("❌ Please enter email")
                        else:
                            res, _ = send_email_otp(reset_email_input, purpose="reset")
                            if res.get("success"):
                                st.session_state.reset_email = reset_email_input
                                st.session_state.reset_otp_sent = True
                                st.success("✅ OTP sent to email")
                                st.rerun()
                            else:
                                st.error(res.get("message", "Failed to send OTP"))
                
                else:
                    reset_otp_input = st.text_input("🔢 Enter OTP", max_chars=6, key="reset_otp_field")
                    new_pass = st.text_input("🔒 New Password", type="password", key="new_password_field")
                    confirm_pass = st.text_input("🔒 Confirm Password", type="password", key="confirm_password_field")
                    
                    if st.button("🔁 Reset Password", use_container_width=True, key="reset_password_submit_btn"):
                        if new_pass != confirm_pass:
                            st.error("❌ Passwords do not match")
                        elif len(new_pass) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            verify_res, _ = verify_email_otp(st.session_state.reset_email, reset_otp_input, "reset")
                            
                            if verify_res.get("success"):
                                reset_res, _ = reset_password(st.session_state.reset_email, new_pass)
                                if reset_res.get("success"):
                                    st.success("✅ Password reset successful! Please login.")
                                    st.session_state.show_reset = False
                                    st.session_state.reset_otp_sent = False
                                    st.session_state.reset_email = ""
                                    st.rerun()
                                else:
                                    st.error(reset_res.get("message", "Reset failed"))
                            else:
                                st.error(verify_res.get("message", "Invalid OTP"))
        
        # ========== REGISTER TAB ==========
        with tab_register:
            st.subheader("Create New Account")
            
            reg_name = st.text_input("👤 Full Name", key="register_name_input")
            reg_email = st.text_input("📧 Email", key="register_email_input")
            reg_password = st.text_input("🔒 Password", type="password", key="register_password_input")
            reg_confirm = st.text_input("🔒 Confirm Password", type="password", key="register_confirm_input")
            reg_role = st.selectbox("👔 Role", ["patient", "doctor", "admin"], key="register_role_select")
            
            st.divider()
            st.markdown("**📧 Email Verification**")
            
            if not st.session_state.otp_sent:
                if st.button("📤 Send OTP", use_container_width=True, key="register_send_otp_btn"):
                    if not reg_email:
                        st.error("❌ Please enter email")
                    else:
                        res, _ = send_email_otp(reg_email, purpose="register")
                        if res.get("success"):
                            st.session_state.current_email = reg_email
                            st.session_state.otp_sent = True
                            st.success("✅ OTP sent to email")
                            st.rerun()
                        else:
                            st.error(res.get("message", "Failed to send OTP"))
            
            else:
                otp_input = st.text_input("🔢 Enter OTP", max_chars=6, key="register_otp_input")
                
                if st.button("✔️ Verify OTP", use_container_width=True, key="register_verify_otp_btn"):
                    verify_res, _ = verify_email_otp(st.session_state.current_email, otp_input, "register")
                    if verify_res.get("success"):
                        st.session_state.otp_verified = True
                        st.success("✅ Email verified successfully")
                        st.rerun()
                    else:
                        st.error(verify_res.get("message", "Invalid OTP"))
            
            st.divider()
            
            if st.button("📝 Create Account", use_container_width=True, type="primary", key="register_submit_btn"):
                if not all([reg_name, reg_email, reg_password, reg_confirm]):
                    st.error("❌ Please fill all required fields")
                elif reg_password != reg_confirm:
                    st.error("❌ Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif not st.session_state.otp_verified:
                    st.error("❌ Please verify email first")
                else:
                    res, status = register_user(reg_name, reg_email, reg_password, reg_role)
                    
                    if status == 201 and res.get("success"):
                        st.success("✅ Registration successful! Please login.")
                        st.session_state.otp_sent = False
                        st.session_state.otp_verified = False
                        st.session_state.current_email = ""
                        st.rerun()
                    else:
                        st.error(res.get("message", "Registration failed"))
        
    st.markdown('</div>', unsafe_allow_html=True)
        

def show_main_app():
    """Display main application after login"""
    
    # Safety check - if user is None, redirect to login
    if not st.session_state.user:
        st.session_state.authenticated = False
        st.rerun()
        return
    
    # Load chatbot
    @st.cache_resource
    def load_chatbot():
        return ChatbotEngine(similarity_threshold=0.4)
    
    # ✅ ENSURE CHATBOT IS LOADED
    if not st.session_state.chatbot_loaded or st.session_state.chatbot is None:
        with st.spinner("🔄 Loading AI models..."):
            st.session_state.chatbot = load_chatbot()
            st.session_state.chatbot_loaded = True
    
    chatbot = st.session_state.chatbot
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Brain Tumor Medical Assistant</h1>', unsafe_allow_html=True)
    
    # User info display with safety checks
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        user_name = st.session_state.user.get("name", "User") if st.session_state.user else "User"
        st.markdown(f'<div class="user-badge">👤 Welcome, {user_name}</div>', unsafe_allow_html=True)
    with col2:
        user_email = st.session_state.user.get("email", "email@example.com") if st.session_state.user else "email@example.com"
        st.markdown(f'<div class="user-badge">📧 {user_email}</div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", use_container_width=True, key="main_logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Sidebar with safety checks
    with st.sidebar:
        st.header("👤 User Profile")
        st.write(f"**Name:** {st.session_state.user.get('name', 'N/A')}")
        st.write(f"**Role:** {st.session_state.user.get('role', 'patient').title()}")
        st.write(f"**Email:** {st.session_state.user.get('email', 'N/A')}")
        
        st.divider()
        
        st.header("📊 Quick Stats")
        if st.session_state.token:
            history_result, _ = get_scan_history(st.session_state.token, limit=100)
            if history_result and history_result.get('success'):
                st.metric("Total Scans", history_result.get('count', 0))
        
        st.divider()
        
        st.header("🎯 Quick Questions")
        quick_questions = [
            "What is a brain tumor?",
            "What are the symptoms?",
            "What is glioma?",
            "What is meningioma?",
            "What is a pituitary tumor?",
            "What causes brain tumors?",
            "Treatment options?",
            "How are brain tumors diagnosed?"
        ]
        

        for idx, q in enumerate(quick_questions):
            if st.button(q, key=f"sidebar_quick_q_{idx}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                response = chatbot.get_response(q)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

        st.divider()
        
        # Clear Chat button - blue color with icon
        if st.button("🗑️ Clear Chat History", type="primary", key="clear_chat_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ Chat history cleared!")
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📷 MRI Analysis", "📜 Scan History"])
    
    # TAB 1: Chat Assistant
    with tab1:
        st.subheader("💬 Ask Questions About Brain Tumors")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                response = message["content"]
                answer_text = response.get("answer", str(response)) if isinstance(response, dict) else str(response)
                st.markdown(f'<div class="chat-message bot-message">🤖 {answer_text}</div>', 
                          unsafe_allow_html=True)
        
        # User input
        user_input = st.text_input("💭 Type your question...", key="chat_user_input")
        
        if st.button("Send ➤", type="primary", key="chat_send_btn"):
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                response = chatbot.get_response(user_input)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
    
    # TAB 2: MRI Analysis
    with tab2:
        st.subheader("📷 Upload MRI Scan for Analysis")
        
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Important:</strong> This is an AI screening tool for educational purposes. 
            Results should ALWAYS be verified by qualified medical professionals.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name", key="mri_patient_name")
            patient_age = st.text_input("Age", key="mri_patient_age")
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="mri_patient_gender")
        
        with col2:
            uploaded_file = st.file_uploader("Choose MRI image", type=['jpg', 'jpeg', 'png'], key="mri_file_upload")
            
            if uploaded_file:
                # Show small preview of uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded MRI Preview", width=250)
            else:
                st.info("👆 Upload an MRI scan to begin analysis")
        
        # Analysis button and results below (full width)
        if uploaded_file:
            if st.button("🔍 Analyze MRI", type="primary", use_container_width=True, key="mri_analyze_btn"):
                with st.spinner("🧠 Analyzing brain MRI... Please wait..."):
                    try:
                        image = Image.open(uploaded_file)
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        
                        result, status = predict_mri(
                            st.session_state.token,
                            img_byte_arr,
                            patient_name,
                            patient_age,
                            patient_gender
                        )
                        
                        if status == 200 and result.get('success'):
                            st.success("✅ Analysis Complete!")
                            
                            # Display results in columns
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                st.metric("🎯 Detected Condition", result['prediction'].replace('_', ' ').title())
                            with res_col2:
                                st.metric("📊 Confidence Level", f"{result['confidence']:.2f}%")
                            
                            # Show all predictions if available
                            if 'all_predictions' in result:
                                st.subheader("📈 Detailed Probabilities")
                                all_preds = result['all_predictions']
                                for tumor_type, prob in sorted(all_preds.items(), key=lambda x: x[1], reverse=True):
                                    st.progress(prob / 100, text=f"{tumor_type.replace('_', ' ').title()}: {prob:.2f}%")
                            
                            # Generate and offer PDF download
                            pdf = generate_pdf_report(
                                patient_name or "Not Provided",
                                patient_age or "Not Provided",
                                patient_gender or "Not Provided",
                                result['prediction'],
                                result['confidence']
                            )
                            
                            st.download_button(
                                label="📄 Download Professional PDF Report",
                                data=pdf,
                                file_name=f"Brain_MRI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="mri_download_pdf_btn"
                            )
                            
                            st.info("💬 Result has been saved to your scan history!")
                        else:
                            st.error(f"❌ {result.get('error', 'Analysis failed')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")        
            else:
                st.info("👆 Upload an MRI scan to begin analysis")
    
    # TAB 3: Scan History
    with tab3:
        st.subheader("📜 Your Scan History")
        
        if st.session_state.token:
            history_result, status = get_scan_history(st.session_state.token, limit=20)
            
            if status == 200 and history_result.get('success'):
                history = history_result.get('history', [])
                
                if history:
                    for scan in history:
                        with st.expander(f"📅 {scan.get('scan_date', 'N/A')} - {scan.get('prediction', 'Unknown').replace('_', ' ').title()}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Patient:** {scan.get('patient_name') or 'N/A'}")
                                st.write(f"**Age:** {scan.get('patient_age') or 'N/A'}")
                            with col2:
                                st.write(f"**Gender:** {scan.get('patient_gender') or 'N/A'}")
                                st.write(f"**Confidence:** {scan.get('confidence', 0):.2f}%")
                else:
                    st.info("📝 No scan history yet. Upload your first MRI to get started!")
            else:
                st.error("❌ Failed to load scan history")

# ============ MAIN APP LOGIC ============
        

def main():

    # 🔰 1. ABOUT PAGE (primary landing page for everyone)
    if st.session_state.page == "about":
        show_about_page()
        return

    # 🔐 2. LOGIN / REGISTER PAGE
    if st.session_state.page in ["login", "register"]:
        show_login_page()
        return

    # 🚫 3. NOT AUTHENTICATED → redirect to ABOUT
    if not st.session_state.authenticated:
        st.session_state.page = "about"
        st.rerun()

    if st.button("📖 View About Page"):
        st.session_state.page = "about"
        st.rerun()

    # ✅ 4. AUTHENTICATED USER → MAIN APP
    if st.session_state.page == "main":
        show_main_app()
        return

if __name__ == "__main__":
    main()
