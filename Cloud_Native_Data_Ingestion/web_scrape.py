  
import requests,sys
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import pool
from urllib.parse import quote_plus
load_dotenv('tmdbapi.env')
load_dotenv('database_connection.env')

API_KEY = os.getenv("TMDB_API_KEY")

headers = {
    "accept": "application/json",
    
}

db_url = os.getenv("DB_URL")

pg_connection = None


def db_pool():
    global pg_connection

    if pg_connection is None:
        pg_connection = pool.SimpleConnectionPool(
            1,
            10,
            dsn=db_url
        )

    return pg_connection


def dbConn():
    connection_pool = db_pool()
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    return connection, cursor


def release_conn(connection):
    connection_pool = db_pool()
    connection_pool.putconn(connection)




def get_runtime_info(info_url):
    
    info_response = requests.get(info_url,params={'api_key':API_KEY}, headers=headers)
    
    runtime_info_response = info_response.json()
    runtime = runtime_info_response['runtime']
    
    
    return runtime
def get_cast_and_crew(cast_url):
    cast_response = requests.get(cast_url,params={'api_key':API_KEY}, headers=headers)
    cast_and_crew_response = cast_response.json()
    actors = [
        actor["name"]
        for actor in cast_and_crew_response["cast"]
    ]
    return actors


    
def get_gernes(cur):
    
    
    try:
        cur.execute(
            """
                SELECT genre_id,genre_description FROM genres
            """
        )
        genre_data = dict(cur.fetchall())
        return genre_data
    except:
        print("Unable to fetch genres information")
        raise
    
        
        


def  insert_movie_information(json_data):
    conn,cur = dbConn()
    genre_data = get_gernes(cur)
    try:
        cur.execute(
            """
                INSERT INTO movie_information(adult_rated, imdb_id,overview,release_date,runtime,title,ratings,genres,available_languages,cast_and_crew,youtube_trailer_link)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
                (
                    json_data['adult_rated'],json_data['imdb_id'],json_data['overview'],json_data['release_date'],json_data['runtime'],
                    json_data['title'],json_data['ratings'],",".join(genre_data[genre_id] for genre_id in json_data['genres']) ,json_data['original_language'],
                    json_data['cast'],json_data['youtube_trailer']
                )
        )
        conn.commit()
        #return "data inserted successfully"
    except Exception as e:
        raise e
    finally:
        release_conn(conn)

def generate_youtube_links(movie_name):
    youtube_search = (
        f"https://www.youtube.com/results?search_query="
        f"{quote_plus(movie_name + ' official trailer')}"
    )
    return youtube_search



def scrape_web_information(tmdb_url):
    # movie_name = []
    # genres = []
    # overview = []
    # release_date = []
    # ratings = []
    # imdb_id = []
    # adult_rated = []
    # original_language = []
    # youtube_trailer = []
    # runtime = []
    # cast_and_crew = []
    all_movies = []
    
    try:
        for page in range(1,2):
            response = requests.get(
                tmdb_url,
                headers=headers,
                params={
                    "api_key":API_KEY,
                    "page": page,
                    "sort_by": "popularity.desc"
                }
            )
            data = response.json()['results']
            
            for movie in data:
                name_of_movie = movie['title']
                imdb_id_of_movie = movie['id']
                final_data={
                    'title':name_of_movie,
                    'genres':movie['genre_ids'],
                    'overview':movie['overview'],
                    'release_date':movie['release_date'],
                    'ratings':movie['vote_average'],
                    'imdb_id':imdb_id_of_movie,
                    'adult_rated':movie['adult'],
                    'original_language':movie['original_language'],
                    'youtube_trailer':generate_youtube_links(name_of_movie),
                    'runtime':get_runtime_info(f"https://api.themoviedb.org/3/movie/{imdb_id_of_movie}"),
                    'cast':get_cast_and_crew(f"https://api.themoviedb.org/3/movie/{imdb_id_of_movie}/credits"),
                }
                all_movies.append(final_data)
        return all_movies
                #insert_movie_information(final_data)

    except Exception as e:
        print("Error in web scraping:", repr(e))
        import traceback
        traceback.print_exc()
        raise


