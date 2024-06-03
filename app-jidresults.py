#!/Users/hblanco/PycharmProjects/jidResults/bin/python3

from flask import Flask, jsonify, render_template, request, redirect, url_for
import psycopg2
import os
import views

app = Flask(__name__,static_url_path='',static_folder='static',template_folder='templates')

# Test Postgresql connection
conn = psycopg2.connect(database="jidResultsDB",
                            user="dba",
                            password="admin123",
                            host="localhost", port="5432")


# create a cursor
cur = conn.cursor()

# if you already have any table or not id does not matter this
# will create a jidresults table for you.
cur.execute(
    '''CREATE TABLE IF NOT EXISTS jidresults (id serial PRIMARY KEY, createdate TIMESTAMPTZ, spid INT NOT NULL CHECK (spid >= 0), fqdn varchar(50), qid INT NOT NULL CHECK (qid >= 0) UNIQUE, jid INT NOT NULL CHECK (jid >= 0) UNIQUE, jidstatus varchar(50));''')

cur.execute(
    '''ALTER TABLE jidresults ALTER createdate set default now();''')

# Insert some data into the table
#cur.execute(
#    '''INSERT INTO jidresults (spid, fqdn, qid, jid, jidstatus) VALUES ('1', 'server1.itw2.uspto.gov', '1234', '220', 'SUCCESS'), ('2', 'server-2.itw2.uspto.gov', '1235', '221', 'FAILURE');''')

# commit the changes
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

@app.route('/')
def root():
    return redirect("/index")

@app.route("/index", methods=['POST', 'GET'])
def index():  
    try:
        conn = psycopg2.connect(database="jidResultsDB",
                                user="dba",
                                password="admin123",
                                host="localhost", port="5432")

        # create a cursor
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
        # Connect to the database
        conn = psycopg2.connect(database="jidResultsDB",
                                user="dba",
                                password="admin123",
                                host="localhost", port="5432")


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

@app.route('/updatejidstatus', methods=['POST'])
def updatejidstatus():
    try:
        conn = psycopg2.connect(database="jidResultsDB",
                            user="dba",
                            password="admin123",
                            host="localhost", port="5432")

        cur = conn.cursor()

        args = request.args
        id = args.get('id')
        jidstatus = args.get('jidstatus')

        # Update jidstatus
        sql_update_query = "UPDATE jidresults SET jidstatus = %s WHERE id = %s"
        cur.execute(sql_update_query, (jidstatus, id))
        conn.commit()
        count = cur.rowcount
        print(count, "Record Updated successfully ")

        print("Select record after update ")
        sql_select_query = """SELECT * FROM jidresults WHERE id = %s"""
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


# ADJUSTMENT: This is needed for Heroku configuration as in Heroku our
# app will probably not run on port 5000 as Heroku will automatically
# assign a port for our application.
port = int(os.environ.get("PORT", 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
    #app.run(debug=True)
