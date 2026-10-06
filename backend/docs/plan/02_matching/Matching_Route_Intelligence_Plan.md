# Kế hoạch nghiên cứu: Matching có dữ liệu giao thông, ngập, thời tiết

Đây là tài liệu để nghiên cứu thêm, chưa chốt kỹ thuật. Dựa trên 2 file nháp của AI Agent ([draf_system.md](archive/draf_system.md), [matching_new_data.md](archive/matching_new_data.md)) và đối chiếu với code hiện tại.

## 1. Mục tiêu

Người lái xe ngoài đường sợ mưa, ngập, kẹt xe. Bãi tốt nhưng đường tới bãi ngập hoặc kẹt thì không phải lựa chọn tốt. Matching cần trả lời: "bãi nào đến được, đến lúc nào, rủi ro trên đường bao nhiêu".

Nguyên tắc: điểm bãi (chất lượng, giá, chỗ trống) và điểm đường đi (kẹt, ngập, mưa) tính riêng, sau đó mới gộp. Đường bị chặn hoặc ngập nặng là loại bỏ, không phải trừ điểm.

## 2. Hiện trạng matching (code thật)

Pipeline 5 bước ở `backend/app/api/matching/`:
1. Lọc cứng: khoảng cách, giờ mở cửa, dịch vụ, cấp tích hợp, còn nhận đặt chỗ.
2. Làm giàu: thời gian đi (OSRM bảng khoảng cách), thời tiết 1 điểm tại vị trí user (Open-Meteo), dự đoán chỗ trống, báo giá.
3. Chấm điểm 8 thành phần (khoảng cách, chờ, chất lượng, phù hợp, thói quen, giá, tin cậy, môi trường), trọng số đổi theo mưa và giờ cao điểm.
4. Cá nhân hóa.
5. Xếp hạng đa dạng, sinh lý do và đánh đổi.

Điểm yếu cần thay:
- Hệ số kẹt xe là hằng số 1,15 cho giờ cao điểm T2 đến T6.
- Thời tiết chỉ lấy tại 1 điểm, không theo tuyến đường.
- Không có thông tin ngập.
- OSRM đang dùng server demo công cộng, có giới hạn tốc độ.

Chỗ gắn: thêm `RouteContext` (kẹt, ngập, mưa, bị chặn, độ tin cậy) ở bước 2, thêm lọc cứng và điểm đường đi ở bước 3. Điểm "môi trường" hiện tại sẽ được thay.

## 3. Đánh giá 2 file nháp của Agent

Đúng và nên giữ:
- Luồng candidates, lọc, tính tuyến, gắn rủi ro, chấm điểm, Top 3.
- Tách ràng buộc cứng khỏi điểm có trọng số.
- Dữ liệu lịch sử ngập chỉ là xác suất nền, không được ghi là "đang ngập".
- Thời tiết cần mưa theo tọa độ và thời điểm đến.

Cần xem lại:
- Agent chưa biết dự án nên coi như xây hệ thống mới. Thực tế đã có pipeline, chỉ cần cắm thêm.
- Camera AI (VLM ghép lưới 3x3) nằm ngoài phạm vi V1. Đưa vào giai đoạn cuối, chưa cam kết.
- Chưa tính chi phí VLM, chưa kiểm tra điều khoản dùng dữ liệu camera của cổng chính phủ.
- Công thức xác suất ngập P(flood_now) mới là ý tưởng, chưa có dữ liệu để hiệu chỉnh.

## 4. Nguồn dữ liệu

| Dữ liệu | Đang có | Còn thiếu | Cần nghiên cứu |
|---|---|---|---|
| Giao thông | Chưa có | Trạng thái kẹt theo đoạn đường | Cổng giao thông TP.HCM có API không, điều khoản; phương án khác (TomTom, HERE, Google) và chi phí |
| Thời tiết | `weather.json` (cấp thành phố, mưa 15 phút từ Open-Meteo) | Mưa theo tọa độ, dự báo ngắn hạn | Open-Meteo minutely, radar Việt Nam, độ chính xác với TP.HCM |
| Ngập lịch sử | `event_flood.json` (558 sự kiện, 390 ô lưới, 31 đoạn đường, từ 18/09/2026) | Dữ liệu dài hơn, nguồn dự phòng | Lưu bản sao vào DB của mình vì nuoclen.com có thể tắt; ghi rõ nguồn |
| Camera | POC của Hưng: danh sách camera và ảnh snapshot | Chưa vào repo, chưa gắn camera với đường | Tần suất lấy ảnh, giới hạn truy cập, ghép camera vào tuyến |

