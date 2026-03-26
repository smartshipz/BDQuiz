import os
import psycopg2
from flask import Flask, request, render_template, redirect, url_for, jsonify
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

app = Flask(__name__)

# Secure Supabase Connection using a single URI
def get_db_connection():
    # In Render, you will set this Key as 'DATABASE_URL'
    connection_uri = os.environ.get("DATABASE_URL")
    if not connection_uri:
        raise ValueError("No DATABASE_URL found in environment variables")
    
    # Supabase requires sslmode='require' for external connections
    return psycopg2.connect(connection_uri, sslmode="require")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Extracting values from JSON
    reg = data.get('region')
    lo = data.get('location')
    emp = data.get('empCode')
    nam = data.get('name')
    fun = data.get('function')
    sub = data.get('subDepartment')
    date = data.get('date')
    sc = data.get('score', 0)
    total = data.get('total', 0)

    per = (sc / total * 100) if total > 0 else 0
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """INSERT INTO quizmaster (REGION, LOC, EMPLCODE, NAME, FUNCTION, DATE, SCORE, PERCENTAGE, QTYPE) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (reg, lo, emp, nam, fun, date, sc, per, sub)

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        return jsonify({"status": "success", "message": "Data inserted successfully"})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/Result", methods=["GET", "POST"])
def Result():
    if request.method == "POST":
        selected_value = request.form.get("ResType")
        return redirect(url_for('Report', res_type=selected_value))
    return render_template('Result.html')

@app.route('/Report')
def Report():
    res_type = request.args.get('res_type', 'All')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if res_type == 'All':
            cursor.execute("SELECT * FROM quizmaster")
        else:
            cursor.execute("SELECT * FROM quizmaster WHERE qtype=%s", (res_type,))

        data = cursor.fetchall()
        cursor.close()
        return render_template("Report.html", students=data)
    except Exception as e:
        return f"Database Error: {str(e)}", 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Bind to 0.0.0.0 and use Render's PORT or default to 5001
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
