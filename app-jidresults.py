from flask import Flask, jsonify, render_template, request, redirect, url_for
import psycopg2
import os
import views

app = Flask(__name__,static_url_path='',static_folder='static',template_folder='templates')

# Create jidresults table
conn = psycopg2.connect(database="jidResultsDB", user="dba", password="admin123", host="localhost", port="5432")
cur = conn.cursor()
cur.execute(
    '''CREATE TABLE IF NOT EXISTS jidresults (id serial PRIMARY KEY, createdate TIMESTAMPTZ, 
       spid INT NOT NULL CHECK (spid >= 0), fqdn varchar(50), qid INT NOT NULL CHECK (qid >= 0) UNIQUE, 
       jid INT NOT NULL CHECK (jid >= 0) UNIQUE, jidstatus varchar(50));''')
cur.execute(
    '''ALTER TABLE jidresults ALTER createdate set default now();''')
conn.commit()
cur.close()
conn.close()

# Define api routes
@app.route('/')
def root():
    return redirect("/index")

@app.route("/index", methods=['GET'])
def index():  
    try:
        conn = psycopg2.connect(database="jidResultsDB", user="dba", password="admin123", host="localhost", port="5432")
        cur = conn.cursor()
        # Sort table based on column ID DESC
        cur.execute("SELECT * FROM jidresults ORDER BY id DESC")
        data = cur.fetchall()
        return render_template("basic_table.html", data=data)
      
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
      
    finally:
        # closing database connection.
        if cur:
            cur.close()
            print("PostgreSQL cursor is closed")
        if conn:
            conn.close()
            print("PostgreSQL connection is closed")

@app.route('/createrecord', methods=['POST'])
def createrecord():
    try:
        conn = psycopg2.connect(database="jidResultsDB", user="dba", password="admin123", host="localhost", port="5432")
        cur = conn.cursor()

        args = request.args
        spid = args.get('spid')
        fqdn = args.get('fqdn')
        qid = args.get('qid')
        jid = args.get('jid')
        jidstatus = args.get('jidstatus')

        # Insert the data into the table
        sql_insert_query = "INSERT INTO jidresults(spid, fqdn, qid, jid, jidstatus) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(sql_insert_query, (spid, fqdn, qid, jid, jidstatus))
        conn.commit()
        count = cur.rowcount
        print(count, "Record Updated successfully ")

        # Select record based on qid which is always unique
        print("Select record after creation ")
        sql_select_query = "SELECT * FROM jidresults WHERE qid = %s"
        cur.execute(sql_select_query, (qid,))
        record = cur.fetchone()
        print(record)
        return jsonify(record), 200
        
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
      
    finally:
        # closing database connection.
        if cur:
            cur.close()
            print("PostgreSQL cursor is closed")
        if conn:
            conn.close()
            print("PostgreSQL connection is closed")

@app.route('/updaterecord', methods=['POST'])
def updaterecord():
    try:
        conn = psycopg2.connect(database="jidResultsDB", user="dba", password="admin123", host="localhost", port="5432")
        cur = conn.cursor()

        args = request.args
        id = args.get('id')
        status = args.get('jidstatus')
        colname = args.get('colname')

        # Update jidstatus
        sql_update_query = "UPDATE jidresults SET jidstatus = %s WHERE id = %s"
        cur.execute(sql_update_query, (status, id))
        conn.commit()
        count = cur.rowcount
        print(count, "Record Updated successfully ")

        print("Select record after update ")
        sql_select_query = "SELECT * FROM jidresults WHERE id = %s"
        cur.execute(sql_select_query, (id,))
        record = cur.fetchone()
        print(record)
        return jsonify(record), 200

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)

    finally:
        # closing database connection.
        if cur:
            cur.close()
            print("PostgreSQL cursor is closed")
        if conn:
            conn.close()
            print("PostgreSQL connection is closed")

# Used for Heroku
port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
