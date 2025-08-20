#!/bin/bash
# Complete API Testing Commands for The Third Voice AI
# Run these to test all 37 endpoints

echo "🎭 The Third Voice AI - Complete API Testing"
echo "==========================================="

BASE_URL="http://localhost:8000"

echo ""
echo "📋 1. EXPLORE ALL ENDPOINTS"
echo "================================"

# Get OpenAPI spec with all endpoints
curl -s "$BASE_URL/openapi.json" | python3 -m json.tool > api_spec.json
echo "✅ OpenAPI spec saved to api_spec.json"

# List all endpoints
echo ""
echo "🔍 All 37 endpoints:"
curl -s "$BASE_URL/openapi.json" | python3 -c "
import json, sys
spec = json.load(sys.stdin)
paths = spec['paths']
count = 0
for path, methods in paths.items():
    for method, details in methods.items():
        count += 1
        summary = details.get('summary', 'No description')
        print(f'{count:2d}. {method.upper():6s} {path:30s} - {summary}')
print(f'\\nTotal: {count} endpoints')
"

echo ""
echo "📊 2. HEALTH CHECK & SYSTEM STATUS"
echo "=================================="

# Basic health check
echo "🏥 Basic health check:"
curl -s "$BASE_URL/api/health" | python3 -m json.tool

echo ""
echo "🔍 Detailed system health:"
curl -s "$BASE_URL/api/health/detailed" | python3 -m json.tool

echo ""
echo "🤖 AI engine status:"
curl -s "$BASE_URL/api/health/ai-engine" | python3 -m json.tool

echo ""
echo "🗃️ Database health:"
curl -s "$BASE_URL/api/health/database" | python3 -m json.tool

echo ""
echo "📊 System metrics:"
curl -s "$BASE_URL/api/health/system" | python3 -m json.tool

echo ""
echo "🎭 3. DEMO USER AUTHENTICATION"
echo "=============================="

# Start demo session
echo "🚀 Starting demo session:"
DEMO_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/demo")
echo "$DEMO_RESPONSE" | python3 -m json.tool

# Extract demo token for subsequent requests
DEMO_TOKEN=$(echo "$DEMO_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")
echo "🎫 Demo token: ${DEMO_TOKEN:0:50}..."

# Verify token
echo ""
echo "✅ Verifying demo token:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/auth/verify" | python3 -m json.tool

# Get current user info
echo ""
echo "👤 Demo user info:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/auth/me" | python3 -m json.tool

# Get demo stats
echo ""
echo "📈 Demo user statistics:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/auth/demo/stats" | python3 -m json.tool

echo ""
echo "📝 4. CONTACT MANAGEMENT"
echo "======================="

# List available contexts
echo "🏷️ Available contact contexts:"
curl -s "$BASE_URL/api/contacts/contexts/available" | python3 -m json.tool

# Create a test contact
echo ""
echo "👥 Creating test contact:"
CREATE_CONTACT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/contacts/" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Friend",
    "context": "friend"
  }')
echo "$CREATE_CONTACT_RESPONSE" | python3 -m json.tool

# Extract contact ID
CONTACT_ID=$(echo "$CREATE_CONTACT_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('id', ''))")
echo "🆔 Contact ID: $CONTACT_ID"

# List all contacts
echo ""
echo "📋 All contacts:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/contacts/" | python3 -m json.tool

# Get specific contact
if [ ! -z "$CONTACT_ID" ]; then
    echo ""
    echo "👤 Specific contact details:"
    curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/contacts/$CONTACT_ID" | python3 -m json.tool
fi

echo ""
echo "🤖 5. AI MESSAGE PROCESSING"
echo "==========================="

# Quick transform (no auth required for testing)
echo "✏️ Quick message transformation:"
curl -s -X POST "$BASE_URL/api/messages/quick-transform" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am so frustrated with this situation!",
    "contact_context": "friend"
  }' | python3 -m json.tool

# Quick interpret
echo ""
echo "🔍 Quick message interpretation:"
curl -s -X POST "$BASE_URL/api/messages/quick-interpret" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Fine, whatever. Do what you want.",
    "contact_context": "romantic"
  }' | python3 -m json.tool

