#!/usr/bin/env bash
set -euo pipefail

API_KEY="${1:?Usage: integration.sh <api_key>}"
BASE_URL="http://localhost:8000/api"
SERVER_ID=1

pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; exit 1; }

# ---------------------------------------------------------------------------
# Wait for the API to be reachable and Ice-connected
# ---------------------------------------------------------------------------
echo "Waiting for mumble-rest..."
for i in $(seq 1 30); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "key: $API_KEY" "$BASE_URL/health-check" || true)
    if [ "$STATUS" = "200" ]; then
        echo "  Ready after $i attempt(s)"
        break
    fi
    if [ "$i" = "30" ]; then
        fail "Service did not become ready (last status: $STATUS)"
    fi
    sleep 3
done

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
echo
echo "[ health-check ]"
BODY=$(curl -sf -H "key: $API_KEY" "$BASE_URL/health-check")
echo "$BODY" | grep -q '"status":"OK"' || fail "unexpected body: $BODY"
pass "status OK"

# ---------------------------------------------------------------------------
# User count
# ---------------------------------------------------------------------------
echo
echo "[ user_count ]"
curl -sf -H "key: $API_KEY" "$BASE_URL/user_count?server_id=$SERVER_ID" > /dev/null
pass "responded"

# ---------------------------------------------------------------------------
# Register a user
# ---------------------------------------------------------------------------
echo
echo "[ register user ]"
BODY=$(curl -sf -X POST -H "key: $API_KEY" \
    -d "user_name=ci_test_user&user_pass=ci_test_pass_123" \
    "$BASE_URL/auth/user?server_id=$SERVER_ID")
echo "$BODY" | grep -q '"password_test":"Success"' || fail "unexpected body: $BODY"
USER_ID=$(echo "$BODY" | sed 's/.*"user_id":\([0-9]*\).*/\1/')
pass "registered user_id=$USER_ID"

# ---------------------------------------------------------------------------
# Channel export
# ---------------------------------------------------------------------------
echo
echo "[ channel export ]"
CHANNELS=$(curl -sf -H "key: $API_KEY" "$BASE_URL/servers/$SERVER_ID/channels/export")
echo "$CHANNELS" | grep -q '"channels"' || fail "unexpected body: $CHANNELS"
pass "exported"

# ---------------------------------------------------------------------------
# Channel import round-trip
# ---------------------------------------------------------------------------
echo
echo "[ channel import ]"
IMPORT_BODY=$(echo "$CHANNELS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps({'channels': data['channels']}))
")
RESULT=$(curl -sf -X POST -H "key: $API_KEY" -H "Content-Type: application/json" \
    -d "$IMPORT_BODY" \
    "$BASE_URL/servers/$SERVER_ID/channels/import")
echo "$RESULT" | grep -q '"channels_created"' || fail "unexpected body: $RESULT"
pass "imported"

# ---------------------------------------------------------------------------
# Delete test user
# ---------------------------------------------------------------------------
echo
echo "[ delete user ]"
curl -sf -X DELETE -H "key: $API_KEY" \
    "$BASE_URL/auth/users/delete?server_id=$SERVER_ID&user_id=$USER_ID" > /dev/null
pass "deleted user_id=$USER_ID"

echo
echo "All tests passed."
