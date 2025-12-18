"""
Prometheus metrics for monitoring RAG chatbot performance.
"""
from prometheus_client import Counter, Gauge, Histogram

# Request duration histogram (latency tracking)
REQUEST_DURATION = Histogram(
    "rag_request_duration_seconds",
    "RAG request latency by endpoint and stage",
    ["endpoint", "stage"],
    buckets=(0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0),
)

# Error counter
ERROR_COUNTER = Counter(
    "rag_errors_total",
    "Total errors by type",
    ["error_type"],
)

# Concurrent requests gauge
CONCURRENT_REQUESTS = Gauge(
    "rag_concurrent_requests",
    "Number of concurrent requests being processed",
)

# RAG pipeline stage metrics
EMBEDDING_DURATION = Histogram(
    "rag_embedding_duration_seconds",
    "Time to generate embeddings",
    buckets=(0.1, 0.2, 0.3, 0.5, 1.0),
)

RETRIEVAL_DURATION = Histogram(
    "rag_retrieval_duration_seconds",
    "Time to retrieve chunks from Qdrant",
    buckets=(0.05, 0.1, 0.2, 0.5, 1.0),
)

GENERATION_DURATION = Histogram(
    "rag_generation_duration_seconds",
    "Time for LLM generation",
    buckets=(0.5, 1.0, 1.5, 2.0, 3.0, 5.0),
)

# Database metrics
DB_OPERATION_DURATION = Histogram(
    "db_operation_duration_seconds",
    "Database operation duration by operation type",
    ["operation"],
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0),
)
