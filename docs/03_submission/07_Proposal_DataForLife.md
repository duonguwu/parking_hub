# 07. Bản đề xuất Data for Life mùa 4 năm 2026

Parking HUB, mạng lưới bãi đỗ xe thông minh và hạ tầng dữ liệu giao thông tĩnh cho đô thị Việt Nam

Phiên bản: 1.0, bản thảo
Ngày: 21/08/2026
Cuộc thi: Data for Life mùa 4 năm 2026, chủ đề Build Together, Bộ Công an tổ chức
Hạn nộp hồ sơ: 15/09/2026

> Đây là bản thảo nội dung. Trước khi nộp, cần đối chiếu với mẫu hồ sơ chính thức của ban tổ chức trên dataforlife.vn và sắp xếp lại theo đúng thứ tự và giới hạn độ dài mà mẫu yêu cầu. Các mục dưới đây được viết theo bốn nhóm tiêu chí đánh giá đã biết từ mùa trước, gồm điểm kỹ thuật tối đa 40, điểm trình bày tối đa 30, điểm khả năng ứng dụng tối đa 20 và điểm bình chọn trực tuyến tối đa 10.

---

## 1. Thông tin cơ bản

| Hạng mục | Nội dung |
|---|---|
| Tên giải pháp | Parking HUB, tên đang ở trạng thái tạm thời, xem mục 11 của [tài liệu 01](../01_strategy-product/01_Project_Overview.md) |
| Lĩnh vực dự thi | Đô thị thông minh và giao thông, có liên quan tới Chính phủ số và dịch vụ công |
| Bài toán tham chiếu | Bài toán về ứng dụng bản đồ bãi đỗ xe theo thời gian thực trong Ngân hàng ý tưởng của cuộc thi |
| Đối tượng phục vụ | Người sử dụng ô tô, chủ và đơn vị quản lý bãi đỗ xe, ban quản trị nhà chung cư, doanh nghiệp có đội xe, cơ quan quản lý giao thông đô thị |
| Địa bàn triển khai đề xuất | Một khu vực đô thị tại Thành phố Hồ Chí Minh cho giai đoạn thử nghiệm, sau đó nhân rộng |
| Tình trạng sản phẩm | Đã có hai hệ thống nền chạy được, đang hợp nhất thành sản phẩm mới. Chi tiết ở mục 7 |

---

## 2. Tóm tắt giải pháp

Tại trung tâm các đô thị lớn, tìm chỗ đỗ ô tô mất từ mười tới ba mươi phút và không bao giờ chắc chắn. Nghịch lý là chỗ đỗ không thiếu tuyệt đối, nó thiếu tính minh bạch: trong cùng bán kính năm trăm mét quanh một toà nhà kín chỗ, hầm chung cư bên cạnh thường trống đáng kể vào ban ngày, sân của hộ dân để không cả buổi, bãi của nhà hàng chỉ đông vào buổi tối. Không ai biết những chỗ đó đang trống, kể cả chính chủ của chúng.

Việt Nam đã có nhiều ứng dụng tìm bãi đỗ, nhưng tất cả đều gặp cùng một điểm chết: dữ liệu chỗ trống phụ thuộc vào việc con người nhập tay, nên nó luôn trễ vào đúng lúc cần chính xác nhất. Người dùng đến nơi thì hết chỗ, mất niềm tin, và không mở lại lần thứ ba.

Parking HUB giải quyết đúng điểm chết đó. Hệ thống không hỏi chủ bãi còn bao nhiêu chỗ, nó tự nhìn thấy bằng camera mà đa số bãi đã có sẵn, thông qua bốn model thị giác máy tính: đếm chỗ đỗ trống, phát hiện vùng biển số, đọc ký tự biển số, và phát hiện khói cùng lửa ở giai đoạn sớm. Trên nền dữ liệu đó, hệ thống dự đoán tình trạng chỗ trống tại thời điểm người lái xe đến nơi thay vì tại thời điểm họ tìm kiếm, cho phép giữ chỗ có cam kết, vào ra tự động bằng nhận diện biển số, và thanh toán không tiền mặt.

Điểm khác biệt về mô hình: hệ thống mang tới cho chủ bãi hai giá trị đo được ngay trong tháng đầu, đó là chống thất thu nhờ ghi nhận tự động và phát hiện cháy sớm phục vụ nghĩa vụ tuân thủ quy định an toàn với khu để xe điện tại nhà chung cư có hiệu lực từ 15/12/2025. Đổi lại, chủ bãi mở dữ liệu chỗ trống cho mạng lưới. Nhờ đó dự án thoát được vòng luẩn quẩn của mọi nền tảng hai phía, và tạo ra lớp dữ liệu giao thông tĩnh mà hiện nay cả người dân lẫn cơ quan quản lý đều chưa có.

