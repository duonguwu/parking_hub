# Parking HUB: hệ thống đang có những gì

Tài liệu này giới thiệu các tính năng hiện có của Parking HUB theo ba vai trò: tài xế, chủ bãi và quản trị viên. Đọc xong, bạn sẽ biết mỗi vai trò làm được gì và dùng ở màn hình nào.

---

## Trước khi bắt đầu

### Đăng nhập

Mọi vai trò dùng chung một trang đăng nhập. Sau khi đăng nhập, hệ thống tự đưa bạn tới đúng khu vực của mình:

| Vai trò | Khu vực |
|---|---|
| Tài xế | Ứng dụng tài xế |
| Chủ bãi, quản lý bãi, nhân viên bãi | Cổng chủ bãi |
| Quản trị viên | Cổng quản trị |

Tài xế tự đăng ký tài khoản ngay ở trang đăng nhập.

### Tài khoản demo

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Tài xế | `minh.12`, `duong.12`, `driver` | `test123@` |
| Chủ bãi | `vin.q1`, `vin.landmark`, `vin.q3`, `owner`, `manager`, `staff` | `test123@` |
| Quản trị viên | `admin`, `ops` (quản trị viên có thể chuyển sang giao diện tài xế và chủ bãi) | `test123@` |
| Tài xế (dữ liệu sinh tự động) | `customer_01` tới `customer_40` | `Customer@2026` |
| Chủ bãi (dữ liệu sinh tự động) | `owner_<quận>_<số>`, ví dụ `owner_q1_01` | `Owner@2026` |

Danh sách đầy đủ ở [TEST_ACCOUNTS.md](TEST_ACCOUNTS.md).

Dữ liệu demo gồm khoảng 262 bãi đỗ ở 18 quận TP.HCM. Tên bãi, giá, lượt đặt và đánh giá đều là dữ liệu giả.

### Ba cách hệ thống phân loại một bãi

Bạn sẽ gặp ba thông tin sau ở mọi màn hình:

**Loại hình bãi.** Có tám loại: nhà xe chuyên dụng, hầm toà nhà văn phòng, hầm chung cư, nhà xe có mái, bãi ngoài trời, đầu mối giao thông, lòng đường hoặc công cộng, chỗ nhỏ hộ dân.

**Cấp tích hợp.** Cấp cho biết dữ liệu chỗ trống của bãi đáng tin tới đâu, và quyết định bãi có nhận đặt chỗ hay không:

| Cấp | Tên | Chỗ trống hiển thị | Đặt chỗ |
|---|---|---|---|
| 1 | Danh mục | "Chưa có dữ liệu chỗ trống" | Chỉ xem, chưa đặt được |
| 2 | Có cập nhật | Số chỗ kèm giờ cập nhật, ví dụ "Cập nhật lúc 14:05" | Đặt được, nhưng bãi phải xác nhận |
| 3 | Kết nối cảm nhận | Số chỗ theo thời gian thực | Giữ chỗ ngay, tự xác nhận |
| 4 | Kết nối đầy đủ | Số chỗ theo thời gian thực | Giữ chỗ ngay, được ưu tiên khi xếp hạng |

**Hạng sao, từ 1 tới 5.** Hạng sao đo cơ sở vật chất. Quản trị viên chấm hạng bằng checklist kiểm định thực địa thang 100 điểm, gồm sáu nhóm: kết cấu, an ninh, che chắn, tiếp cận, phòng cháy chữa cháy và tiện ích. Từ 85 điểm trở lên là 5 sao. Nhà xe cao tầng có bảo vệ 24/7 thường đạt 5 sao, sân đất ngoài trời thường chỉ 1 tới 2 sao.

Ngoài ra, mỗi bãi có **điểm chất lượng** từ 0 tới 100. Hệ thống tự tính điểm này từ cách bãi vận hành: tỉ lệ giữ đúng chỗ, số khiếu nại, tỉ lệ khách quay lại và điểm đánh giá.

