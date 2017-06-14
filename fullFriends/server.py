from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'fullfriendsdb')
app.secret_key= "ThisIsSecret"
@app.route('/')
def index():
    query = "SELECT * FROM friends"
    friends= mysql.query_db(query)
    print friends
    return render_template('index.html', friends=friends)
@app.route('/process', methods=['POST'])
def surveyinput():
    print "Got Post info"
    firstName= request.form['firstName']
    lastName= request.form['lastName']
    friendSince= request.form['friendSince']
    query = "INSERT INTO friends (firstName, lastName, friendSince,created_at, updated_at) VALUES ('{}','{}','{}', NOW(), NOW())".format(firstName, lastName, friendSince)
    print query
    mysql.query_db(query)
    return redirect('/')
app.run(debug=True)