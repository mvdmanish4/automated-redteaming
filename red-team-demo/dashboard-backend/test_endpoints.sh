#!/bin/bash
# Test script for Dashboard Backend API endpoints

BASE_URL="${1:-http://localhost:5001}"

echo "Testing Dashboard Backend API at $BASE_URL"
echo "=========================================="
echo ""

echo "1. Testing Health Endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

echo "2. Testing Exploit Test Endpoint..."
curl -s "$BASE_URL/api/exploit/test" | python3 -m json.tool | head -100
echo ""
echo ""

echo "3. Testing CVEs Endpoint..."
curl -s "$BASE_URL/api/cves" | python3 -m json.tool | head -150
echo ""
echo ""

echo "4. Testing Get Exploit Script..."
curl -s "$BASE_URL/api/exploit/script?type=exploit" | python3 -m json.tool | head -50
echo ""
echo ""

echo "5. Testing Execute Exploit (read_file)..."
curl -s -X POST "$BASE_URL/api/exploit/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "read_file",
    "target_url": "https://vulnerable-ecommerce-6pgqjb4bma-uc.a.run.app",
    "file_path": "productdata.txt",
    "asset_name": "api-server"
  }' | python3 -m json.tool | head -100
echo ""
echo ""

echo "All tests completed!"
