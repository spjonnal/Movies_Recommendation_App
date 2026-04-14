import json
import chromadb
import psycopg2
import uvicorn
import os, sys, time
from dotenv import load_dotenv
from functools import lru_cache
from fastapi import FastAPI

vector_search = FastAPI()

client = chromadb.Client(
    settings=chromadb.config.Settings(
        persist_directory="./chroma_data"
    )
)

#load_dotenv("pg_admin4_connect_for_py.env")

@vector_search.get('/active')
async def health_chec():
    return {"status":'active'}

# ---------------- DB CONNECTION ---------------- #
def dbConn():
    db_connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return db_connection, db_connection.cursor()

conn,cursor = dbConn()

# ---------------- CHROMA INIT ---------------- #


collection = client.get_or_create_collection("movie_information")

# ---------------- LOAD GENRES ONLY ONCE ---------------- #
def load_genres_once():
    if collection.count() > 0:
        return  # Avoid duplicate embeddings

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

# ---------------- CACHED QUERY ---------------- #
#@lru_cache(maxsize=50)
@vector_search.get("/movie_search")
async def vector_data_retrieval(query:str):
    # -------- VECTOR SEARCH -------- #
    output = collection.query(
        query_texts=[query],
        n_results=5,
        include=["metadatas"]
    )

    resulting_genres = [m['genre'] for m in output['metadatas'][0]]

    if not resulting_genres:
        return []

    # -------- SQL QUERY -------- #
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
    
    # -------- FAST PARSING -------- #
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

    

    #print(f" Total Time: {end - start:.3f}s")
    return results


# ---------------- MAIN ---------------- #
#if __name__ == "__main__":
    #query = sys.argv[1]
    #data = vector_data_retrieval(query)
    #print(json.dumps(data, indent=2, default=str))
    
    
