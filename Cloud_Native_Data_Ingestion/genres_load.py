import os
from dotenv import load_dotenv
import requests,sys
import psycopg2
from psycopg2 import pool
load_dotenv('database_connection.env')
load_dotenv('tmdbapi.env')
db_url = os.getenv("DB_URL")

pg_conn = pool.SimpleConnectionPool(
    1,10,dsn=db_url
)
API_KEY = os.getenv("TMDB_API_KEY")

headers = {
    "accept": "application/json",
    
}
def dbConn():
    conn = pg_conn.getconn()
    cur = conn.cursor()
    return conn, cur

def release_conn(conn):
    pg_conn.putconn(conn)

def get_genres_description(genres_id_url):
    
    response = requests.get(genres_id_url,params={'api_key':API_KEY}, headers=headers)

    genres = response.json()
    return genres



def load_genres_ids_text(imdb_genres_url):
    genres = get_genres_description(imdb_genres_url)
    
    conn,cur = dbConn()
    try:
        genre_values = [
            (genre["id"], genre["name"])
            for genre in genres["genres"]
        ]
        # executemany expects a list of tuples
        cur.executemany( 
            """
            INSERT INTO genres(genre_id, genre_description)
            VALUES (%s, %s)
            
            """,
            genre_values
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Database Error:", e)
    finally:
        release_conn(conn)


if __name__ =="__main__":
    load_genres_ids_text("https://api.themoviedb.org/3/genre/movie/list")
    
    