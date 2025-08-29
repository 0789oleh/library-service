#!/bin/bash

# API base URL
BASE_URL="http://localhost:8000/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to make HTTP requests and handle responses
request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    local headers="Content-Type: application/json"
    [ -n "$token" ] && headers="$headers, Authorization: Bearer $token"

    response=$(curl -s -X "$method" -H "$headers" -d "$data" "$BASE_URL/$endpoint" 2>/dev/null)
    status=$?

    if [ $status -eq 0 ]; then
        echo -e "${GREEN}Success${NC}: $response"
        echo "$response" | jq . > /dev/null 2>&1 || echo "$response"
    else
        echo -e "${RED}Error${NC}: Request failed"
    fi
    echo "-------------------"
}

# Step 1: Register an admin user
echo "Registering admin user..."
admin_data='{"name": "AdminUser", "email": "admin@example.com", "password": "adminpass", "is_admin": true}'
request "POST" "register" "$admin_data"

# Step 2: Login as admin to get token
echo "Logging in as admin..."
login_data='{"email": "admin@example.com", "password": "adminpass"}'
admin_response=$(request "POST" "login" "$login_data")
admin_token=$(echo "$admin_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f3)

# Step 3: Register a regular user
echo "Registering regular user..."
user_data='{"name": "RegularUser", "email": "user@example.com", "password": "userpass"}'
request "POST" "register" "$user_data"

# Step 4: Login as regular user to get token
echo "Logging in as regular user..."
login_data='{"email": "user@example.com", "password": "userpass"}'
user_response=$(request "POST" "login" "$login_data")
user_token=$(echo "$user_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f3)

# Step 5: Create a book as admin (should succeed)
echo "Creating book as admin..."
book_data='{"title": "1984", "author": "George Orwell", "total_copies": 5, "available_copies": 5}'
request "POST" "books" "$book_data" "$admin_token"

# Step 6: Create a book as regular user (should fail with 403)
echo "Creating book as regular user..."
request "POST" "books" "$book_data" "$user_token"

# Optional: Install jq if not present (uncomment if needed)
# if ! command -v jq &> /dev/null; then
#     echo "Installing jq..."
#     sudo apt-get update && sudo apt-get install -y jq
# fi