# 🎙 AI Audio Transcription & Translation System

An AI-powered web application that converts audio into text, generates summaries, translates content into multiple languages, and allows exporting transcripts in multiple formats.

This project uses **OpenAI Whisper** for speech recognition and provides a clean web dashboard where users can upload or record audio and instantly get transcripts.

---

## 🚀 Features

✅ Audio Transcription using AI (Whisper)  
✅ Live Audio Recording from Browser  
✅ Automatic Transcript Title Generation  
✅ Smart Transcript Summary Generation  
✅ Multi-language Translation  
✅ Download Transcript as TXT  
✅ Download Summary as TXT  
✅ Export JSON files for integration  
✅ Export Complete Reports  
✅ User Authentication System  
✅ Admin Login Support  
✅ Beautiful Dashboard UI  
✅ Loading Animation while Processing  

---

## 🧠 AI Technologies Used

- Speech Recognition: **Whisper AI**
- Translation: **Google Translator API**
- Backend: **Python Flask**
- Database: **SQLite**
- Frontend: **HTML, CSS, JavaScript**

---

## 🖥 System Architecture


User Audio
↓
Upload / Live Recording
↓
Whisper AI Transcription
↓
Transcript Processing
↓
Summary Generation
↓
Language Translation
↓
Download / Export Options


---

## 📂 Project Structure


AI-Audio-Transcription/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── templates/
│ ├── base.html
│ ├── login.html
│ ├── register.html
│ └── dashboard.html
│
├── static/
│ └── recorder.js
│
└── uploads/


---

## ⚙ Installation Guide

### 1️⃣ Clone the Repository


git clone https://github.com/YOUR_USERNAME/ai-audio-transcription-app.git


### 2️⃣ Navigate to Project


cd ai-audio-transcription-app


### 3️⃣ Create Virtual Environment


python -m venv venv


Activate:

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate


---

### 4️⃣ Install Dependencies


pip install -r requirements.txt


---

### 5️⃣ Run the Application


python app.py


Open browser:


http://127.0.0.1:5000


---

## 🔐 Default Admin Login

Username


admin


Password


admin1234


---

## 📦 Export Options

The system allows downloading results as:

- TXT files
- JSON files
- Full report exports

Example JSON:


{
"transcript": "AI is transforming the world...",
"summary": "AI is rapidly improving automation and decision making."
}


---

## 🎯 Use Cases

This system can be used for:

🎓 Lecture Transcription  
🎤 Podcast Transcription  
📰 Interview Documentation  
📚 Research Notes  
🎥 YouTube Script Generation  
🧠 Meeting Minutes Automation  

---

## 🔮 Future Improvements

- AI-powered summary using LLM
- Speaker detection
- Subtitle (SRT) export
- Cloud storage integration
- Video transcription
- Real-time transcription

---

## 👨‍💻 Author

**Paidipati Bheemesh**

Computer Science Graduate  
AI | Cybersecurity | Web Development

---

## ⭐ Support

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
📢 Share it with others

---

## 📜 License

This project is open-source and available for educational and research
