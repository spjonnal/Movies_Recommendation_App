Mowickie

Movie recommendation and conversational AI application that integrates a Node.js + React front-end with a Python FastAPI backend (RAG — Retrieval-Augmented Generation) using embeddings and an LLM (ChatOllama).

Core Components

Frontend (React)

A chat interface for users to interact with the system.

Keeps conversation history and displays messages from the user (🧑‍💻) and the LLM (🤖).

Allows user to input queries about movies and displays responses dynamically.

Handles API calls to the Node.js middleware via fetch.

Node.js Middleware

Acts as a bridge between the React frontend and the Python FastAPI backend.

Receives the user query from React, formats it, and forwards it to the Python backend (/ask_llm).

Returns the LLM’s response back to the frontend.

Handles CORS and JSON payloads.

Python Backend (FastAPI)

Implements RAG (Retrieval-Augmented Generation):

Loads precomputed embeddings (movie_embeddings.npy) and corresponding movie text data (movie_texts.pkl).

Uses Sentence Transformers to encode incoming user queries.

Performs cosine similarity search to retrieve relevant movie descriptions.

Generates query variations to improve retrieval coverage.

Passes the retrieved context + user query to ChatOllama LLM for answer generation.

Returns the LLM’s response as JSON to the Node.js middleware.

Supports multiple user queries and is intended to handle follow-up questions (though this is still being worked on to preserve conversation context).

CORS enabled so Node.js or frontend can call it.

Data

Embeddings: Precomputed embeddings of movie texts for semantic search.

Movie Texts: The actual movie descriptions or metadata stored in a pickled file.

Optional: Multi-query variations to improve retrieval.

Technical Goals / Challenges

RAG-based movie assistant

Retrieve top-K similar movies for a user query.

Answer follow-up questions using LLM based on previously retrieved context.

Conversation persistence

Maintain chat history in React and pass context to the backend so LLM can respond intelligently.

Proper integration between layers

Node.js must correctly forward requests to Python backend and return JSON responses.

FastAPI must correctly parse JSON from Node.js and pass it to the LLM.

React must update state properly to reflect both user and LLM responses.

Git and project structure management

Future goals / enhancements

Make follow-up responses aware of previous conversation context.

Display pointers / icons (LLM vs user) properly in the frontend chat.

Possibly refine RAG retrieval with multi-query variations or more advanced output parsing.

High-Level Workflow

User types a query in React frontend.

React calls Node.js middleware (/api/ask_llm) with { question: "..." }.

Node.js forwards this to FastAPI backend (/ask_llm) as JSON.

FastAPI:

Generates query variations.

Retrieves top-K similar movie descriptions using embeddings.

Combines context and sends prompt to LLM (ChatOllama).

Returns LLM response as JSON.

Node.js returns LLM response to React.

React updates llmresponse state to show conversation in the chat UI.
