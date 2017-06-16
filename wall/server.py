from flask import Flask, render_template, request, redirect, session, flash
import bcrypt 
import re
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'walldb')
app.secret_key= "tooeasy"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/createAccount',methods=['POST'])
def createAccount():
    print "Registration POST ok"
    #define variables for form data for use in validaton and SQL query 
    firstName= request.form['firstName']
    lastName= request.form['lastName']
    email= request.form['email']
    #password must be converted to utf-8 to allow password hashing at a later step
    password= request.form['password'].encode('utf-8')
    passwordConfirm= request.form['confirmpass'].encode('utf-8')
    #validation checks, using variable invalid so that I can display flash messages for all errors generated from the form at once
    invalid= False
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address")
        invalid= True 
    if len(firstName) < 2 or len(lastName) < 2: 
        flash("first and last name must be 2 chars long")
        invalid= True
    if password != passwordConfirm:
        flash("Password does not match password confirmation")
        invalid= True
    if len(password) < 8:
        flash("Password must be at least 8 characters long")
    if invalid:
        return redirect('/')
    #hashing the user's password with bcrypt so we don't store the actual password
    hashedPassword= bcrypt.hashpw(password, bcrypt.gensalt())
    query = "INSERT INTO users (firstName, lastName, email,password, created_at, updated_at) VALUES ('{}','{}','{}','{}',NOW(), NOW())".format(firstName, lastName, email, hashedPassword)
    print query
    mysql.query_db(query)
    return redirect('/wall')
@app.route('/signin',methods=['POST'])
def signin():
    email= request.form['email']
    enteredPassword= request.form['password'].encode('utf-8')
    #query database to see if email exits
    query= "SELECT * FROM users WHERE users.email='{}' LIMIT 1".format(email)
    result= mysql.query_db(query)
    #if query doesn't return resuts, prompt user to register
    if len(result) < 1:
        flash('Email not in found, please register')
        return redirect('/')
    #email found, check password. Look for password in first item of list returned from SQL query in teh dictionary with key 'password'. Convert to utf-8 for bcrypt hashing
    truePassword= result[0]['password'].encode('utf-8')
    if bcrypt.hashpw(enteredPassword, truePassword) == truePassword:
        session['loggedin']= True
        session['loggedinUser']= result[0]['id']
        print session['loggedinUser'],"is loggedin"
        return redirect('/wall')
    flash('Incorrect password, please try again')
    return redirect('/')
@app.route('/wall')
def loadWall():
    try: 
        #check if there is a session variable ['loggedin']
        if session['loggedin']:
            query= "SELECT users.firstName, users.Lastname, messages.message, messages.id, messages.created_at FROM users LEFT JOIN messages ON users.id=messages.user_id ORDER BY messages.created_at DESC" 
            messages= mysql.query_db(query)
            query= "SELECT users.firstName, users.Lastname, comments.message_id, comments.comment, comments.created_at FROM users LEFT JOIN comments ON users.id=comments.user_id"
            comments= mysql.query_db(query)
            return render_template('wall.html', messages=messages,comments=comments)
        else:
            flash('Please sign in')
            return redirect('/')
    except: 
        return render_template('index.html')
@app.route('/message',methods=['POST'])
def postmessage():
    message= request.form['message']
    query = "INSERT INTO messages(message, created_at, updated_at, user_id) VALUES ('{}', NOW(), NOW(), {})".format(message, session['loggedinUser'])
    mysql.query_db(query)
    return redirect('/wall')
@app.route('/comment/<id>',methods=['POST'])
def postcomments(id):
    user= session['loggedinUser']
    comment= request.form['comment']
    query= "INSERT INTO comments(comment, user_id, message_id,created_at, updated_at) VALUES('{}','{}','{}', NOW(), NOW())".format(comment, user, id)
    mysql.query_db(query)
    return redirect('/wall')
app.run(debug=True)

