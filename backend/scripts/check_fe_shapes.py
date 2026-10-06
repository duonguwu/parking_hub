#!/usr/bin/env python3
"""Đối chiếu field cấp 1 của interface TypeScript (api.ts) với JSON thật từ API.
Phát hiện trường FE đọc mà BE không trả (nguyên nhân phổ biến của trang trắng / NaN).
Usage: python3 backend/scripts/check_fe_shapes.py [API_BASE]"""
import json, re, subprocess, sys, tempfile, os

API = sys.argv[1] if len(sys.argv) > 1 else "https://api.parkinghub.asia"
SRC = open(os.path.join(os.path.dirname(__file__), "../../frontend/src/services/api.ts"), encoding="utf-8").read()
jar = tempfile.mkdtemp()


def curl(user, path):
    ck = f"{jar}/{user}"
    if not os.path.exists(ck):
        subprocess.run(["curl", "-s", "-c", ck, "-H", "Content-Type: application/json",
                        "-d", json.dumps({"username": user, "password": "test123@"}), f"{API}/auth/login", "-o", "/dev/null"])
    out = subprocess.run(["curl", "-s", "-b", ck, f"{API}{path}"], capture_output=True, text=True).stdout
    return json.loads(out).get("data")


def iface_fields(name):
    m = re.search(r"export interface %s(?:<[^>]*>)?(?: extends (\w+))? \{(.*?)\n\}" % name, SRC, re.S)
    if not m:
        return None
    body = m.group(2)
    fields, depth = {}, 0
    for line in body.split("\n"):
        s = line.strip()
        if depth == 0:
            fm = re.match(r"(\w+)(\?)?:", s)
            if fm:
                fields[fm.group(1)] = bool(fm.group(2))
        depth += line.count("{") - line.count("}")
    if m.group(1):
        fields.update(iface_fields(m.group(1)) or {})
    return fields


def first(d):
    if isinstance(d, list):
        return d[0] if d else None
    return d


def lot(user):
    return curl(user, "/garage-portal/garages")[0]["id"]


gid = lot("vin.q1")
CHECKS = [
    ("minh.12", "/customer/dashboard-summary?lat=10.77&lng=106.70", "DashboardSummary", lambda d: d),
    ("minh.12", "/customer/nearby?lat=10.77&lng=106.70", "NearbyGarage", lambda d: first(d["garages"])),
    ("minh.12", "/customer/garages/%s/portal" % gid, "GarageDetailData", lambda d: d),
    ("minh.12", "/customer/bookings", "Booking", first),
    ("minh.12", "/customer/vehicles", "Vehicle", first),
    ("vin.q1", "/garage-portal/dashboard/overview", "PortalOverview", lambda d: d),
    ("vin.q1", "/garage-portal/bookings?tab=history", "PortalBookings", lambda d: d),
    ("vin.q1", "/garage-portal/bookings?tab=history", "Booking", lambda d: first(d["items"])),
    ("vin.q1", "/garage-portal/analytics?range=30D", "PortalAnalytics", lambda d: d),
    ("vin.q1", "/garage-portal/score", "PortalScore", lambda d: d),
    ("vin.q1", "/garage-portal/garage", "Garage", lambda d: d),
    ("vin.q1", "/garage-portal/services", "PortalServicesOverview", lambda d: d),
    ("admin", "/admin/overview", "AdminOverview", lambda d: d),
    ("admin", "/admin/garages?limit=3", "AdminGarageList", lambda d: d),
    ("admin", "/admin/users?limit=3", "AdminUserList", lambda d: d),
]
bad = 0
for user, path, typ, pick in CHECKS:
    fields = iface_fields(typ)
    if fields is None:
        print(f"?    {typ}: không tìm thấy interface (bỏ qua)")
        continue
    obj = pick(curl(user, path))
    if not isinstance(obj, dict):
        print(f"?    {typ}: không có dữ liệu mẫu ở {path}")
        continue
    missing = sorted(k for k, opt in fields.items() if not opt and k not in obj)
    extra = sorted(k for k in obj if k not in fields)
    flag = "OK  " if not missing else "LỖI "
    bad += bool(missing)
    print(f"{flag} {typ:24} thiếu(bắt buộc): {missing or '-'}   BE thừa: {extra or '-'}")
sys.exit(1 if bad else 0)
