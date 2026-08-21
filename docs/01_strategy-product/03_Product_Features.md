# 03. Tính năng sản phẩm

Kể theo câu chuyện của từng người dùng, kèm những gì hệ thống làm bên trong

Phiên bản: 1.0
Ngày: 21/08/2026
Tài liệu liên quan: [01. Tổng quan dự án](01_Project_Overview.md), [02. Phân tích bài toán](02_Problem_Deep_Dive.md), [05. Playbook onboard bãi đỗ](../02_business-operations/05_Onboarding_Playbook.md)

---

## Mục lục

1. [Cách đọc tài liệu này](#1-cách-đọc-tài-liệu-này)
2. [Bản đồ tính năng tổng thể](#2-bản-đồ-tính-năng-tổng-thể)
3. [Hành trình người lái xe](#3-hành-trình-người-lái-xe)
4. [Cá nhân hoá, thói quen và ưu đãi](#4-cá-nhân-hoá-thói-quen-và-ưu-đãi)
5. [Hành trình chủ bãi](#5-hành-trình-chủ-bãi)
6. [Bộ não hệ thống](#6-bộ-não-hệ-thống)
7. [An toàn cháy nổ trong bãi đỗ](#7-an-toàn-cháy-nổ-trong-bãi-đỗ)
8. [Phân cấp và phân khúc bãi đỗ](#8-phân-cấp-và-phân-khúc-bãi-đỗ)
9. [Lớp dữ liệu công](#9-lớp-dữ-liệu-công)
10. [Bảo vệ dữ liệu cá nhân trong từng tính năng](#10-bảo-vệ-dữ-liệu-cá-nhân-trong-từng-tính-năng)
11. [Thứ tự ưu tiên](#11-thứ-tự-ưu-tiên)

---

## 1. Cách đọc tài liệu này

Mỗi tính năng được trình bày theo năm phần, để người đọc phía sản phẩm và phía kinh doanh thấy được cả trải nghiệm lẫn cơ chế:

**Tình huống.** Bối cảnh thật của một người dùng cụ thể, có tên, có giờ, có địa điểm.
**Trải nghiệm.** Người dùng thấy gì và làm gì, theo từng bước.
**Bên trong.** Hệ thống tính toán và quyết định thế nào.
**Dữ liệu cần.** Tính năng này phụ thuộc vào nguồn dữ liệu nào, và không có nguồn đó thì hỏng ra sao.
**Giá trị.** Người dùng nhận được gì, nền tảng thu được gì.

Tài liệu này chưa chốt phạm vi bản đầu tiên. Mục 11 chỉ xếp thứ tự ưu tiên theo mức độ cần thiết cho câu chuyện lõi. Việc chốt phạm vi bản đầu tiên sẽ làm sau khi bộ tài liệu này được thống nhất.

---

## 2. Bản đồ tính năng tổng thể

| Nhóm | Tính năng | Người dùng | Phụ thuộc dữ liệu | Ưu tiên |
|---|---|---|---|---|
| Người lái xe | Tìm bãi theo điểm đến | Tài xế | Danh mục bãi, định tuyến, quãng đi bộ | P0 |
| Người lái xe | Dự đoán chỗ trống tại thời điểm tới nơi | Tài xế | Chỗ trống thời gian thực, nhịp vào ra lịch sử, thời gian di chuyển | P0 |
| Người lái xe | Đặt chỗ và giữ chỗ theo khoảng thời gian | Tài xế | Dung lượng khả dụng, chính sách bãi | P0 |
| Người lái xe | Đặt trước cho ngày mai, nhiều ngày, qua đêm, theo tháng | Tài xế | Dự báo chỗ trống theo mốc tương lai | P1 |
| Người lái xe | Vào ra không cần dừng, tính phí theo thời gian thực | Tài xế | Nhận diện biển số tại cổng, thanh toán | P0 |
| Người lái xe | Xem hình ảnh khu vực đỗ và cảnh báo bất thường | Tài xế | Camera trong bãi, quyền truy cập theo lượt gửi | P1 |
| Người lái xe | Quãng đi bộ cuối tuyến và gửi xe đổi phương tiện | Tài xế | Định tuyến đi bộ, dữ liệu điểm trung chuyển | P1 |
| Người lái xe | Bộ lọc theo thuộc tính thật của bãi | Tài xế | Hồ sơ thuộc tính bãi đã kiểm định | P0 |
| Người lái xe | Trợ lý hội thoại nhập nhu cầu bằng lời | Tài xế | Bộ hiểu ý định, dữ liệu địa điểm | P2 |
| Người lái xe | Điểm tin cậy của bãi từ dữ liệu vận hành | Tài xế | Lịch sử giữ chỗ, thời gian vào ra, tranh chấp | P1 |
| Cá nhân hoá | Đồ thị thói quen và điểm thân thuộc | Tài xế | Lịch sử đỗ xe của chính người dùng | P1 |
| Cá nhân hoá | Dự đoán ý định và gợi ý chủ động | Tài xế | Đồ thị thói quen, thời gian, ngữ cảnh | P2 |
| Cá nhân hoá | Xếp hạng theo trọng số riêng của từng người | Tài xế | Lịch sử lựa chọn và bỏ qua | P2 |
| Cá nhân hoá | Ưu đãi đúng người đúng lúc | Tài xế và chủ bãi | Dự báo chỗ trống, độ nhạy giá, hồ sơ người dùng | P2 |
| Chủ bãi | Đếm chỗ trống tự động bằng camera | Chủ bãi | Camera trong bãi, thiết bị biên | P0 |
| Chủ bãi | Ghi nhận vào ra và tính phí bằng nhận diện biển số | Chủ bãi | Camera cổng, thiết bị biên | P0 |
| Chủ bãi | Phát hiện khói và lửa sớm | Chủ bãi, cư dân, tài xế | Camera trong bãi, thiết bị biên, kênh cảnh báo | P0 |
| Chủ bãi | Bảng điều khiển vận hành và doanh thu | Chủ bãi | Toàn bộ dữ liệu lượt gửi | P0 |
| Chủ bãi | Bán giờ thấp điểm và định giá theo nhu cầu | Chủ bãi | Dữ liệu lấp đầy theo giờ, dự báo | P1 |
| Chủ bãi | Bán gói tháng và quản lý khách quen | Chủ bãi | Hồ sơ khách, thanh toán định kỳ | P1 |
| Chủ bãi | Bằng chứng hình ảnh và xử lý tranh chấp | Chủ bãi | Lưu trữ hình ảnh có thời hạn | P1 |
| Chủ bãi | Ứng dụng đơn giản cho bảo vệ | Bảo vệ | Danh sách lượt giữ chỗ, cảnh báo | P0 |
| Chủ chỗ nhỏ | Đăng chỗ đỗ, đặt khung giờ, xác thực người thuê | Hộ dân | Xác thực danh tính, bằng chứng hình ảnh | P1 |
| Doanh nghiệp | Hợp đồng đội xe, đối soát tập trung | Quản lý đội xe | Dữ liệu lượt gửi theo xe, hoá đơn | P2 |
| Quản trị mạng lưới | Bản đồ nhiệt cung cầu theo giờ | Nội bộ và cơ quan quản lý | Toàn bộ dữ liệu mạng lưới | P1 |
| Quản trị mạng lưới | Chia sẻ dữ liệu tổng hợp cho cơ quan quản lý | Cơ quan quản lý | Dữ liệu đã phi định danh, cơ chế kiểm toán | P2 |

Ba tính năng in đậm về mặt tầm quan trọng, dù không phải ba tính năng phức tạp nhất: đếm chỗ trống bằng camera, dự đoán trạng thái tại thời điểm tới nơi, và giữ chỗ có cam kết. Ba tính năng này là toàn bộ lý do người dùng tin sản phẩm. Nếu ba tính năng này đúng, những tính năng còn lại làm sản phẩm tốt hơn. Nếu ba tính năng này sai, những tính năng còn lại không có ý nghĩa gì.

---

## 3. Hành trình người lái xe

### A1. Tìm bãi theo điểm đến, không theo vị trí hiện tại

**Tình huống.** Chị Hà đang ở nhà tại Thủ Đức, chuẩn bị chở con đi khám ở một bệnh viện tại Quận 5. Chị chưa xuất phát. Điều chị cần biết không phải bãi nào gần chỗ chị đang đứng, mà bãi nào gần nơi chị sẽ tới, và bãi đó lúc chị tới có còn chỗ hay không.

**Trải nghiệm.** Chị mở ứng dụng, nhập tên bệnh viện. Hệ thống hỏi một câu duy nhất: dự kiến tới lúc nào, với ba lựa chọn nhanh là đi ngay, trong một giờ, hoặc chọn giờ cụ thể. Chị chọn đi ngay. Kết quả trả về ba bãi, sắp theo mức phù hợp, mỗi bãi hiển thị bốn con số dễ so sánh: thời gian lái xe tới bãi, quãng đi bộ từ bãi tới cổng bệnh viện, giá dự kiến cho hai giờ, và xác suất còn chỗ khi chị tới.

**Bên trong.** Hệ thống lấy điểm đến làm tâm, không lấy vị trí người dùng làm tâm. Nó tìm các bãi trong bán kính đi bộ hợp lý quanh điểm đến, mặc định bảy trăm mét và có thể nới ra khi khu vực khan chỗ. Với mỗi bãi, hệ thống tính thời gian lái xe từ vị trí hiện tại của người dùng tới bãi theo tình trạng giao thông, tính quãng đi bộ từ bãi tới điểm đến theo đường đi bộ thực tế chứ không theo đường chim bay, rồi chuyển sang bước dự đoán chỗ trống ở A2.

Điểm cần lưu ý về thiết kế: khoảng cách theo đường chim bay là con số vô dụng trong đô thị Việt Nam, vì hai điểm cách nhau ba trăm mét trên bản đồ có thể phải đi vòng một ki lô mét do đường một chiều và dải phân cách. Đây là lý do phải dùng định tuyến thực. Năng lực này đã có trong nền tảng của đội, với dịch vụ định tuyến trên dữ liệu bản đồ mở kèm cơ chế dự phòng khi dịch vụ định tuyến không phản hồi.

**Dữ liệu cần.** Danh mục bãi với toạ độ chính xác tới cổng vào, không phải toạ độ của toà nhà. Định tuyến cho xe và cho người đi bộ. Bảng giá của bãi. Thiếu toạ độ cổng vào chính xác là lỗi thường gặp và gây hậu quả trực tiếp: người dùng đi tới đúng số nhà nhưng cổng hầm nằm ở mặt sau, đi vòng thêm bốn phút và mất niềm tin.

**Giá trị.** Đây là tính năng đầu tiên người dùng gặp, nên nó quyết định ấn tượng đầu. Với nền tảng, đây là nơi thu thập tín hiệu nhu cầu quan trọng nhất: người ta muốn đỗ ở đâu, vào giờ nào, kể cả khi hệ thống chưa có bãi nào ở đó. Chính tín hiệu này là bản đồ để đi onboard bãi tiếp theo.

### A2. Dự đoán chỗ trống tại thời điểm tới nơi

**Tình huống.** Anh Khoa cách bãi hai mươi ba phút vào giờ cao điểm. Bãi hiện còn chín chỗ. Câu hỏi thật không phải bãi còn chín chỗ hay không, mà là hai mươi ba phút nữa còn chỗ nào không.

**Trải nghiệm.** Trên mỗi lựa chọn, người dùng thấy một dòng ngắn: khi bạn tới, dự kiến còn khoảng bốn chỗ, mức tin cậy cao. Với bãi rủi ro cao thì dòng đó là: khi bạn tới, khả năng còn chỗ khoảng bốn mươi phần trăm, nên giữ chỗ trước.

**Bên trong.** Đây là phần dùng lại trực tiếp engine ghép nối mà đội đã xây dựng, chỉ đổi biến số. Nguyên lý của engine là dự đoán trạng thái của một điểm phục vụ tại thời điểm khách đến nơi thay vì tại thời điểm khách tìm kiếm. Với bài toán đỗ xe, hệ thống dự đoán bao nhiêu xe sẽ vào và bao nhiêu xe sẽ ra khỏi bãi trong khoảng thời gian khách di chuyển.

Công thức ở dạng khái niệm:

```
Chỗ trống dự kiến khi tới
  = Chỗ trống hiện tại (camera đếm được)
  + Số xe dự kiến rời bãi trong khoảng thời gian di chuyển
  - Số xe dự kiến vào bãi trong khoảng thời gian di chuyển
  - Số chỗ đã bị giữ bởi các lượt đặt chỗ khác trong cùng khung giờ
```

Số xe vào và ra được ước lượng từ nhịp vận hành lịch sử của chính bãi đó, phân theo ngày trong tuần và khung giờ, có hiệu chỉnh theo yếu tố ngữ cảnh như mưa, ngày lễ, sự kiện gần đó. Giai đoạn đầu, khi bãi mới lắp và chưa có lịch sử, hệ thống dùng quy tắc và mức trung bình theo loại bãi tương đương, đồng thời hiển thị mức tin cậy thấp hơn để người dùng biết. Càng nhiều tuần vận hành, mô hình càng chuyển dần sang học từ dữ liệu của chính bãi đó.

Một nguyên tắc thiết kế đã có trong nền tảng và cần nhắc lại: hệ thống phải suy giảm mượt. Nếu dịch vụ định tuyến không phản hồi, dùng khoảng cách đường chim bay nhân hệ số điều chỉnh. Nếu chưa đủ dữ liệu lịch sử, dùng trung bình theo loại bãi. Nếu camera của một bãi mất kết nối, hạ mức tin cậy của bãi đó và ưu tiên các bãi có dữ liệu tốt, chứ không loại bãi đó khỏi kết quả và cũng không im lặng trả về số cũ như thể nó còn đúng.

**Dữ liệu cần.** Số chỗ trống theo thời gian thực từ camera. Lịch sử vào ra theo giờ của từng bãi. Thời gian di chuyển thực tế. Danh sách các lượt giữ chỗ đang hiệu lực.

**Giá trị.** Đây là khác biệt cốt lõi so với mọi ứng dụng hiện có tại Việt Nam, và là điều kiện để tính năng giữ chỗ ở A3 có thể cam kết được.

### A3. Đặt chỗ và giữ chỗ theo khoảng thời gian

**Tình huống.** Chị Hà thấy bãi bệnh viện còn xác suất bốn mươi phần trăm. Chị không muốn đánh cược với một đứa trẻ đang mệt trên xe. Chị muốn có chỗ chắc chắn, và sẵn sàng trả thêm cho việc đó.

**Trải nghiệm.** Chị bấm giữ chỗ. Hệ thống hỏi thời gian dự kiến gửi, chị chọn khoảng hai giờ. Chị thấy rõ ba điều trước khi xác nhận: chỗ được giữ tới mấy giờ mấy phút, phí giữ chỗ là bao nhiêu và có được trừ vào tiền gửi hay không, và điều gì xảy ra nếu chị đến muộn hơn khung giữ chỗ. Sau khi xác nhận, chị nhận một mã lượt gửi, và biển số xe của chị được đưa vào danh sách chờ của bãi đó.

**Bên trong.** Giữ chỗ là nghiệp vụ khó nhất trong toàn bộ sản phẩm, vì nó là một cam kết trên một tài sản vật lý mà nền tảng không kiểm soát trực tiếp. Bốn cơ chế cần có:

Một, khoá dung lượng. Khi một lượt giữ chỗ được xác lập, một chỗ trong bãi bị trừ khỏi dung lượng khả dụng của khung giờ tương ứng. Nền tảng hiện tại đã có cơ chế khoá phân tán cho việc này để tránh hai người giữ cùng một chỗ.

Hai, cửa sổ thời gian và thời gian chờ thêm. Chỗ được giữ trong một khung có điểm bắt đầu và điểm kết thúc, cộng thêm một khoảng chờ thêm hợp lý, ví dụ mười lăm phút, vì giao thông đô thị không đúng giờ được. Hết khoảng đó, chỗ được trả lại thị trường.

Ba, giới hạn tỷ lệ giữ chỗ trên tổng dung lượng. Không bãi nào nên cho giữ trước toàn bộ dung lượng, vì như vậy sẽ chặn hết khách vãng lai đang đi tới cổng và làm chủ bãi mất doanh thu chắc chắn để đổi lấy doanh thu không chắc chắn. Tỷ lệ này là một tham số theo từng bãi và từng khung giờ, do chủ bãi đặt cùng nền tảng.

Bốn, chính sách cho cả hai chiều thất bại. Nếu khách không đến, phí giữ chỗ không hoàn lại, và số lần không đến được ghi vào hồ sơ người dùng, quá ngưỡng thì mất quyền giữ chỗ trong một thời gian. Nếu khách đến mà bãi không có chỗ, thì nền tảng phải trả giá: hoàn phí, hỗ trợ chuyển sang bãi khác trong mạng lưới và chịu phần chênh lệch, và điểm tin cậy của bãi bị trừ. Chính sách bất đối xứng này là cố tình, vì niềm tin của người dùng đắt hơn nhiều so với khoản bù cho một lượt gửi.

**Dữ liệu cần.** Dung lượng khả dụng theo khung giờ. Cấu hình chính sách của từng bãi. Biển số xe của người dùng để nhận diện tại cổng.

**Giá trị.** Đây là tính năng biến thông tin thành cam kết, và cam kết là thứ người dùng trả tiền. Với chủ bãi, đây là công cụ để lấp trước những giờ mà bình thường phải chờ khách tự tới.

### A4. Đặt trước cho ngày mai, nhiều ngày, qua đêm, theo tháng

**Tình huống.** Ba nhu cầu rất khác nhau nhưng cùng một bản chất. Anh Nam bay đi Hà Nội sáng thứ Năm, về chiều Chủ nhật, cần gửi xe bốn ngày gần sân bay. Chị Mai ở một khu phố không có chỗ đỗ ban đêm, cần chỗ gửi cố định từ 19 giờ tới 07 giờ mỗi ngày. Anh Khoa cần một chỗ mỗi sáng thứ Hai tới thứ Sáu trong ba tháng tới.

**Trải nghiệm.** Trên ứng dụng, ba nhu cầu này là ba lựa chọn khác nhau ngay ở bước đầu: gửi theo giờ, gửi qua đêm hoặc nhiều ngày, và gói định kỳ. Với gói định kỳ, người dùng chọn khung giờ và các ngày trong tuần, hệ thống trả về các bãi có thể nhận cam kết đó kèm giá theo tháng, thấp hơn đáng kể so với cộng dồn từng lượt.

**Bên trong.** Điều làm tính năng này khả thi là dự báo chỗ trống ở tầm xa hơn thời điểm tới nơi. Hệ thống cần trả lời được: vào 08 giờ thứ Ba tuần sau, bãi này còn bao nhiêu chỗ có thể bán trước. Câu trả lời dựa trên nhịp lấp đầy lịch sử theo ngày trong tuần và khung giờ, trừ đi phần dung lượng đã bán cho các cam kết định kỳ, và giữ lại một phần đệm cho khách vãng lai.

Đây cũng là chỗ bài toán đỗ xe khác hẳn bài toán gọi xe hay gọi món. Một cuốc xe là một lượt, xong là hết. Một lượt đỗ xe là việc chiếm giữ một không gian trong một khoảng thời gian, và chính khoảng thời gian đó là hàng hoá. Vì vậy hệ thống phải quản lý dung lượng theo trục thời gian, giống cách khách sạn quản lý phòng theo đêm, chứ không phải theo trục số lượt.

**Dữ liệu cần.** Dự báo lấp đầy theo mốc tương lai. Cấu hình phần dung lượng được phép bán trước. Thanh toán định kỳ.

**Giá trị.** Đây là nguồn doanh thu định kỳ và dự đoán được, đồng thời là công cụ giữ người dùng mạnh nhất, vì một người đã mua gói tháng thì không mở ứng dụng khác nữa. Với chủ bãi, gói định kỳ chuyển một phần doanh thu bất định thành doanh thu chắc chắn, và đây là lý lẽ bán hàng rất mạnh với những bãi có tỷ lệ lấp đầy dao động lớn.

### A5. Vào ra không cần dừng, tính phí theo thời gian thực

**Tình huống.** Anh Khoa tới cổng bãi lúc 08 giờ 11. Ở bãi truyền thống, anh dừng xe, hạ kính, lấy thẻ, tìm chỗ. Chiều về thì trả thẻ, chờ nhân viên tính tiền, tìm tiền lẻ. Tổng cộng khoảng ba tới bốn phút cho hai lượt, cộng với khả năng tranh luận nếu mất thẻ.

**Trải nghiệm.** Xe chạy chậm qua cổng. Camera đọc biển số. Barrier mở. Trên điện thoại anh hiện thông báo: đã vào bãi lúc 08 giờ 11, đang tính phí, chỗ được gợi ý ở khu B tầng hầm một. Chiều về, camera đọc biển số ở cổng ra, hệ thống chốt thời gian gửi, trừ tiền từ phương thức đã liên kết, barrier mở, hoá đơn hiện trên điện thoại.

**Bên trong.** Đây là luồng đã được xây và chạy thực tế: model thứ nhất phát hiện và cắt vùng biển số từ luồng video, model thứ hai nhận diện từng ký tự rồi ghép theo vị trí toạ độ ngang để tạo thành biển số hoàn chỉnh, hỗ trợ cả biển một dòng và hai dòng của Việt Nam. Kết quả được ghi vào cơ sở dữ liệu kèm mốc thời gian, và dịch vụ tính phí tự động chạy khi có sự kiện ra.

Phần phải làm thêm cho môi trường thật, và cần nói rõ vì đây là rủi ro vận hành:

| Tình huống ngoại lệ | Cách xử lý |
|---|---|
| Đọc sai một ký tự | Đối chiếu với danh sách lượt giữ chỗ và danh sách xe đang trong bãi, chấp nhận sai lệch một ký tự nếu chỉ có một ứng viên khớp. Nếu nhiều ứng viên, chuyển cho bảo vệ xác nhận |
| Biển số bị bẩn, che, hoặc xe không biển | Chuyển sang luồng thủ công, bảo vệ nhập biển số trên ứng dụng, hệ thống lưu ảnh làm bằng chứng |
| Hai xe cùng biển số, hoặc biển giả | Đối chiếu thêm đặc điểm xe từ khung hình, ghi nhận nghi vấn và cảnh báo cho quản lý bãi |
| Xe vào mà không có ghi nhận ra, hoặc ngược lại | Quy trình đối soát cuối ngày, đối chiếu số xe đếm được trong bãi với số lượt đang mở |
| Mất kết nối mạng | Thiết bị biên tiếp tục ghi nhận cục bộ và đồng bộ lại khi có mạng. Barrier vẫn hoạt động theo luồng dự phòng, không được để bãi tắc vì lỗi phần mềm |

Nguyên tắc tuyệt đối: hệ thống không bao giờ được làm bãi ngừng hoạt động. Nếu phần mềm lỗi, bãi phải quay về vận hành thủ công trong vài giây. Chủ bãi sẽ tha thứ cho một lỗi nhận diện, nhưng không tha thứ cho một hàng xe dài ở cổng.

**Dữ liệu cần.** Camera cổng đủ độ phân giải và góc nhìn. Thiết bị biên xử lý cục bộ. Liên kết biển số với người dùng và phương thức thanh toán.

**Giá trị.** Với người dùng, tiết kiệm thời gian và hết tranh chấp. Với chủ bãi, đây là tính năng có giá trị tiền tệ trực tiếp: mọi lượt xe đều được ghi nhận, nên khoản thất thu do quản lý thủ công bị bịt lại. Kinh nghiệm từ việc thu phí đỗ xe lòng đường tại Thành phố Hồ Chí Minh cho thấy khi chuyển sang ghi nhận tự động gắn với phương tiện, doanh thu tăng gần gấp đôi so với cùng kỳ.

### A6. Xem hình ảnh khu vực đỗ và cảnh báo bất thường

**Tình huống.** Chị Hà gửi xe ở một bãi lạ và ngồi trong bệnh viện hai giờ. Nỗi lo của chị không phải mất xe, mà là những chuyện nhỏ hơn và thường xảy ra hơn: xe bị va chạm khi xe khác lùi, bị người khác đỗ chắn không ra được, hoặc bãi ngoài trời bị ngập khi mưa lớn.

**Trải nghiệm.** Trong thời gian xe đang gửi, chị mở ứng dụng và xem được ảnh khu vực đỗ, cập nhật theo chu kỳ. Nếu hệ thống phát hiện bất thường liên quan tới khu vực đó, chị nhận thông báo. Khi lượt gửi kết thúc, quyền xem hình ảnh đóng lại.

**Bên trong.** Đây là điểm cần thiết kế rất cẩn thận về mặt pháp lý và đạo đức, vì camera trong bãi ghi hình cả người khác. Bốn ràng buộc bắt buộc:

Một, chỉ cung cấp hình ảnh khu vực nơi xe của người dùng đang đỗ, trong đúng thời gian lượt gửi của họ, không cung cấp quyền xem toàn bãi.
Hai, mặc định là ảnh theo chu kỳ, không phải video trực tiếp liên tục. Điều này vừa giảm rủi ro riêng tư, vừa phù hợp với giới hạn tài nguyên máy chủ đã được ghi nhận khi thử nghiệm phát video trực tiếp ở quy mô nhiều camera.
Ba, làm mờ mặt người và biển số của các xe khác trong khung hình.
Bốn, ghi nhật ký mọi lượt truy cập hình ảnh, để có thể kiểm toán.

Về cảnh báo bất thường, giai đoạn đầu chỉ nên làm những gì phát hiện được đáng tin cậy: khói và lửa, vì đây là năng lực đã có. Các cảnh báo khác như va chạm hay ngập nước cần thêm dữ liệu huấn luyện và nên đưa vào sau, tránh việc gửi cảnh báo sai làm người dùng lo lắng vô cớ và mất niềm tin.

**Dữ liệu cần.** Camera trong bãi, ánh xạ giữa vị trí xe và khu vực camera, quyền truy cập gắn với lượt gửi.

**Giá trị.** Đây là tính năng tạo cảm giác an tâm, và cảm giác an tâm là thứ khiến người dùng chọn một bãi đắt hơn. Với chủ bãi, cùng bộ dữ liệu này là bằng chứng khi có tranh chấp về hư hỏng xe, vốn là loại tranh chấp tốn kém và khó xử nhất của họ.

### A7. Quãng đi bộ cuối tuyến và gửi xe đổi phương tiện

**Tình huống.** Anh Khoa cần tới một cuộc họp ở khu vực trung tâm vào giờ cao điểm. Bãi ngay cạnh nơi họp có giá cao và gần như chắc chắn hết chỗ. Cách đó chín trăm mét có một bãi rộng, rẻ hơn một nửa, và có tuyến đi bộ trong ngõ mát.

**Trải nghiệm.** Kết quả tìm kiếm không chỉ xếp theo khoảng cách mà hiển thị rõ sự đánh đổi: bãi A cách đích một trăm mét, giá cao, xác suất còn chỗ ba mươi phần trăm. Bãi B cách đích chín trăm mét, đi bộ mười một phút, giá bằng một nửa, chắc chắn còn chỗ. Với những khu vực có phương tiện công cộng, hệ thống bổ sung lựa chọn gửi xe ở vành ngoài rồi đi tiếp bằng phương tiện công cộng, kèm tổng thời gian của cả hành trình.

**Bên trong.** Hệ thống định tuyến cho người đi bộ theo đường thực tế, và cộng tổng thời gian của cả hành trình thay vì chỉ tính thời gian lái xe. Với lựa chọn đổi phương tiện, cần dữ liệu vị trí điểm trung chuyển và thời gian di chuyển bằng phương tiện công cộng, phần này nên coi là mở rộng ở giai đoạn sau.

**Dữ liệu cần.** Định tuyến đi bộ, dữ liệu điểm trung chuyển nếu có.

**Giá trị.** Tính năng này mở rộng cung một cách thông minh mà không cần thêm bãi mới, vì nó khiến những bãi trước đây bị coi là quá xa trở thành lựa chọn hợp lý cho một phần người dùng. Với đô thị, nó giúp giảm dòng xe đi vào lõi trung tâm, tức là đúng mục tiêu quản lý.

### A8. Bộ lọc theo thuộc tính thật của bãi

**Tình huống.** Ba người dùng, ba nhu cầu không thể thay thế nhau. Người thứ nhất lái xe gầm cao và đã hai lần suýt va vào dầm hầm, nên cần biết giới hạn chiều cao. Người thứ hai đi xe điện và cần chỗ có trụ sạc. Người thứ ba từng bị ngập nước hỏng xe ở một bãi ngoài trời trong cơn mưa lớn, nên từ đó chỉ gửi bãi hầm hoặc bãi có mái che.

**Trải nghiệm.** Bộ lọc không phải danh sách tiện ích chung chung mà là các thuộc tính quyết định hành vi thật: loại bãi gồm hầm, có mái che, ngoài trời, hoặc bãi lòng đường. Giới hạn chiều cao. Có bảo vệ trực và trong khung giờ nào. Có camera giám sát. Có trụ sạc và công suất. Lối vào phù hợp xe cỡ lớn. Tiền sử ngập nước. Có dịch vụ kèm theo như rửa xe. Người dùng đặt bộ lọc một lần, hệ thống nhớ và áp dụng cho các lần sau.

**Bên trong.** Toàn bộ thuộc tính này phải được kiểm định trong quá trình onboard, không để bãi tự khai rồi hiển thị nguyên văn. Chi tiết bộ tiêu chí và cách kiểm định nằm trong [tài liệu 05](../02_business-operations/05_Onboarding_Playbook.md). Riêng thuộc tính tiền sử ngập nước là đặc thù Việt Nam và có giá trị thực tế rất cao, nguồn dữ liệu gồm khai báo của chủ bãi, phản hồi người dùng và dữ liệu mưa lịch sử của khu vực.

**Dữ liệu cần.** Hồ sơ thuộc tính bãi đã kiểm định, có phiên bản và có ngày kiểm định lại.

**Giá trị.** Đây là tính năng làm cho gợi ý trở nên đúng chứ không chỉ gần. Một gợi ý gần nhưng xe không vào được vì thấp dầm là một gợi ý sai hoàn toàn, và người dùng sẽ không quay lại.

### A9. Trợ lý hội thoại nhập nhu cầu bằng lời

**Tình huống.** Người dùng đang lái xe, không thể điền form. Hoặc nhu cầu của họ phức tạp hơn một ô tìm kiếm: tối mai tôi ở khu vực này từ bảy giờ tới mười một giờ, tìm chỗ gửi xe có mái che dưới một trăm nghìn.

**Trải nghiệm.** Người dùng nói hoặc gõ một câu tự nhiên. Hệ thống hiểu ra các thành phần gồm địa điểm, thời gian bắt đầu, thời lượng, yêu cầu về thuộc tính, ngưỡng giá, rồi hỏi lại đúng một điều còn thiếu, sau đó trả về kết quả.

**Bên trong.** Bộ hiểu ý định chuyển câu nói thành một truy vấn có cấu trúc, phần còn lại đi qua đúng luồng ở A1 và A2. Đây là lớp giao tiếp, không phải lớp quyết định. Nguyên tắc: trợ lý hội thoại không được tự ý đặt chỗ hay trừ tiền, mọi hành động có ràng buộc tài chính phải có bước xác nhận rõ ràng.

**Dữ liệu cần.** Từ điển địa điểm của khu vực, gồm cả tên gọi dân gian mà bản đồ chính thức không có.

**Giá trị.** Giảm ma sát cho nhóm người dùng không quen dùng ứng dụng, và mở khả năng đặt trước cho các mốc tương lai bằng một câu nói. Đây là tính năng nên làm sau khi ba tính năng lõi đã ổn định, vì nó là tiện lợi chứ không phải nền tảng.

### A10. Điểm tin cậy của bãi từ dữ liệu vận hành

**Tình huống.** Hai bãi cùng khoảng cách, cùng giá. Bãi thứ nhất có ba lần trong tháng qua để khách đã giữ chỗ đến mà không có chỗ. Bãi thứ hai chưa từng. Người dùng không có cách nào biết điều đó, còn hệ thống thì biết.

**Trải nghiệm.** Mỗi bãi có một điểm tin cậy, kèm cách diễn giải bằng lời chứ không chỉ bằng số, ví dụ giữ đúng chỗ đã cam kết trong 98 phần trăm lượt, thời gian qua cổng trung bình bốn mươi giây, chưa có tranh chấp trong sáu mươi ngày.

**Bên trong.** Dùng lại nguyên lý chấm điểm từ dữ liệu vận hành đã có trong nền tảng, đổi bộ tiêu chí sang đặc thù đỗ xe:

```
Điểm tin cậy của bãi = tổ hợp có trọng số của
  Tỷ lệ giữ đúng chỗ đã cam kết
  Độ lệch giữa số chỗ trống báo về và số kiểm đếm thực tế
  Thời gian xe qua cổng vào và cổng ra
  Tỷ lệ khách quay lại
  Số vụ tranh chấp và thời gian xử lý
  Mức độ hoạt động ổn định của thiết bị và camera
```

Điểm này khác căn bản với đánh giá năm sao. Nó đo hành vi vận hành, tức là thứ đo được và khó thao túng, thay vì đo cảm xúc. Nó cũng có tác dụng hai chiều: bãi tốt được xếp trước và nhận nhiều nhu cầu hơn, bãi kém bị cảnh báo sớm trước khi người dùng phàn nàn, và nếu vượt ngưỡng thì tạm dừng nhận giữ chỗ cho tới khi khắc phục.

**Dữ liệu cần.** Toàn bộ lịch sử lượt gửi, đối chiếu định kỳ giữa số camera đếm và số kiểm đếm thủ công, log tình trạng thiết bị.

**Giá trị.** Đây là cơ chế bảo vệ chất lượng mạng lưới khi số bãi tăng lên hàng trăm, mà không cần một đội đi kiểm tra từng bãi mỗi tuần.

---

## 4. Cá nhân hoá, thói quen và ưu đãi

Phần này trả lời câu hỏi: khi hệ thống đã biết người dùng đi đâu, vào lúc nào, thích gì, thì nó nên làm gì với hiểu biết đó.

### 4.1. Bốn nguyên tắc

Trước khi nói tính năng, cần chốt nguyên tắc, vì cá nhân hoá làm sai sẽ gây hại nhiều hơn không làm.

**Nguyên tắc một, cá nhân hoá phải tiết kiệm hành động, không phải tăng hành động.** Thành công của cá nhân hoá đo bằng số bước người dùng không phải làm nữa. Nếu nó chỉ tạo thêm thông báo và thêm lựa chọn, nó đang làm sản phẩm nặng hơn.

**Nguyên tắc hai, người dùng phải thấy được vì sao.** Mỗi gợi ý cá nhân hoá đi kèm một dòng lý do ngắn, ví dụ vì bạn thường gửi ở đây vào sáng thứ Ba. Nếu không giải thích được, gợi ý đó gây cảm giác bị theo dõi thay vì được phục vụ.

**Nguyên tắc ba, tắt được và sửa được.** Người dùng có thể xoá một điểm thân thuộc, sửa nhãn của nó, hoặc tắt toàn bộ cá nhân hoá mà sản phẩm vẫn dùng được bình thường.

**Nguyên tắc bốn, ưu đãi là công cụ lấp dung lượng trống, không phải công cụ mua tăng trưởng.** Đây là nguyên tắc kinh tế quan trọng nhất trong mục này và được nói riêng ở phần 4.5.

### 4.2. Đồ thị thói quen và điểm thân thuộc

**Tình huống.** Sau ba tuần dùng sản phẩm, anh Khoa đã có mười bốn lượt gửi xe. Trong đó mười một lượt vào khoảng 08 giờ ở cùng một khu vực Quận 1 và kết thúc khoảng 18 giờ, hai lượt vào tối thứ Bảy ở một khu ăn uống, một lượt ở bệnh viện.

**Trải nghiệm.** Ứng dụng tự nhận ra và đề nghị đặt tên cho hai địa điểm: nơi làm việc và nhà. Anh xác nhận. Từ đó, mỗi lần mở ứng dụng vào buổi sáng ngày làm việc, gợi ý đầu tiên đã là chỗ gửi quen gần nơi làm việc, kèm giá và tình trạng, chỉ cần một lần bấm.

**Bên trong.** Hệ thống nhóm các lượt gửi theo cụm địa lý và cụm thời gian, rồi gán nhãn suy đoán dựa trên mẫu hành vi: cụm xuất hiện vào giờ hành chính các ngày trong tuần thì có khả năng là nơi làm việc, cụm xuất hiện vào buổi tối và cuối tuần và gần với điểm bắt đầu hành trình thì có khả năng là nhà. Nhãn suy đoán luôn phải được người dùng xác nhận trước khi dùng để hiển thị.

Cấu trúc dữ liệu ở dạng khái niệm:

```
Hồ sơ thói quen của một người dùng
  Danh sách điểm thân thuộc: nhãn, toạ độ, bán kính, độ tin cậy
  Mẫu thời gian: theo ngày trong tuần và khung giờ, tần suất, thời lượng gửi trung bình
  Bãi thường dùng cho mỗi điểm thân thuộc, kèm số lần đã dùng
  Sở thích suy ra: mức giá thường chọn, có ưu tiên mái che hay không,
                    quãng đi bộ tối đa thường chấp nhận
  Ràng buộc cứng do người dùng khai: giới hạn chiều cao xe, xe điện cần sạc
```

**Dữ liệu cần.** Lịch sử lượt gửi của chính người dùng đó. Nền tảng đã được thiết kế theo nguyên tắc ghi nhận đầy đủ truy vấn tìm kiếm, các lựa chọn được hiển thị và quyết định cuối của người dùng, đây chính là nguyên liệu.

**Giá trị.** Giảm hành trình từ nhiều bước xuống một bước cho nhóm người dùng có tần suất cao nhất, tức là nhóm quan trọng nhất về doanh thu. Đồng thời đây là nền cho mọi tính năng cá nhân hoá phía sau.

### 4.3. Dự đoán ý định và gợi ý chủ động

**Tình huống.** 07 giờ 35 sáng thứ Ba. Anh Khoa chưa mở ứng dụng. Hệ thống đã biết ba điều: hôm nay là ngày làm việc, anh thường xuất phát trong khoảng mười phút tới, và bãi anh hay gửi hiện còn năm chỗ nhưng theo nhịp lịch sử thì sẽ hết trước 08 giờ 10.

**Trải nghiệm.** Một thông báo duy nhất: bãi bạn thường gửi còn năm chỗ và thường hết trước 08 giờ 10, giữ chỗ ngay hay không. Một lần bấm là xong. Nếu anh không phản hồi, hệ thống không nhắc lại lần thứ hai trong buổi sáng đó.

**Bên trong.** Điều kiện để gửi một gợi ý chủ động phải chặt, vì thông báo là tài nguyên dễ bị lạm dụng nhất trong sản phẩm. Bốn điều kiện đồng thời: mẫu hành vi phải đủ mạnh, ví dụ ít nhất sáu lần lặp trong bốn tuần; phải có thông tin mới thực sự hữu ích, ví dụ nguy cơ hết chỗ hoặc có ưu đãi, chứ không phải nhắc suông; phải đúng thời điểm còn hành động được; và phải tôn trọng hạn mức thông báo, tối đa một gợi ý chủ động mỗi buổi.

Một mở rộng đáng giá là dự đoán từ lịch trình khi người dùng cho phép: nếu người dùng liên kết lịch làm việc và có một cuộc hẹn ở địa chỉ lạ vào 14 giờ, hệ thống có thể chuẩn bị sẵn phương án đỗ xe cho địa chỉ đó. Tính năng này phải là tuỳ chọn bật, mặc định tắt.

**Dữ liệu cần.** Hồ sơ thói quen, dự báo chỗ trống, và quyền gửi thông báo.

**Giá trị.** Đây là tính năng biến sản phẩm từ công cụ được mở khi cần thành trợ lý luôn đi trước một bước, và đó là khác biệt về mức độ gắn bó. Về mặt kinh doanh, nó nâng tỷ lệ giữ chỗ trước, tức là nâng độ chắc chắn của doanh thu cho bãi.

### 4.4. Xếp hạng theo trọng số riêng của từng người

**Tình huống.** Cùng một danh sách ba bãi, hai người dùng chọn khác nhau. Anh Khoa luôn chọn bãi có mái che dù đắt hơn hai mươi nghìn. Anh Sơn luôn chọn bãi rẻ nhất và sẵn sàng đi bộ mười phút. Nếu hệ thống xếp hạng giống nhau cho cả hai, thì với một trong hai người, gợi ý đầu tiên luôn sai.

**Trải nghiệm.** Người dùng không thấy tính năng này, họ chỉ thấy rằng gợi ý ngày càng đúng ý hơn. Đây là loại tính năng tốt nhất khi vô hình.

**Bên trong.** Điểm phù hợp của một bãi với một người dùng là tổ hợp có trọng số của nhiều thành phần, và trọng số được điều chỉnh theo từng người:

```
Điểm phù hợp
  = w1 * điểm thời gian lái xe tới bãi
  + w2 * điểm quãng đi bộ tới điểm đến
  + w3 * điểm khả năng còn chỗ khi tới
  + w4 * điểm giá so với ngưỡng thường chọn của người dùng
  + w5 * điểm khớp thuộc tính, ví dụ mái che, hầm, sạc điện
  + w6 * điểm tin cậy của bãi
  + w7 * điểm quen thuộc, đã từng gửi và không có sự cố
```

Giai đoạn đầu, khi chưa có dữ liệu người dùng, dùng bộ trọng số mặc định theo loại chuyến đi, vì một chuyến đi làm hàng ngày có ưu tiên khác một chuyến đi bệnh viện. Khi đã có lịch sử, hệ thống điều chỉnh trọng số theo hành vi thật: người dùng bỏ qua lựa chọn rẻ để chọn lựa chọn có mái che thì tăng w5 và giảm w4 cho người đó.

Ba điểm cần cẩn thận. Thứ nhất, phải chống hiệu ứng bong bóng: nếu chỉ luôn gợi ý bãi quen, hệ thống mất khả năng biết người dùng có thể thích bãi khác hơn, nên cần chèn một lựa chọn khám phá ở vị trí thấp hơn. Thứ hai, sự thay đổi hoàn cảnh phải được phát hiện: người dùng đổi nơi làm việc thì hồ sơ cũ trở thành nhiễu, nên trọng số phải suy giảm theo thời gian. Thứ ba, cá nhân hoá không được che mắt về giá: nếu một bãi khác rẻ hơn đáng kể, phải hiển thị điều đó dù người dùng thường không nhạy giá.

**Dữ liệu cần.** Lịch sử các lựa chọn được hiển thị và lựa chọn được chọn, tức là dữ liệu về cả cái được chọn và cái bị bỏ qua. Đây là loại dữ liệu mà chỉ đơn vị tự vận hành mới có.

**Giá trị.** Tăng tỷ lệ người dùng chấp nhận gợi ý đầu tiên, đây là chỉ số trực tiếp của chất lượng sản phẩm. Về phía nền tảng, đây là một trong những lớp phòng vệ bền nhất, vì nó là tài sản dữ liệu tích luỹ theo thời gian.

### 4.5. Ưu đãi đúng người, đúng lúc, đúng chỗ trống

Đây là mục cần nói kỹ, vì đây là nơi các nền tảng thường đốt tiền vô ích.

**Cách làm sai.** Phát mã giảm giá đại trà cho toàn bộ người dùng để tăng số lượt. Kết quả: giảm giá cho cả những lượt vốn đã xảy ra, tức là trả tiền để mua doanh thu của chính mình, đồng thời huấn luyện người dùng chờ có mã mới đặt chỗ.

**Cách làm đúng.** Coi ưu đãi là công cụ dịch chuyển nhu cầu vào những chỗ và giờ đang trống. Một chỗ đỗ trống lúc 14 giờ thứ Ba là hàng hoá sẽ hết giá trị khi 14 giờ đi qua, giống một phòng khách sạn không bán được trong đêm nay. Vì vậy bán nó với giá thấp hơn không phải mất mát, mà là thu hồi một phần giá trị đang bằng không.

**Tình huống.** Bãi hầm của anh Tuấn lấp đầy tám mươi lăm phần trăm ban ngày nhưng chỉ hai mươi phần trăm từ 22 giờ tới 06 giờ. Trong khi đó, cách bãi bốn trăm mét có một khu dân cư mà nhiều hộ không có chỗ đỗ ban đêm.

**Trải nghiệm phía người dùng.** Chị Mai, sống trong khu dân cư đó, nhận một đề nghị: gói gửi qua đêm từ 19 giờ tới 07 giờ tại bãi cách nhà bốn trăm mét, giá thấp hơn ba mươi phần trăm so với giá theo giờ cộng dồn, cam kết có chỗ mỗi đêm. Đề nghị này không đến với những người không sống gần đó, và không đến vào lúc chị đang tìm chỗ gửi ban ngày.

**Bên trong.** Điều kiện để hệ thống phát một ưu đãi:

| Điều kiện | Vì sao cần |
|---|---|
| Dung lượng dự báo còn trống trong khung giờ đích | Không giảm giá khi bãi sắp đầy, vì như vậy là bán rẻ chỗ vốn bán được giá đầy |
| Người nhận có khả năng phát sinh nhu cầu ở khu vực và khung giờ đó | Ưu đãi gửi cho người ở cách mười ki lô mét là ưu đãi bị bỏ qua, làm loãng kênh thông báo |
| Ưu đãi không trùng với hành vi vốn đã xảy ra | Không giảm giá cho lượt mà người dùng chắc chắn sẽ đặt dù không có ưu đãi |
| Chủ bãi đã đồng ý mức giá sàn cho khung giờ đó | Ưu đãi phải nằm trong phần biên mà chủ bãi cho phép, không phải nền tảng tự trợ giá vô hạn |
| Có cách đo được kết quả | Mỗi chiến dịch phải đo được số lượt tăng thêm thật, bằng cách giữ một nhóm đối chứng không nhận ưu đãi |

Ba dạng ưu đãi nên dùng, theo mức độ hiệu quả giảm dần:

Dạng một, giá theo khung giờ thấp điểm, công khai và ổn định. Đây không phải mã giảm giá mà là bảng giá, nên nó tạo thói quen thay vì tạo phản xạ chờ đợi.
Dạng hai, gói định kỳ cho nhu cầu lặp lại, ví dụ gói qua đêm, gói ngày làm việc. Đây là ưu đãi đổi lấy cam kết, tức là hai bên đều được lợi.
Dạng ba, ưu đãi cá nhân có điều kiện, dùng để thử phá vỡ một thói quen cụ thể, ví dụ đưa người dùng thử một bãi mới trong mạng lưới đang thiếu nhu cầu. Dạng này tốn kém nhất nên phải dùng ít và phải đo.

**Giá trị.** Với chủ bãi, đây là công cụ tăng doanh thu từ dung lượng vốn đang mất trắng, và là một trong những lý do mạnh nhất để họ ở lại mạng lưới. Với nền tảng, đây là cách tăng số lượt mà không phá giá, vì mọi khoản giảm đều được cấp phép bởi phần biên của chủ bãi.

### 4.6. Tắc đường, thời tiết và các yếu tố ngữ cảnh

**Tình huống.** 17 giờ 40 một chiều mưa. Anh Khoa cần tới một địa chỉ ở trung tâm. Bình thường mất mười tám phút, hôm nay mất ba mươi lăm phút. Bãi anh hay gửi thường hết chỗ lúc 18 giờ, nhưng khi mưa thì người ta rời bãi chậm hơn và nhu cầu gửi lại tăng lên.

**Trải nghiệm.** Hệ thống cảnh báo trước hai điều: thời gian di chuyển hiện tại cao hơn bình thường, và với thời gian đó thì bãi quen có khả năng đã hết chỗ, nên nên giữ chỗ ngay hoặc chọn bãi thay thế. Ngoài ra, với các bãi ngoài trời có tiền sử ngập, hệ thống hạ thứ hạng khi đang có mưa lớn trong khu vực.

**Bên trong.** Ba yếu tố ngữ cảnh có ảnh hưởng đo được và nên đưa vào mô hình:

| Yếu tố | Ảnh hưởng | Nguồn dữ liệu |
|---|---|---|
| Tình trạng giao thông | Thay đổi thời gian tới nơi, do đó thay đổi toàn bộ kết quả dự đoán chỗ trống khi tới | Dịch vụ định tuyến, kết hợp thời gian di chuyển thực tế ghi nhận từ chính người dùng của hệ thống |
| Mưa | Tăng nhu cầu gửi xe có mái che, kéo dài thời lượng gửi, tăng rủi ro ngập ở bãi ngoài trời | Dịch vụ thời tiết, nền tảng đã có sẵn thành phần này |
| Sự kiện và ngày đặc biệt | Tạo đỉnh nhu cầu bất thường ở một khu vực, ví dụ khu vực quanh nơi tổ chức sự kiện, ngày lễ, cuối tuần dài | Lịch sự kiện của khu vực, dữ liệu lịch sử các dịp tương tự |

Điểm quan trọng về dữ liệu giao thông: dịch vụ định tuyến cho thời gian di chuyển ước lượng, nhưng hệ thống có một nguồn tốt hơn theo thời gian. Mỗi lượt người dùng đi từ lúc giữ chỗ tới lúc camera đọc biển số ở cổng là một điểm dữ liệu về thời gian di chuyển thực tế trên một tuyến, vào một khung giờ, trong một điều kiện thời tiết. Sau vài tháng, dữ liệu này cho phép hiệu chỉnh ước lượng của dịch vụ định tuyến cho đúng đặc thù từng tuyến đường trong thành phố. Đây là một lớp dữ liệu độc quyền mà không mua được.

**Giá trị.** Nâng độ chính xác của dự đoán trong đúng những tình huống mà người dùng cần nhất, tức là lúc đường tắc và trời mưa. Sản phẩm được đánh giá bằng những lần khó, không phải bằng những lần dễ.

### 4.7. Ranh giới của cá nhân hoá

Ba việc hệ thống không làm, và cần ghi rõ để tránh trượt dần theo thời gian:

Không suy đoán và không hiển thị những thông tin nhạy cảm suy ra được từ hành vi đỗ xe. Việc một người thường xuyên gửi xe ở bệnh viện, ở một cơ sở tôn giáo, hay ở một địa chỉ cụ thể vào buổi đêm là thông tin có thể suy ra điều rất riêng tư. Hệ thống dùng dữ liệu này để gợi ý chỗ đỗ, và không tạo ra bất kỳ nhãn suy đoán nào về tình trạng sức khoẻ, tôn giáo, quan hệ hay đời sống cá nhân.

Không chia sẻ hồ sơ thói quen của một người dùng cho chủ bãi. Chủ bãi thấy dữ liệu tổng hợp về nhu cầu, không thấy hành trình của từng người. Thông tin chủ bãi nhận được về một lượt gửi chỉ gồm những gì cần cho vận hành lượt đó.

Không dùng dữ liệu cá nhân để phân biệt giá theo cách gây bất lợi. Nếu hệ thống học được rằng một người ít nhạy cảm về giá, thông tin đó không được dùng để tính giá cao hơn cho cùng một chỗ đỗ vào cùng một thời điểm. Giá thay đổi theo cung cầu và khung giờ, công khai với mọi người, chứ không theo mức độ sẵn sàng trả của từng người.

---

## 5. Hành trình chủ bãi

Phần này quan trọng ngang phần người lái xe, vì không có chủ bãi thì không có dữ liệu, và không có dữ liệu thì không có sản phẩm.

### B1. Ngày đầu tiên: chủ bãi thấy điều họ chưa từng thấy

**Tình huống.** Anh Tuấn quản lý bãi hầm 150 chỗ. Nếu hỏi anh hôm qua bãi lấp đầy bao nhiêu phần trăm vào lúc 15 giờ, anh không trả lời được. Nếu hỏi tháng trước bãi thu bao nhiêu, anh đọc được con số trên sổ, nhưng không biết con số đó có đúng không.

**Trải nghiệm.** Sau khi lắp thiết bị, trong tuần đầu tiên anh nhận một báo cáo mà anh chưa từng có: đường cong lấp đầy theo từng giờ trong ngày, trung bình theo từng ngày trong tuần, số lượt xe vào và ra, thời lượng gửi trung bình, và ba khung giờ đang trống nhiều nhất. Trải nghiệm này là thứ khiến chủ bãi tin rằng hệ thống hoạt động, trước cả khi nói tới doanh thu thêm.

**Bên trong.** Toàn bộ báo cáo được sinh từ hai luồng dữ liệu của lớp cảm nhận: model đếm chỗ trống chạy liên tục theo chu kỳ, và model nhận diện biển số ghi nhận sự kiện vào và ra tại cổng.

**Giá trị.** Đây là tính năng bán hàng mạnh nhất trong buổi gặp thứ hai với chủ bãi, vì nó không phải lời hứa mà là dữ liệu của chính bãi họ.

### B2. Chống thất thu: một con số không tranh chấp được

**Tình huống.** Bãi của anh Tuấn thu tiền mặt cho khách lẻ. Ba bảo vệ ba ca. Cuối tháng, số lượt ghi trong sổ và số tiền nộp về không khớp nhau một cách nhất quán, nhưng không truy được ở đâu và không muốn làm căng với nhân viên vì thiếu bằng chứng.

**Trải nghiệm.** Sau khi lắp, mỗi xe vào bãi đều tạo ra một bản ghi có biển số, ảnh, mốc thời gian. Mỗi xe ra tạo ra bản ghi tương ứng và một số tiền tính theo thời gian gửi thực tế. Cuối ngày, hệ thống đối soát: số lượt hệ thống ghi nhận, số tiền lẽ ra phải thu, số tiền đã thu qua nền tảng, số tiền thu tiền mặt do bảo vệ nhập. Chênh lệch hiện ra thành một dòng, không cần tranh luận.

**Bên trong.** Hai model nhận diện biển số đã làm đúng việc này, gồm cả cơ chế ghép ký tự theo toạ độ ngang để xử lý biển hai dòng. Phần bổ sung là quy trình đối soát và xử lý ngoại lệ đã nêu ở A5.

**Giá trị.** Đây là tính năng có giá trị tiền tệ trực tiếp và đo được trong tháng đầu, nên nó là cơ sở để chủ bãi chấp nhận trả phí thiết bị và phần mềm. Nó cũng là lý do vì sao mô hình kinh doanh của Parking HUB không phụ thuộc hoàn toàn vào số lượt đặt chỗ từ người dùng mới.

### B3. Phát hiện khói và lửa sớm

Tính năng này được trình bày riêng ở mục 7, vì nó có trọng lượng đặc biệt cả về mặt sản phẩm lẫn về mặt bán hàng.

### B4. Bảng điều khiển vận hành hàng ngày

**Trải nghiệm.** Một màn hình duy nhất cho người quản lý bãi: số chỗ trống hiện tại theo từng khu và từng tầng, danh sách xe đang trong bãi, danh sách lượt đã giữ chỗ sắp tới trong hai giờ, doanh thu trong ngày, các cảnh báo đang mở, và tình trạng thiết bị. Trên điện thoại của bảo vệ là một phiên bản rút gọn chỉ còn ba việc: xem lượt giữ chỗ sắp tới, xác nhận thủ công khi nhận diện biển số thất bại, và nhận cảnh báo.

**Bên trong.** Nền tảng đã có cổng dành cho chủ điểm dịch vụ với các trang quản lý hàng đợi, danh mục dịch vụ, điểm chất lượng và phân tích. Bộ khung này chuyển sang dùng cho bãi đỗ với việc đổi nghiệp vụ bên dưới.

**Giá trị.** Công cụ vận hành hàng ngày là thứ tạo ra chi phí chuyển đổi. Khi bảo vệ đã dùng ứng dụng này mỗi ca làm việc và quản lý đã đọc báo cáo này mỗi sáng, việc thay nhà cung cấp không còn là quyết định đơn giản.

### B5. Bán giờ thấp điểm và định giá theo nhu cầu

**Tình huống.** Bãi của anh Tuấn trống tám mươi phần trăm từ 22 giờ tới 06 giờ, và trống một nửa vào cuối tuần vì đây là toà nhà văn phòng.

**Trải nghiệm.** Hệ thống đề xuất cụ thể: mở bán gói gửi qua đêm cho khu dân cư trong bán kính năm trăm mét với mức giá đề xuất, ước tính số lượt và doanh thu tăng thêm dựa trên nhu cầu quan sát được ở khu vực đó. Anh Tuấn bấm đồng ý hoặc sửa giá. Nếu sau bốn tuần kết quả không như ước tính, hệ thống báo lại và đề xuất điều chỉnh.

**Bên trong.** Ba thành phần: dự báo dung lượng trống theo khung giờ, tín hiệu nhu cầu chưa được phục vụ trong khu vực lấy từ các lượt tìm kiếm không tìm được bãi phù hợp, và khung định giá do chủ bãi đặt giới hạn sàn và trần. Nền tảng đề xuất, chủ bãi quyết định. Nguyên tắc này cần giữ nghiêm, vì định giá là quyền của chủ tài sản, và việc nền tảng tự đổi giá sẽ phá vỡ quan hệ.

**Giá trị.** Đây là nguồn doanh thu mới thật cho chủ bãi, và là cơ sở để nền tảng thu phần chia doanh thu một cách chính đáng, vì phần chia đó tính trên doanh thu tăng thêm chứ không phải trên doanh thu vốn đã có.

### B6. Bán gói tháng và quản lý khách quen

**Trải nghiệm.** Chủ bãi tạo các gói: gói ngày làm việc, gói qua đêm, gói cuối tuần, gói không giới hạn theo tháng, mỗi gói có số lượng suất giới hạn để không bán quá dung lượng. Hệ thống lo phần thu tiền định kỳ, nhắc gia hạn, và nhận diện xe của khách gói ngay tại cổng mà không cần thẻ.

**Bên trong.** Dung lượng bán cho gói tháng bị trừ khỏi dung lượng khả dụng của các khung giờ tương ứng, và có ngưỡng tối đa để bảo vệ khách vãng lai.

**Giá trị.** Doanh thu định kỳ cho chủ bãi và cho nền tảng, đồng thời là công cụ giữ người dùng mạnh nhất ở phía cầu.

### B7. Bằng chứng hình ảnh và xử lý tranh chấp

**Tình huống.** Khách khiếu nại rằng xe bị xước trong lúc gửi. Không có bằng chứng, chủ bãi hoặc phải bồi thường cho một việc có thể không do mình gây ra, hoặc phải từ chối và mất khách cùng danh tiếng.

**Trải nghiệm.** Hệ thống lưu ảnh xe tại thời điểm vào và thời điểm ra, cùng ảnh khu vực đỗ theo chu kỳ, trong thời hạn lưu trữ đã công bố. Khi có tranh chấp, quy trình có ba bước rõ ràng và có mốc thời gian, và hai bên đều xem được cùng một bộ bằng chứng.

**Bên trong.** Lưu trữ hình ảnh phải có thời hạn xác định và cơ chế tự động xoá, có nhật ký truy cập, và chỉ những vai trò được phân quyền mới xem được. Đây là yêu cầu tuân thủ, xem mục 10.

**Giá trị.** Giảm loại chi phí khó chịu nhất của chủ bãi, và tạo thêm một lý do để họ chọn hệ thống có camera thay vì vận hành thủ công.

### B8. Chỗ đỗ nhỏ của hộ dân

**Tình huống.** Ông Bảy có bốn chỗ trống ban ngày trong sân nhà tại Quận 3. Không có barrier, không có bảo vệ, không có camera công nghiệp.

**Trải nghiệm.** Ông đăng chỗ bằng điện thoại, chụp ảnh sân và lối vào, khai khung giờ cho thuê, giá theo giờ và theo tháng, và các giới hạn ví dụ chiều cao và chiều dài xe. Người thuê được xác thực danh tính trước khi được phép đặt. Khi có người đặt, ông nhận thông báo với biển số và khung giờ. Lúc giao và nhận, hai bên chụp ảnh xe trong ứng dụng, đây là bằng chứng nếu có tranh chấp. Tiền vào ví của ông theo kỳ, không phải đi thu.

**Bên trong.** Phân khúc này không có lớp cảm nhận bằng camera AI, nên trạng thái chỗ trống được quản lý theo lịch đặt chỗ chứ không theo quan sát. Điều đó chấp nhận được vì dung lượng nhỏ và luôn được bán theo khung giờ đã định trước. Nói cách khác, với bãi lớn thì hệ thống bán chỗ dựa trên quan sát, còn với chỗ nhỏ thì hệ thống bán thời gian dựa trên lịch.

Rủi ro cần kiểm soát: an toàn của cả hai bên, tranh chấp về hư hỏng, và việc chủ chỗ nhận tiền rồi không mở cổng. Cơ chế xử lý gồm xác thực danh tính hai chiều, bằng chứng ảnh, giữ tiền cho tới khi lượt gửi bắt đầu, chấm điểm cả hai phía, và loại khỏi mạng lưới nếu vi phạm nhiều lần. Ngoài ra cần rà soát điều kiện pháp lý của việc cho thuê chỗ đỗ trong nhà ở, đây là hạng mục cần ý kiến pháp lý trước khi mở rộng.

**Giá trị.** Đây là cách tăng mật độ mạng lưới nhanh nhất và rẻ nhất, đúng ở những nơi mà bãi lớn không tồn tại. Nó cũng là phần khiến sản phẩm có tính bao trùm về mặt xã hội, vì nó tạo thu nhập cho hộ gia đình từ tài sản đang bỏ không.

### B9. Ban quản trị chung cư và bài toán tuân thủ

**Tình huống.** Chung cư 400 căn, hầm 210 chỗ, có xe điện sạc trong hầm. Quy định về khu để xe điện tại nhà chung cư có hiệu lực từ 15/12/2025 yêu cầu bố trí khu riêng, có camera giám sát liên tục, báo cháy tự động và thiết bị cảnh báo CO cùng HF. Ban quản trị cần một phương án trình cư dân.

**Trải nghiệm.** Parking HUB cung cấp lớp phát hiện khói lửa sớm bằng thị giác máy tính lắp trên hạ tầng camera của hầm, kết hợp bảng theo dõi cho ban quản lý và kênh cảnh báo tới bảo vệ, ban quản trị và cư dân đang gửi xe. Song song, hệ thống cho phép công khai tình trạng chỗ đỗ trong hầm cho cư dân, và nếu ban quản trị muốn, mở bán phần dung lượng thực sự trống ban ngày cho người ngoài với nguồn thu về quỹ chung.

**Bên trong.** Cần nói rõ giới hạn để không hứa quá: lớp thị giác máy tính bổ sung cho hệ thống phòng cháy chữa cháy chứ không thay thế nó, và không thay thế các thiết bị cảnh báo khí theo quy định. Vai trò của nó là rút ngắn thời gian phát hiện ở giai đoạn khói mỏng, tức là giai đoạn mà đầu báo trên trần chưa kích hoạt.

**Giá trị.** Đây là cửa vào có động lực mạnh nhất hiện nay, vì nó gắn với một nghĩa vụ có thời hạn. Với mạng lưới, mỗi hầm chung cư onboard theo cửa này mang lại một khối dung lượng lớn nằm sâu trong khu dân cư, tức là đúng chỗ mà mạng lưới cần để đạt mật độ.

---

## 6. Bộ não hệ thống

Phần này tóm lược các thành phần thông minh và vai trò của từng thành phần. Đặc tả kỹ thuật chi tiết thuộc tài liệu 09 sẽ viết sau.

### 6.1. Bốn model thị giác máy tính

| Model | Đầu vào | Đầu ra | Đã có gì | Cần làm thêm |
|---|---|---|---|---|
| Đếm chỗ đỗ trống | Khung hình từ camera quan sát khu đỗ | Số ô trống và vị trí ô trống theo khu | Đã chạy trên YOLOv8, đã demo đếm chỗ trên bãi thật | Huấn luyện thêm cho hầm thiếu sáng, góc nghiêng, xe che nhau. Hiệu chuẩn theo từng bãi. Chuyển suy luận ra thiết bị biên |
| Phát hiện vùng biển số | Khung hình từ camera cổng | Vùng ảnh chứa biển số, đã cắt và chuẩn hoá | Đã chạy, gồm cả bước xoay và chuẩn hoá | Tăng dữ liệu ban đêm, ngược sáng, mưa, biển bẩn |
| Đọc ký tự biển số | Ảnh biển số đã cắt | Chuỗi biển số hoàn chỉnh | Đã chạy, ghép ký tự theo toạ độ ngang, hỗ trợ biển một dòng và hai dòng của Việt Nam | Xử lý ngoại lệ, cơ chế đối chiếu với danh sách xe trong bãi để sửa lỗi một ký tự |
| Phát hiện khói và lửa | Khung hình từ camera trong bãi | Có hay không có khói, có hay không có lửa, kèm vị trí trong khung hình | Đã chạy song song với luồng đếm chỗ, có cơ chế ưu tiên khi phát hiện cháy | Giảm báo động sai trong môi trường có khói xe, bụi, đèn xe. Hiệu chuẩn ngưỡng theo từng bãi. Đây là hạng mục cần đầu tư dữ liệu nhiều nhất |

Ba điểm về kiến trúc triển khai, xuất phát từ chính giới hạn đã gặp khi chạy suy luận tập trung trên máy chủ, nơi hiệu năng video trực tiếp bị chặn bởi tài nguyên máy chủ:

Thứ nhất, suy luận phải chạy tại bãi trên thiết bị biên, không đẩy toàn bộ luồng video về máy chủ trung tâm. Băng thông và chi phí máy chủ sẽ không cho phép làm khác khi số bãi tăng lên hàng trăm.

Thứ hai, chỉ dữ liệu kết quả được gửi lên trung tâm, ví dụ số chỗ trống, sự kiện xe vào với biển số, sự kiện phát hiện khói kèm một khung hình. Hình ảnh chỉ được gửi khi cần thiết. Cách này vừa giảm chi phí vừa giảm rủi ro dữ liệu.

Thứ ba, thiết bị biên phải chạy được khi mất mạng và đồng bộ lại sau, vì mất mạng ở tầng hầm là chuyện thường xuyên.

### 6.2. Hai model dữ liệu, cần xây mới

| Model | Nhiệm vụ | Cách làm giai đoạn đầu | Cách làm khi đã có dữ liệu |
|---|---|---|---|
| Dự báo chỗ trống theo thời gian | Trả lời câu hỏi bãi này còn bao nhiêu chỗ vào một mốc thời gian trong tương lai, từ vài phút tới vài ngày | Quy tắc và trung bình lịch sử theo ngày trong tuần và khung giờ, hiệu chỉnh theo mưa và ngày lễ | Mô hình chuỗi thời gian cho từng bãi, có yếu tố ngoại sinh gồm thời tiết, sự kiện, ngày lễ. Đánh giá bằng sai số so với thực tế |
| Xếp hạng và cá nhân hoá | Sắp thứ tự các bãi phù hợp cho một người dùng cụ thể trong một ngữ cảnh cụ thể | Bộ trọng số mặc định theo loại chuyến đi | Học trọng số riêng cho từng người dùng từ lịch sử lựa chọn và bỏ qua |

Nguyên tắc chung: mỗi thành phần chấm điểm là một hàm độc lập, có thể thay thế và hiệu chỉnh riêng, không gộp thành một mô hình lớn duy nhất. Nhờ vậy, giai đoạn khởi động dùng quy tắc, giai đoạn sau dùng học máy, mà đường đi của dữ liệu trong hệ thống không thay đổi.

### 6.3. Engine ghép nối

Engine ghép nối là nơi hợp tất cả lại. Luồng xử lý một truy vấn:

```
Người dùng gửi yêu cầu: điểm đến, thời gian, loại xe, ràng buộc cứng
        |
   Lọc theo ràng buộc cứng
   (chiều cao xe, cần trụ sạc, bãi còn hoạt động trong khung giờ đó)
        |
   Lấy tập bãi trong bán kính đi bộ quanh điểm đến
        |
   Với mỗi bãi:
     tính thời gian lái xe tới bãi và quãng đi bộ tới điểm đến
     lấy chỗ trống hiện tại từ lớp cảm nhận
     dự báo chỗ trống tại thời điểm người dùng tới
     trừ phần dung lượng đã bị giữ trong khung giờ đó
     tính giá dự kiến theo thời lượng gửi
        |
   Tính điểm phù hợp theo trọng số riêng của người dùng
        |
   Sắp thứ tự, chèn một lựa chọn khám phá, trả về ba lựa chọn
        |
   Ghi nhận toàn bộ: truy vấn, các lựa chọn đã hiển thị, lựa chọn được chọn
```

Bước cuối cùng là bước dễ bị bỏ qua nhưng quan trọng nhất về dài hạn. Ghi lại cả những lựa chọn bị bỏ qua chính là điều kiện để học được sở thích của người dùng. Nền tảng đã được thiết kế theo nguyên tắc này từ đầu, và Parking HUB giữ nguyên.

---

## 7. An toàn cháy nổ trong bãi đỗ

### 7.1. Vì sao tính năng này quan trọng hơn vẻ ngoài của nó

Nhìn từ phía sản phẩm dành cho người lái xe, phát hiện cháy là tính năng phụ. Nhìn từ phía mô hình kinh doanh, đây là tính năng mở cửa. Ba lý do:

Thứ nhất, đây là nỗi lo lớn nhất của người quản lý bãi kín, và là loại nỗi lo mà người ta chịu trả tiền để giảm.

Thứ hai, quy định đã chuyển thành nghĩa vụ có thời hạn. Từ ngày 15/12/2025, khu để xe điện tại nhà chung cư phải bố trí riêng, có camera giám sát 24 trên 24, hệ thống báo cháy tự động và thiết bị cảnh báo CO cùng HF. Nghĩa là ngân sách đã có và người quyết định đã có động lực.

Thứ ba, khoảng trống kỹ thuật là thật. Hệ thống báo cháy truyền thống trong hầm dựa vào đầu báo nhiệt hoặc đầu báo khói trên trần, và chúng kích hoạt khi nhiệt hoặc khói đã đủ lớn để lan tới trần. Với một xe bắt đầu cháy trong hầm kín, khoảng thời gian từ lúc có khói mỏng tới lúc đầu báo kích hoạt là khoảng thời gian quyết định giữa một sự cố dập được bằng bình chữa cháy tay và một vụ cháy lan sang các xe bên cạnh. Camera nhìn thấy khói ngay trong khung hình, tại chỗ, không cần chờ khói lan.

### 7.2. Cách hoạt động

**Tình huống.** 02 giờ 15 sáng, một xe điện đang sạc ở góc B của hầm B1 bắt đầu phát khói mỏng. Bảo vệ trực đang ở chốt cổng, cách đó bốn mươi mét và không nhìn thấy.

**Trải nghiệm.** Trong vòng vài giây, ba việc xảy ra cùng lúc. Điện thoại bảo vệ đổ chuông với một khung hình, vị trí chính xác là hầm B1 góc B, và một nút xác nhận đã tiếp cận. Màn hình phòng quản lý hiện cảnh báo. Chủ các xe đang gửi trong hầm nhận thông báo. Nếu sau một khoảng thời gian định trước mà không ai xác nhận đã tiếp cận, cảnh báo leo thang lên số điện thoại của người phụ trách tiếp theo trong danh sách.

**Bên trong.** Model phát hiện khói và lửa chạy trên thiết bị biên, phân tích theo chu kỳ trên các camera đã chọn. Khi có tín hiệu, hệ thống áp một lớp xác nhận để giảm báo động sai, ví dụ yêu cầu tín hiệu duy trì qua nhiều khung hình liên tiếp, và đối chiếu với vùng thường xuyên có nhiễu như miệng đường dốc có khói xe. Sau khi vượt ngưỡng, cảnh báo được phát và toàn bộ chuỗi khung hình quanh thời điểm đó được lưu lại làm bằng chứng.

Trong phiên bản đã chạy thực tế, luồng phát hiện cháy chạy song song với luồng đếm chỗ bằng đa luồng, và khi phát hiện cháy thì luồng đếm chỗ được tạm dừng để ưu tiên xử lý cảnh báo. Nguyên tắc ưu tiên này được giữ lại.

**Điều tính năng này không làm.** Không thay thế hệ thống phòng cháy chữa cháy. Không thay thế thiết bị cảnh báo khí. Không tự động kích hoạt hệ thống chữa cháy trong giai đoạn đầu, vì một cảnh báo sai dẫn tới phun nước trong hầm đầy xe là thiệt hại lớn. Việc liên động với hệ thống chữa cháy chỉ nên xét tới sau khi tỷ lệ báo động sai đã được chứng minh ở mức rất thấp qua nhiều tháng vận hành.

### 7.3. Chỉ tiêu cần đạt

| Chỉ tiêu | Mức mục tiêu | Vì sao |
|---|---|---|
| Thời gian từ khi khói xuất hiện trong khung hình tới khi cảnh báo tới người trực | Dưới 10 giây | Toàn bộ giá trị của tính năng nằm ở thời gian |
| Tỷ lệ bỏ sót | Càng thấp càng tốt, và phải đo được trên bộ dữ liệu kiểm thử có kịch bản khói nhỏ | Bỏ sót là loại lỗi nghiêm trọng nhất |
| Tỷ lệ báo động sai | Dưới 1 lần mỗi camera mỗi tuần sau hiệu chuẩn | Báo động sai nhiều thì người trực sẽ tắt thông báo, và khi đó tính năng mất tác dụng hoàn toàn |
| Hoạt động khi mất mạng | Cảnh báo tại chỗ vẫn phát bằng loa hoặc đèn tại bãi | Mất mạng không được làm mất khả năng cảnh báo |

Chỉ tiêu về báo động sai là chỉ tiêu bị coi nhẹ nhưng quyết định thành công thực tế. Một hệ thống cảnh báo mà người ta đã tắt thông báo là một hệ thống không tồn tại.

---

## 8. Phân cấp và phân khúc bãi đỗ

Người dùng không tìm bãi đỗ, họ tìm loại bãi đỗ phù hợp với hoàn cảnh của mình. Một người gửi xe hai giờ đi họp có nhu cầu khác một người gửi xe bốn ngày đi công tác. Vì vậy hệ thống cần hai trục phân loại độc lập.

### 8.1. Trục thứ nhất: phân khúc theo loại hình

Đây là thuộc tính khách quan, không phải đánh giá chất lượng.

| Loại bãi | Đặc điểm | Phù hợp nhu cầu | Điểm cần lưu ý khi onboard |
|---|---|---|---|
| Hầm toà nhà, văn phòng hoặc thương mại | Có mái, có kiểm soát ra vào, dung lượng lớn | Gửi theo giờ ban ngày, gửi qua đêm nếu toà nhà cho phép | Người quyết định là ban quản lý toà nhà, không phải bảo vệ |
| Hầm chung cư | Có mái, có kiểm soát, dung lượng lớn, trống ban ngày | Gửi ban ngày, gửi theo tháng cho người làm việc gần đó | Cần đồng thuận của ban quản trị và cư dân, có ràng buộc về an ninh và quy định phòng cháy |
| Bãi ngoài trời thương mại | Không mái hoặc mái một phần, dung lượng trung bình | Gửi ngắn, gửi giá thấp, xe cỡ lớn | Rủi ro ngập nước và nắng, cần khai báo trung thực |
| Bãi có mái che dạng nhà xe | Có mái, dung lượng trung bình | Gửi dài, gửi theo tháng | Thường là loại có tỷ lệ lấp đầy dao động lớn, phù hợp bán gói |
| Bãi lòng đường và bãi công cộng | Do đơn vị được giao quản lý, dung lượng nhỏ, phân tán | Gửi rất ngắn | Cần làm việc với đơn vị quản lý và tuân thủ quy định thu phí |
| Chỗ đỗ nhỏ của hộ dân | Từ một tới vài chỗ, không thiết bị | Gửi ban ngày, gửi theo tháng cho người ở gần | Cần cơ chế tin cậy và bằng chứng, xem B8 |
| Bãi tại đầu mối giao thông | Sân bay, bến xe, ga | Gửi nhiều ngày | Cạnh tranh với bãi chính thức, cần khác biệt bằng giá và dịch vụ đưa đón |

### 8.2. Trục thứ hai: phân cấp theo năng lực và mức tích hợp

Trục này quyết định mức cam kết mà nền tảng dám đưa ra với người dùng.

| Cấp | Tên | Điều kiện | Nền tảng cam kết được gì |
|---|---|---|---|
| Cấp 1 | Có trong danh mục | Đã kiểm định thông tin cơ bản: vị trí cổng vào, giá, giờ hoạt động, thuộc tính | Chỉ hiển thị thông tin, không cam kết còn chỗ |
| Cấp 2 | Có cập nhật | Chủ bãi cập nhật trạng thái qua ứng dụng theo quy trình, có ràng buộc về tần suất | Hiển thị trạng thái kèm mốc thời gian cập nhật, cho phép đặt chỗ theo lịch với xác nhận của bãi |
| Cấp 3 | Kết nối cảm nhận | Đã lắp camera AI đếm chỗ trống và nhận diện biển số tại cổng | Cam kết giữ chỗ, vào ra tự động, hiển thị trạng thái theo thời gian thực, tham gia dự báo |
| Cấp 4 | Kết nối đầy đủ | Cấp 3 cộng phát hiện khói lửa, đối soát doanh thu, và đạt ngưỡng điểm tin cậy | Được ưu tiên trong xếp hạng, được mở bán gói tháng và nhận hợp đồng đội xe, được gắn nhãn an toàn |

Ý nghĩa của việc phân cấp: nó cho phép mạng lưới phủ rộng nhanh bằng cấp 1 và cấp 2, trong khi vẫn giữ được chất lượng cam kết ở cấp 3 và cấp 4. Người dùng luôn thấy rõ mức nào, nên không bị hiểu sai. Và chủ bãi có một con đường nâng cấp rõ ràng với lợi ích cụ thể ở mỗi bậc, đây chính là động lực để họ đi lên. Chi tiết quy trình và chi phí từng cấp nằm ở [tài liệu 05](../02_business-operations/05_Onboarding_Playbook.md).

### 8.3. Điểm chất lượng bãi

Ngoài phân khúc và phân cấp, mỗi bãi có một điểm chất lượng tính từ dữ liệu vận hành, đã mô tả ở A10. Ba trục này độc lập với nhau: một bãi ngoài trời cấp 3 có thể có điểm chất lượng cao hơn một hầm cấp 4 vận hành kém. Việc tách ba trục giúp tránh sai lầm thường gặp là gộp mọi thứ vào một ngôi sao duy nhất rồi không ai hiểu ngôi sao đó nghĩa là gì.

---

## 9. Lớp dữ liệu công

### 9.1. Vì sao lớp này tồn tại

Ba lý do, theo thứ tự quan trọng.

Thứ nhất, nó tạo ra giá trị mà không bên nào khác tạo được. Khi mạng lưới có vài chục bãi trong một khu vực, hệ thống biết được điều mà cả cơ quan quản lý lẫn từng chủ bãi đều không biết: nhu cầu thực theo giờ, mức lấp đầy theo khu vực, và quan trọng nhất là nhu cầu không được phục vụ, tức là những lượt tìm kiếm mà hệ thống không có bãi phù hợp để trả về.

Thứ hai, nó gắn dự án với chủ đề của cuộc thi. Data for Life hướng tới Chính phủ số, kinh tế số và xã hội số, và Quyết định 502/QĐ-TTg ngày 28/03/2026 đã đặt ra phương án kết nối, chia sẻ dữ liệu giữa hệ thống camera giám sát an ninh trật tự, xử lý vi phạm và điều hành giao thông với Cơ sở dữ liệu quốc gia về dân cư, cùng việc chia sẻ dữ liệu với trung tâm giám sát và điều hành đô thị thông minh. Một mạng lưới bãi đỗ có dữ liệu chuẩn hoá là một mắt lưới tự nhiên trong bức tranh đó.

Thứ ba, nó là lợi thế cạnh tranh dài hạn. Khi dữ liệu của mạng lưới trở thành một đầu vào cho quy trình điều hành và quy hoạch của địa phương, vị thế đó không sao chép được bằng vốn.

### 9.2. Ba sản phẩm dữ liệu

| Sản phẩm | Nội dung | Dùng để làm gì |
|---|---|---|
| Bản đồ nhiệt giao thông tĩnh | Cung, cầu và mức lấp đầy theo khu vực và theo khung giờ, kèm các điểm có nhu cầu vượt cung kéo dài | Xác định điểm nghẽn, ưu tiên vị trí quy hoạch bãi mới, đánh giá hiệu quả sau khi mở bãi |
| Báo cáo nhu cầu không được phục vụ | Những khu vực và khung giờ mà người dùng tìm nhưng không có bãi phù hợp | Với nền tảng, đây là bản đồ đi onboard bãi tiếp theo. Với cơ quan quản lý, đây là bằng chứng định lượng về thiếu hạ tầng |
| Cảnh báo an toàn liên thông | Sự kiện phát hiện khói và lửa tại các bãi trong mạng lưới, kèm vị trí và thời điểm | Rút ngắn thời gian phản ứng của lực lượng chức năng, và tạo dữ liệu thống kê về rủi ro cháy trong bãi đỗ |

### 9.3. Nguyên tắc chia sẻ

Bốn nguyên tắc, và cả bốn đều phải nêu rõ trong hồ sơ nộp cuộc thi vì đây là điểm mà ban giám khảo thuộc lĩnh vực an ninh dữ liệu sẽ hỏi:

Một, chia sẻ dữ liệu tổng hợp phi định danh làm mặc định. Bản đồ nhiệt và báo cáo nhu cầu không chứa biển số, không chứa thông tin người dùng, không chứa hành trình cá nhân.

Hai, dữ liệu có thể định danh chỉ được chia sẻ trong phạm vi và theo trình tự pháp luật cho phép, với yêu cầu bằng văn bản của cơ quan có thẩm quyền, có nhật ký truy cập đầy đủ, và có thời hạn.

Ba, tuân thủ Luật Dữ liệu số 60/2024/QH15 và Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15, gồm nghĩa vụ thông báo, cơ sở xử lý hợp pháp, quyền truy cập và quyền yêu cầu xoá của người dùng.

Bốn, minh bạch với người dùng và với chủ bãi về việc dữ liệu nào được chia sẻ, ở mức tổng hợp nào, cho ai, và vì mục đích gì.

---

## 10. Bảo vệ dữ liệu cá nhân trong từng tính năng

Dự án này xử lý hai loại dữ liệu có độ nhạy cao: biển số xe, vì nó gắn với chủ xe và gắn với hành trình di chuyển, và hình ảnh camera, vì nó có thể chứa hình ảnh người. Bảng dưới đây là bản kiểm tra theo từng tính năng, và cần được rà soát cùng ý kiến pháp lý trước khi triển khai thật.

| Tính năng | Dữ liệu cá nhân liên quan | Nguyên tắc áp dụng |
|---|---|---|
| Nhận diện biển số tại cổng | Biển số, mốc thời gian ra vào, ảnh xe | Chỉ thu thập trong phạm vi cần cho việc quản lý lượt gửi và tính phí. Thời hạn lưu trữ xác định và tự động xoá. Chủ bãi chỉ thấy dữ liệu của bãi mình |
| Đếm chỗ trống | Không cần dữ liệu cá nhân | Chỉ lưu số đếm và trạng thái ô, không lưu hình ảnh trừ khi cần kiểm chứng, và khi lưu thì làm mờ mặt người và biển số |
| Phát hiện khói lửa | Hình ảnh khung hình tại thời điểm cảnh báo | Lưu để làm bằng chứng, có thời hạn, có nhật ký truy cập, làm mờ mặt người |
| Xem hình ảnh khu vực đỗ | Hình ảnh có thể chứa người và xe khác | Chỉ khu vực xe của người dùng, chỉ trong thời gian lượt gửi, ảnh theo chu kỳ thay vì video liên tục, làm mờ đối tượng khác, ghi nhật ký truy cập |
| Hồ sơ thói quen và điểm thân thuộc | Địa điểm thường đến, khung giờ | Chỉ dùng cho gợi ý của chính người dùng đó. Không chia sẻ cho chủ bãi. Người dùng xem được, sửa được, xoá được, tắt được |
| Ưu đãi cá nhân | Hồ sơ hành vi | Không dùng để định giá cao hơn cho người ít nhạy giá. Không suy đoán các thuộc tính nhạy cảm |
| Chia sẻ dữ liệu cho cơ quan quản lý | Dữ liệu tổng hợp | Phi định danh làm mặc định, dữ liệu định danh chỉ theo yêu cầu hợp pháp và có nhật ký |
| Chỗ đỗ của hộ dân | Danh tính hai bên, ảnh xe | Xác thực để bảo đảm an toàn, nhưng chỉ hiển thị cho nhau thông tin tối thiểu cần cho lượt gửi |

Ba yêu cầu hệ thống mang tính bắt buộc, không phải tuỳ chọn: mọi truy cập vào hình ảnh và biển số phải được ghi nhật ký và có thể kiểm toán; mọi loại dữ liệu phải có thời hạn lưu trữ được công bố và cơ chế xoá tự động; và phải có một trang trong ứng dụng cho phép người dùng xem hệ thống đang lưu gì về mình, sửa hoặc yêu cầu xoá.

---

## 11. Thứ tự ưu tiên

Bảng dưới đây không phải phạm vi bản đầu tiên, mà là thứ tự phụ thuộc. Đọc từ trên xuống: mỗi nhóm chỉ có ý nghĩa khi nhóm phía trên đã hoạt động.

| Mức | Nhóm tính năng | Vì sao ở mức này |
|---|---|---|
| P0, nền móng | Đếm chỗ trống bằng camera, nhận diện biển số tại cổng, phát hiện khói lửa, bảng điều khiển chủ bãi, ứng dụng bảo vệ | Đây là lớp cảm nhận. Không có lớp này thì không có dữ liệu, và mọi thứ phía trên trở thành phỏng đoán |
| P0, nền móng | Tìm bãi theo điểm đến, dự đoán chỗ trống khi tới, giữ chỗ theo khoảng thời gian, bộ lọc thuộc tính, thanh toán | Đây là câu chuyện lõi phía người dùng. Bốn tính năng này là lý do người dùng mở ứng dụng lần thứ hai |
| P1, mở rộng giá trị | Đặt trước nhiều ngày và gói tháng, bán giờ thấp điểm, điểm tin cậy bãi, xem hình ảnh khu đỗ, bằng chứng tranh chấp, đồ thị thói quen, bản đồ nhiệt nội bộ | Nhóm này biến sản phẩm dùng được thành sản phẩm kiếm được tiền định kỳ, và cần dữ liệu vận hành vài tuần mới đủ chất lượng |
| P2, nhân giá trị | Dự đoán ý định và gợi ý chủ động, xếp hạng cá nhân hoá, ưu đãi có điều kiện, trợ lý hội thoại, hợp đồng đội xe, chia sẻ dữ liệu cho cơ quan quản lý, gửi xe đổi phương tiện | Nhóm này cần lượng dữ liệu và mật độ mạng lưới đủ lớn. Làm quá sớm sẽ cho kết quả kém và làm mất niềm tin vào chính tính năng đó |

Nguyên tắc xếp thứ tự: không xây tầng trên trước khi tầng dưới chịu được lực. Cụ thể, không mở tính năng giữ chỗ ở một bãi chưa có camera đếm chỗ trống, và không làm cá nhân hoá trước khi có ít nhất vài tuần dữ liệu hành vi thật.

Bước tiếp theo là chốt phạm vi bản đầu tiên và mốc thời gian, nội dung này ở [tài liệu 06](../02_business-operations/06_Scope_and_Roadmap.md). Phần tiền và định giá ở [tài liệu 04](../02_business-operations/04_Business_Model.md).