Cạnh tên bãi có thể có các **huy hiệu** sau, cũng do hệ thống tự gắn: Đã kiểm định, Bãi chuyên dụng, An toàn PCCC, Thời gian thực, Có sạc EV, Giữ đúng chỗ ≥ 98%.

### Màu chỗ trống trên bản đồ

| Màu | Ý nghĩa |
|---|---|
| Xanh lá | Còn chỗ |
| Vàng | Sắp hết |
| Đỏ | Hết chỗ |
| Xám | Chưa có dữ liệu |

---

## 1. Tài xế

### Trang chủ

- Xem xe mặc định và các lượt đặt đang hoạt động: đang chờ bãi xác nhận, đã giữ chỗ, hoặc đang gửi.
- Xem các bãi gần vị trí của bạn, bãi còn chỗ được xếp lên trước.
- Xem thống kê cá nhân: số lượt đã gửi, tổng chi tiêu, số bãi đã từng gửi.
- Lối tắt mở bản đồ hoặc mở **Gợi ý thông minh**.

### Bản đồ bãi đỗ

- Bản đồ hiển thị các bãi quanh vị trí hiện tại của bạn. Mỗi marker có màu theo tình trạng chỗ trống, kèm số chỗ còn lại.
- Muốn tìm quanh một nơi khác, chẳng hạn điểm đến, bạn bấm vào điểm đó trên bản đồ rồi chọn **Tìm quanh điểm này**.
- Ô tìm kiếm theo tên bãi hoặc tên đường.
- **Bộ lọc** gồm:
  - bán kính tìm và loại bãi;
  - có mái che hoặc hầm, có sạc xe điện, có bảo vệ 24/7, không ngập;
  - chỉ bãi còn chỗ, mở cửa 24 giờ;
  - hạng sao tối thiểu, chiều cao xe, giá giờ tối đa.
- Mỗi thẻ bãi có tên, khoảng cách, hạng sao, loại hình, huy hiệu, số chỗ trống và giá theo giờ.
- Trên điện thoại, nút ở đáy màn hình chuyển qua lại giữa bản đồ và danh sách.

### Chi tiết bãi

- **Thông tin chung:** địa chỉ, loại hình, hạng sao, cấp tích hợp, huy hiệu.
- **Chỗ trống:** số chỗ hiện tại kèm mốc cập nhật, cùng dự báo sau 1, 2 và 3 giờ.
- **Thuộc tính:** che chắn, giới hạn chiều cao, bảo vệ, camera, sạc xe điện, nguy cơ ngập, cách đỗ, giờ mở cửa.
- **Bảng giá** cho từng dịch vụ:
  - gửi theo giờ tính theo block, ví dụ "25.000đ cho 60 phút đầu, 15.000đ mỗi 60 phút tiếp, trần 200.000đ/ngày";
  - các gói trọn như qua đêm, theo ngày, gói tháng;
  - phụ thu giờ cao điểm, nếu bãi có đặt.
- **Biểu đồ lấp đầy theo giờ** trong ngày, giờ hiện tại được tô đậm.
- **Độ tin cậy và đánh giá:** tỉ lệ giữ đúng chỗ, điểm đánh giá, các nhận xét gần đây.

### Đặt chỗ

Bạn đặt chỗ ngay trên trang chi tiết bãi:

1. Chọn dịch vụ: gửi theo giờ, qua đêm, theo ngày…
2. Chọn ngày, giờ bắt đầu và thời lượng.
3. Chọn xe đã lưu, hoặc nhập biển số.
4. Xem **giá dự kiến**, giá tự tính lại mỗi khi bạn đổi lựa chọn.
5. Bấm xác nhận.

Kết quả tuỳ theo cấp của bãi:

- **Bãi cấp 3 và 4:** chỗ được giữ ngay.
- **Bãi cấp 2:** yêu cầu chuyển sang trạng thái chờ, bãi sẽ xác nhận hoặc từ chối.
- **Bãi cấp 1, hoặc bãi đang tạm ngưng nhận khách:** không đặt được, màn hình hiện lý do.

