#!/bin/bash

# Test script for POST /api/v1/chat/stream endpoint
# Tests both with valid session and invalid session

echo "======================================"
echo "Testing POST /api/v1/chat/stream"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Create a new session
echo "Test 1: Creating a new session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
  SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))")
  if [ -n "$SESSION_ID" ]; then
    echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"
  else
    echo -e "${RED}✗ Failed to parse session ID${NC}"
    exit 1
  fi
else
  echo -e "${RED}✗ Failed to create session${NC}"
  exit 1
fi

echo ""

# Test 2: Test streaming with valid session
echo "Test 2: Testing stream with VALID session..."
echo "Request: POST /api/v1/chat/stream"
echo "Payload: {session_id: $SESSION_ID, question: 'Hello'}"
echo ""

STREAM_OUTPUT=$(timeout 5 curl -s -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"question\": \"Hello, what is ROS 2?\"}")

if [ $? -eq 0 ] || [ $? -eq 124 ]; then
  # Exit code 124 means timeout (expected for streams)
  if echo "$STREAM_OUTPUT" | grep -q "data:"; then
    echo -e "${GREEN}✓ Stream response received (contains SSE data)${NC}"
    echo "First few lines:"
    echo "$STREAM_OUTPUT" | head -n 5
  else
    echo -e "${RED}✗ No SSE data in response${NC}"
    echo "Response: $STREAM_OUTPUT"
  fi
else
  echo -e "${RED}✗ Stream request failed${NC}"
fi

echo ""
echo ""

# Test 3: Test streaming with INVALID session
echo "Test 3: Testing stream with INVALID session (should still work)..."
FAKE_SESSION="00000000-0000-0000-0000-000000000000"
echo "Request: POST /api/v1/chat/stream"
echo "Payload: {session_id: $FAKE_SESSION, question: 'Hello'}"
echo ""

STREAM_OUTPUT_INVALID=$(timeout 5 curl -s -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$FAKE_SESSION\", \"question\": \"Hello with invalid session\"}")

if [ $? -eq 0 ] || [ $? -eq 124 ]; then
  if echo "$STREAM_OUTPUT_INVALID" | grep -q "data:"; then
    echo -e "${GREEN}✓ Stream response received even with invalid session${NC}"
    echo "First few lines:"
    echo "$STREAM_OUTPUT_INVALID" | head -n 5
  else
    echo -e "${RED}✗ No SSE data in response${NC}"
    echo "Response: $STREAM_OUTPUT_INVALID"
  fi
else
  echo -e "${RED}✗ Stream request failed${NC}"
fi

echo ""
echo ""

# Test 4: Verify route is registered
echo "Test 4: Checking FastAPI route registration..."
ROUTES=$(curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    paths = data.get('paths', {})
    stream_path = paths.get('/api/v1/chat/stream', {})
    if 'post' in stream_path:
        print('POST /api/v1/chat/stream: REGISTERED')
    else:
        print('POST /api/v1/chat/stream: NOT FOUND')
        print('Available methods:', list(stream_path.keys()))
except Exception as e:
    print(f'Error: {e}')
")

if echo "$ROUTES" | grep -q "REGISTERED"; then
  echo -e "${GREEN}✓ $ROUTES${NC}"
else
  echo -e "${RED}✗ $ROUTES${NC}"
fi

echo ""
echo "======================================"
echo "Test complete!"
echo "======================================"
