-- **** ARTIST **** --
create table artist (
	artist_id serial primary key,
	primary_name varchar(100) not null,
	relevant_city varchar(50),
	relevant_state varchar(50),
	relevant_country varchar(50),
	date_of_birth date,
	date_of_death date,
	biography text
);
create table artist_alt_name (
	artist_id int references artist,
	alt_name varchar(100),
	primary key (artist_id, alt_name)
);
create table artist_membership (
	member_id int references artist,
	parent_id int references artist,
	primary key (member_id, parent_id)
);

-- **** RELEASE **** --
create table release (
	release_id serial primary key,
	title varchar(200) not null,
	release_date date,
	release_type varchar(30),
	track_count smallint,
	true_track_count smallint,
	tags varchar(20)[],
	avg_rating numeric(5,3) check avg_rating <= 10,
	total_likes int
);
create table release_credit (
	artist_id int references artist,
	release_id int references release,
	primary_artist boolean DEFAULT True,
	credit_type varchar(50) DEFAULT null,
	primary key (artist_id, release_id, credit_type)
);
CREATE VIEW release_by_artist AS (
    SELECT artist_id, release_id, MAX(CASE WHEN primary_artist THEN 1 ELSE 0 END) AS primary_artist, COUNT(credit_type) AS num_credits
    FROM release_credit
    GROUP BY artist_id, release_id
);

-- **** SONG **** --
create table song (
	song_id serial primary key,
	title varchar(200) not null,
	year smallint,
	bpm numeric(4, 1),
	key_sig varchar(30),
	tags varchar(20)[],
	avg_rating numeric(5,3) check (avg_rating <= 10 and avg_rating > 0),
	total_likes int
);
create table song_credit (
	artist_id int references artist,
	song_id int references song,
	primary_artist boolean DEFAULT True,
	featured_artist boolean DEFAULT False,
	credit_type varchar(50) DEFAULT null,
	primary key (artist_id, song_id, credit_type),
);
create table song_in_release (
	release_id int references release,
	track_number smallint,
	song_id int references song,
	primary key (release_id, song_id)
);
CREATE VIEW song_by_artist AS (
    SELECT artist_id, song_id, MAX(CASE WHEN primary_artist THEN 1 ELSE 0 END) AS primary_artist, Max(CASE WHEN featured_artist = True Then 1 Else 0 END) AS featured_artist, COUNT(credit_type) AS num_credits
    FROM song_credit
    GROUP BY artist_id, song_id
);

-- **** GENRE **** --
create table genre (
	name varchar(50) primary key,
	descriptor varchar(1000)
);
create table genre_inheritance (
	parent_genre varchar(50) references genre,
	sub_genre varchar(50) references genre,
	primary key (sub_genre, parent_genre)
);
create table release_in_genre (
	genre varchar(50) references genre,
	release_id int references release,
	primary_genre boolean Default True,
	primary key (genre, release_id)
);
create table song_in_genre (
	genre varchar(50) references genre,
	song_id int references song,
	primary_genre boolean Default True,
	primary key (genre, song_id)
);

-- **** LYRIC **** --
create table lyric (
	song_id int primary key references song,
	lyric_type varchar(30),
	lyric_text text not null
);

-- **** USER **** --
create table app_user (
	username varchar(15) primary key,
	password varchar(12) not null,
	name varchar(30)
);
create table playlist (
	playlist_id serial primary key,
	original_creator varchar(15) not null references app_user,
	title varchar(200) not null,
	date_created date,
	date_modified date,
	track_count smallint,
	avg_rating numeric(5,3) check (avg_rating <= 10 and avg_rating > 0),
	total_likes int
);
create table song_in_playlist (
	playlist_id int references playlist,
	track_number smallint,
	song_id int references song,
	primary key (playlist_id, song_id)
);
create table release_opinion (
	username varchar(15) references app_user,
	release_id int references release,
	love boolean,
	stars smallint check (stars <= 10 and stars > 0),
	review text,
	primary key (username, release_id)
);
create table song_opinion (
	username varchar(15) references app_user,
	song_id int references song,
	love boolean,
	stars smallint check (stars <= 10 and stars > 0),
	primary key (username, song_id)
)
create table other_playlist_creator (
	username varchar(15) references app_user
	playlist_id int references playlist,
	primary key (username, playlist_id),
)
