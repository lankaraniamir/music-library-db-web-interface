
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
from flask import Flask, request, render_template, g, redirect, Response
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
	select_query = "SELECT username FROM app_user"
	cursor = g.conn.execute(text(select_query))

	users = []
	for result in cursor:
		users.append(result[0])
	cursor.close()

	context = dict(users = users)
	return render_template("users.html", **context)


@app.route('/charts')
def charts():
	abort(401)
	this_is_never_executed()

@app.route('/genres')
def genres():
	abort(401)
	this_is_never_executed()


@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')




# Create later for users
@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


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