Bãi giữ chỗ cho bạn thêm một khoảng sau giờ hẹn, thường là 15 phút. Quá khoảng này mà xe chưa tới, lượt đặt bị tính là không đến.

### Gợi ý thông minh

Bạn chọn vị trí, thời điểm, dịch vụ và xe. Hệ thống đề xuất vài bãi phù hợp nhất, mỗi bãi kèm thời gian di chuyển, số chỗ dự kiến lúc bạn tới, giá, lý do được chọn và điểm cần cân nhắc. Bạn đặt chỗ ngay từ danh sách gợi ý.

### Lượt đặt của tôi

- Danh sách có hai tab: **Đang hoạt động** và **Lịch sử**.
- Mở một lượt để xem chi tiết và **dòng thời gian**: đã gửi yêu cầu, bãi giữ chỗ, xe vào, xe ra, đã thanh toán.
- Trong lúc bãi đang giữ chỗ, màn hình nhắc "Bãi giữ chỗ đến HH:MM".
- Có thể **huỷ** lượt đang chờ xác nhận hoặc đã giữ chỗ.
- Sau khi xe ra, bạn xem số tiền cuối cùng và tình trạng thanh toán, rồi **đánh giá** bãi từ 1 tới 5 sao, kèm nhận xét nếu muốn.

### Xe của tôi

- Thêm xe: biển số, hãng, dòng xe, màu, kiểu thân xe.
- Chọn xe mặc định. Xe mặc định được điền sẵn khi bạn đặt chỗ.

### Hồ sơ

Hồ sơ hiển thị tên, tên đăng nhập và vai trò. Có lối tắt tới trang xe và nút đăng xuất.

### Ý nghĩa trạng thái lượt đặt

| Trạng thái | Ý nghĩa |
|---|---|
| Chờ bãi xác nhận | Bãi cấp 2 chưa trả lời |
| Đã giữ chỗ | Bãi đã giữ chỗ cho bạn |
| Đang gửi | Xe đang ở trong bãi |
| Đã ra bãi | Đã xong, đã tính tiền |
| Đã huỷ | Bạn huỷ, hoặc bãi huỷ |
| Bãi từ chối | Bãi cấp 2 không nhận yêu cầu |
| Không đến | Quá thời gian giữ chỗ mà xe chưa tới |
| Hết hạn | Tới giờ hẹn mà bãi vẫn chưa xác nhận |

---

## 2. Chủ bãi

Chủ bãi, quản lý bãi và nhân viên bãi dùng chung cổng này. Quyền thao tác khác nhau một chút theo vai trò: nhân viên chủ yếu xử lý xe vào ra và cập nhật chỗ trống.

### Tổng quan

- **Chỗ trống hiện tại:** số chỗ còn lại trên tổng sức chứa.
- **Cập nhật chỗ trống:** dùng nút cộng, trừ hoặc nhập số xe đang trong bãi rồi lưu. Đây là cách cập nhật dành cho bãi cấp 2. Màn hình ghi rõ nguồn số liệu và giờ cập nhật gần nhất.
- **Các con số nhanh:**
  - xe đang trong bãi;
  - lượt chờ xác nhận, bấm vào để mở danh sách;
  - doanh thu hôm nay so với hôm qua;
  - số lượt chưa thanh toán.
- **Sắp đến trong 2 giờ:** các lượt đặt sắp tới.
- **Biểu đồ lấp đầy:** xem theo 24 giờ hoặc trung bình theo giờ trong 7 ngày.
- Bãi chưa được duyệt hoặc đang bị tạm ngưng có thông báo ở đầu trang.

### Lượt đặt và xe vào ra

Màn hình chia bốn tab, mỗi tab kèm số lượng:

| Tab | Gồm | Thao tác |
|---|---|---|
| Sắp đến | Lượt đã giữ chỗ | Check-in (đối chiếu biển số), đánh dấu không đến (chỉ khi đã quá thời gian giữ chỗ), huỷ |
| Chờ xác nhận | Yêu cầu ở bãi cấp 2 | Xác nhận, hoặc từ chối kèm lý do |
| Trong bãi | Xe đang gửi | Xem số tiền tạm tính, check-out và chọn cách thu: tiền mặt, chuyển khoản, hoặc chưa thu |
| Lịch sử | Lượt đã xong, huỷ, từ chối, không đến, hết hạn | Ghi nhận **Đã thu tiền** cho lượt chưa thanh toán |