Chi tiết `event_flood.json`: mỗi ô lưới có `lat`, `lng`, `street`, số báo theo nguồn, `verified`, `maxDepth` (ankle 37, knee 263, wheel 90), thời gian đầu và cuối. Mỗi đoạn có polyline `line`. Điểm nóng gồm Đinh Bộ Lĩnh (Bình Thạnh), Phan Huy Ích (Gò Vấp), Lý Tế Xuyên, Nguyễn Văn Khối.

## 5. Mô hình ngập 3 tầng (đề xuất, cần kiểm chứng)

1. Lịch sử: ô lưới hay ngập thì tăng rủi ro nền. Không bao giờ coi là đang ngập.
2. Bằng chứng thực tế: báo cáo người dùng, camera. Độ tin cậy cao nhưng thưa.
3. Thời tiết: mưa lớn đang hoặc sắp xảy ra làm tăng rủi ro ở các ô nền.

Xử lý: ngập nhẹ thì cộng chi phí, ngập đáng kể thì phạt mạnh, ngập nặng hoặc đường chặn thì loại bãi khỏi danh sách (hoặc cảnh báo rõ nếu không còn lựa chọn).

## 6. Lưu trữ và làm mới (đề xuất)

- Mongo: collection điểm ngập lịch sử (ô lưới, đoạn đường, nguồn, thời gian), danh sách camera.
- Redis: trạng thái giao thông, mưa theo ô, kết quả camera. TTL ngắn, ví dụ giao thông 2 đến 5 phút, mưa 10 đến 15 phút.
- Service mới đặt cạnh `app/services/osm` và `app/services/weather`.
- Khi nguồn lỗi: trả `UNKNOWN`, không chặn matching, giữ hành vi cũ làm mặc định.

## 7. Các giai đoạn

| Giai đoạn | Nội dung | Ghi chú |
|---|---|---|
| 1 | Tự host OSRM, thay hằng số 1,15 bằng giao thông thật, nhập dữ liệu ngập lịch sử vào DB | Giá trị cao nhất, rủi ro thấp |
| 2 | Mưa theo tọa độ và theo tuyến, tính rủi ro ngập kết hợp mưa | Cần chọn nguồn mưa |
| 3 | Nút báo ngập từ người dùng, cảnh báo trên bản đồ | Tạo dữ liệu thật cho tầng 2 |
| 4 | Camera: gắn camera với tuyến, đọc ảnh bằng AI | Sau cùng, cần đo chi phí và benchmark |

## 8. Câu hỏi nghiên cứu

- Cổng giao thông TP.HCM có cho gọi API không, điều khoản sử dụng, giới hạn?
- Nguồn mưa nào đủ chính xác theo từng quận?
- Dữ liệu ngập 3 tuần có đủ làm xác suất không, cần thu thập thêm bao lâu?
- Gắn camera với tuyến đường thế nào cho đúng hướng?
- Chi phí VLM mỗi ngày nếu quét toàn bộ camera?
- Tuyến xe máy và ô tô khác nhau thế nào (ngập sâu mức nào thì xe máy không đi được)?

## 9. Rủi ro

- Nguồn dữ liệu bị tắt hoặc đổi định dạng (nuoclen.com, cổng chính phủ).
- Vấn đề pháp lý và bản quyền khi lấy dữ liệu bên thứ ba.
- Gọi quá nhiều tuyến làm chậm: cần giới hạn số ứng viên và dùng cache.
- Cảnh báo sai làm người dùng mất tin tưởng: luôn hiển thị độ tin cậy.

## 10. Cách đo thành công

- Thời gian phản hồi `/match/search` vẫn dưới mục tiêu hiện tại.
- Tỷ lệ gợi ý đi qua đoạn đang ngập hoặc kẹt nặng giảm so với bản cũ.
- Sai lệch giữa thời gian đến dự kiến và thực tế giảm.
- Người dùng chọn gợi ý số 1 nhiều hơn.
