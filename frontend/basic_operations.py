from flask import Flask, url_for, request, render_template
from flask_mysqldb import MySQL
from markupsafe import escape
import datetime

app = Flask(__name__)

# I made a user on my mysql database with this info. I think if all team members made a user with the same creds on their own servers,
# then the files should work as soon as they are pulled regardless of machine.
# FYI, I made this user with the DBManager administrative role

app.config["MYSQL_USER"] = "hackathon_admin"
app.config["MYSQL_PASSWORD"] = "admin"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_DB"] = "hackathon_management"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

with open("../backend/sql_files/each_project_score.sql", "r") as file:
    data = file.read()


@app.route("/")
def index():
    return render_template("main_menu.html")


@app.route("/menu")
def menu():
    return render_template("main_menu.html")


# ATTENDEE AND JUDGE REGISTRATION------------------------------------------------------------------------------------------------------
@app.route("/register/<type>", methods=["POST", "GET"])
def register(error=None, type=None):
    error = None

    if request.method == "POST":
        if type == "attendee":
            if valid_registration(request.form):
                id = register_attendee(request.form)
                # return confirmation(request.form['firstname'], id, type)
            else:
                error = "Invalid registration"
        elif type == "judge":
            if valid_registration(request.form):
                id = register_judge(request.form)
                # return confirmation(request.form['firstname'], id, type)
            else:
                error = "Invalid registration"

        return confirmation(request.form["firstname"], id, type)

    if type == "attendee":
        return render_template("attendee_registration_form.html", error=error)
    elif type == "judge":
        return render_template("judge_registration_form.html", error=error)


@app.route("/confirmation/<name>")
def confirmation(name=None, id=None, type=None):
    if type == "attendee":
        return render_template(
            "attendee_registration_confirmation.html",
            name=name,
            id=id,
            event_date="Feb. 7, 2020",
        )
    elif type == "judge":
        return render_template(
            "judge_registration_confirmation.html",
            name=name,
            id=id,
            event_date="Feb. 7, 2020",
        )
    elif type == "project_create":
        return render_template("project_creation_confirmation.html", name=name, id=id)
    elif type == "project_join":
        return render_template("project_join_confirmation.html", name=name, id=id)
    elif type == "project_submit":
        return render_template("project_submit_confirmation.html")


def valid_registration(registrationForm):
    # registrationForm['firstname']
    # for now, just to see if I can insert an attendee successfully, default to true
    return True


def register_attendee(form):
    with open("../backend/sql_files/get_max_attendee_id.sql", "r") as file:
        getMaxId = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getMaxId)
        maxId = cur.fetchone()
        id = str(maxId["MAX(attendee_id)"] + 1)
        cur.execute(
            """INSERT INTO Attendee(attendee_id, first_name, last_name, email, age, project_id, checked_in, school, level_of_study, major, shirt_size) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                id,
                form["firstname"],
                form["lastname"],
                form["email"],
                form["age"],
                None,
                0,
                form["school"],
                form["levelOfStudy"],
                form["major"],
                form["shirtsize"],
            ),
        )
        mysql.connection.commit()
        return id


def register_judge(form):
    with open("../backend/sql_files/get_max_judge_id.sql", "r") as file:
        getMaxId = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getMaxId)
        maxId = cur.fetchone()
        now = datetime.date(2009, 5, 5)
        id = str(maxId["MAX(judge_id)"] + 1)
        cur.execute(
            """INSERT INTO Judge(judge_id, first_name, last_name, affiliation, date_contacted, responded, coming, contact_info) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                id,
                form["firstname"],
                form["lastname"],
                form["affiliation"],
                now,
                0,
                0,
                form["contact_info"],
            ),
        )
        mysql.connection.commit()
        return id


# PROJECT CREATION AND JOINING ------------------------------------------------------------------------------------------------------
@app.route("/project/create", methods=["POST", "GET"])
def createprojectrequest(error=None):
    error = None

    if request.method == "POST":
        if valid_project_creation(request.form):
            id = create_project(request.form)
            return confirmation(request.form["name"], id, "project_create")
        else:
            error = "Invalid project creation"

    return render_template("project_create.html", error=error)


def valid_project_creation(project_form):
    # for now, just to see if I can creat a project successfully, default to true
    return True


def create_project(form):
    with open("../backend/sql_files/get_max_project_id.sql", "r") as file:
        getMaxId = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getMaxId)
        maxId = cur.fetchone()
        id = str(maxId["MAX(project_id)"] + 1)
        cur.execute(
            """INSERT INTO project(project_id, project_name, table_num, tagline) VALUES (%s,%s,%s,%s)""",
            (id, form["name"], None, form["tagline"]),
        )
        mysql.connection.commit()
        return id


@app.route("/project/join", methods=["POST", "GET"])
def joinprojectrequest(error=None):
    error = None

    if request.method == "POST":
        if valid_project_join(request.form):
            join_project(request.form)
            return confirmation(None, request.form["project_id"], "project_join")
        else:
            error = "Invalid project creation"

    return render_template("project_join.html", error=error)


