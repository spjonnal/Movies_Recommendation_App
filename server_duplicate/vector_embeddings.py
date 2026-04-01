import os,json, numpy as np
import bs4, pickle
import sqlite3

from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer


def sql_connection(file_name, sql_query):
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    out = []
    for i in range(len(rows)):
        doc = {
            "Adult Rated": True if rows[i][0] else False,
            "IMDB ID": rows[i][1],
            "Overview": rows[i][2],
            "Release Date": rows[i][3],
            "Runtime": rows[i][4],
            "Title": rows[i][5],
            "Ratings": rows[i][6],
            "Genres": rows[i][7],
            "Available Languages": rows[i][8],
            "Cast and Crew": rows[i][9]
        }
        out.append(doc)
    return out


def prepare_movie_texts(file_name, sql_query):
    movies = sql_connection(file_name, sql_query)
    texts = []

    for movie in movies:
        content = "".join([f"{key}: {value}" for key, value in movie.items()])
        texts.append(content)
    return texts


if __name__ == "__main__":
    database_file = "sqdb.db"
    get_all_query = "SELECT * FROM movie_information GROUP BY Title"
    movie_texts = prepare_movie_texts(database_file, get_all_query)

    print(f"Total movies found: {len(movie_texts)}")

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate embeddings locally
    embeddings = model.encode(movie_texts[200:350], convert_to_numpy=True, normalize_embeddings=True)

    print("Embeddings shape:", embeddings.shape)

    # Save both embeddings and text
    np.save("movie_embeddings.npy", embeddings)
    with open("movie_texts.pkl", "wb") as f:
        pickle.dump(movie_texts, f)

    print("✅ Embeddings saved locally!")