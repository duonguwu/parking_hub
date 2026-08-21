# 09. Nguyên tắc thiết kế giao diện

Bộ token màu, thang chữ, quy tắc dựng khối, và những gì đã có sẵn trong code

Phiên bản: 1.0
Ngày: 21/08/2026
Tài liệu liên quan: [08. Hướng dẫn mã nguồn](08_Codebase_Guide.md)

---

## 1. Hướng thiết kế

Giao diện hiện tại theo hướng bản vẽ kỹ thuật: phẳng, nhiều khoảng trắng, phân cấp bằng đường viền một điểm ảnh thay vì bằng đổ bóng, chữ có độ tương phản kích thước lớn giữa số liệu và nhãn.

Lý do hướng này phù hợp với sản phẩm đỗ xe. Người dùng mở ứng dụng để đọc số và ra quyết định nhanh: còn mấy chỗ, bao nhiêu phút tới, giá bao nhiêu, đi bộ mấy phút. Một giao diện phẳng, sạch, ưu tiên số liệu sẽ đọc nhanh hơn giao diện nhiều hiệu ứng. Với cổng chủ bãi, cảm giác công cụ vận hành đáng tin quan trọng hơn cảm giác vui mắt.

Hướng này có thể đổi. Nhưng nếu đổi thì đổi một lần, đổi ở token, không đổi lẻ từng trang.

---

## 2. Token màu

Khai báo trong `frontend/src/index.css` bằng khối `@theme` của Tailwind 4. Dùng bằng class Tailwind tương ứng, ví dụ `bg-surface`, `text-on-surface-variant`, `border-outline-variant`.

| Nhóm | Token | Giá trị | Dùng cho |
|---|---|---|---|
| Chính | `--color-primary` | `#3b82f6` | Hành động chính, trạng thái đang chọn |
| Chính | `--color-primary-container` | `#93c5fd` | Nền của nút chính |
| Chính | `--color-on-primary-container` | `#1e3a8a` | Chữ trên nền nút chính |
| Nền | `--color-background` | `#f8fafc` | Nền toàn trang, không dùng trắng tinh |
| Nền | `--color-surface` | `#ffffff` | Nền thẻ và bảng |
| Nền | `--color-surface-container-low` | `#f1f5f9` | Nền phụ, vùng nhóm nội dung |
| Nền | `--color-surface-container` | `#e2e8f0` | Nền cấp sâu hơn |
| Chữ | `--color-on-surface` | `#191c1e` | Chữ chính, không dùng đen tuyệt đối |
| Chữ | `--color-on-surface-variant` | `#475569` | Chữ phụ, nhãn |
| Đường | `--color-outline` | `#94a3b8` | Viền nhấn |
| Đường | `--color-outline-variant` | `#e2e8f0` | Viền mặc định của thẻ và ô nhập |
| Trạng thái | `--color-success` và `--color-success-soft` | `#059669`, `#d1fae5` | Thành công, còn chỗ, thiết bị hoạt động |
| Trạng thái | `--color-warning` và `--color-warning-soft` | `#d97706`, `#fef3c7` | Cảnh báo, gần hết chỗ |
| Trạng thái | `--color-error` và `--color-error-container` | `#dc2626`, `#fee2e2` | Lỗi, hết chỗ, cảnh báo cháy |
| Trạng thái | `--color-info` và `--color-info-soft` | `#0284c7`, `#e0f2fe` | Thông tin |
| Nhấn | `--color-tertiary-fixed` | `#8cf5e4` | Điểm nhấn dùng tiết chế |

Ba lưu ý khi dùng:

Một, `--shadow-*` được đặt về `none` có chủ đích. Muốn tạo chiều sâu thì lồng khối và dùng viền, không thêm đổ bóng.

Hai, bán kính: `--radius-full` cho nút, `--radius-lg` bằng 1.5rem cho thẻ và ô nhập. Nút tròn hơn thẻ, đây là tín hiệu cho người dùng biết cái nào bấm được.

Ba, nhiều trang hiện đang viết màu trực tiếp bằng class Tailwind mặc định như `bg-slate-50`, `text-blue-600` thay vì dùng token. Đây là nợ kỹ thuật. Khi sửa một trang, chuyển dần sang token để đổi màu chủ đề chỉ cần sửa một chỗ.

---

## 3. Thang chữ

Font `Inter`, khai báo trong `body`. Các lớp tiện dụng đã có trong `index.css`:

