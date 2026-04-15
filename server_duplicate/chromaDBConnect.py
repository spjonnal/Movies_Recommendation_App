import json
import chromadb
import psycopg2
from psycopg2 import pool
import uvicorn
import os, sys, time
from dotenv import load_dotenv
from functools import lru_cache
from fastapi import FastAPI
from contextlib import asynccontextmanager
vector_search = FastAPI()

client = chromadb.Client(
    settings=chromadb.config.Settings(
        persist_directory="./chroma_data"
    )
)

#load_dotenv("pg_admin4_connect_for_py.env")

# pooled connection to overcome random sql connection shutdown
connection_pool = pool.SimpleConnectionPool(
        1,10,host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
# ---------------- DB CONNECTION ---------------- #
def dbConn():
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    return conn, cursor
def release_conn(conn):
    connection_pool.putconn(conn)

# ---------------- CHROMA INIT ---------------- #
collection = None

def get_collection():
    global collection
    if collection is None:
        collection = client.get_or_create_collection("movie_information")
    return collection


# ---------------- LOAD GENRES ONLY ONCE ---------------- #
def load_genres_once():
    
    col = get_collection()

    if col.count() > 0:
        return  # Avoid duplicate embeddings

    conn,cursor = dbConn()
    try:
        cursor.execute("""
            SELECT DISTINCT genres 
            FROM movie_information 
            WHERE genres IS NOT NULL;
        """)
        
        genres = [row[0] for row in cursor.fetchall()]

        col.add(
            ids=[str(i) for i in range(len(genres))],
            documents=genres,
            metadatas=[{"genre": g} for g in genres]
        )
    finally:
        release_conn(conn=conn)

# to improve vector search by reducing cold start
@asynccontextmanager
async def startup(app :FastAPI):
    try:
        print("Starting system warmup")
        conn,cursor = dbConn()
        load_genres_once()

        # Warm vector DB
        vector_collection = get_collection()
        vector_collection.query(
            query_texts=['any genre'],
            n_results=1,
            include=['metadatas']
        )

        # warm up SQL DB
        cursor.execute("SELECT 1;")
        release_conn(conn = conn)

        print("system ready")
        yield# The application serves requests here
    except Exception as e:
        print("some error while warm up = ",e)
        yield# The application serves requests here
        
vector_search = FastAPI(lifespan=startup)

@vector_search.get('/active')
async def health_chec():
    return {"status":'active'}

# ---------------- CACHED QUERY ---------------- #
#@lru_cache(maxsize=50)
@vector_search.get("/movie_search")
async def vector_data_retrieval(query:str):
    
    conn, cursor = dbConn()
    try:
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
                'Youtube Trailer Link': r[10]
            }
            for r in rows
        ]
    finally:
        release_conn(conn)
    return results
    
    
