import numpy as np
import pickle,os
import warnings
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from google import genai
from google.genai import types
from dotenv import load_dotenv

api_key = os.getenv("GEMINI_API_KEY")
port = int(os.getenv("PORT"))
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is not set in environment variables")

client = genai.Client(api_key=api_key)


model = "gemini-3.1-flash-lite-preview"  # or "gemini-2.0-flash" for the latest version
# for mod in client.models.list():
#     print(mod.name)
warnings.filterwarnings("ignore")
#ollama_api  = os.getenv("Ollama_RAG_API","http://localhost:11434")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mowickie-rag-service.onrender.com","http://localhost:8000", "http://127.0.0.1:8000","http://0.0.0.0:8000", "*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load embeddings ----
# embeddings = np.load("movie_embeddings.npy")
# with open("movie_texts.pkl", "rb") as f:
#     movie_texts = pickle.load(f)

# encoder_model = SentenceTransformer("all-MiniLM-L6-v2")
# llm = ChatOllama(model="mistral", temperature=0)

# ---- Retrieval ----
# def retrieve_top_k(query, k=3):
#     query_emb = encoder_model.encode([query], normalize_embeddings=True)
#     sims = cosine_similarity(query_emb, embeddings)[0]
#     top = sims.argsort()[::-1][:k]
#     return [(movie_texts[i], sims[i]) for i in top]

# ---- Query variations ----
def generate_query_variations(q):
    # include context-driven, mood/genre, and user intent rephrases for better retrieval
    return [
        f"What are the best movies if I like {q}?",  # intent-based
        f"Recommend recent and classic movies similar to {q}.",
        f"Provide a personalized list of movies related to {q} for a cozy night in.",
        f"Suggest top-rated and hidden gem films about {q}.",
        f"I want movies with themes like {q}, including genre and mood."
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
    
    #context_text = "\n".join([f"{m.from_user}: {m.text}" for m in messages])
    context_text = ""
    count  = 5
    for m in messages:
        if(m.from_user == "mowickie"):
            if(count > 0):
                context_text += f"{m.from_user}: {m.text}\n"
                count -= 1
    # Use the latest message as the question
    question = messages[-1].text

    # Optionally, generate query variations, retrieval, etc.
    #variations = generate_query_variations(question)
    retrieved = []
    # for v in variations:
    #     retrieved.extend(retrieve_top_k(v, k=3))
    # for v in variations:
    #     variations_response = client.models.generate_content(
    #         model=model,
    #         contents=v,
    #         config=types.GenerateContentConfig(
    #             max_output_tokens=65535, # default output tokens
    #             temperature=0.7
    #         ),
    #     )
    #     print(f"for the variation: {v}, the response is: {variations_response.text}")
    #     retrieved.append(variations_response.text)
    # unique = []
    # seen = set()
    # for doc in retrieved:
    #     if doc not in seen:
    #         unique.append(doc)
    #         seen.add(doc)

    # context_docs = "\n\n".join(unique[:10])

    prompt = f"""
    You are a friendly, conversational movie recommendation assistant.

    Your goal is to have a natural, engaging conversation with the user while recommending movies.
    Do NOT respond in JSON. Respond in normal human language.

    Guidelines:
    - Talk like a helpful friend, not a database.
    - Understand the user's mood, preferences, and context (e.g., weekend, weather, watching alone or with others).
    - Ask ONLY ONE follow-up questions if you need clarification.
    - When recommending movies, present them clearly in a readable format (bullet points or short paragraphs).
    - For each movie, naturally include:
    - Title
    - IMDb rating (if available)
    - Cast or notable crew
    - Where it can be streamed (if known)
    - Give 1 short reason in 2 sentences ONLY, why it fits the user
    - Limit recommendations to only 2 movies which are top IMDB rated out of the retrieved ones, and make sure they are relevant to the user's query and context.    
    - Do NOT include extra information or unrelated movies. Focus on quality and relevance, not quantity.   
    - Do NOT include unnecesary formatting symbols like asterisks, brackets, 
      or any other symbols. Instead, list the movies like first recommendation as 
      1 and sub parts like 
      a) IMDB rating, 
      b) cast and 
      so on..     
    Adapt to the user’s context:
    - Consider mood, occasion, and setting (e.g., weekend, weather, solo, friends)

    If the query is vague:
    - Ask 1 short follow-up question instead of guessing.

    Conversation so far:
    {context_text}



    User question:
    {question}

    Now respond conversationally and helpfully:
    """

    #response = llm.invoke(prompt)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=65530, # default output tokens
            temperature=0.7,
            # thinking_config=types.ThinkingConfig(
            #     thinking_level=types.ThinkingLevel.LOW
            # )
        ),
    )
    return {"answer": response.text}

if __name__ == "__main__":
    print("in the main python")
    #uvicorn.run("RAG:app", host="0.0.0.0", port=8000,reload=True)
    uvicorn.run("RAG:app", host="0.0.0.0", port=port)

