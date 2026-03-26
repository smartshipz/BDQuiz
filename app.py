from flask import Flask, request, render_template ,redirect,url_for
import psycopg2
import os

app = Flask(__name__)

#Supabase Database Connection
def get_db_connection():

    return psycopg2.connect(
        host=os.getenv("db.mmviznnkehyjfcwauzum.supabase.co"),
        database=os.getenv("postgres"),
        user=os.getenv("postgres"),
        password=os.getenv("Godisgood@llthetime"),
        port="5432",
        sslmode="require"
    )
    
    '''return psycopg2.connect(
        host="db.mmviznnkehyjfcwauzum.supabase.co",
        database="postgres",
        user="postgres",
        password="Godisgood@llthetime",
        port="5432"
    )'''


@app.route('/')
def home():
    return render_template('index.html')  # Your quiz HTML file

@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json()
    print("Received JSON:", data)  # DEBUG: check what is received

    if not data:
        return {"status": "error", "message": "No data received"}, 400

    reg = data.get('region')
    lo = data.get('location')
    emp = data.get('empCode')
    nam = data.get('name')
    fun = data.get('function')
    sub = data.get('subDepartment')
    date = data.get('date')
    sc = data.get('score')
    total = data.get('total', 0)

    per = (sc / total * 100) if total else 0
    
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO quizscore (REGION, LOC, EMPLCODE,NAME, FUNCTION, DATE, MARK,PERCENTAGE,QTYPE) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)"
    values = (reg, lo, emp,nam, fun, date, sc,per,sub)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return {"status": "success"}
       # print("Insert successful")  # DEBUG
        #response = {"status": "success", "message": "Data inserted"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
        #print(f"Error inserting data: {e}")
        #response = {"status": "error", "message": str(e)}
    finally:
       cursor.close()
       conn.close()

    return response


@app.route("/Result", methods=["GET", "POST"])
def Result():
     if request.method == "POST":
        selected_value = request.form.get("ResType")
        print(selected_value)
        return redirect(url_for('Report', res_type=selected_value))

     return render_template('Result.html')

@app.route('/Report')
def Report():
    res_type = request.args.get('res_type')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if res_type == 'All':
        cursor.execute("SELECT * FROM quizscore")
    elif res_type in ['OPSTEST', 'ITTEST']:
        cursor.execute("SELECT * FROM quizscore WHERE qtype=%s", (res_type,))
    else:
        return "Invalid filter", 400

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("Report.html", students=data)
if __name__ == '__main__':
    app.run(debug=True, port=5001)
