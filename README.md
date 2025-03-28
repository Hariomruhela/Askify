# 🚀Askify

🚀Askify is an interactive web application built with Flask that allows users to upload CSV or Excel files and query the data using natural language. The app leverages Google Gemini AI for generating precise MySQL queries.

## Features
- 📂 **File Upload**: Supports CSV and Excel files for data processing.
- 💬 **Chat Interface**: Interactive chat UI to ask queries about uploaded data.
- 🧠 **AI-Powered**: Uses Google Gemini AI to generate optimized MySQL queries.
- 📋 **Data Display**: Presents query results in a clear and organized table format.
- 🌐 **Responsive UI**: Modern, user-friendly design with dynamic components.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AshishP-armar/Askify.git
   cd Askify
2. Create a virtual environment and activate it:
     ```bash
     python -m venv venv
    source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
3. Install dependencies:
    ```bash
     pip install -r requirements.txt
4. Create a .env file and add your Gemini API key:
   ```bash
     GEMINI_API_KEY=your_api_key
5. Add your Mysql credentials:
    ```bash
      mysql+pymysql://{user_name}:{password}@{host}:{port}/{db_name}
7. Run the application:
    ```bash
      python app.py
## 🔥Usage
1. Navigate to the Home page to learn about the app.

2. Upload your data file on the Upload page.

3. Ask queries about your data on the Chat page.

## Tech Stack
1. Backend: Flask, SQLAlchemy

2. Database: MySQL

3. AI Integration: Google Gemini

4. Frontend: HTML, CSS, JavaScript

## 📬 Contact
📧 Email: ashishparmar9817@gmail.com

📞 Phone: 7879069817

🌐 LinkedIn | GitHub



