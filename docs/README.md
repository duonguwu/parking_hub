# Parking HUB

Mạng lưới bãi đỗ xe ô tô thông minh cho đô thị Việt Nam.

Ngày cập nhật: 21/08/2026  
Trạng thái: bản thảo lần 1, chờ phản hồi  
Bối cảnh: Data for Life mùa 4 năm 2026

## Bắt đầu ở đây

Không cần đọc toàn bộ thư mục `docs`. Trang này là bản định hướng nhanh; các tài liệu còn lại chỉ mở khi cần giải quyết một câu hỏi cụ thể.

Parking HUB kết nối các bãi đỗ xe rời rạc thành một mạng lưới chung. Hệ thống dùng camera và thị giác máy tính để ghi nhận chỗ trống, biển số, thời gian xe vào ra và cảnh báo khói lửa. Trên lớp dữ liệu đó, nền tảng hỗ trợ tìm bãi theo điểm đến, dự đoán khả năng còn chỗ khi xe tới, giữ chỗ, thanh toán và vận hành bãi.

Giá trị chính:

- Người lái xe biết trước nơi đỗ, giá và khả năng còn chỗ.
- Chủ bãi giảm thất thu, theo dõi vận hành và bán phần công suất đang trống.
- Cơ quan quản lý có dữ liệu tổng hợp phục vụ điều hành và quy hoạch.

Ba phần cần làm mới là triển khai suy luận trên thiết bị biên tại bãi, dự báo chỗ trống theo thời gian và nghiệp vụ giữ chỗ có cam kết hai chiều.

## Chọn đường đọc

| Bạn đang cần gì | Chỉ cần đọc |
|---|---|
| Hiểu nhanh dự án | Trang README này |
| Chốt định vị và sản phẩm | [01. Tổng quan dự án](01_strategy-product/01_Project_Overview.md), sau đó chỉ tra [02](01_strategy-product/02_Problem_Deep_Dive.md) hoặc [03](01_strategy-product/03_Product_Features.md) khi cần |
| Chuẩn bị hồ sơ cuộc thi | [07. Bản đề xuất Data for Life](03_submission/07_Proposal_DataForLife.md) và [99. Nguồn, giả định](99_reference/99_Sources_and_Assumptions.md) |
| Làm mô hình kinh doanh | [04. Mô hình kinh doanh](02_business-operations/04_Business_Model.md) |
| Triển khai một bãi | [05. Playbook onboard](02_business-operations/05_Onboarding_Playbook.md) và [06. Phạm vi, lộ trình](02_business-operations/06_Scope_and_Roadmap.md) |
| Bắt đầu phát triển mã nguồn | [08. Hướng dẫn mã nguồn](04_technical/08_Codebase_Guide.md) và [09. Thiết kế giao diện](04_technical/09_Frontend_Design_System.md) |

## Cấu trúc tài liệu

```text
docs/
├── README.md                       Bắt đầu ở đây
├── 01_strategy-product/            Định vị, bài toán, tính năng
├── 02_business-operations/         Doanh thu, onboard, lộ trình
├── 03_submission/                  Hồ sơ dùng để nộp
├── 04_technical/                   Mã nguồn và thiết kế giao diện
└── 99_reference/                   Nguồn dữ liệu và giả định
```

## Việc cần làm ngay

1. Chốt tên dự án chính thức; hiện dùng tên tạm Parking HUB.
2. Xác nhận thể lệ và mẫu hồ sơ chính thức của cuộc thi.
3. Kiểm chứng các số liệu còn được đánh dấu là giả định.
4. Đo lại độ chính xác của bốn model thị giác máy tính.
5. Hoàn thiện hồ sơ 07 dựa trên kết quả kiểm chứng.

Tài liệu 10 tới 12 về kiến trúc hệ thống, model thị giác máy tính và chiến lược dữ liệu chưa viết. Chỉ tạo khi bước triển khai thực sự cần, không tạo trước để lấp danh mục.