---

## 3. Vấn đề và tính cấp thiết

### 3.1. Thực trạng

Cả nước hiện có khoảng 6,8 triệu ô tô đang lưu hành và số lượng tiếp tục tăng nhanh, trong khi diện tích đất dành cho giao thông tại các đô thị lớn chỉ chiếm khoảng 6 tới 8 phần trăm, thấp hơn nhiều mức 15 tới 20 phần trăm của đô thị hiện đại. Riêng tại Thành phố Hồ Chí Minh, hệ thống bến bãi giữ xe mới đạt khoảng 20 phần trăm quy hoạch.

Khoảng cách giữa nhu cầu và hạ tầng đang mở rộng theo thời gian, và không thể thu hẹp bằng xây dựng trong ngắn hạn vì một bãi đỗ ngầm cần đất, vốn, giấy phép và nhiều năm thi công.

### 3.2. Thiệt hại

Một lượt tìm chỗ đỗ thất bại vào giờ cao điểm tiêu tốn khoảng mười lăm phút, ba tới năm ki lô mét chạy vòng, và nhiên liệu tương ứng. Nhưng thiệt hại không dừng ở người lái: một xe đang tìm chỗ là một xe di chuyển chậm, phanh và rẽ nhiều, tạo nhiễu cho toàn bộ dòng xe phía sau. Các nghiên cứu quốc tế về kinh tế đỗ xe cho thấy tại một số khu trung tâm, xe đang tìm chỗ đỗ chiếm một tỷ lệ đáng kể lưu lượng đường, và kết cục xấu nhất của chuỗi này là đỗ xe sai quy định, vốn là phương án cuối cùng khi mọi phương án khác đã thất bại.

### 3.3. Bằng chứng về thất thu và về nguyên nhân gốc

Trường hợp thu phí đỗ xe lòng đường tại Thành phố Hồ Chí Minh là minh chứng rõ nhất cho việc nguyên nhân nằm ở khâu ghi nhận, không nằm ở thiếu quy định hay thiếu ứng dụng:

| Chỉ số | Số liệu |
|---|---|
| Tổng thu từ đỗ xe lòng đường giai đoạn 2021 tới 2024 | Hơn 23,1 tỷ đồng |
| Chi phí vận hành cùng giai đoạn | Hơn 25,1 tỷ đồng, ngân sách bù lỗ khoảng 2 tỷ đồng |
| Số lượt xe không đóng phí | Gần 363.000 lượt, thất thu hơn 7,25 tỷ đồng |
| Chi phí phần mềm thu phí đang dùng | Gần 8 tỷ đồng, kèm nhiều lỗi về thanh toán, định vị và tìm bãi |
| Sau khi thí điểm thu qua thẻ thu phí không dừng từ tháng 01/2025 | Doanh thu ba tháng đầu năm 2025 hơn 1,3 tỷ đồng, gần gấp đôi cùng kỳ năm trước |

Kết luận rút ra và cũng là luận điểm trung tâm của giải pháp: cái gì không được máy ghi nhận thì cái đó sẽ rơi. Khi khâu ghi nhận được gắn vào phương tiện thay vì phụ thuộc lời khai của người lái, tiền quay lại ngay.

### 3.4. Vấn đề an toàn cháy nổ trong bãi đỗ

Bãi đỗ kín, đặc biệt là hầm nhà chung cư có xe điện sạc, là khu vực rủi ro cháy cao. Hệ thống báo cháy truyền thống dựa vào đầu báo nhiệt hoặc đầu báo khói trên trần, chỉ kích hoạt khi nhiệt hoặc khói đã đủ lớn để lan tới trần, và khi đó thiệt hại đã xảy ra. Từ ngày 15/12/2025, quy định mới yêu cầu khu để xe điện tại nhà chung cư phải bố trí riêng, có camera giám sát 24 trên 24, hệ thống báo cháy tự động và thiết bị cảnh báo CO cùng HF. Nghĩa là nhu cầu đã trở thành nghĩa vụ có thời hạn, nhưng lời giải kỹ thuật cho việc phát hiện ở giai đoạn khói mỏng vẫn còn khoảng trống.

---

## 4. Giải pháp và cách hoạt động

### 4.1. Kiến trúc bốn lớp

