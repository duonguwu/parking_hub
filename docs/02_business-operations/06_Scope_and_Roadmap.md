# 06. Phạm vi và lộ trình

Làm gì, không làm gì, theo mốc thời gian nào, và rủi ro nằm ở đâu

Phiên bản: 1.0
Ngày: 21/08/2026
Mốc gần nhất: hạn nộp hồ sơ vòng Tuyển chọn của Data for Life mùa 4 là 15/09/2026

---

## Mục lục

1. [Nguyên tắc xác định phạm vi](#1-nguyên-tắc-xác-định-phạm-vi)
2. [Trong phạm vi, ngoài phạm vi, hoãn lại](#2-trong-phạm-vi-ngoài-phạm-vi-hoãn-lại)
3. [Ranh giới hệ thống và các bên tích hợp](#3-ranh-giới-hệ-thống-và-các-bên-tích-hợp)
4. [Việc phải làm trong 25 ngày tới](#4-việc-phải-làm-trong-25-ngày-tới)
5. [Lộ trình theo bốn vòng của cuộc thi](#5-lộ-trình-theo-bốn-vòng-của-cuộc-thi)
6. [Lộ trình 12 tháng sau cuộc thi](#6-lộ-trình-12-tháng-sau-cuộc-thi)
7. [Tiêu chí thành công từng giai đoạn](#7-tiêu-chí-thành-công-từng-giai-đoạn)
8. [Đội ngũ và vai trò](#8-đội-ngũ-và-vai-trò)
9. [Rủi ro và cách xử lý](#9-rủi-ro-và-cách-xử-lý)
10. [Phụ thuộc và giả định](#10-phụ-thuộc-và-giả-định)
11. [Điều kiện điều chỉnh hướng đi](#11-điều-kiện-điều-chỉnh-hướng-đi)

---

## 1. Nguyên tắc xác định phạm vi

**Nguyên tắc một, một khu vực làm cho xong thay vì nhiều khu vực làm dở.** Toàn bộ giai đoạn đầu tập trung vào một khu vực đô thị được chọn, với mục tiêu đạt mật độ đủ để sản phẩm thực sự dùng được. Không mở khu vực thứ hai trước khi khu vực thứ nhất chứng minh được cả ba điều: dữ liệu chính xác, người dùng quay lại, và chủ bãi ở lại.

**Nguyên tắc hai, chiều sâu của lớp cảm nhận quan trọng hơn chiều rộng của tính năng.** Nếu phải chọn giữa việc thêm năm tính năng cho người dùng và việc nâng độ chính xác đếm chỗ trống từ 90 lên 97 phần trăm, chọn việc thứ hai. Toàn bộ sản phẩm dựa trên niềm tin vào dữ liệu.

**Nguyên tắc ba, mọi cam kết với người dùng phải có chỗ dựa vật lý.** Không bật tính năng giữ chỗ ở bãi chưa qua giai đoạn kiểm chứng. Không hiển thị số chỗ trống mà không kèm mốc thời gian và mức tin cậy.

**Nguyên tắc bốn, tính năng nào phụ thuộc dữ liệu tích luỹ thì để sau.** Cá nhân hoá, dự báo dài hạn, định giá theo nhu cầu đều cần vài tuần tới vài tháng dữ liệu thật. Làm sớm sẽ cho kết quả kém, và người dùng sẽ kết luận rằng tính năng đó không hoạt động, chứ không kết luận rằng nó chưa đủ dữ liệu.

---

## 2. Trong phạm vi, ngoài phạm vi, hoãn lại

### 2.1. Trong phạm vi giai đoạn đầu

| Hạng mục | Nội dung |
|---|---|
| Lớp cảm nhận | Đếm chỗ trống bằng camera, nhận diện biển số hai bước tại cổng, phát hiện khói và lửa. Suy luận trên thiết bị biên tại bãi |
| Lớp điều phối | Tìm bãi theo điểm đến, dự đoán chỗ trống tại thời điểm tới nơi, xếp hạng theo bộ trọng số mặc định, bộ lọc theo thuộc tính bãi |
| Lớp mạng lưới | Giữ chỗ theo khoảng thời gian, vào ra tự động, thanh toán không tiền mặt, hồ sơ và điểm tin cậy của bãi |
| Ứng dụng người lái xe | Ứng dụng di động là kênh chính |
| Cổng chủ bãi | Bảng điều khiển vận hành, đối soát doanh thu, cấu hình giá và hạn mức giữ chỗ, quản lý cảnh báo |
| Ứng dụng bảo vệ | Ba chức năng như mô tả tại mục 8.2 của [tài liệu 05](05_Onboarding_Playbook.md) |
| Cổng quản trị mạng lưới | Theo dõi sức khoẻ từng bãi, bản đồ nhu cầu chưa được phục vụ, quản lý onboard |
| Tuân thủ dữ liệu | Thời hạn lưu trữ và xoá tự động, nhật ký truy cập, trang quản lý dữ liệu cá nhân cho người dùng |

### 2.2. Ngoài phạm vi, và sẽ không làm

| Hạng mục | Vì sao không làm |
|---|---|
| Thay thế hệ thống phòng cháy chữa cháy hoặc thiết bị cảnh báo khí | Đây là lĩnh vực có quy chuẩn riêng và cần đơn vị chuyên môn. Parking HUB chỉ bổ sung lớp phát hiện sớm bằng thị giác máy tính |
| Tự động kích hoạt hệ thống chữa cháy | Một cảnh báo sai dẫn tới phun nước trong hầm đầy xe là thiệt hại lớn. Chỉ xét sau khi tỷ lệ báo động sai đã được chứng minh rất thấp qua nhiều tháng |
| Xử lý vi phạm hoặc xử phạt | Không phải chức năng của một nền tảng tư nhân. Vai trò của dự án là cung cấp dữ liệu và điều hướng nhu cầu về chỗ đỗ hợp pháp |
| Nhận diện khuôn mặt | Không cần cho bài toán đỗ xe, và tạo ra rủi ro pháp lý cùng rủi ro về quyền riêng tư không tương xứng với lợi ích |
| Xây dựng bãi đỗ xe | Không phải năng lực của đội và không phải mô hình của dự án |
| Cảm biến gắn từng ô đỗ | Kinh tế không phù hợp với thị trường Việt Nam, đã phân tích tại mục 2 của [tài liệu 02](../01_strategy-product/02_Problem_Deep_Dive.md) |

### 2.3. Hoãn lại có chủ đích

| Hạng mục | Điều kiện để mở |
|---|---|
| Cá nhân hoá theo thói quen và gợi ý chủ động | Có ít nhất bốn tuần dữ liệu hành vi thật của một tệp người dùng đủ lớn |
| Dự báo chỗ trống cho các mốc nhiều ngày | Có ít nhất tám tuần dữ liệu vận hành của bãi đó |
| Định giá theo nhu cầu | Sau khi bán giờ thấp điểm bằng bảng giá cố định đã chứng minh có hiệu quả |
| Hợp đồng đội xe | Sau khi mạng lưới phủ được vùng hoạt động của ít nhất một khách hàng mục tiêu |
| Trợ lý hội thoại | Sau khi ba tính năng lõi ổn định |
| Chia sẻ dữ liệu chính thức cho cơ quan quản lý | Sau khi có quy trình tuân thủ đầy đủ và có ý kiến pháp lý |
| Gửi xe đổi phương tiện công cộng | Sau khi có dữ liệu về điểm trung chuyển trong khu vực |
| Mở khu vực thứ hai | Sau khi khu vực thứ nhất đạt các tiêu chí ở mục 7 |

---

## 3. Ranh giới hệ thống và các bên tích hợp

| Thành phần | Vai trò | Tình trạng |
|---|---|---|
| Thiết bị biên tại bãi | Chạy bốn model thị giác, ghi nhận cục bộ khi mất mạng, gửi kết quả lên trung tâm | Cần xây mới phần triển khai, model đã có |
| Nền tảng trung tâm | Quản lý bãi, lượt gửi, giữ chỗ, thanh toán, dự báo, xếp hạng | Phần lớn đã có trong nền tảng hiện tại của đội |
| Dịch vụ định tuyến và bản đồ | Thời gian di chuyển, tuyến đường, quãng đi bộ, hiển thị bản đồ | Đã có, xây trên dữ liệu bản đồ mở, có cơ chế dự phòng |
| Dịch vụ thời tiết | Yếu tố ngữ cảnh cho dự báo và cho cảnh báo ngập | Đã có |
| Cổng thanh toán | Thanh toán không tiền mặt, thu định kỳ cho gói tháng | Cần tích hợp, lựa chọn nhà cung cấp là quyết định cần chốt |
| Định danh và xác thực người dùng | Xác thực để bảo đảm an toàn cho phân khúc chỗ đỗ hộ dân, và cho các nghĩa vụ tuân thủ | Cần nghiên cứu khả năng và thủ tục tích hợp với hệ sinh thái định danh quốc gia. Đây là hạng mục có giá trị lớn cho hồ sơ cuộc thi và cần được xác minh về mặt thủ tục, không nên tuyên bố trước khi xác minh |
| Kênh chia sẻ dữ liệu cho cơ quan quản lý | Báo cáo tổng hợp phi định danh, cảnh báo an toàn | Cần thiết kế và cần cơ sở pháp lý |
| Hệ thống barrier và thiết bị hiện có của bãi | Liên động khi chủ bãi đồng ý, luôn giữ phương án thủ công | Cần khảo sát theo từng bãi |

Về mục định danh và xác thực, cần nói rõ thái độ trong tài liệu: đây là hướng có giá trị cao và phù hợp với bối cảnh Đề án 06, nhưng khả năng và thủ tục tích hợp phải được xác minh với cơ quan có thẩm quyền trước khi đưa vào cam kết. Trong hồ sơ nộp cuộc thi, nên trình bày ở dạng đề xuất tích hợp và nêu rõ lợi ích, không trình bày như một việc đã có.

---

## 4. Việc phải làm trong 25 ngày tới

Hôm nay là 21/08/2026. Hạn nộp hồ sơ là 15/09/2026. Đây là danh sách việc theo thứ tự ưu tiên, với nguyên tắc: hồ sơ mạnh nhất là hồ sơ có một thứ đang chạy thật, không phải hồ sơ có nhiều trang.

| Tuần | Việc | Kết quả cần có |
|---|---|---|
| Tuần 1, 21/08 tới 27/08 | Chốt tên dự án và định vị. Hoàn thiện bộ tài liệu này. Kiểm chứng lại toàn bộ số liệu trong [tài liệu 99](../99_reference/99_Sources_and_Assumptions.md) từ nguồn chính thức. Rà soát thể lệ và mẫu hồ sơ chính thức trên trang của ban tổ chức | Tên đã chốt, bộ tài liệu đã rà soát, danh mục yêu cầu của hồ sơ |
| Tuần 1 và 2 | Dựng lại bốn model thị giác trên môi trường hiện tại, kiểm thử trên video bãi đỗ thật, đo lại độ chính xác để có số liệu trung thực đưa vào hồ sơ | Bảng số liệu kết quả kiểm thử của bốn model, có ảnh và video minh chứng |
| Tuần 2, 28/08 tới 03/09 | Chuyển nền tảng hiện có sang nghiệp vụ bãi đỗ ở mức đủ để demo: danh mục bãi, tìm theo điểm đến, dự đoán chỗ trống, giữ chỗ | Một bản demo chạy được từ đầu tới cuối với dữ liệu của hai tới ba bãi mẫu |
| Tuần 2 và 3 | Tiếp cận từ ba tới năm bãi trong khu vực mục tiêu, xin khảo sát. Ưu tiên một hầm chung cư có xe điện và một hầm toà nhà | Ít nhất một biên bản ghi nhớ hoặc một thư đồng ý cho thử nghiệm. Đây là hạng mục có giá trị cao nhất cho hồ sơ |
| Tuần 3, 04/09 tới 10/09 | Viết hồ sơ nộp theo mẫu của ban tổ chức, dựa trên [tài liệu 07](../03_submission/07_Proposal_DataForLife.md). Chuẩn bị video demo ngắn | Bản hồ sơ hoàn chỉnh, video demo |
| Tuần 4, 11/09 tới 15/09 | Rà soát pháp lý và bảo vệ dữ liệu trong hồ sơ. Rà soát lần cuối các con số. Nộp | Đã nộp trước hạn ít nhất hai ngày |

Ba việc có giá trị cao nhất trong danh sách này, nếu buộc phải chọn: một bản demo chạy được từ đầu tới cuối, một bộ số liệu thật về độ chính xác của bốn model, và một thư đồng ý cho thử nghiệm từ một bãi thật. Ba thứ đó nói được nhiều hơn bất kỳ trang mô tả nào, đặc biệt với một cuộc thi tuyên bố rõ rằng họ tìm giải pháp triển khai được chứ không chỉ tìm ý tưởng.

---

## 5. Lộ trình theo bốn vòng của cuộc thi

| Vòng | Thời gian | Mục tiêu sản phẩm | Mục tiêu thực địa | Kết quả cần chứng minh |
|---|---|---|---|---|
| Tuyển chọn hồ sơ | Tới 15/09/2026 | Demo chạy được từ đầu tới cuối, số liệu kiểm thử bốn model | Từ một tới ba bãi đồng ý cho thử nghiệm | Bài toán rõ, giải pháp khả thi, đội có năng lực thực thi và đã có sản phẩm chạy |
| Chinh phục và phát triển giải pháp | Sau khi qua vòng hồ sơ | Lắp đặt thật tại bãi đầu tiên, hoàn thiện luồng giữ chỗ và thanh toán, cổng chủ bãi | Từ ba tới năm bãi kết nối cấp 3, bắt đầu có người dùng thật trong khu vực | Dữ liệu chỗ trống chính xác trên bãi thật, có lượt đỗ xe hoàn tất qua nền tảng |
| Triển lãm | Theo lịch ban tổ chức | Sản phẩm ở trạng thái trình diễn được, có bảng số liệu vận hành thật | Từ năm tới mười bãi, mở rộng trong cùng khu vực | Có số liệu thật về độ chính xác, số lượt, thời gian tiết kiệm, và ít nhất một tình huống cảnh báo an toàn nếu có |
| Chung kết | Theo lịch ban tổ chức | Hoàn thiện phần trình bày, tài liệu kỹ thuật, phương án nhân rộng | Đủ dữ liệu để trình bày tác động | Bằng chứng về tác động xã hội, phương án nhân rộng cho các đô thị khác, và phương án chia sẻ dữ liệu cho cơ quan quản lý |

Lưu ý về cơ cấu điểm ở mùa trước, gồm điểm kỹ thuật tối đa 40, điểm trình bày tối đa 30, điểm khả năng ứng dụng tối đa 20 và điểm bình chọn trực tuyến tối đa 10. Hai hàm ý. Thứ nhất, điểm kỹ thuật là phần lớn nhất, nên phần bốn model thị giác và kiến trúc triển khai trên thiết bị biên phải được trình bày sâu và có số liệu. Thứ hai, điểm trình bày cộng điểm bình chọn chiếm 40, tức là ngang phần kỹ thuật, nên việc kể được câu chuyện rõ ràng và dễ hiểu cho công chúng là việc phải đầu tư thật, không phải việc làm cho có.

---

## 6. Lộ trình 12 tháng sau cuộc thi

| Giai đoạn | Sản phẩm | Mạng lưới | Kinh doanh | Mục tiêu |
|---|---|---|---|---|
| Tháng 1 tới 3 | Ổn định lớp cảm nhận, hoàn thiện đối soát doanh thu, mô đun an toàn đạt ngưỡng báo động sai | 10 tới 20 bãi trong một khu vực, cộng chỗ đỗ hộ dân | Bật phí phần mềm và mô đun an toàn. Bắt đầu chia doanh thu trên lượt mới | Chứng minh dữ liệu chính xác và chủ bãi trả tiền |
| Tháng 4 tới 6 | Dự báo chỗ trống nhiều ngày, gói tháng, bán giờ thấp điểm | 30 tới 50 bãi, mở khu vực thứ hai nếu khu vực thứ nhất đạt tiêu chí | Gói tháng cho người lái xe, tiếp cận khách đội xe đầu tiên | Đạt điểm tự trang trải chi phí cố định |
| Tháng 7 tới 9 | Cá nhân hoá, xếp hạng theo trọng số riêng, ưu đãi có điều kiện | 80 tới 120 bãi, hai tới ba khu vực | Hợp đồng đội xe, kênh tự đăng ký cho bãi nhỏ | Chứng minh mô hình nhân rộng được, chi phí onboard giảm |
| Tháng 10 tới 12 | Chia sẻ dữ liệu cho cơ quan quản lý, mở giao diện cho đối tác | Trên 150 bãi, mở thành phố thứ hai | Dịch vụ kèm theo trong bãi, chuẩn bị vòng vốn tiếp theo | Có vị thế hạ tầng dữ liệu giao thông tĩnh tại ít nhất một địa phương |

Các con số về số bãi là mục tiêu định hướng, cần điều chỉnh sau khi có dữ liệu thật về tốc độ onboard từ hai mươi bãi đầu tiên.

---

## 7. Tiêu chí thành công từng giai đoạn

Nguyên tắc: mỗi giai đoạn chỉ có ba tới bốn tiêu chí, và phải là tiêu chí có thể trả lời đúng hoặc sai, không phải tiêu chí mô tả.

### Giai đoạn hồ sơ, tới 15/09/2026

| Tiêu chí | Đạt là gì |
|---|---|
| Demo chạy được | Một người ngoài đội có thể mở ứng dụng, tìm bãi theo điểm đến, thấy dự đoán chỗ trống, và giữ chỗ thành công |
| Số liệu model trung thực | Có bảng độ chính xác của bốn model trên dữ liệu kiểm thử, kèm điều kiện kiểm thử |
| Có bãi thật đồng ý | Ít nhất một văn bản đồng ý cho thử nghiệm |

### Giai đoạn bãi đầu tiên

| Tiêu chí | Đạt là gì |
|---|---|
| Độ chính xác đếm chỗ trống | Sai số dưới 5 phần trăm dung lượng trong điều kiện đủ sáng, đo bằng kiểm đếm thủ công ba lần mỗi ngày trong hai tuần |
| Độ chính xác nhận diện biển số | Trên 95 phần trăm ban ngày, trên 90 phần trăm ban đêm có đèn |
| Báo động sai của mô đun an toàn | Dưới một lần mỗi camera mỗi tuần sau hiệu chuẩn |
| Bãi vẫn hoạt động bình thường | Không có sự cố nào làm bãi ngừng hoạt động do hệ thống |

### Giai đoạn một khu vực

| Tiêu chí | Đạt là gì |
|---|---|
| Mật độ | Tối thiểu tám điểm đỗ nhận đặt chỗ trong khu vực mục tiêu |
| Niềm tin | Tỷ lệ giữ đúng chỗ đã cam kết trên 98 phần trăm |
| Người dùng quay lại | Trên 35 phần trăm người dùng có lượt thứ hai trong 30 ngày |
| Chủ bãi ở lại | Trên 90 phần trăm bãi vẫn hoạt động tốt sau 90 ngày |

### Giai đoạn nhân rộng

| Tiêu chí | Đạt là gì |
|---|---|
| Chi phí onboard giảm | Giảm ít nhất 30 phần trăm so với hai mươi bãi đầu |
| Tỷ lệ bãi tự đăng ký | Trên 40 phần trăm bãi mới đến từ kênh tự đăng ký hoặc lan truyền |
| Biên đóng góp | Tổng biên đóng góp vượt chi phí cố định |
| Khu vực thứ hai | Đạt mật độ tối thiểu trong vòng ba tháng kể từ khi mở |

---

## 8. Đội ngũ và vai trò

Thể lệ cuộc thi cho phép tối đa mười thành viên mỗi đội. Bảng dưới đây là các vai trò cần có, không phải danh sách nhân sự đã chốt. Phần tên người cần được điền và xác nhận trước khi nộp hồ sơ.

| Vai trò | Trách nhiệm | Mức độ cần thiết |
|---|---|---|
| Trưởng nhóm và phụ trách sản phẩm | Định hướng, ra quyết định phạm vi, chủ trì hồ sơ và phần trình bày | Bắt buộc |
| Kỹ sư thị giác máy tính | Bốn model, huấn luyện lại, đo lường, triển khai trên thiết bị biên | Bắt buộc, đây là vai trò quyết định điểm kỹ thuật |
| Kỹ sư backend | Nền tảng trung tâm, giữ chỗ, thanh toán, dữ liệu | Bắt buộc |
| Kỹ sư ứng dụng di động và giao diện | Ứng dụng người lái, cổng chủ bãi, ứng dụng bảo vệ | Bắt buộc |
| Kỹ sư dữ liệu và dự báo | Dự báo chỗ trống, xếp hạng, cá nhân hoá | Cần từ giai đoạn có dữ liệu |
| Phụ trách vận hành thực địa | Onboard bãi, lắp đặt, đào tạo, chăm sóc bãi | Bắt buộc từ khi có bãi đầu tiên |
| Phụ trách kinh doanh | Tiếp cận chủ bãi, đàm phán, khách đội xe | Bắt buộc |
| Thiết kế sản phẩm | Trải nghiệm người dùng, nhận diện thương hiệu, tài liệu trình bày | Cần, ảnh hưởng trực tiếp tới điểm trình bày |
| Tư vấn pháp lý và tuân thủ | Bảo vệ dữ liệu cá nhân, hợp đồng, quy định phòng cháy, chia sẻ dữ liệu | Cần, có thể là cố vấn bên ngoài |

Ghi chú về năng lực đã có: đội đã trực tiếp xây dựng cả hai khối năng lực cốt lõi của hệ thống, gồm bốn model thị giác máy tính cùng hệ thống quản lý bãi đỗ, và nền tảng điều phối mạng lưới điểm dịch vụ. Việc tập hợp đúng những người đã làm hai phần này là lợi thế lớn nhất về thời gian, và cần được nêu rõ trong hồ sơ ở phần năng lực thực thi.

---

## 9. Rủi ro và cách xử lý

| Rủi ro | Mức độ | Dấu hiệu sớm | Cách xử lý |
|---|---|---|---|
| Độ chính xác đếm chỗ trống không đạt trong hầm thiếu sáng | Cao | Sai số vượt ngưỡng ngay trong tuần kiểm chứng đầu | Bổ sung chiếu sáng, đổi góc camera, huấn luyện thêm với dữ liệu của chính bãi đó. Nếu vẫn không đạt, hạ bãi xuống cấp 2 và không cam kết giữ chỗ |
| Báo động sai của mô đun phát hiện cháy quá nhiều | Cao | Bảo vệ bắt đầu bỏ qua thông báo | Hiệu chuẩn ngưỡng theo bãi, loại trừ vùng nhiễu, yêu cầu tín hiệu duy trì qua nhiều khung hình. Đây là rủi ro phải xử lý bằng dữ liệu, không bằng lời hứa |
| Chủ bãi không đồng ý tham gia | Cao | Tỷ lệ chốt sau khảo sát thấp | Đi vào bằng mô đun an toàn với hầm chung cư có xe điện, vì đó là nhóm có nghĩa vụ tuân thủ. Dùng bằng chứng từ bãi đã chạy |
| Không đạt mật độ trong khu vực mục tiêu | Cao | Sau hai tháng vẫn dưới tám điểm đỗ | Bổ sung mật độ bằng chỗ đỗ hộ dân, vì chi phí gần bằng không. Nếu vẫn không đạt, đổi khu vực thay vì cố |
| Người dùng thử một lần rồi không quay lại | Cao | Tỷ lệ lượt thứ hai dưới 20 phần trăm | Điều tra nguyên nhân theo từng lượt thất bại. Ba nguyên nhân thường gặp là dữ liệu sai, cổng vào khó tìm, và giá không như hiển thị. Cả ba đều sửa được |
| Sự cố an toàn hoặc mất mát tại bãi trong mạng lưới | Trung bình, hậu quả lớn | Không có dấu hiệu sớm | Quy trình bằng chứng hình ảnh, phân định trách nhiệm rõ trong hợp đồng, và không mở phân khúc chỗ đỗ hộ dân trước khi quy trình đã chạy ổn ở phân khúc có kiểm soát |
| Vi phạm quy định về bảo vệ dữ liệu cá nhân | Trung bình, hậu quả rất lớn | Không có dấu hiệu sớm nếu không rà soát | Rà soát pháp lý trước khi triển khai. Thời hạn lưu trữ và xoá tự động. Nhật ký truy cập. Phi định danh mặc định. Đây là hạng mục không được đánh đổi lấy tốc độ |
| Thiết bị hỏng hoặc mất mạng làm gián đoạn vận hành bãi | Trung bình | Thời gian hoạt động thiết bị giảm | Ghi nhận cục bộ khi mất mạng, phương án thủ công luôn sẵn, cam kết thời gian phản hồi hỗ trợ |
| Chi phí thiết bị và vốn lưu động vượt dự kiến | Trung bình | Dòng tiền âm dù biên dương | Hạn chế cho thuê thiết bị, mua theo lô, ưu tiên tận dụng camera có sẵn của bãi |
| Một đơn vị lớn có sẵn tệp khách hàng làm điều tương tự | Trung bình | Xuất hiện sản phẩm tương tự trong cùng khu vực | Cạnh tranh bằng độ chính xác dữ liệu và bằng việc chiếm sớm những bãi có nghĩa vụ tuân thủ. Không cạnh tranh bằng giá |
| Đội thiếu vai trò vận hành thực địa | Trung bình | Bãi onboard rồi chết dần | Xác định người phụ trách thực địa từ bãi đầu tiên. Đây là vai trò không thể làm kiêm nhiệm quá lâu |
| Phụ thuộc vào một nhà cung cấp thanh toán hoặc một dịch vụ bản đồ | Thấp | Dịch vụ thay đổi chính sách hoặc giá | Thiết kế lớp bọc để có thể thay thế, nguyên tắc này đã được áp dụng cho dịch vụ định tuyến trong nền tảng hiện tại |

---

## 10. Phụ thuộc và giả định

### 10.1. Phụ thuộc bên ngoài

| Phụ thuộc | Nếu không có thì sao |
|---|---|
| Sự đồng ý của chủ bãi | Không có dữ liệu, không có sản phẩm. Đây là phụ thuộc nghiêm trọng nhất và cũng là việc phải làm sớm nhất |
| Hạ tầng camera, điện và mạng tại bãi | Chi phí onboard tăng, một số bãi không khả thi ở cấp 3 |
| Cổng thanh toán | Không có thanh toán thì không có vào ra tự động, và mất phần lớn giá trị với người dùng |
| Dịch vụ định tuyến và bản đồ | Có thể tự triển khai trên dữ liệu mở, đội đã có kinh nghiệm làm việc này |
| Cơ sở pháp lý cho việc chia sẻ dữ liệu và xử lý biển số | Nếu chưa rõ thì thu hẹp phạm vi xử lý dữ liệu, không mở rộng cho tới khi có ý kiến pháp lý |

### 10.2. Giả định cần kiểm chứng sớm nhất

Xếp theo mức độ ảnh hưởng nếu giả định sai:

| Giả định | Cách kiểm chứng | Thời điểm |
|---|---|---|
| Model đếm chỗ trống đạt độ chính xác đủ để cam kết giữ chỗ trong điều kiện hầm thật | Kiểm đếm thủ công đối chiếu trong hai tuần tại bãi đầu tiên | Ngay tại bãi đầu tiên |
| Chủ bãi trả tiền cho phần mềm và mô đun an toàn ở mức đề xuất | Đàm phán thật với năm bãi | Trong tháng đầu tiên |
| Bãi bán được giờ thấp điểm ở mức đủ tạo doanh thu mới | Thử nghiệm bảng giá giờ thấp điểm trong bốn tuần tại một bãi | Trong ba tháng đầu |
| Người lái xe trả phí giữ chỗ | Thử nghiệm hai mức giá khác nhau | Sau khi có người dùng đầu tiên |
| Mật độ tám điểm đỗ là đủ để người dùng thấy giá trị | Đo tỷ lệ quay lại theo mật độ khu vực | Khi có hai khu vực để so sánh |
| Chỗ đỗ của hộ dân là phân khúc khả thi về pháp lý và về an toàn | Ý kiến pháp lý, cộng thử nghiệm nhỏ có kiểm soát | Trước khi mở rộng phân khúc này |

---

## 11. Điều kiện điều chỉnh hướng đi

Ba tình huống cần được nhận ra sớm và xử lý bằng cách đổi hướng thay vì cố gắng thêm.

**Tình huống một, lớp cảm nhận không đạt độ chính xác cần thiết trong môi trường hầm thật.** Nếu sau ba bãi mà sai số đếm chỗ trống vẫn vượt ngưỡng cho phép cam kết, thì hướng đi cần đổi: tập trung vào nhận diện biển số và mô đun an toàn, là hai năng lực đã chín, và chuyển bài toán chỗ trống sang tính theo số xe vào ra thay vì đếm ô trực tiếp. Cách này cho độ chính xác về số lượng nhưng không cho biết vị trí ô nào trống, chấp nhận được với nhiều bãi có kiểm soát cổng.

**Tình huống hai, phía cầu không hình thành dù mật độ đã đủ.** Nếu một khu vực đã có mười điểm đỗ mà tỷ lệ người dùng quay lại vẫn thấp, thì vấn đề không phải cung mà là giá trị cảm nhận. Khi đó hướng đi cần đổi sang mô hình bán phần mềm cho chủ bãi làm trọng tâm, tức là mô hình phần mềm vận hành và an toàn cho bãi đỗ, còn mạng lưới cho người lái xe trở thành phần bổ trợ. Đây là hướng lùi có kiểm soát, vẫn giữ được doanh thu và vẫn giữ được tài sản dữ liệu.

**Tình huống ba, phân khúc chỗ đỗ hộ dân gặp rào cản pháp lý hoặc rủi ro không kiểm soát được.** Khi đó đóng phân khúc này và bù mật độ bằng cách onboard sâu hơn vào hầm chung cư, nơi dung lượng lớn và có người chịu trách nhiệm rõ ràng.

Nguyên tắc chung: nhận ra sớm và đổi hướng có kiểm soát là dấu hiệu của một đội biết mình đang làm gì, không phải dấu hiệu thất bại. Việc cần tránh là tiếp tục đầu tư vào một giả định đã được dữ liệu phủ định.
