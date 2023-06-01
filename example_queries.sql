-- Query 1 
-- Get all songs in the database along with info about all of its artists and genres
-- Second query is the same but for music relases
SELECT S.title AS song,
    ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN C.primary_artist and not C.featured_artist THEN A.primary_name END),
        NULL) AS main_artists,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN C.featured_artist THEN A.primary_name END), 
        NULL), '{}') AS featured_artists,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN not C.primary_artist and not C.featured_artist THEN A.primary_name END), 
        NULL), '{}') AS other_artists,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN primary_genre THEN genre END),
        Null), '{}') AS primary_genres,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN not primary_genre THEN genre END),
        Null), '{}') AS secondary_genre
FROM song S, artist A, song_credit C, song_in_genre G
WHERE S.song_id = C.song_id AND A.artist_id = C.artist_id AND S.song_id = G.song_id
GROUP BY S.song_id, S.title;

SELECT R.title AS release,
    ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN C.primary_artist THEN A.primary_name END),
    NULL) AS main_artists,
    NULLIF(ARRAY_REMOVE(ARRAY_AGG(DISTINCT CASE WHEN not C.primary_artist THEN A.primary_name END),
    NULL), '{}') AS other_artists,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN primary_genre THEN genre END),
        Null), '{}') AS primary_genres,
    NULLIF(ARRAY_REMOVE(
        ARRAY_AGG(DISTINCT CASE WHEN not primary_genre THEN genre END),
        Null), '{}') AS secondary_genres
FROM release R, artist A, release_credit C, release_in_genre G
WHERE R.release_id = C.release_id AND A.artist_id = C.artist_id AND R.release_id = G.release_id
GROUP BY R.release_id, R.title;


-- Query 2
-- Get all songs that belong to hip hop or any of its subgenres (including the
-- subgenres of its subgenres and so on). This will only include songs that have
-- any form of a hip hop primary excluding exclude songs that ony have a secondary)
SELECT DISTINCT title
FROM song S, song_in_genre G, (
    WITH RECURSIVE
        subgenres(sub_genre, parent_genre) AS (
            SELECT sub_genre, parent_genre
            FROM genre_inheritance
            WHERE parent_genre = 'Hip Hop'
            UNION
                SELECT A.sub_genre, A.parent_genre
                FROM genre_inheritance A
                INNER JOIN subgenres S ON S.sub_genre = A.parent_genre
        )
    SELECT DISTINCT sub_genre FROM subgenres
    UNION SELECT DISTINCT parent_genre FROM subgenres
) AS SG
WHERE G.genre = SG.sub_genre and S.song_id = G.song_id and G.primary_genre = True;


-- Query 3
-- Find songs in database with no files associated with them or 
-- releases with less  songs than the amount of tracks it should have.
-- There's no need to check for releases not having enough song files 
-- b/c this is checked when checking songs since song files are weak entities of song
(
    SELECT 'song' as type, title
    FROM song S
    WHERE NOT EXISTS (SELECT S.song_id FROM song_file F WHERE S.song_id = F.song_id)
) UNION (
    SELECT 'release' as type, title
    FROM release R, song_in_release SR
    WHERE R.release_id = SR.release_id
    GROUP BY title, true_track_count
    HAVING COUNT(DISTINCT SR.song_id) < R.true_track_count
) ORDER BY type, title;


-- Query 4
-- Provides an overall summary of the reviews of any individual release
-- and sorts them by the predicted quality from the reviews. Uses ranking
-- of negative and positive keywords as an additional form of evaluation
SELECT title, ROUND(AVG(stars), 2) AS average_rating, SUM(CASE WHEN love THEN 1 ELSE 0 END) AS total_likes,
    AVG(ts_rank(to_tsvector(O.review), positive, 0)) AS avg_pos_word_rank_per_review,
    AVG(ts_rank(to_tsvector(O.review), negative, 0)) AS avg_neg_word_rank_per_review
FROM release R, release_opinion O, 
    to_tsquery('good|fun|exciting|perfect|underrated|love|excellent|unique|innovative|best|flawless|great|amazing|heals|positive|beautiful') positive, 
    to_tsquery('bad|unfun|boring|tiring|annoying|ugly|painful|generic|cliche|overrated|dislike|flawed|hate|terrible|horrendous|hurts|negative') negative
WHERE R.release_id = O.release_id 
GROUP BY title
ORDER BY average_rating DESC, total_likes DESC, avg_pos_word_rank_per_review DESC, avg_neg_word_rank_per_review ASC, title


-- Query 5
-- Isolates each tag from every release and ranks the tags by their
-- average rating while also outputting the tags' associated releases
SELECT DISTINCT tag, 
    ROUND(SUM(CASE WHEN avg_rating > 0 THEN avg_rating ELSE 0 END), 2) AS average_rating,
    STRING_AGG(DISTINCT releases_A, ', ') AS releases
FROM (
    (
        SELECT DISTINCT tag, AVG(stars) as avg_rating, STRING_AGG(DISTINCT title, ', ') AS releases_A
        FROM release_opinion O, release R, unnest (R.tags) as tag 
        WHERE O.release_id = R.release_id
        GROUP BY tag
    )
    UNION
    (
        SELECT tag, NULL as avg_rating, STRING_AGG(DISTINCT title, ', ') AS releases_A
        FROM release R, unnest (R.tags) as tag 
        WHERE release_id not in (SELECT distinct release_id FROM release_opinion)
        GROUP BY tag
    )
) AS A
GROUP BY tag, releases_A
ORDER BY average_rating DESC, tag ASC
;
