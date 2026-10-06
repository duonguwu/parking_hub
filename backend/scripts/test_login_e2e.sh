#!/usr/bin/env bash
# E2E login test như trình duyệt: preflight → login → cookie → /auth/me → refresh
API=${API:-https://api.parkinghub.asia}
ORIGIN="Origin: https://app.parkinghub.asia"
ENV_FILE=/root/parking_hub/backend/.env.production
U=$(grep -E '^SUPER_ADMIN_USERNAME=' $ENV_FILE | cut -d= -f2-)
P=$(grep -E '^SUPER_ADMIN_PASSWORD=' $ENV_FILE | cut -d= -f2-)
J=$(mktemp); H=$(mktemp); B=$(mktemp)

echo "== 1. preflight"
curl -s -o /dev/null -D - -X OPTIONS "$API/auth/login" -H "$ORIGIN" \
  -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type" \
  | grep -iE "^HTTP|allow-origin|allow-credentials|allow-headers"

echo "== 2. login ($U)"
curl -s -c "$J" -D "$H" -o "$B" -X POST "$API/auth/login" -H "$ORIGIN" \
  -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}"
grep -iE "^HTTP|allow-origin|allow-credentials" "$H"
grep -i "^set-cookie" "$H" | sed -E 's/=[^;]{20,};/=<token>;/'
head -c 300 "$B"; echo

echo "== 3. /auth/me with cookie"
curl -s -b "$J" -H "$ORIGIN" "$API/auth/me" | head -c 300; echo

echo "== 4. refresh"
curl -s -b "$J" -c "$J" -o /dev/null -w "%{http_code}\n" -X POST -H "$ORIGIN" "$API/auth/refresh"

echo "== 5. wrong password"
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$API/auth/login" -H "$ORIGIN" \
  -H "Content-Type: application/json" -d '{"username":"superadmin","password":"wrong"}'

rm -f "$J" "$H" "$B"
