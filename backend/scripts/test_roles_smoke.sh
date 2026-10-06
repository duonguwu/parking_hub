#!/usr/bin/env bash
# Smoke test API theo từng vai trò trên domain thật. Chỉ in mã HTTP và vài trường chính, không in secret.
# Usage: bash backend/scripts/test_roles_smoke.sh [API_BASE]
API="${1:-https://api.parkinghub.asia}"
PASS="test123@"
J=$(mktemp -d)
fail=0

login() { # $1 user -> cookie jar $J/$1
  curl -s -c "$J/$1" -H 'Content-Type: application/json' -d "{\"username\":\"$1\",\"password\":\"$PASS\"}" "$API/auth/login" -o /dev/null -w "%{http_code}"
}
get() { # $1 user $2 path -> prints "code" and writes body to $J/out
  curl -s -b "$J/$1" -o "$J/out" -w "%{http_code}" "$API$2"
}
check() { # label user path [jq-ish python expr over data]
  local code; code=$(get "$2" "$3")
  local extra=""
  if [ -n "$4" ]; then
    extra=$(python3 - "$J/out" "$4" <<'EOF'
import json,sys
try:
    d=json.load(open(sys.argv[1])).get("data")
    print(eval(sys.argv[2]))
except Exception as e:
    print("ERR", e)
EOF
)
  fi
  [ "$code" = "200" ] || fail=1
  printf "%s %-12s %s -> %s\n" "$code" "$2" "$3" "$extra"
}

echo "== Đăng nhập"
for u in admin superadmin ops owner manager staff driver fleet minh.12 duong.12 vin.q1 vin.landmark vin.q3 owner_q1_01 customer_01; do
  printf "%-14s %s\n" "$u" "$(login $u)"
done
printf "%-14s %s (mong đợi 401)\n" "sai-mat-khau" "$(curl -s -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' -d '{"username":"owner","password":"x"}' $API/auth/login)"

echo; echo "== Tài xế minh.12"
check x minh.12 /customer/dashboard-summary "len(d['active_bookings']), d['default_vehicle'] and d['default_vehicle']['model']"
check x minh.12 /customer/vehicles "[(v['brand'],v['model'],v['vehicle_type']) for v in d]"
check x minh.12 "/customer/bookings" "type(d).__name__"
check x minh.12 "/customer/nearby?lat=10.7769&lng=106.7009&radius_km=3" "len(d['garages'])"
check x duong.12 /customer/vehicles "[(v['brand'],v['model'],v['vehicle_type']) for v in d]"

echo; echo "== Chủ bãi (vin.q1 có 2 bãi)"
check x vin.q1 /garage-portal/garages "[l['name'] for l in d]"
check x vin.q1 /garage-portal/dashboard/overview "(d['garage']['name'], d['availability']['available'], d['inside_count'])"
check x vin.landmark /garage-portal/dashboard/overview "(d['garage']['name'], d['availability']['total_spots'])"
check x vin.q3 /garage-portal/garages "[l['name'] for l in d]"
check x vin.q3 /garage-portal/services "len(d['services'])"
check x vin.q3 "/garage-portal/bookings?tab=inside" "d['counts']"
check x vin.q3 "/garage-portal/analytics?range=30D" "d['metrics']['sessions']"
check x vin.q3 /garage-portal/score "(d['grade']['stars'], d['quality_score'])"
check x owner /garage-portal/dashboard/overview "d['garage']['name']"
check x manager /garage-portal/dashboard/overview "d['garage']['name']"
check x staff /garage-portal/bookings?tab=upcoming "d['counts']"

echo; echo "== Admin"
check x admin /admin/overview "(d['garages']['total'], d['spots']['total'], d['bookings_30d'])"
check x admin /admin/garages?limit=5 "d['pagination']['total_items']"
check x admin /admin/map "len(d)"
check x admin /admin/users?limit=5 "d['pagination']['total_items']"
check x admin /admin/service-types "len(d)"
check x admin /garage-portal/garages "len(d)"
check x admin /customer/dashboard-summary "d['default_vehicle']"
check x ops /admin/overview "d['garages']['total']"

echo; echo "== Phân quyền (mong đợi 403/401, không phải 200)"
for pair in "driver /admin/overview" "owner /admin/overview" "driver /garage-portal/garages" "vin.q1 /admin/overview"; do
  set -- $pair; printf "%-10s %-30s %s\n" "$1" "$2" "$(get $1 $2)"
done
rm -rf "$J"
exit $fail
