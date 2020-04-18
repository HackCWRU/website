from flask import Flask, url_for, request, render_template
from flask_mysqldb import MySQL
from markupsafe import escape

app = Flask(__name__)

#I made a user on my mysql database with this info. I think if all team members made a user with the same creds on their own servers,
# then the files should work as soon as they are pulled regardless of machine.
# FYI, I made this user with the DBManager administrative role


app.config['MYSQL_USER'] = 'hackathon_admin'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'hackathon_management'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

with open('../each_project_score.sql', 'r') as file:
    data = file.read()

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    #to apply an insertion or deletion to the database
    #   mysql.connection.commit()
    #to execute a typed query on the database
    #   cur.execute('''SELECT restriction, COUNT(*) FROM dietrestriction GROUP BY restriction ORDER BY COUNT(*) desc''')
    cur.execute(data)
    results = cur.fetchall()
    print(results)
    return results[0]

#@app.route('/register/<error>')
@app.route('/register/', methods=['POST', 'GET'])
def register(error = None):
    error = None
    if request.method == 'POST':
        if valid_registration(request.form):
            register_attendee(request.form)
            return confirmation(request.form['firstname'])
        else:
            error = "Invalid registration"
    
    return render_template('attendee_register.html', error = error)

@app.route('/confirmation/<name>')
def confirmation(name=None): 
    return render_template('registration_confirmation.html', name = name)


def valid_registration(registrationForm):
    #registrationForm['firstname'] 
    # for now, just to see if I can insert an attendee successfully
    return True

def register_attendee(form):
    with open('../get_max_attendee_id.sql', 'r') as file:
        getMaxId = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getMaxId)
        maxId = cur.fetchone()
        cur.execute('''INSERT INTO attendee(attendee_id, first_name, last_name, email, age, project_id, checked_in, school, level_of_study, major, shirt_size) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (str(maxId['MAX(attendee_id)'] + 1),form['firstname'],form['lastname'], form['email'], form['age'], None , 0 , form['school'], form['levelOfStudy'], form['major'], form['shirtsize']))
        mysql.connection.commit()



    
