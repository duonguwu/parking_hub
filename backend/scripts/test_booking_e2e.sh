#!/usr/bin/env bash
# E2E nghiệp vụ trên domain thật: tài xế đặt giữ chỗ -> chủ bãi check-in/out -> thanh toán -> huỷ -> các ca lỗi.
# Dữ liệu tạo ra là lượt đặt thật của minh.12 tại một bãi demo cấp 4. Không in secret.
# Usage: bash backend/scripts/test_booking_e2e.sh [API_BASE]
export LC_ALL=C.UTF-8 PYTHONIOENCODING=utf-8
API="${1:-https://api.parkinghub.asia}"
PASS="test123@"
J=$(mktemp -d); fail=0

login() { curl -s -c "$J/$1" -H 'Content-Type: application/json' -d "{\"username\":\"$1\",\"password\":\"$PASS\"}" "$API/auth/login" -o /dev/null; }
call() { # user method path [json] -> body in $J/out, prints code
  curl -s -b "$J/$1" -X "$2" -H 'Content-Type: application/json' ${4:+-d "$4"} -o "$J/out" -w "%{http_code}" "$API$3"
}
errmsg() { python3 -c "import json; print(json.load(open('$J/out')).get('detail'))" 2>/dev/null; }
pyget() { python3 -c "import json,sys; d=json.load(open('$J/out')).get('data'); print(eval(sys.argv[1]))" "$1" 2>/dev/null; }
expect() { # label got want
  if [ "$2" = "$3" ]; then echo "OK   $1 ($2)"; else echo "FAIL $1: got $2, want $3"; fail=1; fi
}

login minh.12; login vin.landmark; login vin.q1; login duong.12

GID=$(call vin.landmark GET /garage-portal/garages >/dev/null; pyget "[l['id'] for l in d if l['name']=='Vin Parking Landmark'][0]")
VID=$(call minh.12 GET /customer/vehicles >/dev/null; pyget "[v['id'] for v in d if v['model'].startswith('S 450')][0]")
PLATE=$(pyget "[v['license_plate'] for v in d if v['model'].startswith('S 450')][0]")
echo "garage=$GID vehicle=$VID plate=$PLATE"

# Giờ hẹn trong 2 giờ tới để check-in được (quy tắc: tối đa 2 giờ trước giờ hẹn)
# Dọn lượt đặt dở dang của lần chạy trước (chỉ lượt bắt đầu trong 8 giờ tới) để không bị chặn vì trùng giờ
call minh.12 GET /customer/bookings >/dev/null
for bid in $(pyget "' '.join(b['id'] for b in d if b['status'] in ('reserved','pending') and b['start_time'] < '$(date -u -d '+8 hours' +%Y-%m-%dT%H:%M)')"); do
  call minh.12 POST /bookings/cancel "{\"id\":\"$bid\",\"reason\":\"dọn test\"}" >/dev/null
done

START=$(date -u -d "+1 hour" +%Y-%m-%dT%H:00:00Z); END=$(date -u -d "+4 hours" +%Y-%m-%dT%H:00:00Z)

echo "== Báo giá"
expect "quote 3h" "$(call minh.12 GET "/garage-services/quote?garage_id=$GID&service_type_code=park_hourly&start_time=$START&end_time=$END")" 200
echo "     $(pyget "d")"

echo "== Đặt chỗ (cấp 4: tự xác nhận)"
BODY="{\"garage_id\":\"$GID\",\"service_type_code\":\"park_hourly\",\"start_time\":\"$START\",\"end_time\":\"$END\",\"vehicle_id\":\"$VID\"}"
expect "create" "$(call minh.12 POST /bookings/create "$BODY")" 200
[ "$(pyget "d['status']")" = "reserved" ] || echo "     $(errmsg)"
BID=$(pyget "d['id']"); echo "     id=$BID status=$(pyget "d['status']") price=$(pyget "d['quoted_price']")"
expect "status reserved" "$(pyget "d['status']")" reserved

