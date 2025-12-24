import numpy as np
import pickle
import warnings
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.chat_models import ChatOllama
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict


warnings.filterwarnings("ignore")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load embeddings ----
embeddings = np.load("movie_embeddings.npy")
with open("movie_texts.pkl", "rb") as f:
    movie_texts = pickle.load(f)

encoder_model = SentenceTransformer("all-MiniLM-L6-v2")
llm = ChatOllama(model="mistral", temperature=0)

# ---- Retrieval ----
def retrieve_top_k(query, k=3):
    query_emb = encoder_model.encode([query], normalize_embeddings=True)
    sims = cosine_similarity(query_emb, embeddings)[0]
    top = sims.argsort()[::-1][:k]
    return [(movie_texts[i], sims[i]) for i in top]

# ---- Query variations ----
def generate_query_variations(q):
    return [
        q,
        f"Tell me about movies related to {q}",
        f"Movies similar to {q}",
        f"Recommend movies for {q}",
        f"List top movies about {q}",
    ]

class Message(BaseModel):
    from_user: str
    text: str

class ConversationRequest(BaseModel):
    conversation: List[Message]

@app.post("/ask_llm")
async def ask_llm(request: ConversationRequest):
    # Build context from conversation
    messages = request.conversation
    context_text = "\n".join([f"{m.from_user}: {m.text}" for m in messages])
    
    # Use the latest message as the question
    question = messages[-1].text

    # Optionally, generate query variations, retrieval, etc.
    variations = generate_query_variations(question)
    retrieved = []
    for v in variations:
        retrieved.extend(retrieve_top_k(v, k=3))

    unique = []
    seen = set()
    for doc, score in retrieved:
        if doc not in seen:
            unique.append(doc)
            seen.add(doc)

    context_docs = "\n\n".join(unique[:10])

    prompt = f"""
Conversation so far:
{context_text}

Answer the following based on the movie database:
{context_docs}

Question: {question}
"""

    response = llm.invoke(prompt)
    return {"answer": response.content}

if __name__ == "__main__":
    print("in the main python")
    uvicorn.run("RAG:app", host="0.0.0.0", port=8000,reload=True)
