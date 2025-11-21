# 🎓 Handy & HandyChat – ZJNU International Student Assistant  

– ZJNU_HACKATHON_2025_TEAM10_

Handy & HandyChat is an AI-powered assistant designed to help international students at **Zhejiang Normal University (ZJNU)** access important information quickly and easily.  
It brings together PE class details, campus rules, and handbook policies into one unified platform.

---

# 🌟 What This Project Solves

International students often struggle with:

- Scattered information  
- Language barriers  
- Difficulty finding PE class locations  
- Not knowing handbook rules when they need them  
- Asking the same questions every semester  

**Handy & HandyChat** solves this by providing instant, accurate, bilingual answers.

---

# 🚀 Key Features

### 🏫 Handy — Web App  
- Running rules and weekly PE requirements  
- Quick-access information  
- Frequent questions  
- Introduction to support teams (e.g., Shining Team)
  
### 🤖 HandyChat — AI Chatbot  
- Understands English + Chinese  
- Answers questions about PE classes and the university handbook  
- Handles mixed questions (e.g., “Do PE credits count for graduation?”)  
- Provides structured information instantly  

### 🗂 Data & Intelligence  
- Database-backed PE class information  
- JSON-based handbook knowledge base  
- Optimized semantic search  
- Intent detection + fallback logic

# ▶️ How to Run the Project 
## 1️⃣ Clone the Repository

    git clone https://github.com/fatima-zouhra/ZJNU_HACKATHON_2025_TEAM10.git
    cd ZJNU_HACKATHON_2025_TEAM10\HandyChat
    
## 2️⃣ Create & Activate a Virtual Environment
    python -m venv .venv
    source .venv/bin/activate     # Mac / Linux
    .\.venv\Scripts\activate      # Windows

## 3️⃣ Install Dependencies
    pip install -r requirements.txt

## 4️⃣ Create a .env File

Inside the project folder, create a file named .env:

    OPENAI_API_KEY=your_key_here
    DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost/hackathon_team10_db
    FLASK_ENV=development
    SECRET_KEY=your_secret_key

(The real project contains more variables, but these are the minimum required.)

## 5️⃣ Setup the Database

Create the database in MySQL:

    CREATE DATABASE hackathon_team10_db;


Then run the database initializer:

    python create_sample_data.py


This creates tables + inserts sample PE class data.

## 6️⃣ Start the Server
    python app.py


Your local API will be running on:

     http://localhost:5000

## 7️⃣ Open the Web App (Handy)

From your browser, open:

    http://localhost:5000/static/index.html

This loads the Handy web interface with the link to HandyChat.

## 8️⃣ Test the Chatbot API

    curl -X POST http://localhost:5000/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Where is the basketball class?"}'
    
📂 Additional Project Resources
    
📘 Documentation

The complete documentation for the project is available inside the DOCUMENTATION/ folder:

Technical Documentation

System Design Document (UML)

Developer Guide

API Documentation

📁 View folder on GitHub:
https://github.com/fatima-zouhra/ZJNU_HACKATHON_2025_TEAM10/tree/main/DOCUMENTATION

🎥 Demo Video

A quick walkthrough of Handy & HandyChat is available on YouTube:

▶️ https://youtu.be/sILAd6U6Ehw

📄 Business Plan PDF:
https://github.com/fatima-zouhra/ZJNU_HACKATHON_2025_TEAM10/blob/main/BUSINESS_PLAN.pdf
