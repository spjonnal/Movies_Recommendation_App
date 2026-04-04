from select import select

import chromadb, uuid
import pandas as pd
import psycopg2
import os,sys
from dotenv import load_dotenv
def vector_data_retrieval(query):

    #load_dotenv("pg_admin4_connect_for_py.env")

    pg_host = os.getenv("DB_HOST") 
    pg_db_name = os.getenv("DB_NAME")
    pg_user = os.getenv("DB_USER") 
    pg_port = os.getenv("DB_PORT")
    pg_password = os.getenv("DB_PASSWORD")


    db_connection = psycopg2.connect(
        host = pg_host,
        port = pg_port,
        database = pg_db_name,
        password = pg_password,
        user = pg_user,
    )

    cursor = db_connection.cursor()
    cursor.execute("select distinct(genres) from movie_information where genres is not Null order by genres asc;")
    unique_genres = cursor.fetchall()
    values_genres = []
    for i in unique_genres:
        values_genres.append(i[0])


    client = chromadb.Client()
    collection = client.get_or_create_collection("movie_information")




    collection.add(
        ids = [str(uuid.uuid4()) for _ in range(len(values_genres))],                   
        documents = values_genres,
        metadatas = [{"genre": genre} for genre in values_genres]
    )


    output = collection.query(
        query_texts=[query],
        n_results=2,
        include=["metadatas"]
    )
    resulting_genres = []
    if output['metadatas'][0]:
        for i in output['metadatas'][0]:
            resulting_genres.append(i['genre'])
    print("resulting genres = ",resulting_genres)
    entire_data = []
    for genre in resulting_genres:
        cursor.execute(
           f"select * from movie_information where genres like '%{genre}%' and ratings>=3 ORDER BY RANDOM() limit 50;"
        )
        data = cursor.fetchall()
        certificate = data[0][0]
        imdb_id = data[0][1]
        overview = data[0][2]
        release_date = data[0][3]
        runtime = data[0][4]
        title = data[0][5]
        ratings = data[0][6]
        genres = data[0][7]
        available_languages = data[0][8]
        cast_and_crew = data[0][9]
        youtube_trailer_link = data[0][10]
        entire_data.append({
            'Certificate':certificate,
            'IMDB ID':imdb_id,
            'Overview':overview,
            'Release Date':release_date,
            'Runtime':runtime,
            'Title':title,
            'Ratings':ratings,
            'Genres':genres,
            'Available Languages':available_languages,
            'Cast and Crew':cast_and_crew,
            'Youtube Trailer Link':youtube_trailer_link

        })
    return entire_data
        


if __name__ == "__main__":
    node_input = sys.argv[1]
    vector_data_retrieval(node_input)
