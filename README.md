# 🧠 Brain Tumor Detection & Chatbot System

An AI-powered system for **brain MRI analysis and tumor classification**, integrated with an **NLP-based medical chatbot** for brain tumor-related queries and assistance.

---

## 📌 Project Overview

This project is an AI-powered system that analyzes brain MRI scans using **Deep Learning** and provides an interactive **NLP-based chatbot** for brain tumor-related queries.

The system is designed as an **educational and assistive tool** to demonstrate AI-based MRI analysis and chatbot functionality. It is not a replacement for professional medical diagnosis.

---

## ✨ Key Features
- 🧠 AI-based brain tumor classification from MRI scans
- 🤖 NLP-based medical chatbot for brain tumor-related queries
- 🔐 User authentication with Email/OTP verification
- 🗂️ User profile and scan history
- 📄 Automated PDF medical report generation
- 🎨 Interactive web interface using Streamlit

---

## 🛠️ Tech Stack
- **Frontend / UI:** Streamlit
- **Backend / API:** Flask
- **Language:** Python
- **Deep Learning:** TensorFlow, Keras
- **Machine Learning:** Scikit-learn
- **NLP / Chatbot:** Sentence Transformers, NLTK
- **Knowledge Base:** JSON
- **Data Processing:** NumPy, Pandas
- **Image Processing:** OpenCV, Pillow
- **PDF Reports:** ReportLab
- **API Communication:** REST APIs / HTTP Requests 

---

## 📂 Project Structure

```text
brain-tumor-detection-and-chatbot-system/
│
├── Chatbot/                             # Streamlit chatbot frontend and NLP components
│   ├── about/
│   │   └── assets/
│   │       ├── images/
│   │       └── video/
│   ├── src/
│   │   ├── chatbot_engine.py
│   │   ├── knowledge_base_manager.py
│   │   └── nlp_processor.py
│   ├── requirements.txt
│   └── streamlit_app.py
│
├── backend/                             # Backend API and ML model
│   ├── MobileNetV2.ipynb
│   ├── auth_system.py
│   ├── main.py
│   └── mobilenetv2_best.h5
│
├── data/                                # Chatbot knowledge base
│   └── knowledge_base.json
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── runtime.txt