```
Lớp 4  DỮ LIỆU CÔNG      Bản đồ nhiệt giao thông tĩnh theo giờ, báo cáo nhu cầu
                         chưa được phục vụ, cảnh báo an toàn liên thông
Lớp 3  MẠNG LƯỚI         Giữ chỗ có cam kết, thanh toán, gói tháng, đội xe,
                         điểm tin cậy của bãi
Lớp 2  ĐIỀU PHỐI         Gợi ý theo điểm đến, dự đoán chỗ trống tại thời điểm
                         tới nơi, dự báo tương lai, cá nhân hoá
Lớp 1  CẢM NHẬN          Bốn model thị giác máy tính chạy trên thiết bị biên
                         tại từng bãi
```

### 4.2. Một hành trình cụ thể

Người lái xe nhập điểm đến, không phải vị trí hiện tại, vì điều họ cần là chỗ đỗ gần nơi sẽ tới. Hệ thống lấy các bãi trong bán kính đi bộ quanh điểm đến, tính thời gian lái xe tới từng bãi theo giao thông thực và quãng đi bộ từ bãi tới đích theo đường đi bộ thực tế. Với mỗi bãi, hệ thống không trả lời câu hỏi hiện tại còn mấy chỗ, mà trả lời câu hỏi khi người này tới thì còn mấy chỗ, bằng cách lấy số chỗ trống camera đang đếm được, cộng số xe dự kiến rời bãi và trừ số xe dự kiến vào bãi trong khoảng thời gian di chuyển, rồi trừ tiếp phần dung lượng đã bị các lượt giữ chỗ khác chiếm.

Kết quả là ba lựa chọn có thể so sánh trực tiếp: thời gian lái xe, quãng đi bộ, giá dự kiến, và khả năng còn chỗ khi tới. Người dùng giữ chỗ, tới cổng không cần dừng vì camera đọc biển số và đối chiếu với lượt giữ chỗ, và khi ra thì hệ thống chốt thời gian gửi rồi trừ tiền tự động.

### 4.3. Vì sao chủ bãi tham gia

Đây là mấu chốt khiến giải pháp khả thi trên thực tế. Chủ bãi trong trung tâm không thiếu khách vào giờ cao điểm, nên lời hứa về khách hàng mới không đủ để họ thay đổi vận hành. Parking HUB đi vào bằng ba giá trị mà họ đang mất tiền hoặc mất ngủ vì nó:

| Giá trị | Cơ chế | Thời điểm chủ bãi thấy kết quả |
|---|---|---|
| Chống thất thu | Mọi lượt xe được ghi nhận tự động bằng biển số, có bảng đối soát cuối ngày | Tháng đầu tiên |
| An toàn cháy nổ | Phát hiện khói và lửa ở giai đoạn sớm, cảnh báo nhiều cấp, lưu bằng chứng | Ngay khi lắp đặt, và là hạng mục phục vụ nghĩa vụ tuân thủ |
| Doanh thu từ giờ đang trống | Dữ liệu lấp đầy theo giờ, công cụ bán gói cho khung giờ thấp điểm | Từ tháng thứ hai tới thứ ba |

---

## 5. Tính sáng tạo và điểm khác biệt

| Khía cạnh | Cách làm phổ biến hiện nay | Parking HUB |
|---|---|---|
| Nguồn dữ liệu chỗ trống | Chủ bãi nhập tay hoặc người dùng báo, nên luôn trễ | Camera AI đếm liên tục, hai nguồn kia chỉ dùng để đối chiếu |
| Câu hỏi mà hệ thống trả lời | Hiện tại còn mấy chỗ | Khi bạn tới thì còn mấy chỗ, và ngày mai giờ này thì còn mấy chỗ |
| Mức cam kết | Chỉ hiển thị thông tin | Giữ chỗ có ràng buộc hai chiều, có chính sách khi mỗi bên không thực hiện |
| Chi phí cảm nhận | Cảm biến gắn từng ô, khoảng 300 tới 500 đô la Mỹ mỗi ô | Một camera phân tích được hàng chục tới hàng trăm ô, tận dụng camera có sẵn |
| Lý do phía cung tham gia | Hứa mang thêm khách | Chống thất thu và an toàn cháy nổ, hai giá trị đo được ngay |
| Phạm vi giá trị | Dừng ở giao dịch đỗ xe | Tạo ra lớp dữ liệu giao thông tĩnh dùng được cho điều hành và quy hoạch đô thị |
| An toàn | Không nằm trong phạm vi | Phát hiện khói ở giai đoạn còn dập được, phù hợp yêu cầu pháp lý mới với khu để xe điện |

