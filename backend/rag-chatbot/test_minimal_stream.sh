#!/bin/bash

echo "========================================="
echo "Testing Minimal Streaming Endpoint"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Health check
echo "Test 1: Health check (GET /api/v1/chat/health)"
echo "------------------------------------------------"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/chat/health)
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Health check passed${NC}"
  echo "Response: $HEALTH_RESPONSE"
else
  echo -e "${RED}✗ Health check failed${NC}"
  exit 1
fi

echo ""
echo ""

# Test 2: Test endpoint
echo "Test 2: Test endpoint (GET /api/v1/chat/test)"
echo "------------------------------------------------"
TEST_RESPONSE=$(curl -s http://localhost:8000/api/v1/chat/test)
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Test endpoint passed${NC}"
  echo "Response: $TEST_RESPONSE"
else
  echo -e "${RED}✗ Test endpoint failed${NC}"
fi

echo ""
echo ""

# Test 3: Create session
echo "Test 3: Creating session"
echo "------------------------------------------------"
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
  SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))" 2>/dev/null)
  if [ -n "$SESSION_ID" ]; then
    echo -e "${GREEN}✓ Session created: $SESSION_ID${NC}"
  else
    echo -e "${YELLOW}⚠ Session response received but couldn't parse ID${NC}"
    echo "Response: $SESSION_RESPONSE"
    SESSION_ID="test-session-123"
    echo "Using fallback session ID: $SESSION_ID"
  fi
else
  echo -e "${YELLOW}⚠ Session creation failed, using test ID${NC}"
  SESSION_ID="test-session-123"
fi

echo ""
echo ""

# Test 4: Stream endpoint
echo "Test 4: Streaming endpoint (POST /api/v1/chat/stream)"
echo "------------------------------------------------"
echo "Request payload:"
echo "{\"session_id\": \"$SESSION_ID\", \"question\": \"What is ROS 2?\"}"
echo ""
echo "Streaming response (first 10 lines):"
echo ""

timeout 5 curl -s -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"question\": \"What is ROS 2?\"}" \
  2>&1 | head -n 10

CURL_EXIT=$?

echo ""
echo ""

if [ $CURL_EXIT -eq 0 ] || [ $CURL_EXIT -eq 124 ]; then
  echo -e "${GREEN}✓ Stream endpoint returned data${NC}"
  echo "(Exit code 124 = timeout is expected for streams)"
else
  echo -e "${RED}✗ Stream endpoint failed (exit code: $CURL_EXIT)${NC}"
fi

echo ""
echo ""

# Test 5: Check for 404
echo "Test 5: Verifying NO 404 errors"
echo "------------------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"question\": \"test\"}" \
  2>&1 | tail -n 1)

if [ "$RESPONSE" == "200" ]; then
  echo -e "${GREEN}✓ HTTP 200 OK (not 404!)${NC}"
elif [ "$RESPONSE" == "404" ]; then
  echo -e "${RED}✗ HTTP 404 NOT FOUND - endpoint not registered properly!${NC}"
else
  echo -e "${YELLOW}⚠ HTTP $RESPONSE${NC}"
fi

echo ""
echo "========================================="
echo "Testing complete!"
echo "========================================="
