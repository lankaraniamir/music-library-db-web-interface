
"""
Amir & Imani's Music Database Server
"""
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for


""" Pre-made Server Code """

# Setting up flask
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# Creates database connecting to the given URI
DATABASE_USERNAME = "al3625"
DATABASE_PASSWRD = "bread"
DATABASE_HOST = "34.148.107.47"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"
engine = create_engine(DATABASEURI)

app.secret_key = b'11+\x0e\x9b\xe9A\xe4ZR]\xb5'
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



def get_query(query):
    cursor = g.conn.execute(text(query))
    result = []
    for row in cursor:
        result.append(row)
    cursor.close()
    return result



@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('profile', username=session['username']))
    else:
        return render_template('login.html')
    # return render_template("base.html", title="Homepage")

@app.route('/genres')
def genres():
	genres = get_query("SELECT * FROM genre")
	context = dict(genres = genres)
	return render_template("genres.html", title="All Genres", **context)

@app.route('/genres/<name>')
def genre(name):
    # select_query = (
    # "SELECT DISTINCT genre "
    # "FROM ( "
    #     "WITH RECURSIVE "
    #     "   subgenres(sub_genre, parent_genre) AS ( "
    #     "       SELECT sub_genre, parent_genre "
    #     "       FROM genre_inheritance "
    #     f"       WHERE parent_genre = '{name}' "
    #     "       UNION "
    #     "           SELECT A.sub_genre, A.parent_genre "
    #     "           FROM genre_inheritance A "
    #     "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
    #     "   ) "
    #     "SELECT DISTINCT sub_genre FROM subgenres "
    #     "UNION SELECT DISTINCT parent_genre FROM subgenres "
    # ") AS SG "
    # "WHERE G.genre = SG.sub_genre and S.song_id = G.song_id and G.primary_genre = True; "
    # )

    select_query = (
    "SELECT DISTINCT sub_genre "
    "FROM genre_inheritance A "
    f"WHERE parent_genre = '{name}' "
    )

    select_query = (
    "SELECT DISTINCT parent_genre "
    "FROM genre_inheritance A "
    f"WHERE sub_genre = '{name}' "
    )

    select_query = (
    "SELECT DISTINCT sub_genre "
    "FROM ( "
        "WITH RECURSIVE "
        "   subgenres(sub_genre, parent_genre) AS ( "
        "       FROM genre_inheritance "
        f"       WHERE parent_genre = '{name}' "
        "       UNION "
        "           SELECT A.sub_genre, A.parent_genre "
        "           FROM genre_inheritance A "
        "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
        "   ) "
        "SELECT DISTINCT sub_genre FROM subgenres "
        "UNION SELECT DISTINCT parent_genre FROM subgenres "
    ") AS SG "
    # f"WHERE SG.primary_genre != {name}; "
    )
    descendants = get_query(query)

    # query = (
    # "SELECT DISTINCT title "
    # "FROM song S, song_in_genre G, ( "
    #     "WITH RECURSIVE "
    #     "   subgenres(sub_genre, parent_genre) AS ( "
    #     "       SELECT sub_genre, parent_genre "
    #     "       FROM genre_inheritance "
    #     f"       WHERE parent_genre = '{name}' "
    #     "       UNION "
    #     "           SELECT A.sub_genre, A.parent_genre "
    #     "           FROM genre_inheritance A "
    #     "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
    #     "   ) "
    #     "SELECT DISTINCT sub_genre FROM subgenres "
    #     "UNION SELECT DISTINCT parent_genre FROM subgenres "
    # ") AS SG "
    # "WHERE G.genre = SG.sub_genre and S.song_id = G.song_id and G.primary_genre = True; "
    # )

    context = dict(descendants = descendants)
    return render_template("genre.html", title=name, **context)


# add radio button for primary, secondary, or both
# error = None
# if request.method == 'POST' and len(request.form) > 0:
#     selection = request.form['selection']
# elif request.method == 'POST' and len(request.form) == 0:
#     error = "Please select a category."
#     selection = None
# else:
#     selection = None




@app.route('/song/<title>')
def song(title):
    return redirect(url_for('profile', username=session['username']))




""""""
""" *** USER INFO ***"""
""""""

@app.route('/users')
def users():
    # select_query = "SELECT * FROM app_user"
    # cursor = g.conn.execute(text(select_query))

    # users = []
    # for result in cursor:
    # 	users.append(result)
    # cursor.close()

    users = get_query("SELECT * FROM app_user")
    context = dict(users = users)
    return render_template("users.html", title="All Users", **context)