Sáng tạo cốt lõi của giải pháp không phải một thuật toán đơn lẻ, mà là việc ghép hai bài toán vốn được giải riêng: bài toán an toàn và vận hành của chủ bãi, và bài toán tìm chỗ đỗ của người lái xe. Cùng một hệ thống camera, cùng một thiết bị biên, cùng một lần lắp đặt, phục vụ cả hai. Chính việc ghép này làm cho dữ liệu chỗ trống theo thời gian thực trở nên khả thi về kinh tế, và đó là điều mà mọi lời giải trước đây tại Việt Nam đều chưa đạt được.

---

## 6. Công nghệ và dữ liệu

### 6.1. Bốn model thị giác máy tính

| Model | Nhiệm vụ | Cách tiếp cận | Tình trạng |
|---|---|---|---|
| Đếm chỗ đỗ trống | Đếm số ô trống theo khu từ khung hình | Phát hiện đối tượng trên nền YOLOv8, hậu xử lý theo vùng ô đỗ đã hiệu chuẩn cho từng bãi | Đã chạy trên bãi đỗ thật, cần huấn luyện thêm cho hầm thiếu sáng và góc bị che |
| Phát hiện vùng biển số | Tìm và cắt vùng biển số | Phát hiện đối tượng, sau đó xoay và chuẩn hoá vùng ảnh | Đã chạy |
| Đọc ký tự biển số | Nhận diện từng ký tự rồi ghép thành biển số hoàn chỉnh | Phát hiện từng ký tự, ghép theo toạ độ trên trục ngang, hỗ trợ biển một dòng và hai dòng của Việt Nam | Đã chạy, cần tăng dữ liệu ban đêm và điều kiện thời tiết xấu |
| Phát hiện khói và lửa | Phát hiện khói mỏng và ngọn lửa mới bùng | Phát hiện đối tượng, kèm lớp xác nhận theo thời gian để giảm báo động sai | Đã chạy song song với luồng đếm chỗ bằng đa luồng, cần hiệu chuẩn theo từng bãi |

### 6.2. Kiến trúc triển khai

Điểm kỹ thuật quan trọng, và cũng là bài học rút ra từ chính giới hạn của phiên bản trước: suy luận phải chạy trên thiết bị biên tại bãi, không đẩy luồng video về máy chủ trung tâm. Thử nghiệm ở phiên bản trước cho thấy việc hiển thị và xử lý video trực tiếp tập trung bị giới hạn bởi tài nguyên máy chủ. Khi số bãi tăng lên hàng chục rồi hàng trăm, kiến trúc tập trung sẽ không khả thi cả về băng thông, chi phí, lẫn độ trễ của cảnh báo cháy.

Ba hệ quả thiết kế:

Một, thiết bị biên chạy toàn bộ suy luận tại bãi và chỉ gửi kết quả lên trung tâm, gồm số chỗ trống, sự kiện xe vào và ra kèm biển số, sự kiện phát hiện khói kèm một khung hình. Cách này giảm mạnh chi phí hạ tầng và giảm rủi ro dữ liệu, vì hình ảnh không rời khỏi bãi trừ khi cần thiết.

Hai, thiết bị biên hoạt động độc lập khi mất mạng, ghi nhận cục bộ và đồng bộ khi có mạng trở lại. Cảnh báo cháy vẫn phát tại chỗ. Mất mạng trong hầm là chuyện thường xuyên và không được phép biến thành sự cố an toàn.

Ba, hệ thống suy giảm mượt. Nếu dịch vụ định tuyến không phản hồi thì dùng khoảng cách có hệ số điều chỉnh. Nếu một bãi mất kết nối thì hạ mức tin cậy của bãi đó và ưu tiên bãi có dữ liệu tốt, chứ không im lặng trả về số liệu cũ như thể nó còn đúng.

### 6.3. Hai model dữ liệu

| Model | Nhiệm vụ | Giai đoạn khởi động | Khi đã có dữ liệu |
|---|---|---|---|
| Dự báo chỗ trống theo thời gian | Trả lời còn bao nhiêu chỗ tại một mốc tương lai, từ vài phút tới vài ngày | Quy tắc và trung bình lịch sử theo ngày trong tuần và khung giờ, hiệu chỉnh theo mưa và ngày lễ | Mô hình chuỗi thời gian cho từng bãi với yếu tố ngoại sinh |
| Xếp hạng và cá nhân hoá | Sắp thứ tự bãi phù hợp cho một người dùng trong một ngữ cảnh | Bộ trọng số mặc định theo loại chuyến đi | Học trọng số riêng từ lịch sử lựa chọn và bỏ qua của từng người |

### 6.4. Các lớp dữ liệu tạo ra

Đây là phần trả lời trực tiếp cho tinh thần của cuộc thi, vì giá trị dài hạn của giải pháp nằm ở dữ liệu mà nó sinh ra:

