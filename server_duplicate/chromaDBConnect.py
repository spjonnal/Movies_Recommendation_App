import chromadb, uuid
from chromadb.config import Settings
import csv, numpy as np, pandas as pd
client = chromadb.HttpClient(
  host="localhost",  # e.g. "api.trychroma.com"
  port=8001,                      # if using HTTPS / secure port
  ssl=True,                      # if your endpoint uses HTTPS
  settings=Settings(
    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
    chroma_client_auth_credentials="ck-6BYV9MmX5kp3NCngcYTK5aZp7Usr2YkZ7NEnXY5xRdKv",
    anonymized_telemetry=False
  ),
  tenant="1617e74b-281c-4642-a673-502ce85eb5d8",       # if needed
  database="Movie Recommendation"  # if needed
)

collection = client.get_or_create_collection("movie_information")

# movie_data = pd.read_csv("./final_movie_data.csv")
# batch_size = 1000

# for i in range(0, movie_data.shape[0], batch_size):
#     batch = movie_data.iloc[i:i+batch_size]

#     ids = [str(uuid.uuid4()) for _ in range(len(batch))]
#     documents = batch["Overview"].fillna("N/A").astype(str).tolist()
#     metadatas = batch[[
#         "Adult Rated","Release Date","Runtime","Title","Ratings",
#         "Genre","Available Languages","Cast and Crew"
#     ]].rename(columns={
#         "Adult Rated": "certificate",
#         "Release Date": "release",
#         "Runtime": "length",
#         "Title": "title",
#         "Ratings": "ratings",
#         "Genre": "genre",
#         "Available Languages": "languages",
#         "Cast and Crew": "cast"
#     }).to_dict(orient="records")

#     collection.add(
#         ids=ids,
#         documents=documents,
#         metadatas=metadatas
#     )
#     print(f"Inserted batch {i//batch_size + 1}")


output = collection.query(
    query_texts=["I want to watch something funny"],
    n_results=15,
    include=["metadatas","documents"]
)

print("output = ",output)