from flask import Flask, render_template, request, redirect, session, flash
import re
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'emailvaldb')
app.secret_key= "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/process',methods=['POST'])
def formProcess():
    email= request.form['email']
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address")
        return redirect('/')   
    query= "INSERT INTO emails(email, created_at, updated_at) VALUES('{}', NOW(), NOW())".format(email)
    print query 
    mysql.query_db(query)
    session['email'] = request.form['email']
    flash("Success! the email you entered, {} , was accepted".format(session['email']))
    return redirect('/success')
@app.route('/success')
def success():
    query = "SELECT * FROM emails"
    emails= mysql.query_db(query)
    return render_template('success.html', emails=emails)
@app.route('/deleteRow',methods=['POST'])
def deleteRow():
    deleteThisRow= request.form['deleteThisRow']
    query= "DELETE FROM emails WHERE emails.id={}".format(deleteThisRow)
    print query
    mysql.query_db(query)
    return redirect('/success')




app.run(debug=True)