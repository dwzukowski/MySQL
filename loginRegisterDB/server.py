from flask import Flask, render_template, request, redirect, session, flash
import bcrypt 
import re
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'loginregisterdb')
app.secret_key= "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route('/')
def index():
    password= 'abc123'
    print password
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print hashed
    newpassword= 'abc13'
    print newpassword
    print bcrypt.hashpw(newpassword, hashed) == hashed
    #print test
    return render_template('index.html')
@app.route('/signin', methods=['POST'])
def login():
    email= request.form['email']
    enteredPassword= request.form['password'].encode('utf-8')
    query= "SELECT * FROM users WHERE users.email='{}' LIMIT 1".format(email)
    result= mysql.query_db(query)
    print result 
    print len(result)
    if len(result) < 1: 
        flash('Email not in database, please register')
        return redirect('/register')
    result= result[0]['password'].encode('utf-8')
    #print type(result)
    #print type(enteredPassword)
    if bcrypt.hashpw(enteredPassword, result) == result:
        session['loggedIn']= True
        print session['loggedIn']
        return redirect('/loggedin')
    flash('Incorrect password, please reenter')
    return redirect('/')
@app.route('/register')
def registrationPage():
    return render_template('register.html')
@app.route('/createAccount',methods=['POST'])
def creatingAccount():
    print "Got Post info"
    firstName= request.form['firstName']
    lastName= request.form['lastName']
    email= request.form['email']
    password= request.form['password'].encode('utf-8')
    passwordConfirm= request.form['confirmpass'].encode('utf-8')
    #validation checks
    invalid= False
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address")
        invalid= True
        #return redirect('/register')  
    if len(firstName) < 2 or len(lastName) < 2: 
        flash("first and last name must be 2 chars long")
        invalid= True
    if password != passwordConfirm:
        flash("Password does not match password confirmation")
        invalid= True
    if len(password) < 8:
        flash("Password must be at least 8 characters long")
    if invalid:
        return redirect('/register')
        password= 'abc123'
    hashedPassword= bcrypt.hashpw(password, bcrypt.gensalt())
    #print hashedPassword
    #print type(hashedPassword)
    query = "INSERT INTO users (firstName, lastName, email,password, loggedin) VALUES ('{}','{}','{}','{}',True)".format(firstName, lastName, email, hashedPassword)
    print query
    mysql.query_db(query)
    return redirect('/loggedin')
@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')

app.run(debug=True)