"""
STEP 3: Nuclear Option - Minimal RAG Endpoint
Bypasses all existing code, uses direct Qdrant + OpenRouter

Add to app/main.py:
  from chat_debug_endpoint import debug_router
  app.include_router(debug_router)

Then test: POST http://localhost:8000/debug/chat {"message": "What is ROS 2?"}
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import requests

debug_router = APIRouter(prefix="/debug", tags=["debug"])

class DebugChatRequest(BaseModel):
    message: str

@debug_router.post("/chat")
async def debug_chat(request: DebugChatRequest):
    """
    Minimal RAG endpoint that bypasses all existing code.
    Returns detailed debug info + actual response.
    """
    debug_info = {
        "query": request.message,
        "steps": []
    }

    try:
        # Step 1: Connect to Qdrant
        debug_info["steps"].append("Connecting to Qdrant...")

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_key = os.getenv("QDRANT_API_KEY")
        collection = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

        if not qdrant_url or not qdrant_key:
            raise ValueError("Missing QDRANT_URL or QDRANT_API_KEY in .env")

        qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        debug_info["qdrant_connected"] = True
        debug_info["collection"] = collection

        # Step 2: Load embedding model
        debug_info["steps"].append("Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        debug_info["embedding_model"] = "all-MiniLM-L6-v2"

        # Step 3: Generate query embedding
        debug_info["steps"].append("Generating query embedding...")
        query_embedding = model.encode(request.message).tolist()
        debug_info["embedding_dims"] = len(query_embedding)
        debug_info["embedding_sample"] = query_embedding[:3]

        # Step 4: Search Qdrant with VERY LOW threshold
        debug_info["steps"].append("Searching Qdrant (threshold=0.3)...")

        results = qdrant.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=3,
            score_threshold=0.3
        )

        debug_info["results_count"] = len(results)
        debug_info["results"] = []

        if not results:
            debug_info["error"] = "NO RESULTS from Qdrant even with threshold=0.3"
            debug_info["recommendation"] = "Check: 1) Collection has vectors, 2) Embedding model matches ingestion, 3) Query is reasonable"
            return {
                "answer": "I couldn't find relevant information (DEBUG: Qdrant returned 0 results)",
                "debug": debug_info
            }

        # Format results
        context_parts = []
        for i, result in enumerate(results):
            debug_info["results"].append({
                "score": round(result.score, 3),
                "chapter": result.payload.get("chapter_path", "N/A"),
                "section": result.payload.get("section_title", "N/A"),
                "text_preview": result.payload.get("text_content", "")[:100]
            })

            context_parts.append(
                f"[Source {i+1}] {result.payload.get('section_title', 'Unknown')}\n"
                f"{result.payload.get('text_content', '')}\n"
            )

        context = "\n".join(context_parts)
        debug_info["context_length"] = len(context)

        # Step 5: Generate response with OpenRouter
        debug_info["steps"].append("Generating response with OpenRouter LLM...")

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError("Missing OPENROUTER_API_KEY in .env")

        prompt = f"""You are a helpful assistant answering questions about a Physical AI and Robotics textbook.

Context from textbook:
{context}

User question: {request.message}

Provide a clear, accurate answer based on the context above. If the context doesn't contain enough information, say so."""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        if response.status_code != 200:
            debug_info["llm_error"] = f"OpenRouter returned {response.status_code}: {response.text}"
            return {
                "answer": "Error calling LLM",
                "debug": debug_info
            }

        llm_response = response.json()
        answer = llm_response["choices"][0]["message"]["content"]

        debug_info["llm_model"] = llm_response.get("model", "unknown")
        debug_info["steps"].append("✅ Response generated")

        return {
            "answer": answer,
            "debug": debug_info
        }

    except Exception as e:
        import traceback
        debug_info["exception"] = str(e)
        debug_info["traceback"] = traceback.format_exc()

        return {
            "answer": f"Error: {e}",
            "debug": debug_info
        }

# To use: Add to app/main.py after other includes:
#   from chat_debug_endpoint import debug_router
#   app.include_router(debug_router)
#
# Then test:
#   curl -X POST "http://localhost:8000/debug/chat" \
#     -H "Content-Type: application/json" \
#     -d '{"message": "What is ROS 2?"}'