def valid_project_join(join_form):
    # for now, just to see if I can creat a project successfully, default to true
    return True


def join_project(form):
    cur = mysql.connection.cursor()
    # join the new team WILL OVERWRITE old team affiliation
    cur.execute(
        """UPDATE attendee SET project_id = %s WHERE attendee_id = %s""",
        (form["project_id"], form["attendee_id"]),
    )
    mysql.connection.commit()


# PROJECT SUBMISSION FOR PRIZE ------------------------------------------------------------------------------------------------------
@app.route("/project/submitforprize", methods=["POST", "GET"])
def submitprojectrequest(error=None):
    error = None

    with open("../backend/sql_files/get_prize_names.sql", "r") as file:
        getPrizeNames = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getPrizeNames)
        # prize names
        names = cur.fetchall()

        if request.method == "POST":
            if valid_project_submission(request.form):
                id = submit_project(names, request.form)
                return confirmation(request.form["project_id"], id, "project_submit")
            else:
                error = "Invalid project creation"

        return render_template(
            "project_submission_form.html", error=error, prizes=names
        )


def valid_project_submission(project_form):
    # for now, just to see if I can creat a project successfully, default to true
    return True


def submit_project(prizes, form):
    for prize in prizes:
        if request.form.get(prize["prize_name"]):
            print("submitting project for %s " % (str(prize["prize_name"])))
            cur = mysql.connection.cursor()
            cur.execute(
                """INSERT INTO projectforprize(project_id, prize_name) VALUES (%s,%s)""",
                (form["project_id"], str(prize["prize_name"])),
            )
            mysql.connection.commit()

    return id

# LINKS FOR ORGANIZERS -----------------------------------------------------------------------------------------------
@app.route("/winners")
def winners():
    cur = mysql.connection.cursor()
    # to apply an insertion or deletion to the database
    #   mysql.connection.commit()
    # to execute a typed query on the database
    #   cur.execute('''SELECT restriction, COUNT(*) FROM dietrestriction GROUP BY restriction ORDER BY COUNT(*) desc''')
    cur.execute(data)
    results = cur.fetchall()
    print(results)
    return results[0]

def get_judge_email(form):
    with open('../backend/sql_files/get_max_judge_id.sql', 'r') as file:
        getMaxId = file.read()
        cur = mysql.connection.cursor()
        cur.execute(getMaxId)
        maxId = cur.fetchone()
        now = datetime.date(2009, 5, 5)
        id = str(maxId['MAX(judge_id)'] + 1)
        cur.execute('''INSERT INTO Judge(judge_id, first_name, last_name, affiliation, date_contacted, responded, coming, contact_info) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''', (id, form['firstname'], form['lastname'], form['affiliation'], now, 0, 0 , form['contact_info']))
        mysql.connection.commit()
        return id

# LINKS FOR JUDGES ---------------------------------------------------------------------------------------------------
@app.route("/judging/score")
def judge_project():
    # First we have to identify the judge
    return render_template("judge_score_email.html")

@app.route('/judging/score')
def scoring_email_form():
    # First we have to identify the judge
    return render_template("judge_score_email.html")
    
@app.route('/judging/scoreform', methods=["POST", "GET"])
def scoring_form():
    if request.method == "POST":
        email = request.form['email']
        # get judge id
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT judge_id from Judge where contact_info="{email}"')
        judge_id = cur.fetchone()['judge_id']       

        # now use judge id to get list of prizes this judge is judging
        cur.execute(f'''
            SELECT DISTINCT prize_name
            FROM JudgesProject WHERE judge_id={judge_id}
        '''
        )
        prize_list = [p['prize_name'] for p in cur.fetchall()]

        # get list of project names and table numbers submitted for each of these prizes that judge is judging
        projects_and_tables = []
        prize_categories = []
        for prize in prize_list:
            cur.execute(f'''
                SELECT DISTINCT project_name, table_num
                FROM JudgesProject JOIN Project ON JudgesProject.project_id = Project.project_id 
                WHERE judge_id={judge_id} and prize_name="{prize}"
            '''
            )
            projects_and_tables.append(cur.fetchall())

            # get scoring categories for each of the prizes
            cur.execute(f'''
                SELECT HasCriteria.category_name, min_score, max_score FROM HasCriteria
                JOIN ScoringCategory ON HasCriteria.category_name = ScoringCategory.category_name
                AND prize_name="{prize}"
            ''')
            prize_categories.append(cur.fetchall())

        # zip prize list with projects, tables, and categories for each prize. Each element of this list is
        # (prize name, names and table numbers of each project submitted for this prize that this judge is judging, scoring categories for this prize)
        project_list = list(zip(prize_list, projects_and_tables, prize_categories))

        return render_template("judge_score.html", projects=project_list)

@app.route('/judging/submitscoreform', methods=["POST", "GET"])
def submit_scoring_form():
    if request.method == "POST":
        print(request.form)
        return render_template("main_menu.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