Ngoài ra:

- Tìm nhanh theo biển số hoặc mã lượt.
- **Xe vãng lai vào:** nhập biển số và chọn dịch vụ để ghi nhận xe không đặt trước. Khi xe ra, bạn check-out ở tab Trong bãi như mọi xe khác.
- Khi check-out, hệ thống tự tính tiền theo thời gian gửi thực tế và bảng giá của bãi.

### Hồ sơ bãi

Chủ bãi tự sửa các nhóm thông tin sau:

- **Thông tin chung:** tên, mô tả, loại hình, địa chỉ, người liên hệ, bật hoặc tắt nhận đặt chỗ.
- **Sức chứa:**
  - tổng số chỗ, chỗ cho khách vãng lai, chỗ cho thuê tháng;
  - tỉ lệ tối đa được đặt trước;
  - số phút giữ chỗ sau giờ hẹn.
- **Thuộc tính:**
  - che chắn, chiều cao tối đa, bảo vệ, camera;
  - trụ sạc xe điện, nguy cơ ngập, cách đỗ;
  - chiếu sáng, mặt sàn, phòng cháy chữa cháy, nhà vệ sinh.
- **Giờ mở cửa:** mở 24 giờ, hoặc đặt giờ riêng cho từng ngày, có thể đánh dấu ngày nghỉ.
- **Cổng vào xe:** bấm lên bản đồ để đánh dấu.

Cấp tích hợp và hạng sao chỉ hiển thị để xem. Hai mục này do quản trị viên kiểm định và chấm, chủ bãi không tự sửa.

### Dịch vụ và bảng giá

- Bật thêm dịch vụ từ danh mục chung của nền tảng: gửi theo giờ, qua đêm, theo ngày, gói ngày làm việc, gói tháng, sạc xe điện, rửa xe, đỗ hộ.
- Mỗi dịch vụ đặt giá theo một trong hai cách:
  - **Theo block:** giá block đầu, giá các block tiếp theo, kèm trần theo ngày;
  - **Trọn gói:** một giá cho mỗi đêm, mỗi ngày hoặc mỗi tháng.
- Thêm quy tắc **giờ cao điểm**: chọn ngày trong tuần, khung giờ và hệ số nhân giá.
- Sửa ghi chú, ngừng cung cấp một dịch vụ.
- Xem số lượt đặt trong 30 ngày của từng dịch vụ.

### Phân tích

Chọn khoảng thời gian 7, 30 hoặc 90 ngày. Màn hình hiển thị:

- **Doanh thu, số lượt gửi, thời lượng gửi trung bình, giá trị trung bình mỗi lượt.** Doanh thu và số lượt kèm mức tăng giảm so với kỳ trước.
- **Biểu đồ doanh thu theo ngày.**
- **Lấp đầy theo giờ,** so sánh ngày thường với cuối tuần.
- **Nguồn lượt:** đặt qua ứng dụng hay khách vãng lai.
- **Dịch vụ:** số lượt và doanh thu từng dịch vụ.
- **Trạng thái lượt đặt** và **khách hàng:** tổng số khách, số khách quay lại.

### Chất lượng

- **Điểm chất lượng.** Bãi cần ít nhất 5 lượt gửi hoàn tất thì mới có điểm.
- **Chỉ số vận hành:** tỉ lệ giữ đúng chỗ, tỉ lệ khách không đến, tỉ lệ khách quay lại, số khiếu nại, điểm đánh giá.
- **Cấp tích hợp hiện tại** kèm mô tả.
- **Hạng sao:** điểm checklist, điểm từng nhóm, các mục đã đạt và chưa đạt, ghi chú của người kiểm định, ngày kiểm định lại.
- **Huy hiệu** đang có.
- **Gợi ý cải thiện,** ví dụ nâng cấp tích hợp, hoặc các tiêu chí kiểm định đang mất nhiều điểm nhất.