| Lớp dữ liệu | Nội dung | Không thể có được nếu không tự vận hành |
|---|---|---|
| Trạng thái giao thông tĩnh theo thời gian thực | Chỗ trống theo bãi, theo khu, theo phút | Đúng, vì cần camera tại bãi |
| Nhịp vận hành của từng bãi | Nhịp xe vào và ra theo ngày trong tuần, theo giờ, theo thời tiết | Đúng, cần nhiều tuần vận hành liên tục |
| Nhu cầu chưa được phục vụ | Những khu vực và khung giờ mà người dùng tìm nhưng không có bãi phù hợp | Đúng, chỉ thấy được khi có người dùng thật |
| Thời gian di chuyển thực tế theo tuyến | Từ thời điểm giữ chỗ tới thời điểm camera đọc biển số ở cổng | Đúng, và dữ liệu này còn dùng để hiệu chỉnh ước lượng của dịch vụ định tuyến |
| Sự kiện an toàn | Thống kê phát hiện khói và lửa theo loại bãi, theo thời điểm | Đúng, và đây là dữ liệu có giá trị cho công tác phòng cháy |

---

## 7. Mức độ hoàn thiện hiện tại

Phần này có trọng lượng đặc biệt vì ban tổ chức tuyên bố rõ rằng cuộc thi tìm giải pháp triển khai được trong thực tế, không chỉ tìm ý tưởng.

Parking HUB không phải một bản mô tả ý tưởng. Hai khối năng lực cốt lõi của hệ thống đã được đội xây dựng, chạy thực tế và trình diễn được.

| Khối năng lực | Nội dung đã có và đã chạy | Vai trò trong giải pháp |
|---|---|---|
| Lớp cảm nhận bằng thị giác máy tính | Bốn model trên nền YOLOv8: phát hiện vùng biển số, đọc ký tự biển số theo cơ chế ghép ký tự hỗ trợ biển một dòng và hai dòng của Việt Nam, đếm chỗ đỗ trống theo khung hình, phát hiện khói và lửa. Bốn model chạy song song bằng đa luồng, có cơ chế ưu tiên xử lý cảnh báo cháy. Luồng ghi nhận giờ xe vào và giờ xe ra để tính phí theo thời gian gửi và trừ tiền tự động đã hoạt động, kèm giao diện quản trị trên web và ứng dụng di động | Toàn bộ lớp cảm nhận, là nguồn dữ liệu chỗ trống theo thời gian thực |
| Nền tảng điều phối mạng lưới | Backend FastAPI, cơ sở dữ liệu MongoDB, bộ đệm Redis, dịch vụ định tuyến và tính thời gian di chuyển trên dữ liệu bản đồ mở kèm cơ chế dự phòng, dịch vụ thời tiết, engine ghép nối tính điểm theo nhiều biến với nguyên lý dự đoán trạng thái điểm phục vụ tại thời điểm khách đến nơi, hệ thống phân cấp và chấm điểm từ dữ liệu vận hành, luồng đặt lịch có máy trạng thái và khoá phân tán để không trùng chỗ, kiến trúc đa chủ thể với phân quyền theo vai trò, ba cổng giao diện cho khách hàng, cho chủ điểm dịch vụ và cho quản trị viên | Lớp điều phối và lớp mạng lưới |

Việc còn lại không phải phát minh mà là hợp nhất hai khối này và chỉnh cho đúng bài toán đỗ xe. Ba hạng mục phải làm mới, và được nêu trung thực: chuyển suy luận ra thiết bị biên tại bãi, xây model dự báo chỗ trống theo thời gian, và xây nghiệp vụ giữ chỗ có cam kết hai chiều.

---

## 8. Tính khả thi triển khai

### 8.1. Vì sao khả thi về kinh tế

Toàn bộ tính khả thi nằm ở một so sánh: cảm biến gắn từng ô đỗ có chi phí lắp đặt khoảng 300 tới 500 đô la Mỹ mỗi ô, còn một camera phân tích được hàng chục tới hàng trăm ô. Với một bãi 150 chỗ, đó là khoảng cách giữa một dự án đầu tư hạ tầng và một khoản chi phần mềm. Thêm vào đó, phần lớn bãi có hệ thống đã lắp camera an ninh từ trước, nên phần cần bổ sung chủ yếu là camera cổng và một thiết bị biên.

### 8.2. Vì sao khả thi về vận hành

Bốn cấp tích hợp cho phép mạng lưới phủ rộng nhanh mà vẫn giữ chất lượng cam kết. Bãi ở cấp 1 và cấp 2 chỉ cần thông tin đã kiểm định, onboard trong nửa ngày tới một ngày, tạo mật độ bản đồ. Bãi ở cấp 3 và cấp 4 có thiết bị, cho phép cam kết giữ chỗ. Người dùng luôn thấy rõ bãi đang ở mức nào nên không bị hiểu sai, và chủ bãi có con đường nâng cấp với lợi ích cụ thể ở mỗi bậc.

