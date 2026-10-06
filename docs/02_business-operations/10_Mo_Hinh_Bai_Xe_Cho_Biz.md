# Mô hình bãi xe và cách chấm điểm (dành cho team Biz)

Tóm tắt từ [huong_dan_tinh_nang.md](../../backend/docs/huong_dan_tinh_nang.md). Đọc khoảng 3 phút. Dữ liệu hiện tại là dữ liệu giả: 262 bãi, 18 quận TP.HCM.

## 1. Mỗi bãi được mô tả bằng 4 thứ

| Thông tin | Trả lời câu hỏi | Ai quyết định |
|---|---|---|
| Loại hình | Bãi này là loại gì | Chủ bãi khai, admin duyệt |
| Cấp tích hợp (1 đến 4) | Dữ liệu chỗ trống đáng tin tới đâu | Admin |
| Hạng sao (1 đến 5) | Cơ sở vật chất tốt tới đâu | Admin kiểm định thực địa |
| Điểm chất lượng (0 đến 100) | Vận hành thực tế tốt tới đâu | Hệ thống tự tính |

Hạng sao nhìn vào "bãi được xây thế nào". Điểm chất lượng nhìn vào "bãi chạy thế nào". Hai cái độc lập, nên bãi mới xây đẹp nhưng vận hành kém vẫn lộ ra.

## 2. Loại hình (8 loại) và số lượng trong dữ liệu demo

| Loại | Số bãi |
|---|---|
| Hầm chung cư | 68 |
| Bãi ngoài trời | 46 |
| Hầm tòa nhà văn phòng | 44 |
| Nhà xe có mái | 32 |
| Chỗ nhỏ hộ dân | 24 |
| Nhà xe chuyên dụng (cao tầng) | 18 |
| Lòng đường, công cộng | 17 |
| Đầu mối giao thông | 13 |

## 3. Cấp tích hợp

| Cấp | Tên | Chỗ trống | Đặt chỗ | Số bãi demo |
|---|---|---|---|---|
| 1 | Danh mục | Không có dữ liệu | Chỉ xem | 49 |
| 2 | Có cập nhật | Chủ bãi tự nhập, có giờ cập nhật | Đặt được, bãi phải xác nhận | 103 |
| 3 | Kết nối cảm nhận | Thời gian thực | Giữ chỗ tự động | 79 |
| 4 | Kết nối đầy đủ | Thời gian thực | Giữ chỗ tự động, được ưu tiên xếp hạng | 31 |

Ý nghĩa kinh doanh: cấp càng cao, trải nghiệm tài xế càng tốt, và bãi càng được ưu tiên hiển thị. Đây là đòn bẩy để thuyết phục chủ bãi nâng cấp (và có thể là cơ sở tính phí, cần team Biz cân nhắc). Số liệu thời gian thực ở cấp 3 và 4 hiện là mô phỏng.

## 4. Hạng sao: chống bãi kém và bãi "chỉ để đỗ xe"

Admin chấm bằng checklist 100 điểm, 6 nhóm: kết cấu, an ninh, che chắn, tiếp cận, phòng cháy chữa cháy, tiện ích. Từ 85 điểm là 5 sao. Nhà xe cao tầng có bảo vệ 24/7 thường 5 sao, sân đất ngoài trời thường 1 đến 2 sao.

Phân bố demo: 1 sao 100 bãi, 2 sao 41, 3 sao 43, 4 sao 53, 5 sao 25.

Sau khi chấm, bãi có nhãn "Đã kiểm định" và tự hẹn kiểm định lại sau 6 tháng.

## 5. Điểm chất lượng

Hệ thống tự tính, bãi cần ít nhất 5 lượt gửi hoàn tất mới có điểm:

| Thành phần | Tỷ trọng |
|---|---|
| Giữ đúng chỗ cho khách đã đặt | 45% |
| Ít khiếu nại | 20% |
| Điểm đánh giá của khách | 20% |
| Khách quay lại | 15% |

Huy hiệu tự gắn: Đã kiểm định, Bãi chuyên dụng, An toàn PCCC, Thời gian thực, Có sạc EV, Giữ đúng chỗ từ 98%.

## 6. Bãi được chọn để gợi ý thế nào

Khi tài xế bấm "Gợi ý thông minh", hệ thống lọc rồi chấm 8 yếu tố: khoảng cách, thời gian chờ, chất lượng, độ phù hợp xe và dịch vụ, thói quen cá nhân, giá, độ tin cậy, môi trường (mưa). Trọng số đổi theo bối cảnh, ví dụ trời mưa ưu tiên bãi có mái. Sau đó xếp hạng đa dạng, hiển thị lý do. Chi tiết nâng cấp: [Matching_Route_Intelligence_Plan.md](../../backend/docs/plan/02_matching/Matching_Route_Intelligence_Plan.md).

## 7. Vòng đời một bãi

1. Chủ bãi đăng ký, bãi ở trạng thái chờ duyệt.
2. Admin kiểm tra, duyệt, đặt cấp tích hợp, chấm sao.
3. Bãi hiện với tài xế. Vận hành sinh ra điểm chất lượng.
4. Admin có thể tạm ngưng hoặc mở lại. Demo hiện có 244 bãi hoạt động, 13 chờ duyệt, 5 tạm ngưng.

Một chủ bãi có thể quản lý nhiều bãi (demo: 36 chủ có 2 đến 3 bãi).

## 8. Câu hỏi cho team Biz

- Tiêu chí kiểm định có đủ chặt để loại bãi dỏm và bãi chỉ phục vụ nội bộ không? Ai trả chi phí kiểm định thực địa?
- Có thu phí theo cấp tích hợp hoặc hạng sao không?
- Hạng sao có công khai cho tài xế không, và chủ bãi phản ứng ra sao khi bị chấm thấp?
- Ngưỡng 85 điểm cho 5 sao và trọng số điểm chất lượng có hợp thị trường không?
- Bãi do doanh nghiệp lớn quản lý có quy trình duyệt riêng không?