| Lớp | Cỡ | Dùng cho |
|---|---|---|
| `.text-display-lg` | 3.5rem | Số liệu lớn nhất trên một màn hình, ví dụ số chỗ trống |
| `.text-display-md` | 2.75rem | Số liệu chính trong thẻ |
| `.text-headline-lg` | 2rem | Tiêu đề trang |
| `.text-headline-sm` | 1.5rem | Tiêu đề mục, đã kèm khoảng cách trên 2rem |
| `.text-title-lg` | 1.25rem | Tiêu đề thẻ |
| `.text-title-md` | 1rem | Tiêu đề phụ |
| `.text-body-md` | 0.875rem | Nội dung chính |
| `.text-body-sm` | 0.8125rem | Nội dung phụ |
| `.text-label-md` | 0.75rem | Nhãn, chữ in hoa, giãn chữ 0.05em |
| `.text-label-sm` | 0.6875rem | Nhãn kỹ thuật: biển số, mốc thời gian, mã lượt gửi |

Cách dùng đặc trưng của hướng thiết kế này là ghép một số rất lớn với một nhãn rất nhỏ. Ví dụ số chỗ trống ở `display-lg` kèm nhãn `label-sm` ghi rõ đây là số chỗ trống dự kiến khi tới nơi và mốc thời gian cập nhật.

---

## 4. Quy tắc dựng khối

**Viền là công cụ phân cấp chính.** Thẻ luôn có viền một điểm ảnh màu `outline-variant` và bán kính `lg`. Không đổ bóng.

**Tạo chiều sâu bằng cách lồng khối.** Thẻ trắng trên nền `background` xám nhạt, bên trong dùng `surface-container-low` cho vùng nhóm nội dung.

**Khoảng trắng rộng.** Khoảng cách giữa các thẻ từ 1.5rem trở lên, đệm trong thẻ từ 1.5rem. Màn hình vận hành cho chủ bãi có thể chặt hơn vì cần mật độ thông tin cao, nhưng vẫn giữ viền và bán kính.

**Không dùng đường kẻ ngang trong thẻ.** Tách nội dung bằng khoảng trắng hoặc đổi nền nhẹ.

**Trạng thái phải đọc được không cần màu.** Người dùng có thể nhìn màn hình ngoài trời nắng, hoặc bị mù màu. Mỗi trạng thái cần có chữ kèm theo, không chỉ có màu.

---

## 5. Thành phần đã có trong code

| Thành phần | File | Ghi chú |
|---|---|---|
| `Button` | `src/components/ui/button.tsx` | Dùng `class-variance-authority`, có sáu biến thể và bốn kích cỡ. Mặc định là nút tròn có viền, không bóng |
| `Card` | `src/components/ui/card.tsx` | Bộ `Card`, `CardHeader`, `CardTitle`, `CardContent` theo khuôn quen thuộc |
| `Badge` | `src/components/ui/badge.tsx` | Năm biến thể theo trạng thái, chữ in hoa cỡ nhỏ, dùng cho nhãn trạng thái lượt gửi |
| `Brand` | `src/components/Brand.tsx` | Wordmark dùng chung, đọc tên từ `config/app.ts` |
| `SmartBookingModal` | `src/components/SmartBookingModal.tsx` | Modal nhiều bước: chọn thời gian, chọn dịch vụ, chọn xe, chờ hệ thống chấm điểm, xem kết quả. Đây là khuôn dùng lại được cho luồng đặt chỗ mới |
| `cn` | `src/services/utils.ts` | Gộp class Tailwind, dùng ở mọi thành phần |

Ba layout trong `src/layouts/`: `CustomerLayout` có thanh bên rộng 280 điểm ảnh và thanh trên có ô tìm kiếm, `GarageLayout` có thanh bên 256 điểm ảnh theo kiểu công cụ vận hành, `AdminLayout` hiện chỉ là khung trống cần dựng lại theo khuôn `GarageLayout`.

---

## 6. Việc cần làm về giao diện

| Việc | Vì sao |
|---|---|
| Chuyển màu cắm trực tiếp sang token | Hiện đổi màu chủ đề phải sửa hàng chục file |
| Thống nhất ngôn ngữ hiển thị về tiếng Việt | Hiện trộn tiếng Anh và tiếng Việt trong cùng một màn hình |
| Bỏ phụ thuộc ảnh và font từ dịch vụ ngoài | Mất mạng là giao diện hỏng, và dữ liệu người dùng bị gửi ra ngoài |
| Dựng trạng thái rỗng và trạng thái lỗi cho mọi trang | Hiện một số trang không có gì để hiển thị khi API trả về rỗng |
| Dựng `AdminLayout` và nhóm màn hình quản trị | Vai trò quản trị nền tảng chưa có giao diện thật |
| Kiểm tra trên màn hình điện thoại | Ứng dụng cho người lái xe sẽ dùng chủ yếu trên điện thoại, nhưng bố cục hiện tại thiên về máy tính với thanh bên cố định |

Việc cuối là việc quan trọng nhất về mặt sản phẩm. Người lái xe tìm chỗ đỗ khi đang ngồi trong xe, nên bố cục cho điện thoại phải là bố cục chính, không phải bản rút gọn của bố cục máy tính.
