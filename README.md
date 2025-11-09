# ZJNU_HACKATHON_2025_TEAM10

## 🎯 Project Overview

The **HandyChat** -ZJNU Student Assistant is a chatbot designed to help international students at Zhejiang Normal University find PE class information and access university handbook policies through natural language conversations.

### ✨ Key Features

- **🏀 PE Class Finder**: Locate sports facilities, schedules, and   teachers
- **📚 Handbook Assistant**: Access university policies and procedures  
- **🤖 AI-Powered**: Natural language understanding with OpenAI GPT-4
- **🌐 Bilingual Support**: English and Chinese language processing
- **🔗 Combined Queries**: Handle complex questions spanning multiple domains
- **📱 Modern Interface**: Responsive web design with real-time chat

## System Architecture

Frontend (HTML/CSS/JS) → Flask Backend → AI Service →   Database
      ↓                      ↓               ↓              ↓
Modern Chat UI           RESTful API    OpenAI GPT-4  MySQL Database

### Core Components

1. **Unified Chat Service** - Single endpoint for all queries
2. **AI Intent Analysis** - Smart question classification
3. **Multi-source Handbook** - PDF + Database + AI fallback
4. **PE Class Database** - Complete sports information with maps

## 🚀 Quick Start

  ### Prerequisites
        - Python 3.8+
        - MySQL 5.7+
        - OpenAI API key
        
  ### Installation
         1. **Clone the repository**
           ```bash 
           git clone https://github.com/fatimazouhra/ZJNU_HACKATHON_2025_TEAM10.git
           cd ZJNU_HACKATHON_2025_TEAM10/HandyChat

         2. **Set up environment**
           ```bash 
           python -m venv venv
           source venv/bin/activate  # Windows: venv\Scripts\activate
           pip install -r requirements.txt

         3. **Configure database**
            CREATE DATABASE hackathon_team10_db;

         4. **Set environment variables**
            #.env file
            OPENAI_API_KEY=your_openai_key_here
            MYSQL_HOST=localhost
            MYSQL_USER=root
            MYSQL_PASSWORD=your_password
            MYSQL_DB=hackathon_team10_db

         5. **Initialize the system**
           ```bash 
           python reset_database.py
           python app.py

         6. **Access the application**
            http://localhost:5000


🎮 Usage Examples

**PE Class Queries

      "Where is basketball class?"
      
      "游泳课在哪里?" (Chinese)
      
      "tennis schedule with Coach Wang"
      
      "badminton location and time"

**Handbook Queries

      "graduation requirements"
      
      "visa extension process"
      
      "tuition fees for international students"
      
      "scholarship application deadline"
**Combined Queries

      "Do I need PE credits to graduate?"
      
      "basketball registration deadline"
      
      "swimming class and health insurance"

🔧 API Endpoints
  
      Method	     Endpoint	               Description
      POST	      /api/chat/ask	Main      chat interface
      GET	        /api/chat/sports	      Available sports list
      GET	        /api/chat/health	      System health check
      POST	      /api/chat/analyze	      Question analysis debug
      
🤖 AI Integration
The system uses OpenAI GPT-4o-mini for:

      -Intent classification (PE vs Handbook vs Combined)
      -Response enhancement and natural language generation
      -Bilingual query understanding
      -Complex query handling
      
Sample AI Analysis

          {
          "intent": "combined",
          "sport": "basketball",
          "handbook_topic": "graduation",
          "confidence": 0.92,
          "language": "english"
        }
        
🗄️ Database Schema
Core Tables

        -sport_classes - PE class information
        -locations - Sports facilities with maps
        -teachers - Instructor details
        -class_schedules - Timetable data
        -handbook_categories - Policy categories
        -handbook_faqs - Frequently asked questions

🎨 Frontend Features

        -Modern Chat Interface - Real-time messaging
        -Quick Action Buttons - One-click common queries
        -Media Support - Location photos and maps
        -Responsive Design - Mobile-friendly
        -Typing Indicators - Enhanced UX

🔍 Response Types
PE Class Response

        {
          "type": "pe",
          "sport": "basketball",
          "location_details": {...},
          "schedule": {...},
          "teacher": {...},
          "images": [...],
          "maps": {...}
        }
Handbook Response

        {
          "type": "handbook", 
          "source": "pdf_handbook",
          "answer": "Detailed policy information...",
          "ai_enhanced": true
        }
        
🚀 Deployment

        python app.py




#####################################################################


*Built with ❤️ for ZJNU International Students*