Nguyên tắc vận hành xuyên suốt: hệ thống không bao giờ được làm bãi ngừng hoạt động. Barrier luôn mở được bằng tay, thiết bị chạy được khi mất mạng, và mỗi bãi có một tới hai tuần chạy song song với quy trình cũ trước khi bật bất cứ tính năng nào ảnh hưởng tới vận hành.

### 8.3. Kế hoạch triển khai theo bốn vòng của cuộc thi

| Vòng | Mục tiêu sản phẩm | Mục tiêu thực địa |
|---|---|---|
| Tuyển chọn hồ sơ | Bản demo chạy từ đầu tới cuối, số liệu kiểm thử bốn model | Từ một tới ba bãi đồng ý cho thử nghiệm |
| Chinh phục và phát triển giải pháp | Lắp đặt thật tại bãi đầu tiên, hoàn thiện giữ chỗ và thanh toán | Từ ba tới năm bãi kết nối, có người dùng thật |
| Triển lãm | Sản phẩm trình diễn được với số liệu vận hành thật | Từ năm tới mười bãi trong cùng khu vực |
| Chung kết | Tài liệu kỹ thuật, phương án nhân rộng, phương án chia sẻ dữ liệu | Đủ dữ liệu để chứng minh tác động |

---

## 9. Tác động

### 9.1. Với người dân

| Tác động | Cách đo |
|---|---|
| Giảm thời gian tìm chỗ đỗ | So sánh thời gian từ lúc mở ứng dụng tới lúc xe vào bãi với hành vi trước đó |
| Giảm nhiên liệu và quãng đường chạy vòng | Quy đổi từ số ki lô mét tiết kiệm được mỗi lượt |
| Giảm rủi ro bị xử phạt do đỗ sai quy định | Số lượt được điều hướng về bãi hợp pháp trong khu vực có mật độ đỗ sai cao |
| An tâm về xe và về an toàn | Số vụ phát hiện khói ở giai đoạn sớm, số tranh chấp được giải quyết bằng bằng chứng hình ảnh |

### 9.2. Với giao thông đô thị và môi trường

Mỗi lượt tìm chỗ thất bại là ba tới năm ki lô mét chạy vòng ở tốc độ thấp trong khu vực đông đúc. Khi số lượt đỗ xe qua nền tảng tăng lên, phần quãng đường này được cắt bỏ, và tác động thể hiện ở ba mặt: giảm phát thải, giảm nhiễu cho dòng xe, và giảm hiện tượng đỗ xe sai quy định gây cản trở giao thông. Đây là loại tác động có thể định lượng được bằng dữ liệu của chính hệ thống, chứ không phải bằng ước đoán, và đó là một điểm mạnh khi trình bày.

### 9.3. Với công tác quản lý nhà nước

| Sản phẩm dữ liệu | Giá trị cho quản lý |
|---|---|
| Bản đồ nhiệt giao thông tĩnh theo giờ | Xác định điểm nghẽn, ưu tiên vị trí quy hoạch bãi mới, đánh giá hiệu quả sau khi mở bãi |
| Báo cáo nhu cầu chưa được phục vụ | Bằng chứng định lượng về nơi thiếu hạ tầng, thay cho khảo sát định kỳ |
| Cảnh báo an toàn liên thông | Rút ngắn thời gian phản ứng, và tạo dữ liệu thống kê về rủi ro cháy trong bãi đỗ |
| Hỗ trợ minh bạch thu phí đỗ xe công cộng | Ghi nhận tự động gắn với phương tiện, giảm thất thu như bằng chứng từ việc thí điểm thu qua thẻ thu phí không dừng đã cho thấy |

### 9.4. Với an toàn cháy nổ

Đây là tác động khó quy ra tiền nhưng lớn nhất về mặt xã hội. Mỗi vụ cháy được phát hiện ở giai đoạn khói mỏng, thay vì khi lửa đã lớn, là một chuỗi hậu quả không xảy ra: xe không cháy, không lan sang các xe bên cạnh, không có nguy cơ nổ trong không gian kín, và không có thiệt hại về người. Với một hầm chung cư có hàng trăm xe và hàng trăm hộ dân ở phía trên, khoảng thời gian vài phút đầu là toàn bộ khác biệt.

---

## 10. Phù hợp với định hướng chuyển đổi số quốc gia

