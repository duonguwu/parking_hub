# 02. Phân tích bài toán

Tại sao tìm chỗ đỗ xe ở trung tâm đô thị Việt Nam vẫn là việc khó, dù đã có nhiều ứng dụng ra đời

Phiên bản: 1.0
Ngày: 21/08/2026
Tài liệu liên quan: [01. Tổng quan dự án](01_Project_Overview.md), [03. Tính năng sản phẩm](03_Product_Features.md)

---

## Mục lục

1. [Phát biểu lại bài toán](#1-phát-biểu-lại-bài-toán)
2. [Bốn nút thắt thật sự](#2-bốn-nút-thắt-thật-sự)
3. [Chuỗi thiệt hại: một lượt tìm chỗ thất bại tốn bao nhiêu](#3-chuỗi-thiệt-hại-một-lượt-tìm-chỗ-thất-bại-tốn-bao-nhiêu)
4. [Hiện trạng bằng số](#4-hiện-trạng-bằng-số)
5. [Tại sao các giải pháp đi trước thất bại](#5-tại-sao-các-giải-pháp-đi-trước-thất-bại)
6. [Bảy câu chuyện người dùng](#6-bảy-câu-chuyện-người-dùng)
7. [Bản đồ các bên liên quan và động lực](#7-bản-đồ-các-bên-liên-quan-và-động-lực)
8. [Kết luận: đây là bài toán dữ liệu, không phải bài toán ứng dụng](#8-kết-luận-đây-là-bài-toán-dữ-liệu-không-phải-bài-toán-ứng-dụng)

---

## 1. Phát biểu lại bài toán

Đề bài của ban tổ chức mô tả hiện tượng: tìm chỗ đậu xe ô tô khó khăn tại khu vực trung tâm, dẫn tới mất thời gian và đậu xe sai quy định. Để thiết kế được sản phẩm, cần phát biểu lại theo nguyên nhân.

Hiện tượng bề mặt là thiếu chỗ đỗ. Nhưng nếu đi khảo sát một khu vực trung tâm vào giờ cao điểm, sẽ thấy một bức tranh khác. Cùng lúc mà một dòng xe đang chạy vòng quanh khối phố để tìm chỗ, trong bán kính năm trăm mét thường vẫn còn dung lượng đang trống:

Hầm của các chung cư quanh đó trống đáng kể vào ban ngày, vì cư dân đã lái xe đi làm. Bãi của các nhà hàng và quán ăn trống suốt buổi sáng, chỉ đông từ chiều tối. Sân của các hộ dân mặt tiền để không cả ngày. Bãi của các cơ quan có khoảng trống vào giờ nghỉ. Tầng hầm của một số toà nhà văn phòng còn chỗ ở tầng B3 nhưng người bên ngoài không biết vì bảng thông báo ở cổng chỉ ghi hai chữ hết chỗ.

Vấn đề vì vậy có hai tầng. Tầng dài hạn là thiếu hạ tầng thật, và tầng này chỉ giải được bằng đầu tư và quy hoạch trong nhiều năm. Tầng ngắn hạn là dung lượng đang có nhưng vô hình, và tầng này giải được bằng dữ liệu trong vài tuần.

> Bài toán mà Parking HUB nhận: không phải làm ra chỗ đỗ mới, mà làm cho những chỗ đỗ đang tồn tại trở nên nhìn thấy được, tin được và đặt được.

Phát biểu như vậy có ba hệ quả thiết kế, và ba hệ quả này chi phối toàn bộ các tài liệu còn lại:

Thứ nhất, ưu tiên số một là chất lượng dữ liệu trạng thái, không phải chất lượng giao diện. Một ứng dụng đẹp với dữ liệu sai thì tệ hơn không có ứng dụng, vì nó khiến người dùng đi tới một nơi rồi thất vọng, và họ sẽ không mở lại lần thứ ba.

Thứ hai, phía cung phải được giải quyết trước phía cầu. Người lái xe không có gì để mất khi thử một ứng dụng mới, nên họ dễ đến và cũng dễ đi. Chủ bãi thì phải bỏ công, bỏ tiền và thay đổi quy trình vận hành, nên họ là bên khó thuyết phục hơn và cần một lý do mạnh hơn lời hứa về khách hàng.

Thứ ba, nếu chỉ số hoá thông tin mà không số hoá khâu ghi nhận xe vào và xe ra, thì dữ liệu sẽ luôn trễ và luôn sai. Đây là lý do nhận diện biển số không phải tính năng phụ mà là nền móng.

---

## 2. Bốn nút thắt thật sự

### Nút thắt một: không có nguồn dữ liệu chỗ trống đáng tin

Muốn biết một bãi còn mấy chỗ, có bốn cách. Ba cách đầu đều đã được thử ở Việt Nam và đều có điểm chết.

| Cách làm | Cơ chế | Điểm chết |
|---|---|---|
| Chủ bãi tự cập nhật trên ứng dụng | Bảo vệ hoặc quản lý nhập số chỗ trống bằng tay | Không ai nhập liên tục trong lúc đang làm việc. Vào giờ cao điểm, đúng lúc dữ liệu quan trọng nhất, thì không ai có thời gian nhập. Dữ liệu trễ từ ba mươi phút tới vài giờ |
| Người dùng đóng góp | Người đỗ xe báo lại tình trạng bãi | Dữ liệu thưa và lệch. Người dùng chỉ báo khi bãi hết chỗ và họ đang tức, ít ai báo khi bãi còn chỗ. Số lượng báo cáo không đủ dày để tạo trạng thái theo thời gian thực |
| Cảm biến từng ô đỗ | Cảm biến siêu âm hoặc từ tính gắn tại mỗi ô | Chi phí khoảng 300 tới 500 đô la Mỹ mỗi ô kèm lắp đặt. Một bãi 150 chỗ thành một dự án hạ tầng. Còn phải bảo trì, thay pin, xử lý hỏng hóc |
| Camera phân tích bằng thị giác máy tính | Một camera quan sát nhiều ô, model đếm số ô trống theo khung hình | Cần ánh sáng đủ, cần góc nhìn tốt, cần hiệu chuẩn cho từng bãi. Nhưng một camera thay được hàng chục cảm biến, và phần lớn bãi có hệ thống đã lắp camera từ trước |

Cách thứ tư là cách duy nhất có kinh tế đủ tốt để mở rộng ra hàng trăm bãi tại Việt Nam, và đây chính là năng lực mà đội đã xây dựng và kiểm chứng được trên bãi đỗ thật.

### Nút thắt hai: không có cam kết giữ chỗ, nên thông tin không chuyển thành hành động

Giả sử người lái xe biết chắc bãi đang còn mười chỗ. Điều đó vẫn không đủ, vì họ cần hai mươi phút để tới, và trong hai mươi phút đó mười chỗ có thể hết. Thông tin về hiện tại không giải quyết được lo lắng về tương lai.

Đây là lý do một sản phẩm đỗ xe nghiêm túc phải làm hai việc mà không ứng dụng nào tại Việt Nam đang làm tốt. Một là dự đoán trạng thái tại thời điểm người lái tới nơi, chứ không phải tại thời điểm họ tìm kiếm. Hai là giữ chỗ có ràng buộc, tức là bãi cam kết dành chỗ trong một khung thời gian, và người lái cam kết đến trong khung đó.

Nếu thiếu cả hai, sản phẩm chỉ là bản đồ, và bản đồ thì Google đã làm miễn phí.

### Nút thắt ba: phía cung không có động lực đủ mạnh để tham gia

Đây là nút thắt bị xem nhẹ nhất, và cũng là nơi nhiều dự án chết âm thầm. Hãy thử đứng ở vị trí chủ một bãi hầm 150 chỗ tại trung tâm, đang lấp đầy tám mươi lăm phần trăm vào ban ngày.

Một nền tảng đến gặp và nói rằng sẽ mang thêm khách. Câu trả lời hợp lý của chủ bãi là bãi tôi ban ngày gần như đầy, tôi không cần thêm khách vào giờ đó, còn giờ đêm thì có khách cũng chỉ vài xe. Đổi lại, tôi phải cho nhân viên cập nhật số chỗ trống mỗi giờ, phải giữ chỗ cho khách của các anh, và phải chia doanh thu. Tôi không thấy lý do.

Chủ bãi đó nói đúng. Muốn họ tham gia, phải mang tới điều họ đang mất tiền hoặc đang lo lắng, không phải điều mình muốn bán. Có ba điều như vậy:

| Nỗi đau của chủ bãi | Biểu hiện hàng ngày | Giá trị nếu được giải |
|---|---|---|
| Thất thu do quản lý thủ công | Vé giấy, thu tiền mặt, đổi ca không đối soát được, khách nói gửi hai giờ mà thực tế bốn giờ, mất thẻ thì tính theo cảm tính | Ghi nhận tự động bằng biển số cho một con số duy nhất không tranh chấp được, và bịt các đường rò rỉ |
| Rủi ro cháy nổ | Bãi kín, xe san sát, xe điện sạc trong hầm, hệ thống báo cháy chỉ kích hoạt khi lửa và khói đã lớn, khi đó tổn thất đã xảy ra | Phát hiện ở giai đoạn khói mỏng, tức là giai đoạn còn dập được bằng bình chữa cháy tay và còn kịp di dời xe |
| Giờ trống không bán được | Hầm chung cư trống bốn mươi phần trăm ban ngày, bãi nhà hàng trống cả buổi sáng, bãi văn phòng trống cả cuối tuần | Bán đúng những giờ đó cho đúng nhóm khách có nhu cầu vào đúng giờ đó |

Hai nỗi đau đầu là tiền và là rủi ro, chúng có sức thuyết phục ngay lập tức. Nỗi đau thứ ba mới là chỗ nền tảng kiếm tiền. Thứ tự này không được đảo, vì đảo thứ tự là lý do các nền tảng trước đó không onboard được cung.

### Nút thắt bốn: không ai có dữ liệu để quản lý và quy hoạch

Cơ quan quản lý đô thị hiện không có bức tranh thời gian thực về giao thông tĩnh. Số liệu có được đến từ khảo sát định kỳ và báo cáo của đơn vị vận hành, tức là dữ liệu thưa, trễ và mang tính tổng hợp. Từ dữ liệu đó, rất khó trả lời những câu hỏi cụ thể mà việc điều hành cần: khu nào thiếu chỗ vào giờ nào, thiếu bao nhiêu chỗ, xe đỗ sai quy định trên tuyến này là do không có chỗ hay do có chỗ mà đắt hơn, nếu mở thêm một bãi hai trăm chỗ ở vị trí này thì bao nhiêu phần trăm nhu cầu hiện tại được hấp thụ.

Đây là nút thắt tạo ra phần tác động xã hội của dự án, và cũng là phần gắn dự án với chủ đề của cuộc thi.

---

## 3. Chuỗi thiệt hại: một lượt tìm chỗ thất bại tốn bao nhiêu

Để hiểu quy mô, hãy tính chi phí của một lượt tìm chỗ thất bại. Các con số dưới đây là ước lượng minh hoạ theo giả định nêu kèm, dùng để hình dung bậc độ lớn, không phải số đo thực địa.

```
Một lượt tìm chỗ đỗ ở trung tâm vào giờ cao điểm, giả định 15 phút vòng xe:

Thời gian của người lái          15 phút
Quãng đường chạy vòng            khoảng 3 tới 5 km
Nhiên liệu                       khoảng 0,3 tới 0,5 lít
Xe đang chạy chậm và dừng đỗ     chiếm chỗ trên lòng đường trong 15 phút,
                                 làm chậm dòng xe phía sau
Kết cục xấu nhất                 đỗ sai quy định, chịu rủi ro bị xử phạt,
                                 chắn lối, hoặc bị cẩu xe
```

Ba điểm cần nhấn.

Thứ nhất, thiệt hại không dừng ở người lái. Một xe tìm chỗ là một xe di chuyển chậm, phanh và rẽ nhiều, tức là nó tạo ra nhiễu cho toàn bộ dòng xe phía sau. Nghiên cứu quốc tế trong lĩnh vực kinh tế đỗ xe, tiêu biểu là các công trình của Donald Shoup, chỉ ra rằng ở một số khu trung tâm, xe đang tìm chỗ đỗ có thể chiếm một tỷ lệ đáng kể lưu lượng trên đường, với các mức được nhắc tới quanh ba mươi phần trăm trong những nghiên cứu điểm. Con số cụ thể thay đổi theo từng thành phố và cần khảo sát riêng cho đô thị Việt Nam, nhưng chiều của kết luận thì nhất quán: một phần đáng kể tình trạng tắc đường ở trung tâm không phải do người ta đang đi đâu đó, mà do người ta đang tìm chỗ để dừng.

Thứ hai, thiệt hại có tính lặp. Người lái xe đi làm ở trung tâm không mất mười lăm phút một lần, họ mất mười lăm phút mỗi ngày, hai mươi hai ngày mỗi tháng. Đây là lý do nhóm người đi làm cố định là phân khúc có giá trị vòng đời cao nhất và là nhóm cần được nhắm trước.

Thứ ba, đỗ sai quy định không phải hành vi chống đối mà là phương án cuối cùng khi mọi phương án khác đã thất bại. Điều này quan trọng về mặt chính sách: muốn giảm đỗ sai, tăng mức phạt là công cụ có giới hạn, còn cho người lái một chỗ đỗ hợp pháp mà họ tìm được trong hai phút là công cụ hiệu quả hơn. Đây chính là chỗ một nền tảng dữ liệu đóng góp vào mục tiêu quản lý nhà nước.

---

## 4. Hiện trạng bằng số

Bảng dưới đây chỉ giữ những con số có nguồn công khai. Chi tiết nguồn và mức độ tin cậy nằm ở [tài liệu 99](../99_reference/99_Sources_and_Assumptions.md). Những con số cần kiểm chứng lại từ nguồn chính thức trước khi nộp hồ sơ đã được đánh dấu.

| Chỉ số | Giá trị | Ý nghĩa với dự án |
|---|---|---|
| Ô tô đang lưu hành trên cả nước | Khoảng 6,8 triệu xe, số liệu tổng hợp năm 2026, cần kiểm chứng từ nguồn chính thức | Quy mô cầu, và tốc độ tăng cho thấy vấn đề sẽ nặng thêm |
| Tỷ lệ đất dành cho giao thông tại các đô thị lớn | Khoảng 6 tới 8 phần trăm, so với mức 15 tới 20 phần trăm của đô thị hiện đại | Không thể trông vào việc mở rộng hạ tầng trong ngắn hạn |
| Hệ thống bến bãi giữ xe tại Thành phố Hồ Chí Minh | Mới đạt khoảng 20 phần trăm quy hoạch | Khoảng trống giữa nhu cầu và cung được quy hoạch là rất lớn |
| Thu phí đỗ xe lòng đường Thành phố Hồ Chí Minh giai đoạn 2021 tới 2024 | Thu hơn 23,1 tỷ đồng, chi phí vận hành hơn 25,1 tỷ đồng, ngân sách bù lỗ khoảng 2 tỷ đồng | Cách thu thủ công không tự nuôi được chính nó |
| Số lượt xe không đóng phí đỗ trong cùng giai đoạn | Gần 363.000 lượt, thất thu hơn 7,25 tỷ đồng | Thất thu là do khâu ghi nhận, không phải do thiếu quy định |
| Chi phí phần mềm thu phí đỗ xe đang dùng | Gần 8 tỷ đồng, kèm nhiều lỗi về thanh toán, định vị và tìm bãi | Có ngân sách cho phần mềm, vấn đề là phần mềm không giải đúng nút thắt |
| Thí điểm thu phí đỗ xe qua thẻ thu phí không dừng từ tháng 01/2025 | Doanh thu ba tháng đầu 2025 hơn 1,3 tỷ đồng, gần gấp đôi cùng kỳ | Bằng chứng thực địa rằng tự động hoá khâu ghi nhận làm tăng thu ngay |
| Chi phí cảm biến đỗ xe gắn từng ô | Khoảng 300 tới 500 đô la Mỹ mỗi ô kể cả lắp đặt | Giải thích vì sao mô hình cảm biến không mở rộng được |
| Tỷ lệ thay thế của camera | Một camera có thể thay cho hàng chục tới hàng trăm cảm biến ô đỗ, tuỳ bố trí và tầm nhìn | Cơ sở kinh tế của lớp cảm nhận trong dự án này |
| Quy định phòng cháy cho khu để xe điện tại nhà chung cư | Hiệu lực từ 15/12/2025, yêu cầu bố trí khu riêng, camera giám sát 24 trên 24, báo cháy tự động, cảnh báo CO và HF | Biến phát hiện khói lửa sớm thành hạng mục tuân thủ có ngân sách và có thời hạn |
| Quyết định 502/QĐ-TTg ngày 28/03/2026 | Phương án kết nối, chia sẻ dữ liệu camera giám sát an ninh trật tự và điều hành giao thông với Cơ sở dữ liệu quốc gia về dân cư, chia sẻ với trung tâm điều hành đô thị thông minh | Đường đi chính danh để dữ liệu bãi đỗ trở thành dữ liệu công |
| Nghị định 119/2024/NĐ-CP | Quy định thanh toán điện tử giao thông đường bộ, tài khoản giao thông, cơ sở dữ liệu thanh toán | Hành lang cho thanh toán gắn với phương tiện |
| Luật Dữ liệu số 60/2024/QH15 và Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 | Hiệu lực lần lượt từ 01/07/2025 và 01/01/2026 | Khung bắt buộc phải tuân thủ khi xử lý biển số và hình ảnh trong bãi |

---

## 5. Tại sao các giải pháp đi trước thất bại

Việt Nam đã có ứng dụng tìm bãi đỗ từ nhiều năm trước. Việc phân tích vì sao họ chưa thành công không nhằm hạ thấp ai, mà để tránh lặp lại đúng những sai lầm đó.

### 5.1. Bốn nguyên nhân gốc

**Nguyên nhân một, dữ liệu chỗ trống dựa vào con người.** MyParking có mạng lưới bãi đối tác tại Hà Nội và Thành phố Hồ Chí Minh, nhưng bị phản ánh rằng dữ liệu chỗ trống nhiều khi không cập nhật kịp, dẫn tới việc người dùng đến nơi thì bãi đã hết chỗ. Đây không phải lỗi triển khai mà là lỗi thiết kế: nếu nguồn dữ liệu là một con người đang làm việc khác, dữ liệu sẽ luôn trễ vào đúng lúc cần chính xác nhất.

**Nguyên nhân hai, giải quyết bước cuối trước bước đầu.** Nhiều sản phẩm đầu tư mạnh vào thanh toán và ví điện tử, vì đó là phần dễ thấy và dễ đo. Nhưng thanh toán là bước cuối của hành trình. Nếu người lái xe không tin rằng đến nơi sẽ có chỗ, họ không bao giờ đi tới bước thanh toán. Thanh toán tiện lợi trên một dữ liệu không đáng tin là một cây cầu đẹp dẫn tới một bờ sông không có gì.

**Nguyên nhân ba, không giải quyết nỗi đau của phía cung.** Các nền tảng đến với chủ bãi bằng lời hứa về khách hàng mới. Với bãi trong trung tâm đang gần đầy vào ban ngày, lời hứa đó không đủ để đổi lấy việc thay đổi quy trình vận hành. Kết quả là mạng lưới mở rộng chậm, mật độ bãi trong từng khu vực thấp, người dùng mở ứng dụng lên thì bãi gần nhất cách hai ki lô mét, và họ bỏ ứng dụng.

**Nguyên nhân bốn, khâu ghi nhận vẫn thủ công nên tiền vẫn rơi.** Trường hợp thu phí đỗ xe lòng đường tại Thành phố Hồ Chí Minh là minh chứng rõ nhất. Có ứng dụng, có quy định, có nhân viên thu phí, nhưng gần 363.000 lượt xe không đóng phí trong bốn năm, thất thu hơn 7,25 tỷ đồng, và toàn bộ hoạt động thu phí lỗ khoảng 2 tỷ đồng sau khi trừ chi phí vận hành. Khi chuyển sang thu qua thẻ thu phí không dừng, tức là gắn việc thu tiền vào phương tiện thay vì vào lời khai của người lái, doanh thu tăng gần gấp đôi. Bài học rất sạch: cái gì không được máy ghi nhận thì cái đó sẽ rơi.

### 5.2. So sánh cách tiếp cận

| Điểm quyết định | Cách các giải pháp đi trước làm | Parking HUB làm khác |
|---|---|---|
| Nguồn dữ liệu chỗ trống | Chủ bãi nhập tay, người dùng báo | Camera AI đếm liên tục, hai nguồn kia chỉ để đối chiếu |
| Trạng thái được trả về | Trạng thái tại thời điểm tìm kiếm | Trạng thái dự đoán tại thời điểm người lái tới nơi, và dự báo cho các mốc tương lai |
| Cam kết với người dùng | Hiển thị thông tin, không cam kết | Giữ chỗ có ràng buộc hai chiều, có chính sách khi một trong hai bên không thực hiện |
| Lý do để chủ bãi tham gia | Hứa thêm khách hàng | Trước tiên là chống thất thu và an toàn cháy nổ, sau đó mới tới doanh thu từ giờ trống |
| Khâu ghi nhận vào ra | Vé giấy, thẻ từ, hoặc người dùng tự khai | Nhận diện biển số tự động, đối soát giữa lượt đã trả tiền và xe thực tế |
| Chiến lược mở rộng | Trải rộng nhiều khu vực để có nhiều điểm trên bản đồ | Chiếm mật độ từng khu vực trước, vì giá trị với người dùng phụ thuộc mật độ trong bán kính đi bộ |
| Quan hệ với nhà nước | Là nhà cung cấp phần mềm | Là nguồn dữ liệu giao thông tĩnh có thể chia sẻ theo chủ trương hiện hành |

---

## 6. Bảy câu chuyện người dùng

Bảy nhân vật dưới đây là chân dung tổng hợp, đại diện cho bảy nhóm nhu cầu khác nhau. Mỗi câu chuyện gồm hiện trạng, chi phí thật mà họ đang trả, và điều họ thực sự muốn. Chi phí thật là phần quan trọng nhất, vì đó là mức giá trần mà sản phẩm có thể định giá.

### 6.1. Anh Khoa, 34 tuổi, đi làm cố định ở Quận 1

**Hiện trạng.** Anh làm ở một toà nhà trên đường Nguyễn Thị Minh Khai. Hầm toà nhà ưu tiên cho khách thuê lớn, phần chỗ cho khách lẻ thường hết trước 08 giờ. Anh đã thử ba cách. Cách một là đi sớm hơn hai mươi phút để tranh chỗ trong hầm, tức là mất hai mươi phút mỗi ngày. Cách hai là gửi ở một bãi ngoài trời cách bảy trăm mét, nhưng ở đó xe phơi nắng cả ngày và có lần bị xước cửa mà không ai chịu trách nhiệm. Cách ba là đỗ tạm bên lề đường và chấp nhận rủi ro, đã bị xử phạt một lần.

**Chi phí thật.** Hai mươi phút mỗi ngày nhân hai mươi hai ngày là khoảng bảy giờ mỗi tháng. Cộng thêm chi phí bất định: một lần bị phạt, một lần xe bị xước, và cảm giác căng thẳng mỗi sáng.

**Điều anh thực sự muốn.** Không phải giá rẻ nhất. Anh muốn một chỗ chắc chắn có, ở khoảng cách đi bộ dưới bảy phút, có mái che, và không phải suy nghĩ về nó mỗi sáng. Anh sẵn sàng trả theo tháng để đổi lấy việc không phải nghĩ nữa.

**Giá trị của nhóm này với nền tảng.** Đây là nhóm tần suất cao và có thể chuyển sang gói tháng, tức là doanh thu định kỳ và dự đoán được. Đây cũng là nhóm sinh dữ liệu thói quen đều đặn nhất, nên là nhóm mà cá nhân hoá phát huy hiệu quả nhất.

### 6.2. Chị Hà, 41 tuổi, đưa con đi khám bệnh

**Hiện trạng.** Chị chở con đi khám tại một bệnh viện lớn, chưa từng đến bằng xe riêng. Bãi của bệnh viện quá tải từ sáng sớm. Chị vòng ba lượt quanh bệnh viện, mỗi lượt gặp một người vẫy tay chỉ vào chỗ đỗ không rõ hợp pháp hay không, giá thì nói bằng miệng. Cuối cùng chị gửi vào một bãi tự phát với giá 50.000 đồng, không có vé, và suốt buổi khám chị vừa lo cho con vừa lo cho xe.

**Chi phí thật.** Hai mươi lăm phút với một đứa trẻ đang mệt trên xe, một mức giá không biết là đúng hay bị nói quá, và toàn bộ sự bất an trong hai giờ sau đó.

**Điều chị thực sự muốn.** Sự chắc chắn tuyệt đối và giá minh bạch, ở một tình huống mà chị không có tâm trí để tối ưu. Chị đi tới bệnh viện đó có thể chỉ một lần trong năm, nên chị không cần cá nhân hoá, chị cần một câu trả lời đúng ngay lần đầu.

**Giá trị của nhóm này với nền tảng.** Tần suất thấp nhưng ý định rất cao và sẵn sàng trả phí tiện lợi. Nhóm này quyết định danh tiếng của sản phẩm, vì đây là nhóm kể lại trải nghiệm cho người khác. Các điểm đến của họ có tính tập trung cao: bệnh viện, sân bay, trung tâm hành chính, khu sự kiện, nên chỉ cần onboard đúng vài bãi quanh mỗi điểm đến là phục vụ được cả nhóm.

### 6.3. Anh Tuấn, 47 tuổi, quản lý bãi hầm 150 chỗ tại Bình Thạnh

**Hiện trạng.** Bãi thuộc một toà nhà văn phòng kết hợp căn hộ. Ban ngày lấp đầy khoảng tám mươi lăm phần trăm, ban đêm khoảng hai mươi phần trăm. Quản lý bằng thẻ từ và vé giấy cho khách lẻ, ba bảo vệ chia ba ca. Mỗi tháng anh gặp vài chuyện quen thuộc: khách mất thẻ và tranh luận về thời gian gửi, chênh lệch giữa tiền mặt thu được và số lượt ghi trên sổ mà không truy được vì đổi ca, và một nỗi lo lớn hơn là bãi có mười một xe điện sạc ban đêm trong khi hệ thống báo cháy của hầm là loại đầu báo trên trần.

**Chi phí thật.** Anh không biết chính xác thất thu bao nhiêu, và chính việc không biết là vấn đề. Về rủi ro cháy, anh biết rất rõ điều gì sẽ xảy ra nếu một xe cháy trong hầm kín vào hai giờ sáng.

**Điều anh thực sự muốn.** Theo đúng thứ tự: một, ngủ ngon về chuyện cháy nổ. Hai, một con số doanh thu không tranh chấp được. Ba, bán được những giờ ban đêm đang trống. Lưu ý rằng thứ ba là thứ nền tảng muốn bán, nhưng nó chỉ là ưu tiên thứ ba của anh. Đi vào bằng ưu tiên thứ ba là cách nhanh nhất để bị từ chối.

**Giá trị của nhóm này với nền tảng.** Đây là phân khúc xương sống: dung lượng lớn, tập trung, có ngân sách, có người chịu trách nhiệm rõ ràng để ký hợp đồng.

### 6.4. Ông Bảy, 62 tuổi, có sân nhà bốn chỗ tại Quận 3

**Hiện trạng.** Nhà ông có sân đủ đỗ bốn xe, hiện chỉ dùng một chỗ cho xe của con trai, xe này đi từ 07 giờ 30 tới 18 giờ. Vậy là bốn chỗ trống suốt ban ngày, ở một khu vực mà cách đó hai trăm mét là một toà nhà văn phòng luôn thiếu chỗ. Có người từng hỏi thuê tháng, ông từ chối vì ba lo lắng: không biết người lạ là ai, sợ xe đỗ chắn cổng lúc gia đình cần ra vào, và sợ nếu xe bị xước thì tranh chấp không có gì làm bằng.

**Chi phí thật.** Một tài sản có thể tạo ra thu nhập nhưng đang bằng không, chỉ vì không có ai đứng giữa để bảo đảm.

**Điều ông thực sự muốn.** Người thuê được xác thực danh tính, khung giờ rõ ràng và tôn trọng, có bằng chứng hình ảnh khi giao và nhận, tiền vào đều đặn mà không phải đi thu.

**Giá trị của nhóm này với nền tảng.** Đây là phần đuôi dài của cung, và là thứ mà không đối thủ nào tại Việt Nam đang khai thác. Ba đặc điểm khiến nó có giá trị chiến lược. Thứ nhất, nó nằm chính xác ở nơi bãi lớn không có, tức là trong lòng khu dân cư sát các điểm đến đông đúc. Thứ hai, nó không cần đầu tư hạ tầng, chỉ cần một chiếc điện thoại và một tấm biển. Thứ ba, nó tạo mật độ cho mạng lưới nhanh hơn bất kỳ cách nào khác, và mật độ chính là thứ quyết định giá trị với người lái xe. Đổi lại, nhóm này cần một cơ chế tin cậy chặt chẽ, vì một sự cố trong sân nhà người dân sẽ gây tổn hại uy tín lớn hơn nhiều so với sự cố trong bãi thương mại.

### 6.5. Ban quản trị một chung cư 400 căn tại khu vực đông dân

**Hiện trạng.** Hầm có 210 chỗ cho 400 căn hộ, nghĩa là luôn có tranh chấp. Từ khi cư dân bắt đầu mua xe điện, xuất hiện thêm hai vấn đề. Vấn đề thứ nhất là chỗ sạc không đủ và có tình trạng cắm dây kéo từ xa. Vấn đề thứ hai lớn hơn: quy định về khu để xe điện tại nhà chung cư có hiệu lực từ 15/12/2025 yêu cầu bố trí khu riêng, có camera giám sát 24 trên 24, hệ thống báo cháy tự động và thiết bị cảnh báo CO cùng HF. Ban quản trị phải trình cư dân một phương án, và họ chưa có phương án.

**Chi phí thật.** Rủi ro pháp lý và rủi ro trách nhiệm cá nhân của các thành viên ban quản trị, cộng với áp lực từ chính cư dân trong mỗi cuộc họp.

**Điều họ thực sự muốn.** Một phương án tuân thủ được, giải thích được trước cư dân, chi phí chia được cho quỹ bảo trì hoặc bù lại bằng nguồn thu từ chỗ trống ban ngày.

**Giá trị của nhóm này với nền tảng.** Đây là cửa vào có động lực mạnh nhất trong toàn bộ thị trường hiện nay, vì nó gắn với một thời hạn pháp lý. Bán một lớp phát hiện khói lửa sớm cho nhóm này dễ hơn nhiều so với bán một ứng dụng đỗ xe, và khi đã lắp thì dữ liệu chỗ trống của hầm đó thuộc về mạng lưới.

### 6.6. Chị Linh, quản lý đội 40 xe của một công ty dịch vụ

**Hiện trạng.** Bốn mươi xe hoạt động trong nội thành, tài xế tự tìm chỗ đỗ và tự trả tiền, sau đó nộp hoá đơn hoặc ghi vào sổ. Mỗi tháng chị nhận về một tập chi phí rời rạc, không đối soát được, và không biết xe nào đỗ ở đâu bao lâu. Ngoài ra chị không có cách nào biết một tài xế khai đỗ hai giờ trong khi thực tế đỗ bốn giờ hay ngược lại.

**Chi phí thật.** Chi phí đỗ xe không kiểm soát được, thời gian hành chính để đối soát, và không có dữ liệu để tối ưu lộ trình.

**Điều chị thực sự muốn.** Một hợp đồng, một hoá đơn, một báo cáo theo xe và theo tài xế, giá ưu đãi theo khối lượng, và mạng lưới bãi phủ đúng vùng hoạt động của đội xe.

**Giá trị của nhóm này với nền tảng.** Doanh thu lớn, ổn định, ít biến động theo mùa, và quan trọng hơn là nhóm này lấp giờ thấp điểm rất tốt vì lịch hoạt động của họ khác lịch của người đi làm.

### 6.7. Cán bộ quản lý giao thông đô thị của một địa phương

**Hiện trạng.** Trên bàn là ba loại việc. Một, các tuyến phố có tình trạng đỗ xe sai quy định lặp lại, xử phạt thì vẫn tái diễn. Hai, việc thu phí đỗ xe lòng đường không đạt hiệu quả tài chính như kỳ vọng và có thất thu. Ba, phải góp ý cho quy hoạch bãi đỗ mới nhưng dữ liệu về nhu cầu thực chỉ có từ khảo sát định kỳ.

**Chi phí thật.** Ra quyết định trong điều kiện thiếu dữ liệu, và không có cách nào đo hiệu quả của quyết định đã ra.

**Điều họ thực sự muốn.** Bức tranh theo giờ và theo khu vực về cung, cầu và mức lấp đầy. Khả năng biết trước điểm nghẽn thay vì biết sau khi có phản ánh. Và một cơ chế chia sẻ dữ liệu đúng quy định pháp luật, không tạo thêm rủi ro về bảo vệ dữ liệu cá nhân.

**Giá trị của nhóm này với nền tảng.** Không phải nhóm trả tiền chính, nhưng là nhóm quyết định tính chính danh, quyết định khả năng tiếp cận bãi công cộng, và là nhóm làm cho dự án đúng nghĩa là một giải pháp cho xã hội số chứ không chỉ là một ứng dụng thương mại.

### 6.8. Bảng tổng hợp bảy nhóm

| Nhóm | Tần suất | Nhạy cảm về giá | Điều họ mua thực sự | Doanh thu chính từ họ |
|---|---|---|---|---|
| Người đi làm cố định | Rất cao | Trung bình | Sự chắc chắn hàng ngày, hết phải nghĩ | Gói tháng |
| Người đi việc đột xuất | Thấp | Thấp | Đúng ngay lần đầu, giá minh bạch | Phí mỗi lượt, phí giữ chỗ |
| Chủ bãi có hệ thống | Không áp dụng | Cao, xét theo hoàn vốn | Chống thất thu và an toàn cháy nổ | Phí thiết bị và phần mềm, chia doanh thu |
| Chủ chỗ đỗ nhỏ | Không áp dụng | Cao | Sự bảo đảm và bằng chứng | Chia doanh thu tỷ lệ cao hơn |
| Ban quản trị chung cư | Không áp dụng | Trung bình | Tuân thủ quy định và an toàn cho cư dân | Phí thiết bị và phần mềm theo hầm |
| Doanh nghiệp có đội xe | Cao | Trung bình | Kiểm soát chi phí và đối soát | Hợp đồng tháng theo khối lượng |
| Cơ quan quản lý | Không áp dụng | Không áp dụng | Dữ liệu để điều hành và quy hoạch | Không thu, hoặc hợp tác theo đề án |

---

## 7. Bản đồ các bên liên quan và động lực

Một mạng lưới hai phía chỉ chạy được khi động lực của tất cả các bên cùng hướng. Bảng dưới đây là công cụ kiểm tra: nếu một bên nào không có lý do rõ ràng để ở lại, thì đó là chỗ mô hình sẽ vỡ.

| Bên | Lý do tham gia | Lý do có thể rời đi | Cơ chế giữ |
|---|---|---|---|
| Người lái xe | Tiết kiệm thời gian, có chỗ chắc chắn | Một lần đến nơi mà không có chỗ | Cam kết giữ chỗ với chính sách bù đắp rõ ràng, và độ chính xác dữ liệu ở mức cao |
| Chủ bãi lớn | Chống thất thu, an toàn cháy nổ, doanh thu giờ trống | Cảm thấy nền tảng lấy quá nhiều, hoặc tự làm được | Thiết bị và phần mềm gắn với vận hành hàng ngày, dữ liệu lịch sử tích luỹ trong hệ thống, giá trị tăng theo thời gian sử dụng |
| Chủ chỗ đỗ nhỏ | Thu nhập từ tài sản đang để không | Một sự cố với người thuê | Xác thực người thuê, bằng chứng hình ảnh khi giao và nhận, quy trình xử lý tranh chấp, cơ chế bảo đảm |
| Ban quản trị chung cư | Tuân thủ quy định, an toàn cho cư dân | Cư dân phản đối việc người ngoài vào hầm | Thiết kế quyền ra vào theo khung giờ và theo khu, ưu tiên cư dân, minh bạch nguồn thu về quỹ chung |
| Doanh nghiệp đội xe | Kiểm soát chi phí, đối soát tự động | Mạng lưới chưa phủ đủ vùng hoạt động | Ưu tiên onboard bãi theo bản đồ hoạt động của các đội xe đã ký |
| Cơ quan quản lý | Dữ liệu điều hành, giảm đỗ sai, tăng thu phí công | Lo ngại về bảo vệ dữ liệu cá nhân | Chia sẻ dữ liệu tổng hợp phi định danh theo đúng quy định, có kiểm toán truy cập, không chia sẻ dữ liệu cá nhân ngoài phạm vi pháp luật cho phép |
| Nền tảng | Doanh thu và vị thế hạ tầng | Không đạt mật độ ở khu vực nào | Chiến lược chiếm mật độ từng khu vực, và ưu tiên phân khúc có động lực mạnh nhất trước |

Điểm cần nói thẳng: mâu thuẫn có thật nằm giữa cư dân chung cư và người ngoài vào gửi xe. Cư dân sẽ phản đối nếu cảm thấy chỗ của mình bị chia sẻ. Cách xử lý không phải thuyết phục bằng lời mà bằng thiết kế: chỉ mở bán phần dung lượng thực sự trống theo dữ liệu camera, mở theo khung giờ mà cư dân không dùng, giới hạn khu vực, ưu tiên tuyệt đối cho cư dân khi có xung đột, và toàn bộ nguồn thu được minh bạch về quỹ chung của toà nhà. Khi cư dân thấy khoản thu đó làm giảm phí quản lý của chính họ, phản đối sẽ chuyển thành ủng hộ.

---

## 8. Kết luận: đây là bài toán dữ liệu, không phải bài toán ứng dụng

Ba kết luận để chuyển sang thiết kế sản phẩm.

**Kết luận một.** Việt Nam không thiếu ứng dụng đỗ xe, mà thiếu dữ liệu trạng thái đáng tin để những ứng dụng đó hoạt động. Cho nên chỗ đầu tư đúng là lớp cảm nhận, và đó là lý do bốn model thị giác máy tính là trung tâm của dự án chứ không phải phần thêm vào.

**Kết luận hai.** Muốn có dữ liệu, phải có chủ bãi đồng ý. Muốn chủ bãi đồng ý, phải trả tiền cho họ bằng thứ họ đang mất, tức là thất thu và rủi ro cháy nổ, chứ không phải bằng lời hứa về khách hàng mới. Thứ tự này là thứ tự sống còn của mô hình.

**Kết luận ba.** Khi đã có dữ liệu trạng thái đáng tin trên một mật độ bãi đủ dày trong một khu vực, thì mọi giá trị khác đều mở ra gần như tự động: gợi ý theo điểm đến, dự báo tương lai, đặt chỗ nhiều ngày, cá nhân hoá theo thói quen, định giá theo nhu cầu, hợp đồng đội xe, và bản đồ giao thông tĩnh cho cơ quan quản lý. Không có dữ liệu thì không có gì trong danh sách đó tồn tại được.

Tài liệu tiếp theo trình bày các tính năng theo đúng thứ tự này: [03. Tính năng sản phẩm](03_Product_Features.md).
