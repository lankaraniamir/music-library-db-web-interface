
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os

# Accessed from template folder (index.html)
from sqlalchemy import *
from sqlalchemy.pool import NullPool
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Setting up flask
from flask import Flask, request, render_template, g, redirect, Response, flash, session
# flash
app = Flask(__name__, template_folder=tmpl_dir)


# Creates database connecting to the given URI
DATABASE_USERNAME = "al3625"
DATABASE_PASSWRD = "bread"
DATABASE_HOST = "34.148.107.47"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass

@app.route('/')
def home():
	return render_template("base.html", title="Homepage")

@app.route('/users')
def users():
	# select_query = "SELECT username FROM app_user"
	select_query = "SELECT * FROM app_user"
	cursor = g.conn.execute(text(select_query))

	users = []
	for result in cursor:
		users.append(result)
	cursor.close()

	context = dict(users = users)
	return render_template("users.html", **context)


@app.route('/charts')
def charts():
	return render_template("charts.html", title="Charts")
@app.route('/genres')
def genres():
	return render_template("genres.html", title="Genres")
@app.route('/contribute')
def contribute():
	return render_template("contribute.html", title="Contribute")

@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        params = {}

        select_query = f"SELECT * FROM app_user WHERE username = '{username}'"
        cursor = g.conn.execute(text(select_query))

        users = []
        for result in cursor:
            users.append(result)
        cursor.close()


        error = None
        if not users:
            error = 'Username does not exist. Try again.'
        elif len(users) > 1:
            error = "Duplicate username should not exist. Contact site admins."
        elif users[0].password != password:
            error = 'Incorrect password. Try again.'

        if error is None:
            session.clear()
            session['username'] = users[0].password
            return redirect('home', user=username)


        return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')





@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            select_query=(f'SELECT * FROM app_user WHERE username = {username}')
            if not g.conn.execute(text(select_query)):
                g.conn.execute(
                    "INSERT INTO app_user (username, password) VALUES (?, ?)",
                    (username, password),
                )
                g.conn.commit()
            else:
                error = f"User {username} is already registered."
        flash(error)

    return render_template('templates/register.html')

if __name__ == "__main__":
	import click
	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""
		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
run()