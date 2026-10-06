# -*- coding: utf-8 -*-
"""
Đường cong lấp đầy điển hình theo loại bãi (0..1 theo giờ địa phương).
Dùng làm dự đoán dự phòng khi bãi chưa đủ lịch sử, và để sinh dữ liệu demo.
"""

# 24 giá trị, index = giờ. Ngày thường (T2–T6).
_WEEKDAY = {
    # văn phòng: đầy giờ hành chính, trống ban đêm
    "office_basement": [.05, .04, .04, .04, .05, .08, .20, .55, .85, .93, .95, .94,
                        .90, .93, .94, .92, .85, .65, .35, .18, .10, .07, .06, .05],
    # chung cư: đầy ban đêm, vơi ban ngày
    "apartment_basement": [.92, .93, .93, .93, .92, .88, .78, .62, .50, .45, .44, .45,
                           .48, .47, .46, .48, .55, .66, .78, .86, .90, .91, .92, .92],
    # nhà xe chuyên dụng: khu trung tâm, đỉnh trưa và tối
    "parking_building": [.30, .26, .24, .24, .25, .30, .42, .62, .78, .85, .88, .90,
                         .88, .86, .86, .85, .84, .86, .88, .84, .72, .55, .42, .34],
    "covered_garage": [.35, .32, .30, .30, .30, .34, .45, .60, .72, .78, .80, .82,
                       .80, .78, .78, .78, .80, .84, .86, .80, .68, .55, .45, .38],
    "outdoor_commercial": [.15, .12, .10, .10, .10, .14, .25, .45, .62, .72, .78, .84,
                           .82, .76, .74, .74, .78, .86, .90, .86, .70, .48, .30, .20],
    # sân bay / bến xe: đều, cao gần như cả ngày
    "transit_hub": [.55, .52, .50, .50, .55, .65, .75, .82, .86, .88, .88, .87,
                    .86, .86, .87, .88, .88, .88, .86, .84, .80, .74, .66, .60],
    "street": [.05, .04, .03, .03, .04, .10, .30, .60, .80, .88, .90, .92,
               .88, .86, .88, .90, .92, .94, .90, .78, .55, .30, .15, .08],
    "residential": [.70, .70, .70, .70, .70, .66, .55, .40, .32, .30, .30, .32,
                    .34, .32, .32, .34, .40, .52, .62, .68, .70, .70, .70, .70],
}

# Cuối tuần: văn phòng vắng, TTTM/đường phố đông hơn
_WEEKEND_FACTOR = {
    "office_basement": 0.35, "apartment_basement": 1.05, "parking_building": 1.05,
    "covered_garage": 1.0, "outdoor_commercial": 1.12, "transit_hub": 1.05,
    "street": 0.9, "residential": 1.05,
}


def occupancy_profile(lot_type: str, hour: int, weekday: int) -> float:
    """Tỉ lệ lấp đầy điển hình (0..1) cho loại bãi tại giờ/thứ địa phương."""
    curve = _WEEKDAY.get(lot_type) or _WEEKDAY["outdoor_commercial"]
    rate = curve[hour % 24]
    if weekday >= 5:
        rate *= _WEEKEND_FACTOR.get(lot_type, 1.0)
    return max(0.0, min(1.0, rate))
