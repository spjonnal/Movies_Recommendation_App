# import json
# from select import select

# import chromadb, uuid
# import pandas as pd
# import psycopg2
# import os,sys
# from dotenv import load_dotenv
# def vector_data_retrieval(query):

#     #load_dotenv("pg_admin4_connect_for_py.env")

#     pg_host = os.getenv("DB_HOST") 
#     pg_db_name = os.getenv("DB_NAME")
#     pg_user = os.getenv("DB_USER") 
#     pg_port = os.getenv("DB_PORT")
#     pg_password = os.getenv("DB_PASSWORD")


#     db_connection = psycopg2.connect(
#         host = pg_host,
#         port = pg_port,
#         database = pg_db_name,
#         password = pg_password,
#         user = pg_user,
#     )

#     cursor = db_connection.cursor()
#     cursor.execute("select distinct(genres) from movie_information where genres is not Null order by genres asc;")
#     unique_genres = cursor.fetchall()
#     values_genres = []
#     for i in unique_genres:
#         values_genres.append(i[0])


#     client = chromadb.Client()
#     collection = client.get_or_create_collection("movie_information")




#     collection.add(
#         ids = [str(uuid.uuid4()) for _ in range(len(values_genres))],                   
#         documents = values_genres,
#         metadatas = [{"genre": genre} for genre in values_genres]
#     )


#     output = collection.query(
#         query_texts=[query],
#         n_results=5,
#         include=["metadatas"]
#     )
#     resulting_genres = []
#     if output['metadatas'][0]:
#         for i in output['metadatas'][0]:
#             resulting_genres.append(i['genre'])
    
#     entire_data = []
#     for genre in resulting_genres:
#         cursor.execute(
#            f"select * from movie_information where genres like '%{genre}%' and ratings>=3 ORDER BY RANDOM() limit 50;"
#         )
#         data = cursor.fetchall()
#         certificate = str(data[0][0]) if data[0][0] else "False"
#         imdb_id = data[0][1] if data[0][1] else None
#         overview = data[0][2] if data[0][2] else None
#         release_date = data[0][3] if data[0][3] else None
#         runtime = data[0][4] if data[0][4] else None
#         title = data[0][5] if data[0][5] else None
#         ratings = data[0][6] if data[0][6] else None
#         genres = data[0][7] if data[0][7] else None
#         available_languages = data[0][8] if data[0][8] else None
#         cast_and_crew = data[0][9] if data[0][9] else None
#         youtube_trailer_link = data[0][10] if data[0][10] else None
#         entire_data.append({
#             'Certificate':certificate,
#             'IMDB ID':imdb_id,
#             'Overview':overview,
#             'Release Date':release_date,
#             'Runtime':runtime,
#             'Title':title,
#             'Ratings':ratings,
#             'Genres':genres,
#             'Available Languages':available_languages,
#             'Cast and Crew':cast_and_crew,
#             'Youtube Trailer Link':youtube_trailer_link

#         })
#     return entire_data
        


# if __name__ == "__main__":
#     node_input = sys.argv[1]
#     movie_data = vector_data_retrieval(node_input)
#     print(json.dumps(movie_data,indent=4,default=str,sort_keys=True))

import json
import chromadb
import psycopg2
import os, sys, time
from dotenv import load_dotenv
from functools import lru_cache

#load_dotenv("pg_admin4_connect_for_py.env")

db_connection = psycopg2.connect(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
)

cursor = db_connection.cursor()
client = chromadb.Client(
    settings=chromadb.config.Settings(
        persist_directory="./chroma_data"
    )
)

collection = client.get_or_create_collection("movie_information")
def load_genres_once():
    if collection.count() > 0:
        return  # to avoid duplicate embeddings

    cursor.execute("""
        SELECT DISTINCT genres 
        FROM movie_information 
        WHERE genres IS NOT NULL;
    """)
    
    genres = [row[0] for row in cursor.fetchall()]

    collection.add(
        ids=[str(i) for i in range(len(genres))],
        documents=genres,
        metadatas=[{"genre": g} for g in genres]
    )

load_genres_once()

#@lru_cache(maxsize=50)
def vector_data_retrieval(query):
    #start = time.time()

    
    output = collection.query(
        query_texts=[query],
        n_results=5,
        include=["metadatas"]
    )

    resulting_genres = [m['genre'] for m in output['metadatas'][0]]

    if not resulting_genres:
        return []
    placeholders = " OR ".join(["genres ILIKE %s"] * len(resulting_genres))

    sql_query = f"""
        SELECT 
            *
        FROM movie_information
        WHERE ratings >= 3
        AND ({placeholders})
        LIMIT 50;
    """

    params = [f"%{g}%" for g in resulting_genres]

    cursor.execute(sql_query, params)
    rows = cursor.fetchall()
    results = [
        {
            'Certificate': r[0] or "False",
            'IMDB ID': r[1],
            'Overview': r[2] if r[2] else "Not Available",
            'Release Date': r[3] if r[3] else "Not Available",
            'Runtime': r[4],
            'Title': r[5] if r[5] else "Not Available",
            'Ratings': r[6],
            'Genres': r[7] if r[7] else "Not Available",
            'Available Languages': r[8] if r[8] else "Not Available",
            'Cast and Crew': r[9] if r[9] else "Not Available",
            'Youtube Trailer Link': r[10] if r[10] else "Not Available"
        }
        for r in rows
    ]
    return results
if __name__ == "__main__":
    query = sys.argv[1]
    data = vector_data_retrieval(query)
    print(json.dumps(data, indent=2, default=str))