---

## 3. Quản trị viên

### Tổng quan mạng lưới

- **Bãi đỗ:** số bãi đang hoạt động, chờ duyệt, tạm ngưng.
- **Chỗ đỗ:** tổng số chỗ và tỉ lệ lấp đầy toàn mạng, chỉ tính các bãi có dữ liệu.
- **Lượt đặt và doanh thu 30 ngày,** cùng tỉ lệ giữ đúng chỗ toàn mạng.
- **Biểu đồ theo ngày** cho lượt đặt và doanh thu.
- **Phân bố bãi** theo quận, theo cấp tích hợp, theo loại hình và theo hạng sao.
- **Các bãi nhiều lượt gửi nhất** và **số người dùng theo vai trò.**
- Lối tắt tới danh sách bãi đang chờ duyệt.

### Bản đồ mạng lưới

Bản đồ hiển thị toàn bộ bãi, lọc được theo trạng thái và cấp tích hợp. Bấm vào một bãi để xem tóm tắt và mở trang chi tiết.

### Quản lý bãi đỗ

- **Danh sách** lọc theo trạng thái, cấp tích hợp, loại hình, quận, và tìm theo tên.
- **Duyệt nhanh** các bãi chờ duyệt ngay trong danh sách.
- **Trang chi tiết bãi:**
  - hồ sơ đầy đủ: sức chứa, thuộc tính, liên hệ, chủ bãi, chỉ số vận hành, vị trí trên bản đồ;
  - đổi **trạng thái**: duyệt, tạm ngưng, mở lại;
  - đổi **cấp tích hợp** từ 1 tới 4;
  - bật hoặc tắt nhận đặt chỗ.
- **Kiểm định và chấm hạng sao:**
  - Checklist 100 điểm chia theo nhóm. Điểm và số sao tự tính lại mỗi khi bạn tích một mục.
  - Nút **Dùng gợi ý từ thuộc tính** điền sẵn checklist theo những gì chủ bãi đã khai.
  - Thêm ghi chú rồi lưu. Bãi được đánh dấu "Đã kiểm định", và lịch kiểm định lại tự đặt sau 6 tháng.

Bãi mới đăng ký luôn ở trạng thái **chờ duyệt**. Quản trị viên kiểm tra, duyệt và đặt cấp tích hợp thì bãi mới xuất hiện với tài xế.

### Người dùng

- Danh sách người dùng, lọc theo vai trò và tìm theo tên, email hoặc số điện thoại.
- Khoá hoặc mở khoá tài khoản. Không khoá được tài khoản quản trị cấp cao.

### Danh mục dịch vụ

- Danh mục dịch vụ chung mà mọi bãi chọn từ đó.
- Thêm dịch vụ mới: mã, tên, mô tả, nhóm, đơn vị tính, khoảng giá tham khảo, thứ tự hiển thị, đánh dấu phổ biến.
- Sửa thông tin, ẩn hoặc hiện dịch vụ. Dịch vụ bị ẩn không còn xuất hiện cho chủ bãi và tài xế.

---

## Chưa có trong phiên bản này

Các tính năng sau đang nằm trong kế hoạch, chưa có trên hệ thống:

- Camera AI: tự đếm chỗ trống, nhận diện biển số, phát hiện khói và lửa. Số liệu thời gian thực ở bãi cấp 3 và 4 hiện là **dữ liệu mô phỏng**.
- Thanh toán trực tuyến. Hiện chủ bãi chỉ ghi nhận đã thu tiền mặt hoặc chuyển khoản.
- Mua gói tháng và gói ngày làm việc trên ứng dụng. Hiện các gói này chỉ hiển thị trong bảng giá.
- Thông báo đẩy, dữ liệu thời tiết và giao thông, gợi ý cá nhân hoá theo thói quen.
- Hộ dân tự đăng ký chỗ đỗ nhỏ.
