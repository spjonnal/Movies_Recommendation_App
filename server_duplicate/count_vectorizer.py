import os
import sqlite3
import numpy as np
import sys,json,random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

import psycopg2







# def retrieve_youtube_trailers(query,max_result=1):
#     DEVELOPER_KEY  = "AIzaSyBE4ZXk8QZ4_Ktqrx9EpWjN6hJcMTZ8xng"
#     YOUTUBE_API_SERVICE_NAME = 'youtube'
#     YOUTUBE_API_VERSION = 'v3'
#     youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

#     req = youtube.search().list(
#         part = 'id,snippet',
#         q = query,
#         maxResults = max_result,
        
        
#     )
#     resp = req.execute()
    
#     trailer = []
#     for resp_item in resp['items']:
#         video_id = resp_item['id']['videoId']
#         trailer_url = f"https://www.youtube.com/watch?v={video_id}"
#         trailer.append(trailer_url)
       
#     return trailer
        

def db_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        
        return connection
    except sqlite3.Error as e:
        return None
def execute_sql_query(conn, sql_query):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        return rows
    except sqlite3.Error as e:
        print("some error in execution = ",e)
        return None
def count_vectorizer_results(complete_data,user_ip,connection_string):
    complete_data = [i for i in complete_data if i and i]
    
    genres_included = pd.DataFrame(complete_data)
    genres_included = genres_included[0].dropna()
    count_vec = CountVectorizer()
    #count_vec = CountVectorizer(tokenizer=lambda x: x.split(","))
    genres_vec = count_vec.fit_transform(genres_included).toarray()# type: ignore
    user_ip_vector = count_vec.transform([user_ip]).toarray() # type: ignore
    cosine_out = cosine_similarity(genres_vec,user_ip_vector)
    cosine_out = cosine_out.flatten()
    sorted_list = np.argsort(cosine_out)[::-1]
    sorted_list = sorted_list[:100]
    np.random.shuffle(sorted_list)
    
    
    #print("top 30 indexes =  ",sorted_list)
    h_m = {}
    for i in sorted_list:
        h_m[i] = np.round(cosine_out[i],2)
    sql = """
SELECT 
    "Adult Rated",
    "IMDB ID",
    Overview,
    "Release Date",
    Runtime,
    Title,
    Ratings,
    Genres,
    "Available Languages",
    "Cast and Crew"
FROM movie_information
"""
    results = execute_sql_query(connection_string,sql)
    #indexes = [i for i in h_m.keys()]
    output = []
    for i in h_m.keys():
        certificate = results[i][0]  # Adult Rated
        movie_id    = results[i][1]  # Movie id
        overview    = results[i][2]  # Overview
        yr          = results[i][3]  # Release Date
        runtime     = results[i][4]  # Runtime
        title       = results[i][5]  # Title
        rating      = results[i][6]  # Ratings
        genre       = results[i][7]  # Genres
        lang        = results[i][8]  # Available Languages
        cast        = results[i][9]  # Cast and Crew

        #movie_trailer = retrieve_youtube_trailers(trailer_prompt)
        movie_data = {
            'Adult Rated': certificate if certificate else False,
            'IMDB ID':movie_id if movie_id else None,
            'Overview': overview if overview else "Not Available",
            'Release Date':yr if yr else None,
            'Run Time':runtime if runtime else None,
            'Title':title if title else 'Not Available',
            'Ratings': rating if rating else None,
            'Genres': genre if genre else None,
            "Available Languages": lang if lang else None,
            "Cast and Crew":cast if cast else 'Not Available'
            #"trailer": movie_trailer[0]
        }
        output.append(movie_data)

    return output
    
    
if __name__ == "__main__":
    # Path to your SQLite database file
    conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    port=5432
)
    #csv_data = pd.read_csv('C:\\University_of_Waterloo\\winter 2024\\Django_Project\\Node_React_Movie_App\\movies_final_data.csv',low_memory=False)
    
    get_all_query = "SELECT genres FROM movie_information;"
    genres = execute_sql_query(conn,get_all_query)

    node_genre = sys.argv[1]
    
    movies = count_vectorizer_results(genres,node_genre,conn)
    print(json.dumps(movies))
    
    # Send an HTTP POST request to your Node.js server
    # url = "http://localhost:4001/api/receive-movies"
    #response = requests.post(url, json={"movies": movies_json})

    # Check the response from the server
    # if response.status_code == 200:
    #     print("Movies data sent successfully to Node.js server")
    # else:
    #     print("Failed to send movies data to Node.js server")
    #sys.stdout.flush()
    # if conn:
    #     conn.close()
