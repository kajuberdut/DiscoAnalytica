
-- 1. Create an “artists” table.
CREATE SEQUENCE IF NOT EXISTS seq_artist_id START 1;

CREATE TABLE IF NOT EXISTS artists (
    artist_id INTEGER PRIMARY KEY DEFAULT nextval('seq_artist_id')
  , artist_name VARCHAR NOT NULL UNIQUE
);

INSERT OR IGNORE INTO artists (artist_name)
SELECT DISTINCT artist_name
FROM raw_data
;

-- 2. Create a “genres” table.
CREATE SEQUENCE IF NOT EXISTS seq_genres_id START 1;

CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY DEFAULT nextval('seq_genres_id')
  , genre VARCHAR NOT NULL UNIQUE
);

INSERT OR IGNORE INTO genres (genre)
SELECT DISTINCT genre
FROM raw_data
;

-- 3. Create an “topic” table.
CREATE SEQUENCE IF NOT EXISTS seq_topic_id START 1;

CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY DEFAULT nextval('seq_topic_id')
  , topic_name VARCHAR NOT NULL UNIQUE
);

INSERT OR IGNORE INTO topics (topic_name)
SELECT DISTINCT topic
FROM raw_data
;

-- 4. Create a “tracks” table for track-level information.
CREATE TABLE IF NOT EXISTS tracks (
    track_id INTEGER PRIMARY KEY
  , artist_id INTEGER REFERENCES artists(artist_id)
  , genre_id INTEGER REFERENCES genres(genre_id)
  , topic_id INTEGER REFERENCES topics(topic_id)
  , track_name VARCHAR NOT NULL
  , release_date INTEGER
  , len INTEGER
);

INSERT OR IGNORE INTO tracks (track_id, artist_id, genre_id, topic_id, track_name, release_date, len)
SELECT column00
  , (SELECT artist_id FROM artists WHERE artist_name = r.artist_name)
  , (SELECT genre_id FROM genres g WHERE g.genre = r.genre)
  , (SELECT topic_id FROM topics WHERE topic_name = r.topic)
  , r.track_name
  , CAST(r.release_date AS INTEGER)
  , r.len
FROM raw_data r
;

-- 5. Create a table for track features.
CREATE TABLE IF NOT EXISTS track_features (
  track_id INTEGER PRIMARY KEY REFERENCES tracks(track_id),
  dating FLOAT,
  violence FLOAT,
  world_life FLOAT,            -- from "world/life"
  night_time FLOAT,            -- from "night/time"
  shake_the_audience FLOAT,    -- from "shake the audience"
  family_gospel FLOAT,         -- from "family/gospel"
  romantic FLOAT,
  communication FLOAT,
  obscene FLOAT,
  music FLOAT,
  movement_places FLOAT,       -- from "movement/places"
  light_visual_perceptions FLOAT,  -- from "light/visual perceptions"
  family_spiritual FLOAT,      -- from "family/spiritual"
  like_girls FLOAT,            -- from "like/girls"
  sadness FLOAT,
  feelings FLOAT,
  danceability FLOAT,
  loudness FLOAT,
  acousticness FLOAT,
  instrumentalness FLOAT,
  valence FLOAT,
  energy FLOAT
);

INSERT OR IGNORE INTO track_features (track_id, dating, violence, world_life, night_time, shake_the_audience, family_gospel, romantic, communication, obscene, music, movement_places, light_visual_perceptions, family_spiritual, like_girls, sadness, feelings, danceability, loudness, acousticness, instrumentalness, valence, energy)
SELECT
    r.column00
  , r.dating
  , r.violence
  , r."world/life"
  , r."night/time"
  , r."shake the audience"
  , r."family/gospel"
  , r.romantic
  , r.communication
  , r.obscene
  , r.music
  , r."movement/places"
  , r."light/visual perceptions"
  , r."family/spiritual"
  , r."like/girls"
  , r.sadness
  , r.feelings
  , r.danceability
  , r.loudness
  , r.acousticness
  , r.instrumentalness
  , r.valence
  , r.energy
FROM raw_data r
;

-- 6. Lyrics
CREATE TABLE IF NOT EXISTS lyrics(
	  track_id INTEGER PRIMARY KEY REFERENCES tracks(track_id)
  , lyrics TEXT
  , hash TEXT UNIQUE
);

INSERT OR IGNORE INTO lyrics(track_id, lyrics, hash)
SELECT column00, lyrics, sha256(lyrics)
FROM raw_data
;

SELECT
       'tracks' table_name, (SELECT COUNT(1) FROM tracks) row_count, '' table_type
UNION
SELECT 'genre', (SELECT COUNT(1) FROM genre), ''