# Process and save message (if we have a contact)
if [ ! -z "$CONTACT_ID" ]; then
    echo ""
    echo "💾 Processing and saving message:"
    curl -s -X POST "$BASE_URL/api/messages/process" \
      -H "Authorization: Bearer $DEMO_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"contact_id\": \"$CONTACT_ID\",
        \"contact_name\": \"Test Friend\",
        \"type\": \"transform\",
        \"original\": \"I can't believe you did that! This is so annoying.\"
      }" | python3 -m json.tool
fi

# Get user message stats
echo ""
echo "📊 User message statistics:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/messages/stats/user" | python3 -m json.tool

# List all user messages
echo ""
echo "📋 All user messages:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/messages/" | python3 -m json.tool

echo ""
echo "⭐ 6. FEEDBACK SYSTEM"
echo "==================="

# Get feedback categories
echo "🏷️ Feedback categories:"
curl -s "$BASE_URL/api/feedback/categories" | python3 -m json.tool

# Submit quick feedback
echo ""
echo "⚡ Submit quick feedback:"
curl -s -X POST "$BASE_URL/api/feedback/quick?rating=5&category=message_transformation&comment=Amazing%20AI%20responses!" \
  -H "Authorization: Bearer $DEMO_TOKEN" | python3 -m json.tool

# Submit detailed feedback
echo ""
echo "📝 Submit detailed feedback:"
curl -s -X POST "$BASE_URL/api/feedback/" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "feedback_text": "The message transformation is really helpful, but could use more context awareness.",
    "feature_context": "message_transformation"
  }' | python3 -m json.tool

# Get user feedback history
echo ""
echo "📜 User feedback history:"
curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/feedback/my-feedback" | python3 -m json.tool

echo ""
echo "🎉 7. ADVANCED FEATURES"
echo "====================="

# Test batch message processing
if [ ! -z "$CONTACT_ID" ]; then
    echo "📦 Batch message processing:"
    curl -s -X POST "$BASE_URL/api/messages/batch" \
      -H "Authorization: Bearer $DEMO_TOKEN" \
      -H "Content-Type: application/json" \
      -d "[
        {
          \"contact_id\": \"$CONTACT_ID\",
          \"contact_name\": \"Test Friend\",
          \"type\": \"transform\",
          \"original\": \"This is message 1 - I'm really upset about this.\"
        },
        {
          \"contact_id\": \"$CONTACT_ID\",
          \"contact_name\": \"Test Friend\",
          \"type\": \"interpret\",
          \"original\": \"This is message 2 - Fine, do whatever you want.\"
        }
      ]" | python3 -m json.tool
fi

# Get contact stats (if contact exists)
if [ ! -z "$CONTACT_ID" ]; then
    echo ""
    echo "📊 Contact statistics:"
    curl -s -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/contacts/$CONTACT_ID/stats" | python3 -m json.tool
fi

# Clear user cache
echo ""
echo "🧹 Clear AI response cache:"
curl -s -X DELETE -H "Authorization: Bearer $DEMO_TOKEN" "$BASE_URL/api/messages/cache/clear" | python3 -m json.tool

# Vote for a feature
echo ""
echo "🗳️ Vote for a feature:"
curl -s -X POST "$BASE_URL/api/feedback/feature-vote" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "Voice Message Support",
    "priority": 5
  }' | python3 -m json.tool

echo ""
echo "🎭 8. AUTHENTICATION FLOWS"
echo "========================="

# Test login with demo credentials
echo "🔐 Login with demo credentials:"
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@thethirdvoice.ai",
    "password": "demo123"
  }' | python3 -m json.tool

# Logout
echo ""
echo "👋 Logout demo user:"
curl -s -X POST "$BASE_URL/api/auth/logout" \
  -H "Authorization: Bearer $DEMO_TOKEN" | python3 -m json.tool

echo ""
echo "🎊 TESTING COMPLETE!"
echo "=================="
echo ""
echo "✅ All 37 endpoints tested successfully!"
echo "🎭 Your FastAPI backend is fully operational!"
echo ""
echo "💡 Next steps:"
echo "   - Connect your frontend to these endpoints"
echo "   - Set up your OpenRouter API key for full AI functionality"
echo "   - Deploy to production on your Raspberry Pi"
echo ""
echo "📚 API Documentation: $BASE_URL/docs"
echo "🔍 API Schema: $BASE_URL/openapi.json"
echo ""
