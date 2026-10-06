# Kế hoạch tiếp theo sau V1

Tình trạng: V1 đã dùng được (đủ luồng tài xế, chủ bãi, admin, test API đều qua; giao diện chưa kiểm thử trên trình duyệt thật). Xem [V1_Tong_Quan.md](../release/V1_Tong_Quan.md).

Tài liệu này chỉ nêu hướng, chưa đi sâu. Mức ưu tiên: P1 làm trước, P2 tiếp theo, P3 khi rảnh.

## Team Dev

### 1. Cải thiện UI/UX (P1)
- Kiểm thử giao diện trên trình duyệt thật cho 3 vai trò, sửa lỗi vặt.
- Thống nhất phong cách, trạng thái tải, lỗi, danh sách rỗng.
- Tối ưu cho điện thoại, vì tài xế dùng khi đang ở ngoài đường.

### 2. Matching có giao thông, ngập, thời tiết (P1)
- Hướng: bổ sung dữ liệu giao thông, ngập lụt, thời tiết theo tuyến đường, camera giao thông TP.HCM (Hưng đã làm POC) là giai đoạn sau.
- Chi tiết và câu hỏi nghiên cứu: [Matching_Route_Intelligence_Plan.md](02_matching/Matching_Route_Intelligence_Plan.md).

### 3. Thông báo, thiên về trải nghiệm (P2)
Người dùng là người đang ngồi xe ngoài đường, sợ nắng, mưa, kẹt xe, thành phố đông. Ý tưởng:
- Báo trước khi đi: đường tới bãi đang ngập hoặc kẹt, gợi ý bãi khác.
- Báo mưa sắp tới gần điểm đến, ưu tiên bãi có mái che hoặc hầm.
- Báo giờ nên xuất phát để kịp giữ chỗ.
- Báo khi sắp hết giờ, gần hết chỗ, đã đến gần bãi (hướng dẫn vào cổng, tầng, ô).
- Gợi ý bãi gần điểm đến cuối, đi bộ ngắn, có mái che.
- Cần quyết định: kênh (push, SMS, Zalo), tần suất, cho phép tắt từng loại.

### 4. Hạ tầng và việc khác (P2)
- Sao lưu MongoDB tự động (hiện chưa có).
- Tự host OSRM thay server demo.
- Kiểm thử giao diện tự động.
- Chưa làm: camera AI, thanh toán online.

## Team Biz

### 5. Gói đăng ký và giá, bản nháp (P2)
Người dùng Việt Nam nhạy cảm về giá, nên giá thấp, có gói miễn phí đủ dùng.

| Gói | Đối tượng | Giá tham khảo | Nội dung dự kiến |
|---|---|---|---|
| Miễn phí | Tài xế | 0 | Tìm và đặt chỗ cơ bản |
| Chủ động | Tài xế thường xuyên | khoảng 49k đến 99k mỗi tháng | Cảnh báo ngập, kẹt, mưa; ưu tiên gợi ý; lịch sử |
| Gia đình, đi làm hằng ngày | Tài xế đi làm | khoảng 200k mỗi tháng (mức trần) | Giữ chỗ cố định, nhiều xe |
| Chủ bãi cơ bản | Bãi nhỏ | miễn phí hoặc thấp | Hiển thị bãi, nhận đặt chỗ |
| Chủ bãi nâng cao | Chuỗi bãi | theo bãi hoặc hoa hồng | Báo cáo, nhiều bãi, quảng bá |
| Doanh nghiệp | Đội xe, tòa nhà | thỏa thuận | Quản lý nhiều xe |

Tất cả con số chỉ là nháp để team Biz kiểm chứng.

### 6. Việc team Biz cần nghiên cứu
- Mức sẵn sàng trả tiền của tài xế (khảo sát), mức giá hợp lý.
- Hoa hồng hay thuê bao cho chủ bãi, mức nào chủ bãi chấp nhận.
- Xếp hạng và chứng nhận bãi (chống bãi kém chất lượng, bãi chỉ để đỗ xe của khu riêng).
- Điều khoản dùng dữ liệu bên thứ ba: cổng giao thông TP.HCM, camera, nuoclen.com.
- Đối tác: tòa nhà, trung tâm thương mại, đơn vị bản đồ.
- Pháp lý: dữ liệu cá nhân, biển số, hóa đơn.
- Chi phí vận hành khi mở rộng (bản đồ, thông báo, lưu trữ).

## Thứ tự đề xuất
1. UI/UX và kiểm thử (Dev).
2. Matching giai đoạn 1 (Dev) song song với nghiên cứu giá và điều khoản dữ liệu (Biz).
3. Thông báo và gói Chủ động.
4. Camera và các hạng mục sau.