echo "== Ca lỗi"
expect "end<=start bị từ chối" "$(call minh.12 POST /bookings/create "{\"garage_id\":\"$GID\",\"service_type_code\":\"park_hourly\",\"start_time\":\"$END\",\"end_time\":\"$START\"}")" 422
expect "quá khứ xa bị từ chối" "$(call minh.12 POST /bookings/create "{\"garage_id\":\"$GID\",\"service_type_code\":\"park_hourly\",\"start_time\":\"2020-01-01T08:00:00Z\",\"end_time\":\"2020-01-01T10:00:00Z\"}")" 422
expect "dịch vụ không có ở bãi" "$(call minh.12 POST /bookings/create "{\"garage_id\":\"$GID\",\"service_type_code\":\"khong_ton_tai\",\"start_time\":\"$START\",\"end_time\":\"$END\"}")" 409
expect "chủ bãi khác không check-in được" "$(call vin.q1 POST /bookings/checkin "{\"id\":\"$BID\"}")" 403

echo "== Chủ bãi thấy lượt đặt"
expect "tab upcoming" "$(call vin.landmark GET "/garage-portal/bookings?tab=upcoming&q=$PLATE&garage_id=$GID")" 200
expect "có lượt vừa đặt" "$(pyget "any(b['id']=='$BID' for b in d['items'])")" True

echo "== Check-in sai biển số bị chặn"
expect "checkin sai biển" "$(call vin.landmark POST "/garage-portal/bookings/$BID/actions?garage_id=$GID" '{"action":"checkin","license_plate":"99Z-00000"}')" 409
echo "     $(errmsg)"

echo "== Check-in đúng + check-out + thanh toán"
expect "checkin" "$(call vin.landmark POST "/garage-portal/bookings/$BID/actions?garage_id=$GID" "{\"action\":\"checkin\",\"license_plate\":\"$PLATE\"}")" 200
expect "inside" "$(pyget "d['status']")" checked_in
expect "checkout" "$(call vin.landmark POST "/garage-portal/bookings/$BID/actions?garage_id=$GID" '{"action":"checkout","payment_method":"transfer"}')" 200
echo "     status=$(pyget "d['status']") final=$(pyget "d['final_price']") pay=$(pyget "d['payment_status']")"
expect "đã thanh toán" "$(pyget "d['payment_status']")" paid
expect "không huỷ được lượt đã xong" "$(call minh.12 POST /bookings/cancel "{\"id\":\"$BID\"}")" 409

echo "== Tài xế đặt lượt thứ 2 rồi huỷ"
S2=$(date -u -d "+30 hours" +%Y-%m-%dT%H:00:00Z); E2=$(date -u -d "+32 hours" +%Y-%m-%dT%H:00:00Z)
expect "create2" "$(call duong.12 POST /bookings/create "{\"garage_id\":\"$GID\",\"service_type_code\":\"park_hourly\",\"start_time\":\"$S2\",\"end_time\":\"$E2\"}")" 200
B2=$(pyget "d['id']")
expect "cancel" "$(call duong.12 POST /bookings/cancel "{\"id\":\"$B2\",\"reason\":\"Đổi kế hoạch\"}")" 200
expect "cancelled" "$(pyget "d['status']")" cancelled
expect "tracking" "$(call minh.12 GET /customer/bookings/$BID/tracking)" 200

echo "== Cập nhật chỗ trống (chủ bãi)"
call vin.landmark GET "/garage-portal/dashboard/overview?garage_id=$GID" >/dev/null; ORIG=$(pyget "d['availability']['occupied']")
expect "set occupied" "$(call vin.landmark PUT "/garage-portal/occupancy?garage_id=$GID" '{"occupied":200}')" 200
expect "occupied=200" "$(pyget "d['occupied']")" 200
expect "occupied vượt sức chứa bị chặn về tối đa" "$(call vin.landmark PUT "/garage-portal/occupancy?garage_id=$GID" '{"occupied":99999}')" 200
expect "bị chặn ở sức chứa" "$(pyget "d['occupied']")" "$(pyget "d['total_spots']")"
expect "số âm bị từ chối" "$(call vin.landmark PUT "/garage-portal/occupancy?garage_id=$GID" '{"occupied":-5}')" 422
call vin.landmark PUT "/garage-portal/occupancy?garage_id=$GID" "{\"occupied\":$ORIG}" >/dev/null   # trả lại số ban đầu

echo; [ $fail = 0 ] && echo "TẤT CẢ ĐẠT" || echo "CÓ LỖI"
rm -rf "$J"; exit $fail
