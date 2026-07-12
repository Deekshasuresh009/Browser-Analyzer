# 🌐 Browser Analyzer

![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)

A full-stack web application that analyzes URLs and identifies potential privacy and security risks. The application helps users determine whether a website is safe by inspecting URLs and highlighting suspicious indicators.

---

## 📖 Overview

Browser Analyzer is a web-based security tool designed to inspect website URLs and provide a privacy and security assessment. It helps users recognize suspicious websites by checking various URL characteristics and displaying an easy to understand risk analysis.

---

## ✨ Features

- 🔍 Analyze website URLs
- 🛡️ Detect suspicious URL patterns
- 🚨 Identify phishing indicators
- 📊 Generate privacy & security reports
- ⚡ Real-time analysis
- 💻 Responsive and user-friendly interface
- 🔗 FastAPI-powered backend
- 🌐 REST API integration

---

## 🛠️ Tech Stack

### 🎨 Frontend
- React.js
- JavaScript
- HTML5
- CSS3
- Axios

### ⚙️ Backend
- FastAPI
- Python
- Uvicorn

### 🧰 Tools
- Git
- GitHub
- Docker
- VS Code

---

## 📂 Project Structure

```text
Browser-Analyzer/
│
├── public/
├── src/
├── package.json
├── package-lock.json
│
├── backend/
│   ├── analyzer.py
│   ├── utils.py
│   ├── storage.py
│   ├── main.py
│   ├── requirements.txt
│   └── report_schema.json
│
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Deekshasuresh009/Browser-Analyzer.git
```

### 2️⃣ Frontend Setup

```bash
npm install
npm start
```

The frontend will run at:

```
http://localhost:3000
```

---

### 3️⃣ Backend Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will run at:

```
http://127.0.0.1:8000
```

---

## 🧪 How It Works

1. 🌐 Enter a website URL.
2. 🔍 Submit it for analysis.
3. ⚙️ The FastAPI backend processes the request.
4. 📈 The application evaluates potential privacy and security risks.
5. ✅ A detailed analysis report is displayed to the user.

---

## 🎯 Future Enhancements

- 🤖 Machine Learning-based phishing detection
- 🔒 SSL Certificate validation
- 🌍 WHOIS Lookup
- 📈 Domain Reputation Scoring
- 🛡️ VirusTotal API Integration
- 🌐 Browser Extension Support
- 📊 Advanced Security Dashboard

---

## 👩‍💻 Author

**Devi Deekshitha**

📧 Email: deekshasuresh1976@gmail.com

💼 LinkedIn: www.linkedin.com/in/c-s-devi-deekshitha-7a4a51328