@app.route('/users/<username>', methods=('GET', 'POST'))
def profile(username):
    error = None
    if request.method == 'POST' and len(request.form) > 0:
        selection = request.form['selection']
    elif request.method == 'POST' and len(request.form) == 0:
        error = "Please select a category."
        selection = None
    else:
        selection = None

    if selection == 'songs':
        query = (
        "SELECT S.title AS song, S.year as year, "
            "STRING_AGG(DISTINCT CASE WHEN C.primary_artist and not C.featured_artist THEN A.primary_name END, ', ') AS main_artists, "
            "STRING_AGG(DISTINCT CASE WHEN C.featured_artist THEN A.primary_name END, ', ') AS featured_artists, "
            "STRING_AGG(DISTINCT CASE WHEN not C.primary_artist and not C.featured_artist THEN A.primary_name END, ', ') AS other_artists, "
            "STRING_AGG(DISTINCT genre, ', ') AS genres, "
            "O.love as love, ROUND(O.stars/2, 1) as stars "
        "FROM song S, artist A, song_credit C, song_in_genre G, song_opinion O "
        "WHERE S.song_id = C.song_id AND A.artist_id = C.artist_id "
        "AND S.song_id = G.song_id AND S.song_id = O.song_id "
        f"AND O.username = '{username}' AND (O.love = TRUE OR O.stars IS NOT NULL) "
        "GROUP BY S.song_id, S.title, S.year, O.love, O.stars;"
        )
        columns = ["song","main_artists","featured_artists","other_artists","year","genres","love","stars"]

    elif selection == 'albums':
        query = (
        "SELECT R.title AS releases, R.release_date as release_date, "
            "STRING_AGG(DISTINCT CASE WHEN C.primary_artist THEN A.primary_name END, ', ') AS main_artists, "
            "STRING_AGG(DISTINCT CASE WHEN NOT C.primary_artist THEN A.primary_name END, ', ') AS other_artists, "
            "STRING_AGG(DISTINCT genre, ', ') AS genres, "
            "O.love as love, ROUND(O.stars/2, 1) as stars, R.release_type AS release_type "
        "FROM release R, artist A, release_credit C, release_in_genre G, release_opinion O "
        "WHERE R.release_id = C.release_id AND A.artist_id = C.artist_id "
        "AND R.release_id = G.release_id AND R.release_id = O.release_id "
        f"AND O.username = '{username}' AND (O.love = TRUE OR O.stars IS NOT NULL)"
        "GROUP BY R.release_id, R.title, R.release_date, O.love, O.stars;"
        )
        columns = ["releases","main_artists","other_artists","year","genres","release_type","love","stars"]

    elif selection == 'playlists':
        query = (
        "SELECT Distinct P.title as playlists, date_created, date_modified, track_count "
            # "STRING_AGG( DISTINCT JO.playlist_creator ) "
        "FROM playlist P, other_playlist_creator O "
        "WHERE P.playlist_id = O.playlist_id "
        f"AND (P.original_creator = '{username}' OR O.username = '{username}') "
        )
        columns = ["playlists", "date_created", "date_modified", "track_count"]

    else:
        return render_template('profile.html', title=username, user=username,
                               data=None, sort=None, columns=None, error=error, selection=selection)

    rows = get_query(query)
    return render_template('profile.html', title=username, user=username,
                           data=rows, sort="stars", columns=columns, error=error,
                           selection=selection)





""""""
""" *** LOGIN & REGISTRATION ***"""
""""""

def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = f"SELECT * FROM app_user WHERE username = '{username}'"
        users = get_query(query)
        if not users:
            error = 'Username does not exist. Try again.'
        elif len(users) > 1:
            error = "Duplicate username should not exist. Contact site admins."
        elif users[0].password != password:
            error = 'Incorrect password. Try again.'
        if error is None:
            session.clear()
            session['username'] = username
            return redirect(url_for('profile', username=username))

    return render_template('login.html', error=error)

@app.route('/register', methods=('GET', 'POST'))
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name     = request.form['name']

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif len(username) > 15:
            error = 'Username is more than 15 characters.'
        elif len(username) > 15:
            error = 'Password is more than 15 characters.'
        else:
            matching_user = get_query(f"SELECT * FROM app_user WHERE username = '{username}'")
            if len(matching_user) > 0:
                error = f"User {username} is already registered."
            else:
                if name:
                    g.conn.execute(text(f"INSERT INTO app_user (username, password, name) VALUES {username, password, name[:30]}"))
                else:
                    g.conn.execute(text(f"INSERT INTO app_user (username, password) VALUES {username, password}"))
                g.conn.commit()
                return redirect(url_for('profile', username=username))

    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    # session.pop('username', None)
	session.clear()
	return redirect('/')




""""""
""" *** Not made ***"""
""""""
@app.route('/contribute')
def contribute():
	return render_template("contribute.html", title="Contribute")
@app.route('/charts')
def charts():
	return render_template("charts.html", title="Charts")





""" More Pre-made ***"""
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