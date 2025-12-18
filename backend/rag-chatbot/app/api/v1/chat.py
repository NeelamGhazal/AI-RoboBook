"""
Chat endpoints for RAG-based Q&A.
Implements general Q&A and selected-text Q&A with streaming support.
"""
import json
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.db import crud
from app.models.schemas import ChatRequest, ChatResponse, MessageResponse
from app.services.rag import execute_rag_pipeline, execute_rag_pipeline_stream
from app.utils.logging import get_logger

# Import in-memory session store from sessions module
from app.api.v1.sessions import _in_memory_sessions

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.get("/health")
async def chat_health():
    """
    Chat router health check.

    Returns:
        Confirmation that chat endpoints are accessible
    """
    return {
        "status": "healthy",
        "message": "Chat router is loaded and accessible",
        "endpoints": {
            "stream": "/api/v1/chat/stream",
            "chat": "/api/v1/chat",
            "history": "/api/v1/chat/history/{session_id}"
        }
    }


async def validate_session(session_id: str) -> bool:
    """
    Validate session exists in database or in-memory store.

    Args:
        session_id: Session UUID to validate

    Returns:
        True if session exists, False otherwise
    """
    # Check database first
    try:
        session = await crud.get_session(session_id)
        if session:
            print(f"[Backend] ✓ Session validated in database: {session_id}")
            return True
    except Exception as db_error:
        print(f"[Backend] ⚠ Database session lookup failed: {type(db_error).__name__}")

    # Check in-memory store
    if session_id in _in_memory_sessions:
        print(f"[Backend] ✓ Session validated in memory: {session_id}")
        return True

    print(f"[Backend] ✗ Session not found: {session_id}")
    return False


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Generate response to user question using RAG pipeline (non-streaming).

    Args:
        request: Chat request with session_id, question, optional selected_text

    Returns:
        Response with answer, citations, and metadata
    """
    print(f"[Backend] POST /api/v1/chat called")
    print(f"[Backend] Payload received: session_id={request.session_id}, question_length={len(request.question)}")

    try:
        # Validate session exists (check both database and in-memory)
        session_exists = await validate_session(request.session_id)
        if not session_exists:
            print(f"[Backend] ✗ Session validation failed: {request.session_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Session {request.session_id} not found"
            )

        # Load conversation history
        messages, _ = await crud.get_messages_by_session(
            request.session_id,
            limit=12
        )

        logger.info(
            "chat_request",
            session_id=request.session_id,
            question_length=len(request.question),
            has_selected_text=request.selected_text is not None,
            history_count=len(messages),
        )

        # Execute RAG pipeline
        response_text, citations, metadata = await execute_rag_pipeline(
            question=request.question,
            conversation_history=messages,
            selected_text=request.selected_text,
            top_k=8,
            stream=False,
        )

        # Save user message
        await crud.create_message(
            session_id=request.session_id,
            role="user",
            content=request.question,
            token_count=0,  # Will be calculated by LLM service
            citations=None,
        )

        # Save assistant response
        await crud.create_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            token_count=metadata.get("token_count", 0),
            citations=citations,
        )

        # Update session last_activity
        await crud.update_session_activity(request.session_id)

        logger.info(
            "chat_response_generated",
            session_id=request.session_id,
            response_length=len(response_text),
            citations_count=len(citations),
            total_time_ms=metadata.get("total_time_ms"),
        )

        return ChatResponse(
            answer=response_text,
            sources=citations,
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_request_failed",
            session_id=request.session_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate response. Please try again."
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
):
    """
    Generate streaming response to user question using RAG pipeline.

    Args:
        request: Chat request with session_id, question, optional selected_text

    Returns:
        Server-Sent Events stream with tokens, citations, and metadata
    """
    print(f"[Backend] POST /api/v1/chat/stream called")
    print(f"[Backend] Payload received: session_id={request.session_id}, question_length={len(request.question)}, has_selected_text={request.selected_text is not None}")

    try:
        # Validate session exists (check both database and in-memory)
        session_exists = await validate_session(request.session_id)
        if not session_exists:
            print(f"[Backend] ⚠ Session validation failed: {request.session_id} - proceeding anyway")
            print(f"[Backend] This may happen after backend restart. Frontend will auto-recover.")
            # DON'T raise 404 - frontend will detect this and recreate session
            # Just proceed with empty conversation history
        else:
            print(f"[Backend] ✓ Session ID: {request.session_id} - validated")

        # Load conversation history (may fail if database unavailable)
        messages = []
        try:
            print("[Backend] Loading conversation history from database...")
            messages, _ = await crud.get_messages_by_session(
                request.session_id,
                limit=12
            )
            print(f"[Backend] ✓ Loaded {len(messages)} messages from history")
        except Exception as history_error:
            print(f"[Backend] ⚠ Failed to load history: {type(history_error).__name__} - continuing with empty history")
            logger.warning(
                "history_load_failed",
                session_id=request.session_id,
                error=str(history_error),
            )

        logger.info(
            "streaming_chat_request",
            session_id=request.session_id,
            question_length=len(request.question),
            has_selected_text=request.selected_text is not None,
            history_count=len(messages),
        )

        # Try to save user message (may fail if database unavailable)
        try:
            print("[Backend] Saving user message to database...")
            await crud.create_message(
                session_id=request.session_id,
                role="user",
                content=request.question,
                token_count=0,
                citations=None,
            )
            print("[Backend] ✓ User message saved")
        except Exception as save_error:
            print(f"[Backend] ⚠ Failed to save user message: {type(save_error).__name__} - continuing anyway")
            logger.warning(
                "user_message_save_failed",
                session_id=request.session_id,
                error=str(save_error),
            )

        # Stream response generator
        async def event_stream():
            full_response = ""
            citations = []
            metadata = {}

            try:
                print("[Backend] Starting RAG pipeline stream...")

                async for event in execute_rag_pipeline_stream(
                    question=request.question,
                    conversation_history=messages,
                    selected_text=request.selected_text,
                    top_k=8,
                ):
                    # Accumulate full response
                    if event["type"] == "token":
                        full_response += event["content"]
                    elif event["type"] == "citations":
                        citations = event["citations"]
                        print(f"[Backend] ✓ Citations received: {len(citations)} sources")
                    elif event["type"] == "metadata":
                        metadata = event["metadata"]

                    # Send event to client
                    yield f"data: {json.dumps(event)}\n\n"

                print(f"[Backend] ✓ Stream complete - response length: {len(full_response)}")

                # Try to save assistant response
                try:
                    await crud.create_message(
                        session_id=request.session_id,
                        role="assistant",
                        content=full_response,
                        token_count=len(full_response.split()),
                        citations=citations,
                    )
                    print("[Backend] ✓ Assistant response saved to database")
                except Exception as save_error:
                    print(f"[Backend] ⚠ Failed to save assistant response: {type(save_error).__name__}")
                    logger.warning(
                        "assistant_message_save_failed",
                        session_id=request.session_id,
                        error=str(save_error),
                    )

                # Try to update session activity
                try:
                    await crud.update_session_activity(request.session_id)
                except Exception as update_error:
                    print(f"[Backend] ⚠ Failed to update session activity: {type(update_error).__name__}")

                logger.info(
                    "streaming_chat_complete",
                    session_id=request.session_id,
                    response_length=len(full_response),
                    citations_count=len(citations),
                )

            except Exception as e:
                print(f"[Backend] ✗ Stream error: {type(e).__name__}: {str(e)}")
                logger.error(
                    "streaming_chat_failed",
                    session_id=request.session_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )

                # Fallback response - simple echo
                fallback_message = f"I received your message: '{request.question}'. However, I'm having trouble processing it right now. The RAG pipeline is temporarily unavailable."

                # Send fallback as tokens
                for word in fallback_message.split():
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

                # Send empty citations
                yield f"data: {json.dumps({'type': 'citations', 'citations': []})}\n\n"

                # Send done marker
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

                print(f"[Backend] Sent fallback response to client")

        print("[Backend] Returning streaming response...")
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Backend] ✗ Critical streaming setup error: {type(e).__name__}: {str(e)}")
        logger.error(
            "streaming_setup_failed",
            session_id=request.session_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize streaming response: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=List[MessageResponse])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
) -> List[MessageResponse]:
    """
    Get conversation history for a session.

    Args:
        session_id: Session UUID
        limit: Maximum number of messages to return (default 50)
        db: Database session

    Returns:
        List of messages with role, content, sources, and timestamp
    """
    try:
        # Validate session exists
        session = await crud.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        # Get messages
        messages, total = await crud.get_messages_by_session(
            session_id,
            limit=limit
        )

        # Convert to response format
        response = [
            MessageResponse(
                role=msg.role,
                content=msg.content,
                sources=msg.citations,  # Note: CRUD uses 'citations' field
                created_at=msg.timestamp,  # Note: CRUD uses 'timestamp' field
            )
            for msg in messages
        ]

        logger.info(
            "history_retrieved",
            session_id=session_id,
            message_count=len(response),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "history_retrieval_failed",
            session_id=session_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )
