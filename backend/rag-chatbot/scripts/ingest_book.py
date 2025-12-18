"""
Textbook ingestion script with local embeddings.
Chunks markdown files and uploads to Qdrant with sentence-transformers embeddings.
Completely free, unlimited, no API key needed.

Usage:
    python scripts/ingest_book.py
"""
import os
import sys
import uuid
from pathlib import Path
from typing import List, Dict
import re

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL", "https://9927c3c7-270d-4bf1-8fe6-0c2ceb37ac38.us-east4-0.gcp.cloud.qdrant.io:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

# Ingestion configuration
# Path to docs directory - corrected to go up from backend/rag-chatbot/scripts/
# __file__ = backend/rag-chatbot/scripts/ingest_book.py
# parent = backend/rag-chatbot/scripts/
# parent.parent = backend/rag-chatbot/
# parent.parent.parent = backend/
# parent.parent.parent.parent = project root
# project root / frontend / docs = correct path
DOCS_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "docs"
CHUNK_SIZE = 800  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
BATCH_SIZE = 32  # Embeddings per batch


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Characters of overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending (., !, ?)
            last_period = text[start:end].rfind('.')
            last_exclaim = text[start:end].rfind('!')
            last_question = text[start:end].rfind('?')
            last_newline = text[start:end].rfind('\n\n')

            boundary = max(last_period, last_exclaim, last_question, last_newline)
            if boundary > chunk_size // 2:  # Only if not too early
                end = start + boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def extract_metadata(file_path: Path, docs_dir: Path) -> Dict[str, str]:
    """
    Extract metadata from markdown file.

    Args:
        file_path: Path to markdown file
        docs_dir: Root docs directory

    Returns:
        Dictionary with chapter, section, url
    """
    # Get relative path from docs directory
    rel_path = file_path.relative_to(docs_dir)

    # Parse chapter from path (e.g., "module-1-intro/1-1-overview.md")
    parts = rel_path.parts

    if len(parts) >= 2:
        chapter = parts[0].replace("-", " ").title()
        section_file = parts[-1].stem.replace("-", " ").title()
    else:
        chapter = "Introduction"
        section_file = file_path.stem.replace("-", " ").title()

    # Extract section title from first heading in file
    section_title = section_file
    try:
        content = file_path.read_text(encoding="utf-8")
        # Find first # heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            section_title = match.group(1).strip()
    except:
        pass

    # Build URL path (remove .md, convert to lowercase with dashes)
    url_parts = [part.lower().replace(" ", "-") for part in rel_path.parts]
    url_parts[-1] = url_parts[-1].replace(".md", "")
    url_path = "/docs/" + "/".join(url_parts)

    return {
        "chapter_path": chapter,
        "section_title": section_title,
        "url_path": url_path,
    }


def ingest_documents():
    """Main ingestion function."""
    print("=" * 70)
    print("📚 TEXTBOOK INGESTION SCRIPT")
    print("=" * 70)
    print(f"\nDocs directory (resolved): {DOCS_DIR.resolve()}")
    print(f"Docs directory exists: {DOCS_DIR.exists()}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")
    print(f"Batch size: {BATCH_SIZE} embeddings/batch")
    print(f"Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)")
    print(f"Status: 100% FREE - No API key needed!\n")

    # Check if docs directory exists
    if not DOCS_DIR.exists():
        print(f"✗ Error: Docs directory not found: {DOCS_DIR.resolve()}")
        print(f"✗ Please ensure the frontend/docs directory exists at the project root")
        return

    # Load local embedding model
    print("Loading sentence-transformers model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"✓ Model loaded (embedding dimension: {model.get_sentence_embedding_dimension()})\n")

    # Initialize Qdrant client
    print("Connecting to Qdrant...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("✓ Connected to Qdrant\n")

    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files\n")

    if len(md_files) == 0:
        print("✗ No markdown files found!")
        return

    # Process files
    all_points = []
    total_chunks = 0

    for idx, file_path in enumerate(md_files, 1):
        print(f"[{idx}/{len(md_files)}] Processing: {file_path.name}")

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Skip empty files
            if not content.strip():
                print(f"  ⚠ Skipping empty file")
                continue

            # Extract metadata
            metadata = extract_metadata(file_path, DOCS_DIR)

            # Chunk the content
            chunks = chunk_text(content)
            print(f"  Created {len(chunks)} chunks")

            # Create points for each chunk
            for chunk_idx, chunk_text in enumerate(chunks):
                point_id = str(uuid.uuid4())

                point = {
                    "id": point_id,
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                        "file_path": str(file_path.relative_to(DOCS_DIR)),
                    }
                }
                all_points.append(point)

            total_chunks += len(chunks)

        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            continue

    print(f"\n{'=' * 70}")
    print(f"Total chunks created: {total_chunks}")
    print(f"{'=' * 70}\n")

    # Generate embeddings and upload in batches
    print("Generating embeddings and uploading to Qdrant...\n")

    for batch_start in range(0, len(all_points), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(all_points))
        batch_points = all_points[batch_start:batch_end]

        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(all_points) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"Batch {batch_num}/{total_batches} ({len(batch_points)} chunks)...")

        try:
            # Extract texts for embedding
            texts = [p["text"] for p in batch_points]

            # Generate embeddings (local, no API call!)
            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2 normalization for cosine similarity
                show_progress_bar=False,
            )

            # Create Qdrant points
            qdrant_points = []
            for point, embedding in zip(batch_points, embeddings):
                qdrant_point = PointStruct(
                    id=point["id"],
                    vector=embedding.tolist(),
                    payload={
                        "text_content": point["text"],
                        "chapter_path": point["metadata"]["chapter_path"],
                        "section_title": point["metadata"]["section_title"],
                        "url_path": point["metadata"]["url_path"],
                        "chunk_index": point["metadata"]["chunk_index"],
                        "total_chunks": point["metadata"]["total_chunks"],
                        "file_path": point["metadata"]["file_path"],
                    }
                )
                qdrant_points.append(qdrant_point)

            # Upload to Qdrant
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=qdrant_points
            )

            print(f"  ✓ Uploaded batch {batch_num}/{total_batches}")

        except Exception as e:
            print(f"  ✗ Error processing batch {batch_num}: {e}")
            continue

    # Verify upload
    print(f"\n{'=' * 70}")
    print("Verifying upload...")
    info = client.get_collection(COLLECTION_NAME)
    points_count = info.points_count
    print(f"✓ Collection contains {points_count} points")

    if points_count == total_chunks:
        print(f"✓ SUCCESS: All {total_chunks} chunks uploaded successfully!")
    else:
        print(f"⚠ Warning: Expected {total_chunks} points, found {points_count}")

    print(f"{'=' * 70}\n")

    print("✅ Ingestion complete!\n")
    print("Next steps:")
    print("  1. Start backend: uvicorn app.main:app --reload")
    print("  2. Test with: 'What is a ROS 2 node?'")
    print("  3. Verify citations appear correctly\n")


if __name__ == "__main__":
    try:
        ingest_documents()
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        raise