| Định hướng và căn cứ | Parking HUB đóng góp gì |
|---|---|
| Đề án 06 về phát triển ứng dụng dữ liệu về dân cư, định danh và xác thực điện tử | Giải pháp tạo ra một lớp dữ liệu mới về giao thông tĩnh, có thể kết nối với hệ sinh thái định danh để xác thực người dùng, phục vụ an toàn giao dịch giữa người gửi xe và chủ bãi. Khả năng và thủ tục tích hợp cụ thể cần được xác minh với cơ quan có thẩm quyền |
| Quyết định 502/QĐ-TTg ngày 28/03/2026 về phương án kết nối, chia sẻ dữ liệu giữa hệ thống camera giám sát an ninh trật tự, xử lý vi phạm và điều hành giao thông với Cơ sở dữ liệu quốc gia về dân cư, và chia sẻ với trung tâm giám sát điều hành đô thị thông minh | Mạng lưới camera tại bãi đỗ đã được chuẩn hoá về dữ liệu là một mắt lưới tự nhiên trong phương án này. Dữ liệu về giao thông tĩnh và sự kiện an toàn có thể chia sẻ theo đúng quy định |
| Quy định về khu để xe điện tại nhà chung cư, hiệu lực từ 15/12/2025 | Mô đun phát hiện khói và lửa sớm phục vụ trực tiếp yêu cầu về camera giám sát và phát hiện sớm, bổ sung cho hệ thống báo cháy tự động |
| Nghị định 119/2024/NĐ-CP về thanh toán điện tử giao thông đường bộ | Mô hình vào ra tự động và thanh toán gắn với phương tiện nằm đúng trong hành lang này |
| Luật Dữ liệu số 60/2024/QH15, hiệu lực từ 01/07/2025 | Dữ liệu do hệ thống tạo ra được tổ chức theo hướng có thể chia sẻ và tái sử dụng cho mục đích quản lý nhà nước |
| Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15, hiệu lực từ 01/01/2026 | Toàn bộ thiết kế xử lý biển số và hình ảnh tuân thủ nguyên tắc tối thiểu hoá, có thời hạn lưu trữ, có nhật ký truy cập và có quyền của chủ thể dữ liệu. Chi tiết ở mục 11 |

---

## 11. Bảo vệ dữ liệu và an ninh dữ liệu

Giải pháp xử lý hai loại dữ liệu có độ nhạy cao, đó là biển số xe và hình ảnh camera. Bảy nguyên tắc được thiết kế ngay từ đầu, không phải bổ sung về sau:

**Một, tối thiểu hoá.** Chỉ thu thập dữ liệu cần cho việc quản lý lượt gửi, tính phí và bảo đảm an toàn. Không thu thập dữ liệu sinh trắc học, không nhận diện khuôn mặt.

**Hai, xử lý tại chỗ.** Suy luận chạy trên thiết bị biên tại bãi. Chỉ dữ liệu kết quả được gửi lên trung tâm, hình ảnh chỉ gửi khi cần cho cảnh báo hoặc bằng chứng.

**Ba, thời hạn lưu trữ và xoá tự động.** Mỗi loại dữ liệu có thời hạn công bố trước và cơ chế xoá tự động khi hết hạn.

**Bốn, nhật ký truy cập đầy đủ.** Mọi lượt truy cập vào hình ảnh và biển số đều được ghi nhận và có thể kiểm toán.

**Năm, phi định danh làm mặc định khi chia sẻ.** Báo cáo cho cơ quan quản lý và cho bên thứ ba luôn ở dạng tổng hợp phi định danh. Dữ liệu có thể định danh chỉ được cung cấp theo yêu cầu hợp pháp của cơ quan có thẩm quyền, có văn bản, có thời hạn và có nhật ký.

**Sáu, phân quyền chặt theo vai trò.** Chủ bãi chỉ thấy dữ liệu của bãi mình và chỉ ở mức cần cho vận hành. Chủ bãi không được thấy hồ sơ thói quen di chuyển của người dùng.

**Bảy, quyền của người dùng.** Trong ứng dụng có một trang cho phép người dùng xem hệ thống đang lưu gì về mình, sửa, yêu cầu xoá, và tắt cá nhân hoá mà vẫn dùng được sản phẩm.

Ngoài ra, hệ thống không tạo ra bất kỳ nhãn suy đoán nào về thuộc tính nhạy cảm của người dùng từ dữ liệu hành trình, và không dùng dữ liệu hành vi để định giá khác nhau cho cùng một chỗ đỗ tại cùng một thời điểm.

---

## 12. Mô hình bền vững về tài chính

Chi tiết ở [tài liệu 04](../02_business-operations/04_Business_Model.md). Ba điểm cần nêu trong hồ sơ:

