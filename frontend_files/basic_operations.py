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