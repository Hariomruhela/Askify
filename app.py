from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from sqlalchemy import create_engine, Column, String, MetaData, Table, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import os
from dotenv import load_dotenv
from file_reader import csv_reader, excel_reader
import google.generativeai as genai
import re
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling
CORS(app)

# Database Connection
engine = create_engine("mysql+pymysql://root:atp@localhost:3306/RAG")
connection = engine.connect()

Base = declarative_base()
meta = MetaData()

Session = sessionmaker(bind=engine)
session_db = Session()
print(os.getenv("GEMINI_API_KEY"))
# Google Gemini API Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------- Home Page (File Upload) -------------------------
@app.route("/Home")
def main():
    return render_template("main.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return "<h1>Contact Us</h1><p>Contact details for Adderess.</p>"


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"Error": "No file part"})
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"Error": "No selected file"})
        
        temp_file_path = f"temp_{file.filename}".replace(" ", "_")
        file.save(temp_file_path)

        file_extension = os.path.splitext(temp_file_path)[-1].lower()

        if file_extension == ".csv":
            file_type = csv_reader(temp_file_path)
        elif file_extension in [".xls", ".xlsx"]:
            file_type = excel_reader(temp_file_path)
        else:
            os.remove(temp_file_path)
            return jsonify({"Error": "File must be CSV or Excel sheet"})
        print("File Type IS : ",file_type)
        columns = file_type.columns.tolist()
        # columns_table = [Column(column_name, String(255)) for column_name in columns]
        columns_table = []
        for column_name in columns:
            if isinstance(column_name, str) and column_name.strip():  # check it's a valid string
                sanitized_column = column_name.strip()
                columns_table.append(Column(sanitized_column, String(255)))
            else:
                print(f"Skipping invalid column name: {column_name}")



        table_name = temp_file_path.split(".")[0].replace("(", "").replace(")", "")
        table_name = f"temp_{file.filename.split('.')[0].replace(' ', '_')}"
        table_name = table_name.replace("(", "").replace(")", "")

        # Store table name in session
        session["table_name"] = table_name  

        inspector = inspect(engine)

        if table_name in inspector.get_table_names():
            try:
                with engine.begin() as conn:
                    drop_query = text(f'DROP TABLE `{table_name}`;')
                    conn.execute(drop_query)
            except Exception as e:
                return jsonify({"Error": f"Error dropping table '{table_name}': {e}"})

        dynamic_table = Table(table_name, meta, *columns_table, extend_existing=True)
        meta.create_all(engine)

        data_to_insert = file_type.to_dict(orient="records")
        print("data to insert in db ",data_to_insert)
        with connection.begin():
            connection.execute(dynamic_table.insert(), data_to_insert)

        os.remove(temp_file_path)

        return redirect(url_for("chat"))

    return render_template("home.html")

# ------------------------- Chat Page -------------------------

@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        if request.method == "POST":
            user_query = request.form.get("query")
            table_name = session.get("table_name")

            if not table_name:
                return jsonify({"Error": "No table name found in session."})

            # Fetch columns from the database
            inspector = inspect(engine)
            columns = [column["name"] for column in inspector.get_columns(table_name)]

            column_list_str = ", ".join([f"`{col}`" for col in columns])

            system_prompt = (
                f"""You are a skilled MySQL assistant. Your task is to generate precise MySQL queries with the following rules:

1. **Table and Column Names**:
   - Always enclose **table names** and **column names** in **backticks** (`).
   - Example: `SELECT `column_name` FROM `table_name` WHERE `column_name` = 'value';`

2. **Data Format**:
   - All data is stored as **strings**, so even numeric data should be treated as **strings** in conditions, comparisons, and results.

3. **Available Table and Columns**:
   - Use the exact table name: `{table_name}`.
   - Available columns are: {column_list_str}.

4. **Handling NULL Values**:
   - Assume NULL values are represented as `'NaN'`.

5. **Query Structure**:
   - Maintain proper SQL syntax and best practices.
   - Ensure queries are optimized and secure.
"""
            )

            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(f"{system_prompt}\nUser request: {user_query}")

            result = re.sub(r'```[\s\S]*?\n', '', response.text.strip())
            result = result.replace("\n", " ").replace("`", "`").strip()
            result = result[:len(result) - 3]

            with engine.connect() as connection:
                query_result = connection.execute(text(result))
                rows = [dict(zip(query_result.keys(), row)) for row in query_result]

            # ----------------- Add Chat History to Session -----------------
            if "chat_history" not in session:
                session["chat_history"] = []

            session["chat_history"].append({
                "query": user_query,
                "result": rows
            })

            session.modified = True  # Ensures session updates are saved

            return render_template("chat.html")

        # On GET request, simply render the chat page
        return render_template("chat.html")

    except BaseException as Error:
        return jsonify({"Error": str(Error)})
# ------------------------- Main Entry Point -------------------------

if __name__ == "__main__":
    app.run(debug=True)