Thứ nhất, giải pháp có doanh thu từ tháng đầu tiên và không phụ thuộc vào việc phải có sẵn người dùng, vì phần bán cho chủ bãi gồm phần mềm vận hành và mô đun an toàn có giá trị độc lập.

Thứ hai, nền tảng chỉ thu trên phần giá trị tạo thêm, không lấy phần trăm trên doanh thu vốn có của bãi. Điều này làm cho việc mở rộng mạng lưới khả thi trên thực tế.

Thứ ba, theo mô hình minh hoạ với các giả định được nêu rõ, khoảng năm mươi bãi có thiết bị cộng khoảng một trăm chỗ đỗ nhỏ trong một tới hai khu vực đô thị là mốc mà mô hình bắt đầu tự trang trải chi phí cố định. Đây là mốc ở tầm khả thi, không phải mốc cần hàng nghìn điểm.

---

## 13. Khả năng nhân rộng

| Cấp độ | Cách nhân rộng | Điều kiện |
|---|---|---|
| Từ một bãi sang một khu vực | Playbook onboard chuẩn hoá, dùng bằng chứng từ bãi đầu tiên để thuyết phục bãi lân cận | Đạt các tiêu chí ở mục 7 của [tài liệu 06](../02_business-operations/06_Scope_and_Roadmap.md) |
| Từ một khu vực sang một thành phố | Lặp lại theo từng khu vực, ưu tiên khu vực có mật độ điểm đến cao | Chi phí onboard đã giảm và có kênh tự đăng ký |
| Từ một thành phố sang các đô thị khác | Đi qua đầu mối quản lý nhiều bãi, và qua kênh hợp tác với địa phương | Có bằng chứng về tác động và có quy trình tuân thủ hoàn chỉnh |
| Sang các bài toán liền kề | Cùng hạ tầng camera và thiết bị biên đã lắp, phục vụ kiểm soát ra vào, an ninh khuôn viên, dịch vụ cho xe đang gửi | Sau khi lớp cảm nhận đã ổn định |

Điểm quan trọng về tính nhân rộng: đơn vị nhân rộng của giải pháp này là khu vực, không phải bãi, vì giá trị với người lái xe phụ thuộc vào mật độ bãi trong bán kính đi bộ quanh nơi họ cần đến. Chiến lược đúng là chiếm mật độ từng khu vực rồi lặp lại, không phải trải mỏng nhiều nơi.

---

## 14. Đội ngũ

Đội gồm những người đã trực tiếp xây dựng cả hai khối năng lực cốt lõi của giải pháp: bốn model thị giác máy tính cùng hệ thống quản lý bãi đỗ, và nền tảng điều phối mạng lưới điểm dịch vụ. Danh sách thành viên, vai trò và thông tin liên hệ được điền theo mẫu hồ sơ của ban tổ chức, trong giới hạn tối đa mười thành viên mỗi đội.

Các vai trò cần có được nêu tại mục 8 của [tài liệu 06](../02_business-operations/06_Scope_and_Roadmap.md).

---

## 15. Kết luận

Bài toán chỗ đỗ xe ở trung tâm đô thị Việt Nam không phải bài toán thiếu ứng dụng. Đã có nhiều ứng dụng, và tất cả đều gặp cùng một điểm chết là dữ liệu chỗ trống không đáng tin, vì nó phụ thuộc vào việc con người nhập tay trong lúc đang làm việc khác.

Parking HUB giải quyết đúng điểm chết đó, bằng bốn model thị giác máy tính đã được chứng minh chạy được, đặt trên hạ tầng camera mà đa số bãi đã có, và bằng một mô hình kinh doanh mà chủ bãi tham gia vì hai lý do đo được ngay: chống thất thu và an toàn cháy nổ. Đổi lại, mạng lưới có được thứ mà chưa ai ở Việt Nam có, là dữ liệu giao thông tĩnh theo thời gian thực. Từ dữ liệu đó, người lái xe có được sự chắc chắn, chủ bãi bán được những giờ đang trống, và cơ quan quản lý có được bức tranh thực để điều hành và quy hoạch.

Đúng với chủ đề Build Together của cuộc thi, giải pháp này chỉ hoạt động khi ba bên cùng tham gia: người dân đóng góp nhu cầu và hành vi, doanh nghiệp và hộ dân đóng góp dung lượng cùng dữ liệu, và cơ quan quản lý đóng góp tính chính danh cùng khả năng biến dữ liệu thành quyết định công. Không bên nào tự làm được một mình, và đó chính là lý do bài toán này xứng đáng được giải bằng cách cùng nhau xây.
