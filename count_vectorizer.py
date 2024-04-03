import sqlite3
import numpy as np
import sys,json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import requests
import ast
def db_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        #print("connection from db_connection in python file",connection)
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
        return None
def count_vectorizer_results(complete_data,user_ip,connection_string):
    complete_data = [i for i in complete_data ]
    genres_included = pd.DataFrame(complete_data)
    genres_included = genres_included[0].dropna()
    #print("genres included inside count vect",genres_included)
    count_vec = CountVectorizer(tokenizer= lambda x: x.split(","),token_pattern=None)
    #count_vec = CountVectorizer(tokenizer=lambda x: x.split(","))
    genres_vec = count_vec.fit_transform(genres_included).toarray()
    user_ip_vector = count_vec.transform([user_ip]).toarray()
    cosine_out = cosine_similarity(genres_vec,user_ip_vector)
    cosine_out = cosine_out.flatten()
    sorted_list = np.argsort(cosine_out)[::-1]
    sorted_list = sorted_list[:50]
    #print("top 30 indexes =  ",sorted_list)
    h_m = {}
    for i in sorted_list:
        h_m[i] = np.round(cosine_out[i],2)
    sql = "SELECT Adult_Rated, Title,Runtime,Release_Date,ratings,Genres_Included,Original_Language FROM movie_information"#, ,title , Release_Date, ratings, Genres_Included, Original_Language,Cast_Information
    results = execute_sql_query(connection_string,sql)
    #indexes = [i for i in h_m.keys()]
    output = []
    for i in h_m.keys():
        movie_data = {
            'certificate':results[i][0] if results[i][0] else False,
            'Title':str(results[i][1]) if str(results[i][1]) else None,
            'Total_runtime':results[i][2] if results[i][2] else None,
            'release':results[i][3] if results[i][3] else None,
            'movie_ratings':results[i][4] if results[i][4] else None,
            'all_genres':results[i][5] if results[i][5] else None,
            "original_language":results[i][6] if results[i][6] else None
        }
        output.append(movie_data)
    return output
    
    
if __name__ == "__main__":
    # Path to your SQLite database file
    database_file = "sqdb.db"
    #csv_data = pd.read_csv('C:\\University_of_Waterloo\\winter 2024\\Django_Project\\Node_React_Movie_App\\movies_final_data.csv',low_memory=False)
    conn = db_connection(database_file)
    get_all_query = "select genres_included from movie_information"
    genres = execute_sql_query(conn,get_all_query)
    node_genre = sys.argv[1]
    movies = count_vectorizer_results(genres,node_genre,conn)
    print(json.dumps(movies))
    #movies_json = json.dumps(movies)
    
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