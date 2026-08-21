# 01. Parking HUB, tổng quan dự án

Mạng lưới bãi đỗ xe ô tô thông minh cho đô thị Việt Nam

Phiên bản: 1.0
Ngày: 21/08/2026
Bối cảnh: Cuộc thi quốc tế Data for Life mùa 4 năm 2026, chủ đề Build Together, Bộ Công an tổ chức

---

## Mục lục

1. [Tóm tắt điều hành](#1-tóm-tắt-điều-hành)
2. [Bối cảnh cuộc thi và đề bài](#2-bối-cảnh-cuộc-thi-và-đề-bài)
3. [Tại sao là dự án này, tại sao là bây giờ](#3-tại-sao-là-dự-án-này-tại-sao-là-bây-giờ)
4. [Trạng thái hiện tại: dự án đang ở đâu](#4-trạng-thái-hiện-tại-dự-án-đang-ở-đâu)
5. [Định vị: Parking HUB là gì và không phải là gì](#5-định-vị-parking-hub-là-gì-và-không-phải-là-gì)
6. [Kiến trúc giá trị bốn lớp](#6-kiến-trúc-giá-trị-bốn-lớp)
7. [Ai nhận được gì](#7-ai-nhận-được-gì)
8. [Câu chuyện xuyên suốt: một buổi sáng thứ Ba](#8-câu-chuyện-xuyên-suốt-một-buổi-sáng-thứ-ba)
9. [Vì sao dự án này khó bị sao chép](#9-vì-sao-dự-án-này-khó-bị-sao-chép)
10. [Chỉ số thành công](#10-chỉ-số-thành-công)
11. [Ghi chú về tên dự án](#11-ghi-chú-về-tên-dự-án)
12. [Đọc tiếp](#12-đọc-tiếp)

---

## 1. Tóm tắt điều hành

### Bài toán

Tại trung tâm các đô thị lớn của Việt Nam, tìm một chỗ đỗ ô tô là việc mất từ mười tới ba mươi phút, và kết quả không bao giờ chắc chắn. Người lái xe không biết bãi nào còn chỗ, không biết giá bao nhiêu, không biết bãi có mở cửa hay không, và quan trọng nhất là không có cách nào giữ trước một chỗ. Hệ quả là ba khoản lãng phí xảy ra cùng lúc: thời gian của người lái, nhiên liệu bị đốt cho những vòng xe vô ích, và một dòng xe chạy chậm lòng vòng làm nghẽn thêm giao thông vốn đã tắc. Khi tìm không được, người lái chọn phương án cuối cùng là đỗ sai quy định.

Điều nghịch lý là chỗ đỗ không thiếu tuyệt đối, nó thiếu tính minh bạch. Trong cùng bán kính năm trăm mét quanh một toà nhà kín chỗ, thường vẫn còn hầm của chung cư bên cạnh trống bốn mươi phần trăm vào ban ngày, còn sân của một hộ dân trống cả buổi sáng, còn bãi ngoài trời của một nhà hàng chỉ đông từ mười tám giờ. Không ai biết những chỗ đó đang trống, kể cả chính chủ của chúng.

### Giải pháp

Parking HUB là mạng lưới kết nối tất cả các loại bãi đỗ xe ô tô, từ hầm toà nhà, bãi ngoài trời thương mại, bãi lòng đường, tới sân nhà của hộ dân, thành một hệ thống duy nhất mà người lái xe mở lên là biết chắc chỗ nào còn trống, giá bao nhiêu, và đặt được chỗ đó trước khi lăn bánh.

Điểm khác biệt nằm ở chỗ Parking HUB không hỏi chủ bãi rằng còn bao nhiêu chỗ. Hệ thống tự nhìn thấy, bằng camera mà đa số bãi đã có sẵn, thông qua bốn model thị giác máy tính mà đội đã xây dựng, huấn luyện và kiểm chứng trên dữ liệu bãi đỗ thật:

| Model | Nhiệm vụ | Giá trị tạo ra ngay |
|---|---|---|
| Đếm chỗ trống | Phân tích khung hình, đếm số ô đỗ còn trống theo từng khu | Dữ liệu chỗ trống theo thời gian thực, không phụ thuộc người nhập tay |
| Phát hiện vùng biển số | Tìm và cắt vùng biển số từ luồng video tại cổng | Nền tảng cho ghi nhận xe vào và xe ra tự động |
| Đọc ký tự biển số | Nhận diện từng ký tự, ghép lại thành biển số hoàn chỉnh, hỗ trợ biển một dòng và hai dòng của Việt Nam | Tính phí chính xác theo thời gian gửi, chống thất thu, chống tráo vé |
| Phát hiện khói và lửa sớm | Phát hiện đám khói nhỏ và ngọn lửa vừa bùng trong khung hình | Cảnh báo sớm hàng chục phút so với đầu báo nhiệt, đúng thời điểm còn dập được |

Trên nền dữ liệu đó, Parking HUB đặt lớp điều phối đã được đội xây dựng và chạy được: dự đoán tình trạng chỗ trống tại thời điểm người lái xe đến nơi thay vì tại thời điểm họ tìm kiếm, dự báo chỗ trống cho ngày mai và ngày mốt để cho phép đặt trước theo thời gian, và cá nhân hoá gợi ý theo thói quen di chuyển của từng người.

### Vì sao mô hình này thu được tiền

Parking HUB bán hai thứ khác nhau cho hai bên, và cả hai bên đều trả tiền vì lý do riêng của họ:

Với chủ bãi, giá trị đến trước và đo được bằng tiền ngay trong tháng đầu. Nhận diện biển số tự động chặn thất thu và chấm dứt tranh chấp vé. Phát hiện khói lửa sớm là điều kiện tuân thủ quy định phòng cháy chữa cháy mới có hiệu lực từ ngày 15/12/2025 với khu để xe điện tại nhà chung cư, trong đó camera giám sát và báo cháy tự động là bắt buộc. Dữ liệu lấp đầy theo giờ cho phép chủ bãi bán những giờ đang trống. Đổi lại, chủ bãi mở dữ liệu chỗ trống cho mạng lưới.

Với người lái xe, giá trị là sự chắc chắn: một chỗ đỗ đã được giữ, một mức giá biết trước, một quãng đi bộ biết trước, và khả năng xem camera để biết xe mình vẫn ổn.

### Vì sao thời điểm này là đúng

Ba cửa sổ mở cùng lúc. Thứ nhất, quy định pháp luật vừa chuyển từ khuyến khích sang bắt buộc: yêu cầu camera và báo cháy tại khu để xe điện trong chung cư từ 15/12/2025, chủ trương kết nối và chia sẻ dữ liệu camera giám sát với Cơ sở dữ liệu quốc gia về dân cư và trung tâm điều hành đô thị thông minh theo Quyết định 502/QĐ-TTg ngày 28/03/2026, và hành lang thanh toán điện tử giao thông đường bộ theo Nghị định 119/2024/NĐ-CP. Thứ hai, kinh tế của công nghệ đã đảo chiều: một camera phân tích được hàng chục tới hàng trăm ô đỗ, trong khi cảm biến gắn từng ô có giá vài trăm đô la Mỹ mỗi ô, nên trước đây bài toán đếm chỗ trống là bài toán đầu tư hạ tầng, còn bây giờ nó là bài toán phần mềm. Thứ ba, các giải pháp đi trước tại Việt Nam đã thất bại đủ rõ để bài học trở nên cụ thể, và thất bại của họ đều tập trung vào một điểm duy nhất: dữ liệu chỗ trống không đáng tin.

### Vì sao đội này làm được

Hai nửa của bài toán đều đã có bản chạy được. Bốn model thị giác đã được huấn luyện, triển khai và trình diễn trên bãi đỗ thật, kèm luồng ghi nhận giờ vào và giờ ra để tính phí theo thời gian gửi. Nền tảng điều phối mạng lưới cũng đã được đội xây dựng, gồm engine ghép nối dự đoán trạng thái điểm dịch vụ tại thời điểm khách đến, hệ thống phân cấp và chấm điểm, luồng đặt lịch, và ba cổng giao diện cho khách, cho chủ điểm dịch vụ và cho quản trị viên. Việc còn lại không phải phát minh, mà là hợp nhất hai khối năng lực này và chỉnh cho đúng bài toán đỗ xe.

---

## 2. Bối cảnh cuộc thi và đề bài

### 2.1. Cuộc thi

Data for Life mùa 4 năm 2026 là cuộc thi quốc tế do Bộ Công an tổ chức, phối hợp cùng Đài Truyền hình Việt Nam và Đại học Bách khoa Hà Nội, với chủ đề Build Together, hướng tới kết nối Nhà nước, Nhà trường và Nhà doanh nghiệp để tìm và phát triển các giải pháp có tính ứng dụng cao, phục vụ Chính phủ số, kinh tế số và xã hội số.

| Hạng mục | Thông tin |
|---|---|
| Cấu trúc | Bốn vòng: Tuyển chọn hồ sơ, Chinh phục và phát triển giải pháp, Triển lãm, Chung kết |
| Vòng hồ sơ | Từ 10/08/2026 tới 15/09/2026, nộp trực tuyến tại dataforlife.vn |
| Quy mô đội | Tối đa 10 thành viên |
| Đối tượng | Học sinh, sinh viên, người lao động, nhóm nghiên cứu, doanh nghiệp khởi nghiệp, tổ chức và cá nhân, bao gồm người nước ngoài |
| Lĩnh vực | Chính phủ số và dịch vụ công, đô thị thông minh, giao thông, y tế, giáo dục, môi trường, an ninh mạng, an ninh dữ liệu, kinh tế số |
| Giải thưởng | Tổng giá trị tới 1 tỷ đồng, gồm một giải Nhất 500 triệu đồng, hai giải Nhì 100 triệu đồng, ba giải Ba 50 triệu đồng, cùng các giải phụ về sáng tạo, tác động xã hội, công nghệ ấn tượng và bình chọn cộng đồng |
| Cơ cấu điểm vòng chung kết ở mùa trước | Điểm kỹ thuật tối đa 40, điểm trình bày tối đa 30, điểm khả năng ứng dụng tối đa 20, điểm bình chọn trực tuyến tối đa 10 |

Hai đặc điểm của cuộc thi này quyết định cách viết hồ sơ. Thứ nhất, cuộc thi nằm trong khuôn khổ Đề án 06, nên giải pháp càng gắn được với dữ liệu và tiện ích của hệ sinh thái định danh quốc gia thì càng có sức nặng. Thứ hai, ban tổ chức tuyên bố rõ rằng họ không chỉ tìm ý tưởng hay mà tìm giải pháp triển khai được trong thực tế, nên mức độ hoàn thiện của sản phẩm là lợi thế cạnh tranh trực tiếp. Parking HUB có lợi thế đúng ở điểm này vì cả hai nửa của hệ thống đều đã chạy.

### 2.2. Đề bài từ Ngân hàng ý tưởng

Ban tổ chức xây dựng Ngân hàng ý tưởng cùng các bộ ngành và địa phương. Bài toán mà Parking HUB nhận về được phát biểu như sau:

> Đề xuất: Một ứng dụng hiển thị bản đồ các bãi đỗ xe theo thời gian thực, bao gồm thông tin về số chỗ còn trống dựa trên cảm biến hoặc dữ liệu người dùng đóng góp, giá cả, giờ hoạt động. AI dự đoán tình trạng chỗ trống, gợi ý bãi đỗ xe phù hợp nhất dựa trên điểm đến của người dùng và cho phép đặt chỗ, thanh toán trực tuyến.
>
> Đối tượng: Người dùng ô tô, người tham gia giao thông khác.
>
> Tác động: Lãng phí thời gian, nhiên liệu, cản trở giao thông.
>
> Thời điểm và bối cảnh: Số lượng ô tô tăng nhanh, hạ tầng bãi đỗ xe thiếu.
>
> Thực trạng: Vấn đề tìm kiếm chỗ đậu xe ô tô khó khăn tại các khu vực trung tâm thành phố dẫn tới mất thời gian tìm chỗ đậu xe, đậu xe sai quy định.

### 2.3. Cách Parking HUB trả lời đề bài, và chỗ đi xa hơn đề bài

| Yêu cầu trong đề bài | Parking HUB đáp ứng thế nào | Đi xa hơn ở đâu |
|---|---|---|
| Bản đồ bãi đỗ theo thời gian thực | Bản đồ với trạng thái từng bãi, cập nhật liên tục | Trạng thái không do người nhập mà do camera nhìn thấy, nên đáng tin ở mức có thể cam kết giữ chỗ |
| Số chỗ trống từ cảm biến hoặc người dùng đóng góp | Có cả hai, cộng thêm nguồn thứ ba là camera AI | Camera thay thế cảm biến từng ô với chi phí thấp hơn nhiều lần, và người dùng đóng góp chỉ dùng để đối chiếu, không dùng làm nguồn chính |
| Giá cả, giờ hoạt động | Có, chuẩn hoá theo bảng giá và khung giờ của từng bãi | Bổ sung thuộc tính quyết định hành vi thực: có mái che hay không, có hầm, có bảo vệ, giới hạn chiều cao, có trụ sạc, nguy cơ ngập nước |
| AI dự đoán tình trạng chỗ trống | Có, dự đoán ở hai tầm: thời điểm người lái tới nơi, và các mốc tương lai theo ngày và giờ | Dự đoán tương lai là điều kiện để mở tính năng đặt chỗ nhiều ngày, gửi qua đêm và gửi theo tháng |
| Gợi ý bãi phù hợp nhất theo điểm đến | Có, tìm theo điểm đến chứ không theo vị trí hiện tại, tính cả quãng đi bộ cuối tuyến | Cá nhân hoá theo thói quen từng người, học được rằng người này ưu tiên giá, người kia ưu tiên có mái che |
| Đặt chỗ, thanh toán trực tuyến | Có, đặt theo khoảng thời gian, thanh toán không tiền mặt, ra vào tự động bằng nhận diện biển số | Cam kết giữ chỗ có ràng buộc hai chiều, có chính sách xử lý khi bãi không giữ được chỗ và khi khách không đến |
| Giảm đỗ xe sai quy định | Điều hướng nhu cầu về chỗ đỗ hợp pháp gần nhất, kèm giá minh bạch | Cung cấp bản đồ nhiệt nhu cầu và chỗ trống theo giờ cho cơ quan quản lý, phục vụ điều hành và quy hoạch bãi mới |
| Không có trong đề bài | Không có | An toàn cháy nổ trong bãi đỗ, là nỗi đau lớn nhất của chủ bãi hiện nay và là đòn bẩy để họ đồng ý mở dữ liệu |

Điểm cuối cùng là mấu chốt chiến lược của toàn dự án và cần được nói rõ ngay từ đầu. Đề bài mô tả một ứng dụng cho người lái xe. Nhưng một ứng dụng cho người lái xe chỉ hoạt động khi dữ liệu chỗ trống là thật, và dữ liệu chỗ trống chỉ thật khi chủ bãi có động lực đủ mạnh để lắp đặt và duy trì hệ thống. Nếu chỉ mang tới cho chủ bãi lời hứa về khách hàng mới, họ sẽ nghe rồi để đó, vì bãi trong trung tâm vốn đã đông. Phải mang tới cho họ hai thứ họ đang mất tiền và mất ngủ vì nó: thất thu do quản lý vé thủ công, và rủi ro cháy nổ. Đó là lý do bốn model AI không phải phần phụ trợ, mà là cửa vào của cả mô hình kinh doanh.

---

## 3. Tại sao là dự án này, tại sao là bây giờ

### 3.1. Năm lực đẩy cùng hướng

**Lực thứ nhất: số xe tăng nhanh hơn hạ tầng tĩnh.** Cả nước hiện có khoảng 6,8 triệu ô tô đang lưu hành, và tốc độ tăng của ô tô cá nhân cao hơn nhiều tốc độ mở rộng bến bãi. Diện tích đất dành cho giao thông tại các đô thị lớn chỉ chiếm khoảng 6 tới 8 phần trăm, thấp hơn nhiều so với mức 15 tới 20 phần trăm của đô thị hiện đại, còn hệ thống bến bãi giữ xe tại Thành phố Hồ Chí Minh mới đạt khoảng 20 phần trăm quy hoạch. Nói cách khác, khoảng cách giữa nhu cầu và hạ tầng đang mở rộng theo thời gian, không thu hẹp.

**Lực thứ hai: xây thêm bãi không phải lời giải khả thi trong ngắn hạn.** Một bãi đỗ xe ngầm cần đất, vốn, giấy phép và nhiều năm thi công. Trong khi đó, phần dung lượng đang bị bỏ trống vì thiếu thông tin là có thật và có thể khai thác trong vài tuần. Đây là lý do một nền tảng dữ liệu tạo ra giá trị nhanh hơn một dự án hạ tầng, và cũng là lý do bài toán này phù hợp với một cuộc thi về dữ liệu.

**Lực thứ ba: pháp luật vừa chuyển từ khuyến khích sang bắt buộc.** Ba văn bản định hình trực tiếp cơ hội của Parking HUB:

| Văn bản và mốc | Nội dung liên quan | Ý nghĩa với Parking HUB |
|---|---|---|
| Quy định về khu để xe điện tại nhà chung cư, hiệu lực từ 15/12/2025 | Khu để xe điện phải bố trí riêng, có camera giám sát 24 trên 24, hệ thống báo cháy tự động, thiết bị cảnh báo CO và HF | Model phát hiện khói lửa sớm chuyển từ tính năng hay có sang hạng mục tuân thủ, nên chủ bãi có ngân sách và có thời hạn phải làm |
| Quyết định 502/QĐ-TTg ngày 28/03/2026 | Phương án kết nối, chia sẻ dữ liệu giữa các hệ thống camera giám sát an ninh trật tự, xử lý vi phạm và điều hành giao thông với Cơ sở dữ liệu quốc gia về dân cư, và chia sẻ với trung tâm giám sát điều hành đô thị thông minh | Camera tại bãi đỗ có đường đi chính danh để trở thành một phần hạ tầng dữ liệu công, đây là lý do dự án thuộc đúng phạm vi quan tâm của Bộ Công an |
| Nghị định 119/2024/NĐ-CP về thanh toán điện tử giao thông đường bộ | Quy định tài khoản giao thông và cơ sở dữ liệu thanh toán điện tử giao thông đường bộ | Có hành lang cho thanh toán không tiền mặt gắn với phương tiện, phù hợp mô hình vào ra tự động bằng nhận diện biển số |

Bổ sung, từ tháng 01/2025 Thành phố Hồ Chí Minh thí điểm thu phí đỗ xe lòng đường qua thẻ thu phí không dừng trên ba tuyến đường tại Quận 5 và Quận 10, và doanh thu ba tháng đầu năm 2025 đạt hơn 1,3 tỷ đồng, gần gấp đôi cùng kỳ năm trước. Đây là bằng chứng thực địa cho luận điểm cốt lõi: khi khâu ghi nhận và thu tiền được tự động hoá, tiền vốn đang rơi ra ngoài sẽ quay lại.

**Lực thứ tư: kinh tế của công nghệ cảm nhận đã đảo chiều.** Cảm biến siêu âm gắn từng ô đỗ có chi phí lắp đặt khoảng 300 tới 500 đô la Mỹ mỗi ô, còn một camera phân tích được vài chục tới vài trăm ô. Với một bãi 150 chỗ, chênh lệch giữa hai cách làm là khoảng cách giữa một dự án đầu tư hạ tầng và một khoản chi phần mềm. Chính khoảng cách này giải thích vì sao mười năm trước bài toán đếm chỗ trống ở Việt Nam không có lời giải kinh tế, còn bây giờ thì có.

**Lực thứ năm: các giải pháp đi trước đã thất bại đủ rõ.** Việt Nam không thiếu ứng dụng tìm bãi đỗ. MyParking có mạng lưới tại Hà Nội và Thành phố Hồ Chí Minh nhưng bị phản ánh là dữ liệu chỗ trống không cập nhật kịp, dẫn tới tình trạng người dùng đến nơi thì hết chỗ. Phần mềm thu phí đỗ xe lòng đường tại Thành phố Hồ Chí Minh gặp nhiều lỗi về thanh toán, định vị và tìm bãi. Trong giai đoạn 2021 tới 2024, tổng thu từ đỗ xe lòng đường tại Thành phố Hồ Chí Minh là hơn 23,1 tỷ đồng, trong khi chi phí vận hành hơn 25,1 tỷ đồng, nghĩa là ngân sách bù lỗ khoảng 2 tỷ đồng, và có gần 363.000 lượt xe không đóng phí gây thất thu hơn 7,25 tỷ đồng.

Đọc kỹ chuỗi thất bại này sẽ thấy một quy luật. Không đội nào chết vì thiếu ứng dụng, thiếu bản đồ hay thiếu cổng thanh toán. Tất cả đều chết vì dữ liệu về trạng thái thực của chỗ đỗ không đủ tin cậy để người dùng dựa vào, và vì khâu ghi nhận xe vào ra vẫn phụ thuộc vào con người. Đó chính là hai chỗ mà lớp cảm nhận bằng camera AI của Parking HUB giải quyết trực diện.

### 3.2. Cửa sổ cơ hội và cái giá của việc đi chậm

Ba tín hiệu cho thấy khoảng trống này sẽ không mở lâu. Quy định phòng cháy chữa cháy cho khu để xe điện đã có hiệu lực, nên trong 12 tới 24 tháng tới sẽ có một đợt đầu tư camera và báo cháy diện rộng tại chung cư và toà nhà. Đội nào có mặt trong đợt đầu tư đó sẽ nắm luôn quyền đọc dữ liệu chỗ trống của chính những bãi đó. Nếu Parking HUB không đến, nhà thầu phòng cháy chữa cháy sẽ đến, lắp một hệ thống chỉ biết báo cháy, và cánh cửa dữ liệu chỗ trống của bãi đó sẽ đóng lại trong nhiều năm theo tuổi thọ thiết bị.

---

## 4. Trạng thái hiện tại: dự án đang ở đâu

### 4.1. Những gì đã chạy được

Parking HUB không phải một bản mô tả ý tưởng. Hai khối năng lực cốt lõi của hệ thống đã được đội xây dựng, chạy thực tế và trình diễn được. Phần việc phía trước là hợp nhất chúng thành một sản phẩm hoàn chỉnh cho bài toán đỗ xe.

**Khối một, lớp cảm nhận bằng thị giác máy tính.** Bốn model trên nền YOLOv8 đã được huấn luyện và triển khai: phát hiện vùng biển số, đọc ký tự biển số theo cơ chế ghép ký tự để hỗ trợ biển một dòng và hai dòng của Việt Nam, đếm chỗ đỗ trống theo khung hình, và phát hiện khói cùng lửa. Bốn model chạy song song bằng đa luồng, có cơ chế ưu tiên xử lý cảnh báo cháy trước khi tiếp tục đếm chỗ. Trên nền đó, luồng ghi nhận giờ xe vào và giờ xe ra để tính phí theo thời gian gửi và trừ tiền tự động đã hoạt động, kèm giao diện quản trị trên web và ứng dụng di động.

**Khối hai, nền tảng điều phối mạng lưới.** Một nền tảng hoàn chỉnh với backend FastAPI, cơ sở dữ liệu MongoDB, bộ đệm Redis, dịch vụ định tuyến và tính thời gian di chuyển trên dữ liệu bản đồ mở kèm cơ chế dự phòng, dịch vụ thời tiết, engine ghép nối tính điểm theo nhiều biến với nguyên lý dự đoán trạng thái điểm dịch vụ tại thời điểm khách đến, hệ thống phân cấp và chấm điểm điểm dịch vụ từ dữ liệu vận hành thay cho đánh giá cảm tính, luồng đặt lịch có máy trạng thái và khoá phân tán để không xảy ra trùng chỗ, kiến trúc đa chủ thể với phân quyền theo vai trò, và ba cổng giao diện cho khách hàng, cho chủ điểm dịch vụ và cho quản trị viên.

### 4.2. Từ năng lực có sẵn tới sản phẩm Parking HUB

| Năng lực đã có | Vai trò trong Parking HUB | Việc còn phải làm |
|---|---|---|
| Bốn model thị giác trên nền YOLOv8 | Toàn bộ lớp cảm nhận: đếm chỗ trống, nhận diện biển số hai bước, phát hiện khói lửa | Huấn luyện lại và mở rộng dữ liệu cho hầm thiếu sáng, ban đêm, mưa. Chuyển suy luận ra thiết bị biên tại bãi |
| Luồng ghi nhận vào ra và tính phí theo thời gian | Nghiệp vụ cổng bãi, hoá đơn theo thời gian gửi, đối soát doanh thu | Bổ sung quy trình đối soát, xử lý ngoại lệ khi đọc sai biển số, tích hợp thanh toán |
| Engine ghép nối dự đoán trạng thái tại thời điểm khách đến | Trái tim của gợi ý bãi đỗ theo điểm đến | Đổi biến từ thời gian phục vụ sang nhịp xe vào và xe ra của bãi. Giữ nguyên tư duy và phần lớn mã |
| Hệ thống phân cấp và chấm điểm từ dữ liệu vận hành | Phân cấp và phân khúc bãi đỗ theo năng lực và thuộc tính, điểm tin cậy của bãi | Đổi bộ tiêu chí sang đặc thù bãi đỗ: mái che, hầm, bảo vệ, giới hạn chiều cao, trụ sạc, nguy cơ ngập nước |
| Luồng đặt lịch, máy trạng thái, khoá phân tán | Đặt chỗ theo khoảng thời gian, giữ chỗ, xử lý trường hợp khách không đến | Mở rộng từ đặt theo lượt sang đặt theo khoảng thời gian và nhiều ngày |
| Định tuyến, thời gian di chuyển, dịch vụ thời tiết | Tính thời gian tới bãi, quãng đi bộ cuối tuyến, ảnh hưởng của tắc đường và mưa | Bổ sung định tuyến đi bộ từ bãi tới điểm đến |
| Kiến trúc đa chủ thể và phân quyền theo vai trò | Mỗi chủ bãi là một chủ thể độc lập, phân quyền riêng cho bảo vệ, quản lý, kế toán | Bổ sung các vai trò đặc thù của bãi đỗ |
| Ba cổng giao diện | Ứng dụng người lái xe, cổng chủ bãi, cổng quản trị mạng lưới | Thiết kế lại theo nghiệp vụ đỗ xe, ứng dụng di động là kênh chính |
| Nguyên tắc ghi nhận toàn bộ truy vấn tìm kiếm và lựa chọn của người dùng | Nền cho cá nhân hoá và cho dự báo | Giữ nguyên nguyên tắc, mở rộng trường dữ liệu theo bài toán đỗ xe |

Ý nghĩa của bảng này với cuộc thi rất cụ thể. Ở tiêu chí mức độ hoàn thiện và khả năng ứng dụng, phần lớn các đội thi sẽ mang tới bản mô tả ý tưởng kèm bản vẽ giao diện. Parking HUB mang tới hai khối năng lực đã chạy được và một kế hoạch hợp nhất rõ ràng, nên khoảng cách từ hồ sơ tới bản demo hoạt động là ngắn hơn hẳn.

### 4.3. Cái gì phải làm mới

Trung thực về những phần chưa có, vì đây là phần rủi ro thật của dự án:

| Phần phải làm mới | Vì sao chưa có | Mức khó |
|---|---|---|
| Model dự báo chỗ trống theo thời gian cho từng bãi | Cần dữ liệu vận hành theo giờ, chỉ có sau khi có bãi thật chạy | Trung bình, giai đoạn đầu dùng quy tắc và trung bình lịch sử, sau đó chuyển sang học máy |
| Suy luận trên thiết bị biên tại bãi | Phiên bản trước chạy suy luận trên máy chủ và gặp giới hạn tài nguyên khi phát video trực tiếp, nên kiến trúc phải đổi | Cao về kỹ thuật triển khai, nhưng bắt buộc để chi phí mỗi bãi ở mức chấp nhận được |
| Nghiệp vụ giữ chỗ có cam kết hai chiều | Đỗ xe là việc chiếm giữ một không gian trong một khoảng thời gian, khác hẳn đặt một lượt phục vụ | Trung bình về kỹ thuật, cao về thiết kế chính sách |
| Cá nhân hoá theo thói quen và điểm thân thuộc | Dữ liệu hành vi đã được ghi nhận nhưng tầng suy luận chưa xây | Trung bình, phụ thuộc lượng dữ liệu tích luỹ |
| Tuân thủ Luật Bảo vệ dữ liệu cá nhân với dữ liệu biển số và hình ảnh | Đây là hạng mục bắt buộc, không phải tuỳ chọn | Cao về quy trình và thiết kế hệ thống, xem mục 10 của tài liệu 03 |

---

## 5. Định vị: Parking HUB là gì và không phải là gì

### 5.1. Một câu định vị

Parking HUB là lớp dữ liệu và điều phối cho giao thông tĩnh đô thị, biến các bãi đỗ xe rời rạc thành một mạng lưới duy nhất mà người lái xe có thể tin, đặt trước và trả tiền, còn chủ bãi thì vận hành an toàn hơn và bán được những giờ đang bỏ trống.

### 5.2. Không phải là gì

| Không phải | Vì sao cần nói rõ |
|---|---|
| Không phải bản đồ liệt kê bãi đỗ | Bản đồ trả về danh sách để người dùng tự đoán. Parking HUB trả về một chỗ đã được giữ, có giá và có thời gian |
| Không phải ứng dụng dựa vào người dùng đóng góp dữ liệu | Dữ liệu do người dùng báo là dữ liệu trễ và thưa. Nó chỉ dùng để đối chiếu, không dùng để cam kết |
| Không phải phần mềm quản lý bãi đơn lẻ | Một phần mềm cho một bãi thì giá trị dừng ở hàng rào của bãi đó. Parking HUB có giá trị vì nó nhìn thấy toàn mạng lưới, biết khi bãi này hết chỗ thì dòng xe chảy sang đâu |
| Không phải hệ thống chấm điểm theo cảm xúc người dùng | Điểm của bãi tính từ dữ liệu vận hành: tỷ lệ giữ đúng chỗ đã cam kết, thời gian vào ra, tỷ lệ khách quay lại, số vụ tranh chấp |
| Không phải nhà thầu phòng cháy chữa cháy | Parking HUB không thay hệ thống chữa cháy. Nó thêm một lớp phát hiện sớm bằng thị giác máy tính, đứng trước đầu báo nhiệt và khói theo thời gian |

### 5.3. So với các nhóm giải pháp hiện có

| Nhóm | Đại diện | Điểm mạnh | Điểm chết | Parking HUB khác ở đâu |
|---|---|---|---|---|
| Ứng dụng tìm bãi đỗ | MyParking, ezPark | Có mạng lưới, có bản đồ, có đặt chỗ | Dữ liệu chỗ trống phụ thuộc chủ bãi cập nhật thủ công, nên hay sai, người dùng mất niềm tin sau một lần đến nơi hết chỗ | Dữ liệu chỗ trống do camera sinh ra, đủ tin để cam kết giữ chỗ |
| Ứng dụng gắn hệ sinh thái thu phí | iParking | Thanh toán thuận tiện, gắn tài khoản giao thông | Vẫn không giải được bài toán biết trước còn chỗ hay không | Thanh toán là bước cuối, giá trị nằm ở bước biết chắc còn chỗ |
| Phần mềm thu phí đỗ xe công cộng | Hệ thống thu phí lòng đường | Có thẩm quyền quản lý, có nguồn thu ngân sách | Thất thu lớn vì phụ thuộc người dùng tự khai và nhân viên thu, phần mềm nhiều lỗi | Ghi nhận tự động bằng nhận diện biển số, khớp lệnh giữa xe thực tế và lượt đã trả tiền |
| Thiết bị cảm biến từng ô | Nhà cung cấp cảm biến quốc tế | Chính xác từng ô | Chi phí mỗi ô cao, phải đào lắp, bảo trì tốn kém, không mở rộng được ở Việt Nam | Một camera thay cho hàng chục cảm biến, dùng lại hạ tầng camera đã có |
| Hệ thống quản lý bãi truyền thống | Đầu đọc thẻ, barrier | Đã quen, đã có | Đảo lộn khi mất thẻ, dễ thất thu, không sinh dữ liệu dùng được cho mạng lưới | Không thay barrier, chỉ bổ sung lớp nhìn và lớp dữ liệu lên trên |

---

## 6. Kiến trúc giá trị bốn lớp

Đây là cách tổ chức toàn bộ dự án. Mỗi lớp có lý do tồn tại độc lập, có thể bán riêng, và lớp dưới là điều kiện cho lớp trên.

```
Lớp 4  DỮ LIỆU CÔNG          Bản đồ nhiệt giao thông tĩnh, chia sẻ dữ liệu
                             cho cơ quan quản lý, hỗ trợ quy hoạch bãi mới,
                             liên thông cảnh báo cháy
                                        ^
Lớp 3  MẠNG LƯỚI             Đặt chỗ theo thời gian, thanh toán, giữ chỗ,
                             gói tháng, đội xe doanh nghiệp, danh tiếng bãi
                                        ^
Lớp 2  ĐIỀU PHỐI             Gợi ý theo điểm đến, dự đoán chỗ trống tại thời
                             điểm tới nơi, dự báo tương lai, cá nhân hoá,
                             định giá theo nhu cầu
                                        ^
Lớp 1  CẢM NHẬN              Camera AI: đếm chỗ trống, nhận diện biển số,
                             phát hiện khói lửa sớm. Cộng nguồn phụ: chủ bãi
                             cập nhật, người dùng phản hồi, cảm biến nếu có
```

| Lớp | Bán cho ai | Bán bằng lý lẽ gì | Không có lớp này thì sao |
|---|---|---|---|
| Lớp 1, cảm nhận | Chủ bãi | Chống thất thu, tuân thủ quy định phòng cháy, biết chính xác bãi mình đang lấp đầy bao nhiêu | Không có dữ liệu thật. Toàn bộ phần còn lại trở thành phỏng đoán, và đây chính là chỗ các giải pháp trước đã chết |
| Lớp 2, điều phối | Người lái xe | Không phải đoán, không phải chạy vòng, biết trước quãng đi bộ và giá | Chỉ còn là bản đồ. Người dùng vẫn phải tự chọn và tự chịu rủi ro |
| Lớp 3, mạng lưới | Cả hai bên | Người lái có sự chắc chắn, chủ bãi có thêm doanh thu từ giờ trống | Mỗi bãi lại là một hòn đảo, không có hiệu ứng mạng lưới, không có doanh thu nền tảng |
| Lớp 4, dữ liệu công | Cơ quan quản lý đô thị và giao thông | Biết thật sự thiếu chỗ ở đâu, giờ nào, để điều hành và quy hoạch, thay vì dựa vào khảo sát định kỳ | Mất phần tác động xã hội và mất tính chính danh của dự án trong bối cảnh Chính phủ số |

---

## 7. Ai nhận được gì

| Bên tham gia | Họ đang mất gì | Parking HUB mang lại gì | Họ đóng góp gì vào mạng lưới |
|---|---|---|---|
| Người lái xe cá nhân | Thời gian tìm chỗ, nhiên liệu, tiền phạt đỗ sai, lo lắng về an toàn xe | Chỗ đã giữ trước, giá biết trước, quãng đi bộ biết trước, xem được camera, cảnh báo sự cố | Nhu cầu, hành vi, và một dòng doanh thu ổn định cho bãi |
| Chủ bãi có hệ thống, hầm toà nhà và bãi thương mại | Thất thu do quản lý vé thủ công, rủi ro cháy nổ, giờ thấp điểm bỏ trống, tranh chấp với khách | Ghi nhận vào ra tự động, cảnh báo cháy sớm, bán được giờ trống, dữ liệu vận hành theo giờ | Dữ liệu chỗ trống theo thời gian thực, dung lượng đỗ xe |
| Chủ chỗ đỗ nhỏ, sân nhà và mặt bằng trống | Tài sản để không, muốn cho thuê nhưng không có kênh và sợ rủi ro | Kênh cho thuê theo giờ, theo buổi hoặc theo tháng, có xác thực người thuê và có bằng chứng hình ảnh | Dung lượng ở những nơi mà bãi lớn không có, tức là phần đuôi dài của cung |
| Ban quản trị và ban quản lý toà nhà | Áp lực tuân thủ quy định phòng cháy mới, khiếu nại của cư dân về chỗ đỗ | Lớp phát hiện cháy sớm, minh bạch chỗ đỗ cho cư dân và khách, thêm nguồn thu từ chỗ trống ban ngày | Dung lượng lớn tập trung, và là nhóm khách hàng có ngân sách |
| Doanh nghiệp có đội xe | Không kiểm soát được chi phí đỗ xe rải rác, khó đối soát hoá đơn | Hợp đồng tập trung, đỗ xe theo tuyến hoạt động, một hoá đơn, báo cáo theo xe và theo người lái | Nhu cầu ổn định, khối lượng lớn, ít biến động |
| Cơ quan quản lý đô thị và giao thông | Không có dữ liệu thực về giao thông tĩnh, thất thu phí đỗ xe công cộng, đỗ sai quy định tràn lan | Bản đồ nhu cầu và chỗ trống theo giờ, dữ liệu phục vụ quy hoạch, công cụ giảm đỗ sai bằng điều hướng nhu cầu | Thẩm quyền, dữ liệu bãi công cộng, tính chính danh |
| Đơn vị bảo hiểm và cứu hộ, giai đoạn sau | Thiếu bằng chứng khi xảy ra sự cố trong bãi | Bằng chứng hình ảnh và mốc thời gian, cảnh báo sớm giúp giảm tổn thất | Sản phẩm bảo hiểm gắn với bãi đạt chuẩn, tạo thêm lý do để bãi nâng cấp |

---

## 8. Câu chuyện xuyên suốt: một buổi sáng thứ Ba

Câu chuyện dưới đây không mô tả một tính năng, nó mô tả cách bốn lớp làm việc cùng nhau trong hai mươi phút của một người thật.

**07 giờ 42, tại một chung cư ở Bình Thạnh.** Anh Khoa chuẩn bị đi làm. Nơi làm việc của anh là một toà nhà trên đường Nguyễn Thị Minh Khai, Quận 1. Hai tháng nay anh đến sớm hơn hai mươi phút, không vì họp sớm, mà vì cần thời gian tìm chỗ đỗ. Sáng nay anh mở Parking HUB. Ứng dụng không hỏi anh muốn đi đâu, nó hiển thị sẵn: điểm đến quen thuộc, toà nhà nơi anh làm việc, giờ tới dự kiến 08 giờ 15. Hệ thống biết điều này vì đã học từ mười bốn lần đỗ xe của anh trong ba tuần, tất cả đều vào khoảng thời gian này, tất cả đều ở cùng một khu vực.

**Điều hệ thống làm trong hai giây đó.** Lớp điều phối lấy danh sách bãi trong bán kính đi bộ bảy trăm mét từ toà nhà đích. Với mỗi bãi, nó không hỏi hiện tại còn mấy chỗ, mà hỏi vào 08 giờ 15 thì còn mấy chỗ. Câu trả lời đến từ ba nguồn ghép lại: số chỗ trống hiện tại do camera đếm được, tốc độ xe vào và ra của bãi đó vào sáng thứ Ba theo dữ liệu bốn tuần gần nhất, và thời gian di chuyển thực tế từ nhà anh Khoa tới bãi theo tình trạng giao thông lúc này. Bãi hầm của toà nhà đích hiện còn mười một chỗ nhưng vào 08 giờ 15 thì gần như chắc chắn hết, vì mỗi sáng thứ Ba từ 07 giờ 50 tới 08 giờ 20 bãi này nhận trung bình hai mươi ba xe. Bãi thứ hai, một hầm chung cư cách đích bốn trăm mét, sáng nào cũng trống khoảng bốn mươi phần trăm vì cư dân đã đi làm.

**Ứng dụng đưa ra một đề nghị, không phải một danh sách.** Bãi hầm chung cư, cách đích bốn trăm mét, đi bộ năm phút, có mái che, có bảo vệ, 20.000 đồng cho ba giờ đầu và 8.000 đồng mỗi giờ tiếp theo, giữ chỗ tới 08 giờ 30. Bên dưới là hai lựa chọn thay thế, một rẻ hơn nhưng đi bộ mười một phút, một đắt hơn nhưng ngay dưới toà nhà đích và chỉ còn xác suất bốn mươi phần trăm còn chỗ khi anh đến. Anh Khoa bấm giữ chỗ.

**08 giờ 11, tại cổng bãi.** Anh không dừng lại lấy thẻ. Camera cổng đọc biển số xe anh, đối chiếu với lượt giữ chỗ, barrier mở. Từ lúc này đồng hồ tính phí bắt đầu chạy, và trên ứng dụng của anh hiện số tiền đang phát sinh. Bên trong bãi, một camera khác cập nhật số chỗ trống vừa giảm đi một, và con số đó lập tức có hiệu lực với mọi người dùng khác đang tìm chỗ quanh khu vực này.

**09 giờ 30, tại tầng hầm.** Một xe điện đang sạc ở góc B bắt đầu phát ra khói mỏng, thứ mà đầu báo nhiệt trên trần chưa cảm nhận được vì nhiệt độ chưa đủ và khói chưa lan tới. Camera nhìn thấy. Trong vòng vài giây, cảnh báo đi tới ba nơi cùng lúc: điện thoại của bảo vệ đang trực với ảnh khung hình và vị trí góc B, màn hình phòng quản lý toà nhà, và điện thoại của những người đang gửi xe trong bãi. Bảo vệ xuống tới nơi khi đó vẫn còn là đám khói, chưa là đám cháy.

**17 giờ 45, khi anh Khoa ra xe.** Camera cổng đọc biển số, hệ thống chốt thời gian gửi là chín giờ ba mươi bốn phút, trừ tiền từ phương thức thanh toán đã liên kết, barrier mở, hoá đơn hiện trên điện thoại. Anh không nói chuyện với ai, không đưa thẻ, không đếm tiền lẻ.

**Cùng lúc đó, ở ba nơi khác.** Chủ bãi thấy trên cổng quản lý của mình rằng hôm nay bãi đạt tỷ lệ lấp đầy tám mươi hai phần trăm trong khung giờ 08 tới 18, nhưng chỉ hai mươi mốt phần trăm trong khung 22 giờ tới 06 giờ, kèm một đề xuất: mở bán gói gửi qua đêm cho khu vực dân cư xung quanh với giá thấp hơn ba mươi phần trăm, ước tính thêm khoảng chín triệu đồng mỗi tháng. Trên cổng quản trị mạng lưới, một điểm màu đỏ hiện lên tại khu vực quanh toà nhà đích của anh Khoa, nghĩa là nhu cầu trong bán kính ba trăm mét vượt cung trong khung giờ 08 tới 09 suốt hai mươi ngày liên tục, đây là dữ liệu để đi thuyết phục bãi kế tiếp trong khu vực tham gia mạng lưới. Và trong báo cáo tổng hợp phi định danh gửi cơ quan quản lý giao thông đô thị, khu vực này được đánh dấu là điểm nghẽn giao thông tĩnh cần được xem xét khi quy hoạch bãi mới.

Một hành động của một người, bốn lớp giá trị được tạo ra. Đó là toàn bộ luận điểm của dự án này.

---

## 9. Vì sao dự án này khó bị sao chép

Câu hỏi mà mọi ban giám khảo và mọi nhà đầu tư đều hỏi: nếu ý tưởng này tốt, tại sao một đơn vị lớn hơn không làm được trong sáu tháng. Có năm lớp phòng vệ, xếp theo độ bền tăng dần.

**Lớp một, tốc độ khởi động.** Bốn model thị giác và một nền tảng điều phối đều đã chạy. Đội khác bắt đầu từ đầu sẽ mất từ sáu tới chín tháng chỉ để tới điểm mà dự án này đang đứng. Đây là lợi thế thật nhưng mòn theo thời gian, nên nó chỉ là lớp ngoài cùng.

**Lớp hai, chi phí chuyển đổi của phần cứng đã lắp.** Khi một bãi đã lắp thiết bị biên và camera đã hiệu chuẩn theo đúng góc nhìn của bãi đó, việc thay nhà cung cấp không phải là đổi ứng dụng mà là làm lại toàn bộ khảo sát, lắp đặt, hiệu chuẩn và đào tạo. Trong ngành này, ai lắp trước sẽ giữ được bãi đó nhiều năm.

**Lớp ba, dữ liệu vận hành không thể mua.** Mỗi bãi tích luỹ một hồ sơ hành vi riêng: nhịp xe vào ra theo từng ngày trong tuần, cách bãi phản ứng khi trời mưa, thời điểm bãi thực sự hết chỗ so với thời điểm bãi báo hết chỗ, tỷ lệ khách giữ chỗ nhưng không đến. Sau ba tới sáu tháng, chất lượng dự báo của một mạng lưới có dữ liệu sẽ vượt xa một mạng lưới mới, và người dùng cảm nhận điều đó ngay ở lần đầu tiên họ đến nơi mà chỗ vẫn còn.

**Lớp bốn, hiệu ứng mạng lưới hai phía có tính địa phương.** Giá trị của Parking HUB với một người lái xe không phụ thuộc vào tổng số bãi trên cả nước, mà phụ thuộc vào mật độ bãi trong bán kính đi bộ quanh nơi họ cần đến. Điều này có hai hệ quả. Thứ nhất, chiến lược đúng là chiếm mật độ từng khu vực, không phải trải mỏng nhiều thành phố. Thứ hai, khi một khu vực đã đạt mật độ, đối thủ vào sau phải giành lại từng bãi trong đúng khu vực đó, chứ không thể bù bằng quy mô ở nơi khác.

**Lớp năm, vị thế trong hạ tầng dữ liệu công.** Một mạng lưới đã kết nối và chia sẻ dữ liệu giao thông tĩnh cho cơ quan quản lý, theo đúng chủ trương tại Quyết định 502/QĐ-TTg, sẽ trở thành một phần của quy trình điều hành. Vị thế đó không mua được bằng vốn và không sao chép được bằng công nghệ, nó chỉ đến từ việc làm đúng, làm sớm và làm minh bạch.

---

## 10. Chỉ số thành công

Ba nhóm chỉ số, tương ứng ba câu hỏi khác nhau. Các mức mục tiêu dưới đây là mốc tham chiếu để hiệu chỉnh sau khi có dữ liệu thực từ những bãi đầu tiên, không phải cam kết.

### 10.1. Nhóm một, chứng minh dữ liệu đáng tin

Đây là nhóm quan trọng nhất, vì đây là chỗ mọi giải pháp đi trước đã thất bại.

| Chỉ số | Ý nghĩa | Mốc tham chiếu |
|---|---|---|
| Độ chính xác đếm chỗ trống | So sánh số camera đếm với số kiểm đếm thủ công | Sai số dưới 5 phần trăm số ô trong điều kiện đủ sáng |
| Độ chính xác đọc biển số | Tỷ lệ đọc đúng toàn bộ biển số ở cổng | Trên 95 phần trăm ban ngày, trên 90 phần trăm ban đêm có đèn |
| Tỷ lệ giữ đúng chỗ đã cam kết | Số lượt khách đến và có chỗ trên tổng số lượt đã giữ chỗ | Trên 98 phần trăm |
| Độ chính xác dự báo chỗ trống | Sai số giữa dự báo và thực tế tại thời điểm khách đến | Sai số trung bình dưới 10 phần trăm dung lượng bãi |
| Thời gian phát hiện khói | Từ lúc khói xuất hiện trong khung hình tới lúc cảnh báo tới người trực | Dưới 10 giây |
| Tỷ lệ báo động sai của phát hiện cháy | Số cảnh báo sai mỗi camera mỗi tuần | Dưới 1 lần một tuần một camera sau hiệu chuẩn |

### 10.2. Nhóm hai, chứng minh có giá trị kinh tế

| Chỉ số | Ý nghĩa | Mốc tham chiếu |
|---|---|---|
| Thời gian tìm chỗ của người dùng | Từ lúc mở ứng dụng tới lúc xe vào bãi | Giảm còn dưới một phần ba so với hành vi trước đó, do người dùng tự báo cáo và đối chiếu bằng dữ liệu |
| Tỷ lệ lấp đầy giờ thấp điểm của bãi | Phần dung lượng bán được thêm nhờ nền tảng | Tăng ít nhất 10 điểm phần trăm trong khung giờ thấp điểm sau 3 tháng |
| Doanh thu thu hồi được nhờ ghi nhận tự động | Chênh lệch giữa doanh thu ghi nhận trước và sau khi lắp | Đo bằng đối chiếu thực tế tại bãi thử nghiệm |
| Tỷ lệ lượt đỗ xe đến từ nền tảng | Mức độ nền tảng trở nên quan trọng với bãi | Trên 15 phần trăm sau 6 tháng tại bãi đã kết nối đầy đủ |
| Tỷ lệ quay lại trong 30 ngày | Sản phẩm có tạo thói quen hay không | Trên 35 phần trăm |
| Chi phí đưa một bãi lên hệ thống | Hiệu quả của playbook onboard | Giảm ít nhất 30 phần trăm sau mỗi 20 bãi |

### 10.3. Nhóm ba, chứng minh tác động xã hội

| Chỉ số | Cách đo | Vì sao quan trọng với cuộc thi |
|---|---|---|
| Số phút và số km tiết kiệm được cho mỗi lượt đỗ xe | So sánh quãng đường thực tế với quãng đường trung bình khi tìm chỗ thủ công | Đây là con số quy đổi trực tiếp ra nhiên liệu và khí thải, tức là tác động môi trường |
| Số lượt đỗ xe được điều hướng từ nơi không hợp lệ về bãi hợp pháp | Đếm lượt người dùng chọn bãi sau khi được gợi ý trong khu vực có mật độ đỗ sai cao | Gắn trực tiếp với mục tiêu giảm đỗ xe sai quy định trong đề bài |
| Số vụ cháy được phát hiện ở giai đoạn khói | Đếm và ghi nhận từng vụ với mốc thời gian | Đây là chỉ số tác động mạnh nhất về mặt xã hội, mỗi vụ là tài sản và có thể là tính mạng |
| Số khu vực được đánh dấu là điểm nghẽn giao thông tĩnh | Số điểm nóng phát hiện được và chuyển cho cơ quan quản lý | Chứng minh giá trị cho quản lý nhà nước và quy hoạch |

---

## 11. Ghi chú về tên dự án

Tên đang dùng là Parking HUB, ghi nhận là tên tạm thời. Ba điểm cần cân nhắc trước khi chốt:

Thứ nhất, cụm từ Parking Hub rất phổ biến trong ngành nên khả năng trùng tên thương hiệu và khó đăng ký nhãn hiệu là cao. Cần tra cứu trước khi in vào hồ sơ chính thức.

Thứ hai, tên hiện tại mô tả nơi tập trung bãi đỗ, nghĩa là nó đóng khung dự án ở lớp mạng lưới. Trong khi giá trị khó sao chép nhất của dự án nằm ở lớp cảm nhận và lớp dữ liệu. Nếu tầm nhìn dài hạn là hạ tầng dữ liệu giao thông tĩnh, tên nên gợi được điều đó.

Thứ ba, với một cuộc thi do Bộ Công an tổ chức và hướng tới Chính phủ số, một cái tên đọc được bằng tiếng Việt sẽ có lợi thế truyền thông, nhất là ở vòng bình chọn cộng đồng chiếm 10 điểm.

Đề nghị: giữ Parking HUB cho bản thảo nội bộ, và chốt tên cuối cùng trước khi nộp hồ sơ. Toàn bộ tài liệu dùng đúng một chuỗi tên nên việc thay tên chỉ là một lần tìm và thay thế.

---

## 12. Đọc tiếp

| Bạn cần biết | Đọc tài liệu |
|---|---|
| Nỗi đau cụ thể của từng nhóm người dùng, và tại sao đối thủ thất bại | [02. Phân tích bài toán](02_Problem_Deep_Dive.md) |
| Sản phẩm làm được gì, kể theo câu chuyện, gồm cả cá nhân hoá và bốn model AI | [03. Tính năng sản phẩm](03_Product_Features.md) |
| Tiền đến từ đâu, ai trả, bao nhiêu | [04. Mô hình kinh doanh](../02_business-operations/04_Business_Model.md) |
| Cách đưa bãi đỗ lên hệ thống, phân loại và phân cấp bãi | [05. Playbook onboard bãi đỗ](../02_business-operations/05_Onboarding_Playbook.md) |
| Làm gì, không làm gì, theo mốc nào, rủi ro gì | [06. Phạm vi và lộ trình](../02_business-operations/06_Scope_and_Roadmap.md) |
| Bản nộp cuộc thi | [07. Bản đề xuất Data for Life](../03_submission/07_Proposal_DataForLife.md) |
| Số nào có nguồn, số nào là giả định | [99. Nguồn dữ liệu và giả định](../99_reference/99_Sources_and_Assumptions.md) |
