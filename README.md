# 🎓 SmartCurriculum – AI-Powered Educational Assistant

SmartCurriculum is a modern, AI-driven platform designed to generate personalized learning paths and curriculum designs based on user input. It provides a seamless experience for students and educators to organize their learning journey with the power of Generative AI.

---

## 🚀 Key Features

- **AI Curriculum Generation**: Leverages Google's Gemini AI to create tailored educational paths.
- **Personalized Dashboards**: Track your progress and view generated curricula.
- **Smart Analytics**: Visualize learning trends and engagement.
- **Secure Authentication**: Built-in login and registration system.
- **Interactive UI**: A premium, responsive design built for students.
- **Profile Management**: Customize your learning preferences.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React.js (via Vite)
- **Styling**: Vanilla CSS (Modern SaaS Aesthetics)
- **Routing**: React Router DOM
- **API Communication**: Axios

### Backend
- **Framework**: Python Flask
- **AI Engine**: Google Generative AI (Gemini)
- **Database**: SQLite
- **Security**: CORS, Environment-based configuration
- **PDF Export**: FPDF for curriculum downloads

---

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Gemini API Key** (Required for AI features)

---

## ⚙️ Installation & Setup

### 1. Clone the project
```bash
git clone <your-repo-url>
cd SmartCurriculum
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```
- Create a `.env` file in the `backend/` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 🏃 Running the Application

### Start the Backend
```bash
cd backend
# Ensure venv is active
python app.py
```
*Backend runs on: `http://127.0.0.1:5000`*

### Start the Frontend
```bash
cd frontend
npm run dev
```
*Frontend runs on: `http://localhost:5173`*

---

## 📂 Project Structure

```text
SmartCurriculum/
├── backend/                # Flask Server
│   ├── routes/             # API Endpoints (Auth, AI, Analytics)
│   ├── database.py         # DB Initialization
│   ├── ai_service.py       # Gemini AI Integration
│   └── smart_curriculum.db # Local SQLite DB
├── frontend/               # React Client
│   ├── src/
│   │   ├── components/     # UI Components
│   │   └── App.jsx         # Main Entry
│   └── vite.config.js      # Build config
└── README.md
```

---

## 📝 License
This project is licensed under the MIT License.

