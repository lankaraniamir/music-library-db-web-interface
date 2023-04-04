
"""
Amir & Imani's Music Database Server
"""
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for
from jinja2 import Environment


""" Pre-made Server Code """

# Setting up flask
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

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


def get_query(query, single=False, deref=False):
    cursor = g.conn.execute(text(query))
    result = []
    for row in cursor:
        if single:
            result.append(row[0])
        else:
            result.append(row)
    cursor.close()
    if deref:
        return result[0]
    return result



@app.route('/songs')
def songs():
    rows = get_query("""
    SELECT S.title AS song,
    ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN C.primary_artist and not C.featured_artist THEN A.primary_name END),
        NULL) AS main_artists,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN C.featured_artist THEN A.primary_name END),
        NULL), '{}') AS featured_artists
    FROM song S, artist A, song_credit C
    WHERE S.song_id = C.song_id AND A.artist_id = C.artist_id
    GROUP BY S.song_id, S.title
    ORDER BY song, main_artists
    """)
    columns = ["song", "main_artists", "featured_artists"]
    references = ["song","artist", "artist"]
    extra_text = ["", " by "," featuring "]
    # columns = ["song","main_artists","featured_artists","other_artists","genres","year","love","stars"]
    # NULLIF(ARRAY_REMOVE(
    #     ARRAY_AGG(DISTINCT CASE WHEN not C.primary_artist and not C.featured_artist THEN A.primary_name END),
    #     NULL), '{}') AS other_artists,
    # NULLIF(ARRAY_REMOVE(
    #     ARRAY_AGG(DISTINCT CASE WHEN primary_genre THEN genre END),
    #     Null), '{}') AS primary_genres,
    # NULLIF(ARRAY_REMOVE(
    #     ARRAY_AGG(DISTINCT CASE WHEN not primary_genre THEN genre END),
    #     Null), '{}') AS secondary_genre
    # columns = ["song","main_artists","featured_artists","other_artists","genres","year","love","stars"]
    # references = ["release","artist","artist","genre",None,None,None,None]

    #          """
    #     SELECT S.title as title, A.primary_name as artist, S.year as year
    #     FROM song S, song_credit C, artist A
    #     WHERE S.song_id = C.song_id AND C.primary_artist = True AND C.artist_id = A.artist_id
    #     ORDER BY title, artist, year
    # """)
    context = dict(data=rows, columns=columns, references=references, extra_text=extra_text)
    return render_template("songs.html", title="All Songs", **context)

@app.route('/song/<var>')
def song(var):
    return redirect(url_for('user', var=session['username']))





@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('user', var=session['username']))
    else:
        return render_template('login.html')
    # return render_template("base.html", title="Homepage")

@app.route('/genres')
def genres():
	genres = get_query("SELECT * FROM genre ORDER BY name")
	context = dict(genres = genres)
	return render_template("genres.html", title="All Genres", **context)

@app.route('/genres/<var>', methods=('GET', 'POST'))
def genre(var):
    error = None
    if request.method == 'POST' and len(request.form) > 0:
        genre_type = request.form['genre_type']
    elif request.method == 'POST' and len(request.form) == 0:
        error = "Please select a category."
        genre_type = None
    else:
        # selection = None
        genre_type = 'primary'

    if genre_type == 'primary':
        type_string = "and primary_genre = True"
    elif genre_type == 'secondary':
        type_string = "and primary_genre = False"
    else:
        type_string = ""


    description = get_query(
        f"SELECT descriptor FROM genre WHERE name = '{var}'",
        single=True, deref=True
    )

    children = get_query(
        "SELECT DISTINCT sub_genre "
        "FROM genre_inheritance "
        f"WHERE parent_genre = '{var}' "
        "ORDER BY sub_genre ",
        single=True
    )

    parents = get_query(
        "SELECT DISTINCT parent_genre "
        "FROM genre_inheritance "
        f"WHERE sub_genre = '{var}' "
        "ORDER BY parent_genre ",
        single = True
    )

    subgenres = get_query(
    "WITH RECURSIVE "
    "   subgenres(sub_genre, parent_genre) AS ( "
    "       SELECT sub_genre, parent_genre "
    "       FROM genre_inheritance "
    f"       WHERE parent_genre = '{var}'"
    "       UNION "
    "           SELECT A.sub_genre, A.parent_genre "
    "           FROM genre_inheritance A "
    "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
    "   ) "
    "SELECT DISTINCT sub_genre FROM subgenres "
    "ORDER BY sub_genre ",
    single=True
    )

    all_songs = get_query(
    "SELECT DISTINCT title "
    "FROM song S, song_in_genre G, ( "
        "WITH RECURSIVE "
        "   subgenres(sub_genre, parent_genre) AS ( "
        "       SELECT sub_genre, parent_genre "
        "       FROM genre_inheritance "
        f"       WHERE parent_genre = '{var}' "
        "       UNION "
        "           SELECT A.sub_genre, A.parent_genre "
        "           FROM genre_inheritance A "
        "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
        "   ) "
        "SELECT DISTINCT sub_genre AS genre FROM subgenres "
        f"UNION (SELECT DISTINCT name AS genre FROM genre WHERE name = '{var}') "
    ") AS SG "
    f"WHERE G.genre = SG.genre and S.song_id = G.song_id {type_string} "
    "ORDER BY title ",
    single=True
    )

    all_releases = get_query(
    "SELECT DISTINCT title "
    "FROM release R, release_in_genre G, ( "
        "WITH RECURSIVE "
        "   subgenres(sub_genre, parent_genre) AS ( "
        "       SELECT sub_genre, parent_genre "
        "       FROM genre_inheritance "
        f"       WHERE parent_genre = '{var}' "
        "       UNION "
        "           SELECT A.sub_genre, A.parent_genre "
        "           FROM genre_inheritance A "
        "           INNER JOIN subgenres S ON S.sub_genre = A.parent_genre "
        "   ) "
        "SELECT DISTINCT sub_genre AS genre FROM subgenres "
        f"UNION (SELECT DISTINCT name AS genre FROM genre WHERE name = '{var}') "
    ") AS SG "
    f"WHERE G.genre = SG.genre and R.release_id = G.release_id {type_string} "
    # "WHERE G.genre = SG.genre and R.release_id = G.release_id and G.primary_genre = True "
    "ORDER BY title ",
    single=True
    )

    context = dict(description=description, children=children, parents=parents, songs=all_songs,
                   subgenres=subgenres, releases=all_releases, main_genre=var)
    return render_template("genre.html", title=var, **context)


