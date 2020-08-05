# Employee Management System 
# Local web server application, MySQL database, CRUD operations, injection safe queries, file reading

from flask import Flask, render_template, url_for, request, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

# Import packages as variables and load environment variables
app = Flask(__name__)
mysql = MySQL(app)
app.config.from_envvar('APP_SETTINGS')

# Render index page, add new employee into database
@app.route('/', methods = ['POST', 'GET'])
def index():
    cur = mysql.connection.cursor()

    # Check if user send a post request
    if request.method == 'POST':
        con = mysql.connection
        form = request.form
        query1 = 'SELECT email FROM employees WHERE email = %s'
        query2 = 'INSERT INTO employees (name, email, job, salary) VALUES (%s, %s, %s, %s)'

        # Check if insert failed
        try:
            cur.execute(query1, (form['email'],))

            # Check if email not used then insert new employee
            if len(cur.fetchall()) == 0:
                cur.execute(query2, (form['name'], form['email'], form['job'], form['salary']))
                con.commit()
            else:
                print('Email used')
        except:
            print('Insert failed')
        return redirect('/')

    # Retrieve all employees from database and render page
    else:
        cur.execute('SELECT * FROM employees')
        return render_template('index.html', employees = cur.fetchall())

# Render update page, update selected employee's information
@app.route('/update/<string:email>', methods = ['POST', 'GET'])
def update(email):
    cur = mysql.connection.cursor()
    query1 = 'SELECT * FROM employees WHERE email = %s'
  
    # Check if user send a post request
    if request.method == 'POST':
        con = mysql.connection
        form = request.form
        query2 = 'UPDATE employees SET name = %s, email = %s, job = %s, salary = %s WHERE email = %s'

        # Check if update failed
        try:
            cur.execute(query1, (form['email'],))

            # Check if email not used or same then update employee
            if len(cur.fetchall()) == 0 or form['email'] == email:
                cur.execute(query2, (form['name'], form['email'], form['job'], form['salary'], email))    
                con.commit()
            else:
                print('Email used')
                return redirect('/update/' + email)
        except:
            print('Update failed')
        return redirect('/')

    # Retrieve selected employee from database and render page
    else:
        cur.execute(query1, (email,))
        return render_template('update.html', employee = cur.fetchall()[0])

# Delete selected employee
@app.route('/delete/<string:email>')
def delete(email):
    cur = mysql.connection.cursor()
    con = mysql.connection
    query = 'DELETE FROM employees WHERE email = %s'
    
    # Check if delete failed
    try:
        cur.execute(query, (email,))
        con.commit()
    except:
        print('Delete failed')
    return redirect('/')

# Read uploaded text file, add all new employees in file into database
@app.route('/upload', methods = ['POST', 'GET'])
def upload():

    # Check if user send a post request
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        con = mysql.connection
        query1 = 'SELECT email FROM employees WHERE email = %s'
        query2 = 'INSERT INTO employees (name, email, job, salary) VALUES (%s, %s, %s, %s)'
        files = request.files['file']

        # Check if file exist
        if files.filename == '':
            print('No file')
            return redirect('/')

        # Save file with secure filename into designated folder
        filename = secure_filename(files.filename)
        files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Open file for reading
        with open(app.config['UPLOAD_FOLDER'] + filename) as file:
            name = email = job = salary = count = 0

            # For each word seperated by a comma in the file
            for line in file:
                for word in line.split(','):
                   
                    # Store each employee's information
                    if count == 0:
                        name = word
                    elif count == 1:
                        email = word
                    elif count == 2:
                        job = word
                    elif count == 3:
                        salary = word
                    count += 1
                count = 0

                # Check if insert failed
                try:
                    cur.execute(query1, (email,))

                    # Check if email not used then insert new employee
                    if len(cur.fetchall()) == 0:
                        cur.execute(query2, (name, email, job, salary))
                        con.commit()
                    else:
                        print('Email used')
                except:
                    print('Insert failed')
    return redirect('/')