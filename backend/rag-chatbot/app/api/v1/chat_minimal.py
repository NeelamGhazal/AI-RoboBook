"""
Minimal streaming chat endpoint - guaranteed to work.
This is a standalone test endpoint to verify streaming works.
"""
import json
import asyncio
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

# Create router WITHOUT prefix (will add in main.py)
router = APIRouter()


@router.post("/stream")
async def stream_chat_minimal(request: Request):
    """
    Minimal streaming endpoint that always works.

    Frontend calls: POST /api/v1/chat/stream
    Router registered with prefix: /api/v1/chat
    Route path: /stream
    Final path: /api/v1/chat + /stream = /api/v1/chat/stream
    """
    print("\n" + "="*50)
    print("[Backend] ✓✓✓ POST /stream endpoint called!")
    print("="*50)

    try:
        # Parse request body
        body = await request.json()
        session_id = body.get("session_id", "unknown")
        question = body.get("question", body.get("message", ""))
        selected_text = body.get("selected_text", None)

        print(f"[Backend] Session ID: {session_id}")
        print(f"[Backend] Question: {question}")

        if selected_text:
            print(f"[Backend] ✓ Context-aware mode (selected text provided)")
            print(f"[Backend] Selected text length: {len(selected_text)} chars")
            print(f"[Backend] Selected text preview: {selected_text[:100]}...")
        else:
            print(f"[Backend] ℹ️ General query mode (no selected text)")

        async def generate():
            """Generate SSE stream with progressive tokens"""
            print("[Backend] Starting token generation...")

            # Build context-aware or general response
            if selected_text:
                # Context-aware response using selected text
                print("[Backend] Generating context-aware response...")

                response_parts = [
                    "Based on the text you selected:\n\n",
                    f"--- Selected Text ---\n{selected_text}\n--- End ---\n\n",
                    f"You asked: \"{question}\"\n\n",
                    "Let me explain this section for you:\n\n",
                    "This text discusses important concepts related to your question. ",
                    f"The selected passage (approximately {len(selected_text)} characters) contains key information. ",
                    "\n\nHere's a detailed explanation:\n",
                    "[In production, the RAG pipeline would analyze the selected text and provide a context-specific answer based on the broader document context.]\n\n",
                    "The selected text is particularly relevant because it appears in a section covering these topics. ",
                    "Would you like me to explain any specific part in more detail, or discuss how this relates to other sections?\n\n",
                    "💡 Tip: You can select any text in the documentation and ask specific questions about it for targeted explanations!"
                ]
            else:
                # General response without selected text
                print("[Backend] Generating general response...")

                response_parts = [
                    "Hello! ",
                    f"You asked: \"{question}\"\n\n",
                    "This is a general query response. ",
                    "I'm ready to help you understand the Physical AI & Humanoid Robotics textbook!\n\n",
                    "[In production, the RAG pipeline would search the entire document and provide relevant information based on your question.]\n\n",
                    "💡 Pro tip: For more specific answers, try selecting text from the documentation and clicking 'Ask about this'. ",
                    "This enables context-aware responses tailored to the exact section you're reading!\n\n",
                    "Feel free to ask any questions about ROS 2, simulation, hardware, or any other topics covered in the book."
                ]

            # Stream response parts as tokens
            for i, part in enumerate(response_parts):
                token_event = {
                    "type": "token",
                    "content": part
                }
                yield f'data: {json.dumps(token_event)}\n\n'
                await asyncio.sleep(0.05)  # Faster streaming

                if i % 3 == 0:
                    print(f"[Backend] Sent {i+1}/{len(response_parts)} chunks")

            # Send citations (include selected text reference if applicable)
            citations = []
            if selected_text:
                citations.append({
                    "source": "Selected Text Context",
                    "page": 0,
                    "text": selected_text[:200] + ("..." if len(selected_text) > 200 else ""),
                    "confidence_score": 0.95
                })
                citations.append({
                    "source": "Textbook Context",
                    "page": 1,
                    "text": "Additional context from the broader document...",
                    "confidence_score": 0.85
                })
            else:
                citations.append({
                    "source": "General Knowledge Base",
                    "page": 1,
                    "text": "Information retrieved from the textbook index...",
                    "confidence_score": 0.75
                })

            citations_event = {
                "type": "citations",
                "citations": citations
            }
            yield f'data: {json.dumps(citations_event)}\n\n'
            print(f"[Backend] Sent {len(citations)} citations")

            # Send done signal
            done_event = {"type": "done"}
            yield f'data: {json.dumps(done_event)}\n\n'

            print("[Backend] ✓ Stream completed successfully!")
            if selected_text:
                print(f"[Backend] Context-aware response delivered for {len(selected_text)} char selection")
            print("="*50 + "\n")

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        print(f"[Backend] ✗ Stream error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Stream error: {str(e)}")


@router.get("/health")
async def health_minimal():
    """Health check for minimal chat router"""
    return {
        "status": "healthy",
        "message": "Minimal chat router loaded",
        "endpoint": "/api/v1/chat/stream"
    }


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify router is working"""
    return {
        "message": "Router is working!",
        "endpoints": {
            "stream": "POST /api/v1/chat/stream",
            "health": "GET /api/v1/chat/health",
            "test": "GET /api/v1/chat/test"
        }
    }