# add radio button for primary, secondary, or both
# error = None
# if request.method == 'POST' and len(request.form) > 0:
#     selection = request.form['selection']
# elif request.method == 'POST' and len(request.form) == 0:
#     error = "Please select a category."
#     selection = None
# else:
#     selection = None




@app.route('/release/<var>')
def release(var):
    return redirect(url_for('user', var=session['username']))

@app.route('/artist/<var>')
def artist(var):
    songs = get_query("SELECT * FROM app_user ORDER BY username")
    return redirect(url_for('user', var=session['username']))




""""""
""" *** USER INFO ***"""
""""""

@app.route('/users')
def users():
    users = get_query("SELECT * FROM app_user ORDER BY username")
    context = dict(users = users)
    return render_template("users.html", title="All Users", **context)

@app.route('/users/<var>', methods=('GET', 'POST'))
def user(var):
    error = None
    if request.method == 'POST' and len(request.form) > 0:
        selection = request.form['selection']
    elif request.method == 'POST' and len(request.form) == 0:
        error = "Please select a category."
        selection = None
    else:
        # selection = None
        selection = 'songs'

    if selection == 'songs':
        query = (
        "SELECT S.title AS song, "
            "ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN C.primary_artist and not C.featured_artist THEN A.primary_name END), "
            "NULL) AS main_artists, "
            "NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN C.featured_artist THEN A.primary_name END), "
            "NULL), '{}') AS featured_artists, "
            "NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN not C.primary_artist and not C.featured_artist THEN A.primary_name END), "
            "NULL), '{}') AS other_artists, "
            "NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT genre), NULL), '{}') AS genres, "
            "S.year as year, O.love as love, ROUND(O.stars/2, 1) as stars "
        "FROM song S, artist A, song_credit C, song_in_genre G, song_opinion O "
        "WHERE S.song_id = C.song_id AND A.artist_id = C.artist_id "
        "AND S.song_id = G.song_id AND S.song_id = O.song_id "
        f"AND O.username = '{var}' AND (O.love = TRUE OR O.stars IS NOT NULL) "
        "GROUP BY S.song_id, S.title, S.year, O.love, O.stars;"
        )
        columns = ["song","main_artists","featured_artists","other_artists","genres","year","love","stars"]
        references = ["song","artist","artist","artist","genre",None,None,None]

    elif selection == 'albums':
        query = (
        "SELECT R.title AS album, "
            "ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN C.primary_artist THEN A.primary_name END), NULL) AS main_artists, "
            "NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN NOT C.primary_artist THEN A.primary_name END), NULL), '{}') AS other_artists, "
            "NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT genre), NULL), '{}') AS genres, "
            "R.release_date as release_date, R.release_type AS release_type, "
            "O.love as love, ROUND(O.stars/2, 1) as stars "
        "FROM release R, artist A, release_credit C, release_in_genre G, release_opinion O "
        "WHERE R.release_id = C.release_id AND A.artist_id = C.artist_id "
        "AND R.release_id = G.release_id AND R.release_id = O.release_id "
        f"AND O.username = '{var}' AND (O.love = TRUE OR O.stars IS NOT NULL)"
        "GROUP BY R.release_id, R.title, R.release_date, O.love, O.stars;"
        )
        columns = ["album","main_artists","other_artists","genres","release_date","release_type","love","stars"]
        references = ["release","artist","artist","genre",None,None,None,None]

    elif selection == 'playlists':
        query = (
        "SELECT Distinct P.title as playlist, date_created, date_modified, track_count "
        "FROM playlist P, other_playlist_creator O "
        "WHERE P.playlist_id = O.playlist_id "
        f"AND (P.original_creator = '{var}' OR O.username = '{var}') "
        )
        columns = ["playlist", "date_created", "date_modified", "track_count"]
        references = ["release", None, None, None]

    else:
        return render_template('user.html', title=var, user=var,
                               data=None, sort=None, columns=None, error=error, selection=selection)

    rows = get_query(query)
    # print(rows)
    return render_template('user.html', title=var, user=var,
                           data=rows, sort="stars", columns=columns, error=error,
                           selection=selection, references=references)





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
            return redirect(url_for('user', var=username))

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
                return redirect(url_for('user', var=username))

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