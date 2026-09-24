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
```

---

## 🔄 How It Works

The system works through the following flow:

1. **User Authentication**  
   Users can register and log in using email/OTP verification.

2. **MRI Upload**  
   The user uploads a brain MRI scan through the Streamlit interface.

3. **API Request**  
   The Streamlit frontend sends the MRI image and required patient information to the Flask backend through REST APIs.

4. **AI-Based Analysis**  
   The backend processes the MRI image and uses the trained Deep Learning model for tumor classification.

5. **Result & Report**  
   The prediction result and confidence information are displayed to the user, with an option to generate a PDF report.

6. **Chatbot Assistance**  
   Users can interact with the NLP-based chatbot for brain tumor-related queries using the project's JSON knowledge base.

---

## 🧠 AI Model

The system uses a **MobileNetV2-based Deep Learning model** for brain MRI image classification.

- **Model Architecture:** MobileNetV2
- **Framework:** TensorFlow / Keras
- **Input:** Brain MRI scan
- **Output:** Predicted tumor class with confidence information
- **Model File:** `mobilenetv2_best.h5`

The trained model is integrated with the Flask backend to process MRI images and return the prediction results to the Streamlit interface.

---

## 🤖 Chatbot

The project includes an **NLP-based chatbot** that provides information related to brain tumors.

The chatbot uses **Sentence Transformers and NLTK** for natural language processing and retrieves responses from a JSON-based knowledge base.

The `knowledge_base.json` contains predefined questions, answers, keywords, and categories used by the chatbot.

**Chatbot Flow:**

```text
User Query
    ↓
NLP Processing
    ↓
Question / Keyword Matching
    ↓
knowledge_base.json
    ↓
Chatbot Response
```

---

## 📄 PDF Report

The system can generate a **PDF report** based on the MRI analysis results.

The report can include:

- Patient information
- Predicted tumor class
- Confidence information
- AI analysis details
- General information related to the prediction

PDF reports are generated using the **ReportLab** library.

---

## ⚙️ Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/Sunlight8169/brain-tumor-detection-and-chatbot-system.git
cd brain-tumor-detection-and-chatbot-system
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Backend

```bash
python backend/main.py
```

### Run the Streamlit Application

```bash
streamlit run Chatbot/streamlit_app.py
```

The application will open in the browser.

---

## ⚠️ Disclaimer

This project is developed for **educational and assistive purposes only**. It is not intended to replace professional medical diagnosis, advice, or treatment.

The MRI classification results and chatbot responses should not be considered a medical diagnosis.
