#!/bin/bash

# ===== Test Hugging Face Spaces Docker Deployment Locally =====
# This script builds and runs the HF Spaces Docker image locally
# to verify it works before pushing to HF Spaces

set -e  # Exit on error

echo "=================================================="
echo "🧪 Testing HF Spaces Docker Deployment Locally"
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required environment variables"
    echo "See .env.hf-example for reference"
    exit 1
fi

echo "✓ Found .env file"
echo ""

# Build Docker image
echo "📦 Building Docker image (this may take 5-10 minutes)..."
docker build -f Dockerfile.hf -t rag-chatbot-hf-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✓ Docker build successful"
echo ""

# Stop any existing container
echo "🧹 Cleaning up existing containers..."
docker stop rag-chatbot-hf-test-container 2>/dev/null || true
docker rm rag-chatbot-hf-test-container 2>/dev/null || true
echo ""

# Run container
echo "🚀 Starting container on port 7860..."
docker run -d \
    --name rag-chatbot-hf-test-container \
    -p 7860:7860 \
    --env-file .env \
    rag-chatbot-hf-test

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi

echo "✓ Container started"
echo ""

# Wait for application to start
echo "⏳ Waiting for application to start (30 seconds)..."
sleep 30
echo ""

# Test health endpoint
echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:7860/health)

if [ -z "$HEALTH_RESPONSE" ]; then
    echo "❌ Health endpoint not responding"
    echo "Container logs:"
    docker logs rag-chatbot-hf-test-container
    exit 1
fi

echo "✓ Health endpoint response:"
echo "$HEALTH_RESPONSE" | python3 -m json.tool
echo ""

# Check if status is healthy
STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

if [ "$STATUS" = "healthy" ]; then
    echo "✅ All systems healthy!"
else
    echo "⚠️  Status: $STATUS (some dependencies may be down)"
fi
echo ""

# Test API docs
echo "📚 Testing API documentation endpoint..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7860/docs)

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo "✓ API docs accessible at http://localhost:7860/docs"
else
    echo "❌ API docs not accessible (HTTP $DOCS_RESPONSE)"
fi
echo ""

# Show container logs
echo "📋 Container logs (last 20 lines):"
docker logs --tail 20 rag-chatbot-hf-test-container
echo ""

# Summary
echo "=================================================="
echo "🎉 Docker Test Complete!"
echo "=================================================="
echo ""
echo "Container is running at: http://localhost:7860"
echo "API Documentation: http://localhost:7860/docs"
echo "Health Check: http://localhost:7860/health"
echo ""
echo "To test the chat endpoint:"
echo "curl -X POST http://localhost:7860/api/v1/chat/stream \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"session_id\": \"test\", \"question\": \"What is ROS 2?\"}'"
echo ""
echo "To view logs: docker logs -f rag-chatbot-hf-test-container"
echo "To stop: docker stop rag-chatbot-hf-test-container"
echo "To cleanup: docker rm rag-chatbot-hf-test-container"
echo ""
echo "If everything works, you're ready to deploy to HF Spaces! 🚀"
echo "=================================================="
