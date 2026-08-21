# 04. Mô hình kinh doanh

Tiền đến từ đâu, ai trả, trả bao nhiêu, và bao lâu thì tự nuôi được

Phiên bản: 1.0
Ngày: 21/08/2026
Tài liệu liên quan: [02. Phân tích bài toán](../01_strategy-product/02_Problem_Deep_Dive.md), [05. Playbook onboard bãi đỗ](05_Onboarding_Playbook.md)

> Lưu ý quan trọng về các con số trong tài liệu này. Toàn bộ số liệu tài chính dưới đây là mô hình minh hoạ, xây từ các giả định được nêu rõ kèm theo, nhằm kiểm tra xem mô hình kinh doanh có logic hay không. Chúng không phải dự báo và không phải cam kết. Mọi giả định cần được kiểm chứng bằng dữ liệu thực tại các bãi thử nghiệm đầu tiên, và bảng tổng hợp giả định nằm ở [tài liệu 99](../99_reference/99_Sources_and_Assumptions.md).

---

## Mục lục

1. [Nguyên tắc nền tảng của mô hình](#1-nguyên-tắc-nền-tảng-của-mô-hình)
2. [Bốn nhóm khách hàng trả tiền](#2-bốn-nhóm-khách-hàng-trả-tiền)
3. [Các luồng doanh thu](#3-các-luồng-doanh-thu)
4. [Định giá](#4-định-giá)
5. [Kinh tế đơn vị theo ba loại bãi](#5-kinh-tế-đơn-vị-theo-ba-loại-bãi)
6. [Kinh tế phía người dùng](#6-kinh-tế-phía-người-dùng)
7. [Đường tới điểm tự nuôi được](#7-đường-tới-điểm-tự-nuôi-được)
8. [Vì sao thu được tiền trong khi các bên đi trước không thu được](#8-vì-sao-thu-được-tiền-trong-khi-các-bên-đi-trước-không-thu-được)
9. [Rủi ro của mô hình và cách xử lý](#9-rủi-ro-của-mô-hình-và-cách-xử-lý)
10. [Tầm nhìn doanh thu dài hạn](#10-tầm-nhìn-doanh-thu-dài-hạn)

---

## 1. Nguyên tắc nền tảng của mô hình

Bốn nguyên tắc dưới đây quyết định toàn bộ cấu trúc doanh thu. Chúng được rút ra từ việc phân tích lý do các nền tảng đỗ xe trước đó không thu được tiền, xem mục 5 của [tài liệu 02](../01_strategy-product/02_Problem_Deep_Dive.md).

**Nguyên tắc một, chỉ thu trên phần giá trị mình tạo ra thêm.** Nền tảng không lấy phần trăm trên doanh thu vốn đã có của bãi. Một bãi đang thu 180 triệu mỗi tháng trước khi tham gia thì phần 180 triệu đó vẫn nguyên của họ. Nền tảng chỉ chia phần doanh thu mới đến từ mạng lưới, cộng với phí phần mềm và thiết bị. Đây là điều làm cho cuộc đàm phán với chủ bãi trở nên dễ, vì họ không phải bỏ ra cái gì đang có để đổi lấy một lời hứa.

**Nguyên tắc hai, doanh thu đầu tiên không được phụ thuộc vào việc có người dùng.** Nếu mô hình chỉ kiếm tiền từ hoa hồng trên lượt đặt chỗ, thì trong ba tháng đầu khi chưa có người dùng, nền tảng không có doanh thu và chủ bãi không thấy giá trị. Vì vậy phải có một dòng doanh thu chạy ngay từ tháng đầu, độc lập với lưu lượng người dùng. Dòng đó là phần mềm vận hành và an toàn bán cho chủ bãi: ghi nhận vào ra tự động, chống thất thu, phát hiện khói lửa sớm. Đây là điểm khác biệt cấu trúc so với mô hình sàn thuần túy.

**Nguyên tắc ba, hai bên trả tiền cho hai thứ khác nhau.** Chủ bãi trả cho vận hành và an toàn. Người lái xe trả cho sự chắc chắn và tiện lợi. Không cố bán cùng một câu chuyện cho cả hai.

**Nguyên tắc bốn, giảm giá chỉ được dùng để bán dung lượng đang trống.** Chi tiết ở mục 4.5 của [tài liệu 03](../01_strategy-product/03_Product_Features.md). Hệ quả tài chính: chi phí khuyến mại của nền tảng có trần rõ ràng, vì nó luôn nằm trong phần biên mà chủ bãi đã đồng ý cho khung giờ thấp điểm, chứ không phải khoản trợ giá lấy từ vốn.

---

## 2. Bốn nhóm khách hàng trả tiền

| Nhóm | Họ mua gì | Cơ chế thu | Bắt đầu từ khi nào |
|---|---|---|---|
| Chủ bãi và ban quản lý toà nhà | Phần mềm vận hành, ghi nhận vào ra tự động, phát hiện khói lửa sớm, công cụ bán giờ trống | Phí thiết bị và phần mềm theo tháng, cộng chia doanh thu trên phần doanh thu mới | Ngay từ bãi đầu tiên, không cần chờ có người dùng |
| Người lái xe cá nhân | Sự chắc chắn về chỗ đỗ, tiện lợi khi vào ra và thanh toán | Phí giữ chỗ theo lượt, gói tháng, phí tiện lợi trong một số trường hợp | Từ khi mạng lưới đạt mật độ tối thiểu trong một khu vực |
| Doanh nghiệp có đội xe | Kiểm soát chi phí đỗ xe, đối soát tập trung, phủ mạng lưới theo vùng hoạt động | Hợp đồng theo tháng, phí quản lý theo đầu xe, chiết khấu theo khối lượng | Sau khi mạng lưới phủ đủ vùng hoạt động của khách |
| Chủ chỗ đỗ nhỏ | Kênh cho thuê có bảo đảm, không phải tự tìm khách và tự thu tiền | Hoa hồng trên doanh thu cho thuê, ở mức cao hơn vì nền tảng làm toàn bộ | Ngay khi có nhu cầu trong khu vực đó |

Cơ quan quản lý nhà nước không nằm trong danh sách nhóm trả tiền ở giai đoạn đầu. Quan hệ với cơ quan quản lý là quan hệ chia sẻ dữ liệu và hợp tác theo đề án, tạo tính chính danh và khả năng tiếp cận bãi công cộng. Nếu về sau có hình thức hợp tác có thu, thì đó là kết quả của việc đã chứng minh giá trị, không phải giả định của mô hình.

---

## 3. Các luồng doanh thu

### 3.1. Bảng tổng hợp

| Luồng | Cơ chế | Ai trả | Đặc điểm | Thời điểm bật |
|---|---|---|---|---|
| L1. Phần mềm và thiết bị vận hành | Phí theo tháng tính theo quy mô bãi và số camera, gồm đếm chỗ trống, nhận diện biển số, bảng điều khiển, ứng dụng bảo vệ | Chủ bãi | Doanh thu định kỳ, không phụ thuộc lưu lượng người dùng | Tháng đầu tiên |
| L2. Mô đun an toàn cháy nổ | Phí theo tháng tính theo số camera được bật phát hiện khói lửa | Chủ bãi, ban quản trị chung cư | Doanh thu định kỳ, gắn với nghĩa vụ tuân thủ nên ít bị cắt khi khó khăn | Tháng đầu tiên |
| L3. Chia doanh thu trên lượt mới | Phần trăm trên doanh thu đến từ mạng lưới, không tính trên doanh thu vốn có của bãi | Chủ bãi, trích từ doanh thu mới | Tăng theo mật độ mạng lưới và số người dùng | Khi có người dùng đầu tiên trong khu vực |
| L4. Phí giữ chỗ | Một khoản nhỏ cho mỗi lượt giữ chỗ, có thể trừ vào tiền gửi | Người lái xe | Đơn giá nhỏ, số lượng lớn, đồng thời có tác dụng giảm tỷ lệ giữ chỗ rồi không đến | Cùng lúc với tính năng giữ chỗ |
| L5. Gói tháng cho người lái xe | Gói ngày làm việc, gói qua đêm, gói theo khu vực, bán qua nền tảng và chia với bãi | Người lái xe | Doanh thu định kỳ, giữ người dùng rất mạnh | Sau khi mật độ bãi trong khu vực đủ |
| L6. Hợp đồng đội xe | Phí quản lý theo đầu xe cộng doanh thu đỗ xe theo khối lượng | Doanh nghiệp | Giá trị hợp đồng lớn, ít biến động, lấp giờ thấp điểm tốt | Sau khi phủ được vùng hoạt động của khách |
| L7. Hoa hồng chỗ đỗ nhỏ | Phần trăm cao hơn trên doanh thu cho thuê chỗ của hộ dân | Chủ chỗ nhỏ, trích từ doanh thu | Không cần đầu tư thiết bị, biên cao, mở rộng nhanh | Khi có nhu cầu trong khu vực |
| L8. Dịch vụ kèm theo trong bãi | Chia doanh thu với các dịch vụ bán cho xe đang gửi, ví dụ rửa xe, sạc điện, bảo dưỡng cơ bản | Đơn vị cung cấp dịch vụ | Biên cao, tận dụng thời gian xe đang đứng yên | Sau khi có lưu lượng ổn định |

Về L8, cần nói thêm một điều có ý nghĩa chiến lược. Một chiếc xe đang gửi trong bãi tám tiếng là một chiếc xe đứng yên tám tiếng, và đó là thời điểm lý tưởng nhất để thực hiện bất kỳ dịch vụ nào cho xe. Mạng lưới bãi đỗ và mạng lưới điểm dịch vụ chăm sóc xe là hai mặt của cùng một bài toán, và đội đã có kinh nghiệm cùng phần lõi kỹ thuật cho việc điều phối mạng lưới điểm dịch vụ. Về dài hạn, bãi đỗ là điểm tiếp xúc tự nhiên nhất với chiếc xe, và điều đó mở ra một hướng phát triển rộng hơn nhiều so với việc chỉ bán chỗ đỗ. Tuy nhiên đây là chuyện của giai đoạn sau, không nên đưa vào mô hình cơ sở.

### 3.2. Thứ tự bật các luồng, và vì sao thứ tự đó quan trọng

```
Tháng 1 tới 3     L1, L2            Bán cho chủ bãi. Doanh thu chạy trước khi có người dùng.
                                    Đồng thời tạo ra dữ liệu chỗ trống, tức là tạo ra sản phẩm.

Tháng 3 tới 6     L3, L4, L7        Khi mật độ bãi trong khu vực đủ để người dùng luôn có
                                    lựa chọn gần, phía cầu bắt đầu tạo doanh thu.

Tháng 6 tới 12    L5, L6            Khi đã có dữ liệu dự báo đủ tốt để cam kết dài hạn,
                                    mở gói tháng và hợp đồng đội xe.

Sau tháng 12      L8                Khi lưu lượng đủ lớn để dịch vụ kèm theo có ý nghĩa.
```

Thứ tự này giải quyết vấn đề khởi động của mọi mạng lưới hai phía. Thông thường, phía cung không tham gia vì chưa có cầu, và phía cầu không tham gia vì chưa có cung. Parking HUB thoát vòng đó bằng cách bán cho phía cung một sản phẩm có giá trị độc lập với phía cầu. Nói cách khác, chủ bãi tham gia không phải để chờ khách mới, mà để chống thất thu và để an toàn. Khách mới là phần thưởng đến sau.

---

## 4. Định giá

Các mức giá dưới đây là mức đề xuất khởi điểm để thảo luận, cần kiểm chứng qua đàm phán thực tế với năm tới mười bãi đầu tiên.

### 4.1. Phía chủ bãi

| Gói | Đối tượng | Phạm vi | Mức đề xuất mỗi tháng |
|---|---|---|---|
| Cơ bản | Bãi cấp 1 và cấp 2, chưa lắp thiết bị | Có mặt trong danh mục, nhận đặt chỗ theo lịch, bảng điều khiển đơn giản | Miễn phí, chỉ chia doanh thu trên lượt mới |
| Vận hành | Bãi cấp 3, có camera đếm chỗ và nhận diện biển số | Toàn bộ L1: đếm chỗ trống, ghi nhận vào ra, đối soát, bảng điều khiển, ứng dụng bảo vệ | Từ 1,5 triệu tới 3,5 triệu đồng tuỳ quy mô bãi và số camera |
| An toàn | Bãi kín, hầm chung cư, khu để xe điện | Mô đun phát hiện khói lửa sớm, kênh cảnh báo nhiều cấp, lưu bằng chứng | Từ 300 nghìn tới 500 nghìn đồng mỗi camera được bật |
| Đầy đủ | Bãi cấp 4 | Gói Vận hành cộng gói An toàn cộng công cụ định giá và bán gói tháng | Giá gộp có chiết khấu |

Về thiết bị, có hai lựa chọn và nên cho chủ bãi chọn:

Lựa chọn một, chủ bãi mua thiết bị. Chi phí một lần, phù hợp với toà nhà có ngân sách đầu tư và muốn ghi tài sản.
Lựa chọn hai, nền tảng cho thuê thiết bị, tính vào phí tháng. Rào cản ban đầu bằng không, nhưng phí tháng cao hơn, và nền tảng chịu chi phí vốn.

Trong giai đoạn đầu nên nghiêng về lựa chọn hai cho những bãi đầu tiên, vì mục tiêu giai đoạn đó là có bãi để chứng minh, không phải tối ưu dòng tiền. Từ giai đoạn mở rộng thì chuyển dần sang lựa chọn một để không bị vốn hoá thiết bị chặn tốc độ.

Về chia doanh thu trên lượt mới, mức đề xuất từ 10 tới 15 phần trăm. Mức này thấp hơn các sàn đỗ xe quốc tế, nơi phần chia thường ở khoảng 15 tới 30 phần trăm mỗi lượt đặt chỗ. Có hai lý do chọn mức thấp hơn: sức chi trả của thị trường Việt Nam thấp hơn, và nền tảng đã có doanh thu từ L1 và L2 nên không cần dựa hết vào phần chia.

### 4.2. Phía người lái xe

| Sản phẩm | Mức đề xuất | Ghi chú |
|---|---|---|
| Tìm kiếm và xem thông tin | Miễn phí | Không bao giờ thu tiền cho việc xem thông tin, vì đó là thứ tạo thói quen |
| Giữ chỗ theo lượt | Từ 5 nghìn tới 10 nghìn đồng, được trừ vào tiền gửi khi tới đúng hẹn | Khoản này vừa là doanh thu vừa là cơ chế giảm giữ chỗ rồi không đến |
| Gói ngày làm việc theo tháng | Theo giá của bãi, thấp hơn tổng cộng dồn từng lượt từ 20 tới 30 phần trăm | Nền tảng chia với bãi, tỷ lệ chia thấp hơn so với lượt lẻ vì đây là doanh thu chắc chắn cho bãi |
| Gói qua đêm theo tháng | Theo giá của bãi cho khung giờ thấp điểm | Đây là sản phẩm bán dung lượng vốn đang trống, nên biên rộng |
| Phí tiện lợi khi vào ra tự động | Miễn phí | Không thu, vì đây là tính năng làm người dùng ở lại |

Nguyên tắc: không thu tiền của người lái xe cho những gì họ vốn nhận miễn phí ở nơi khác. Chỉ thu cho hai thứ mà nơi khác không có, đó là sự chắc chắn về chỗ và cam kết dài hạn theo gói.

---

## 5. Kinh tế đơn vị theo ba loại bãi

Mục này kiểm tra xem mỗi bãi tham gia mạng lưới có tạo ra biên đóng góp dương hay không. Đây là câu hỏi quan trọng nhất của mô hình, vì nếu một bãi không tự có lãi thì càng nhiều bãi càng lỗ nặng.

### 5.1. Trường hợp A: hầm toà nhà 150 chỗ ở khu vực trung tâm

```
GIẢ ĐỊNH VỀ BÃI
  Dung lượng                                150 chỗ
  Lấp đầy ban ngày trước khi tham gia       khoảng 85 phần trăm
  Lấp đầy từ 22 giờ tới 06 giờ              khoảng 20 phần trăm
  Doanh thu hiện tại của bãi                khoảng 180 triệu đồng mỗi tháng
                                            (vé tháng và khách lẻ)

GIÁ TRỊ TẠO RA THÊM CHO CHỦ BÃI, MỖI THÁNG
  Thu hồi thất thu nhờ ghi nhận tự động     khoảng 3 triệu
    (giả định 5 phần trăm doanh thu khách lẻ đang bị rơi)
  Doanh thu mới từ gói gửi qua đêm          khoảng 22 triệu
    (giả định bán được 25 suất, giá 900 nghìn mỗi suất mỗi tháng)
  Doanh thu mới từ lượt lẻ qua nền tảng     khoảng 10 triệu
    (giả định 8 lượt mỗi ngày, 50 nghìn mỗi lượt, 26 ngày)
  Tổng giá trị thêm                         khoảng 35 triệu

CHỦ BÃI TRẢ CHO NỀN TẢNG, MỖI THÁNG
  Gói Vận hành                              3,0 triệu
  Gói An toàn, 4 camera                     1,6 triệu
  Chia doanh thu 12 phần trăm trên 32 triệu  3,8 triệu
  Tổng                                      khoảng 8,4 triệu

KẾT QUẢ VỚI CHỦ BÃI
  Nhận thêm khoảng 35 triệu, trả khoảng 8,4 triệu
  Lợi ích ròng khoảng 26 triệu mỗi tháng
  Chưa tính giá trị của việc giảm rủi ro cháy nổ và giảm tranh chấp,
  là những khoản khó quy ra tiền nhưng có trọng lượng lớn trong quyết định

CHI PHÍ CỦA NỀN TẢNG CHO BÃI NÀY, MỖI THÁNG
  Khấu hao thiết bị                         0,8 triệu
    (giả định thiết bị biên và camera bổ sung khoảng 30 triệu, khấu hao 36 tháng)
  Hạ tầng máy chủ và lưu trữ                0,3 triệu
  Chi phí hỗ trợ và bảo trì phân bổ         0,6 triệu
  Tổng                                      khoảng 1,7 triệu

BIÊN ĐÓNG GÓP CỦA MỘT BÃI LOẠI A          khoảng 6,7 triệu đồng mỗi tháng
CHI PHÍ ĐƯA BÃI LÊN HỆ THỐNG               khoảng 8 tới 15 triệu đồng một lần
                                            (khảo sát, lắp đặt, hiệu chuẩn, đào tạo)
THỜI GIAN HOÀN CHI PHÍ ONBOARD              khoảng 2 tháng
```

### 5.2. Trường hợp B: bãi ngoài trời 60 chỗ ở khu vực ven trung tâm

```
GIẢ ĐỊNH VỀ BÃI
  Dung lượng                                60 chỗ
  Lấp đầy trung bình                        khoảng 55 phần trăm
  Doanh thu hiện tại                        khoảng 45 triệu đồng mỗi tháng

GIÁ TRỊ TẠO RA THÊM, MỖI THÁNG
  Doanh thu mới từ lượt lẻ qua nền tảng     khoảng 6 triệu
  Doanh thu mới từ vé tháng qua nền tảng    khoảng 6 triệu
  Thu hồi thất thu                          khoảng 1 triệu
  Tổng                                      khoảng 13 triệu

CHỦ BÃI TRẢ, MỖI THÁNG
  Gói Vận hành                              1,5 triệu
  Chia doanh thu 12 phần trăm trên 12 triệu  1,4 triệu
  Tổng                                      khoảng 2,9 triệu

CHI PHÍ CỦA NỀN TẢNG, MỖI THÁNG
  Khấu hao thiết bị                         0,6 triệu
    (giả định khoảng 20 triệu, khấu hao 36 tháng)
  Hạ tầng và hỗ trợ                         0,4 triệu
  Tổng                                      khoảng 1,0 triệu

BIÊN ĐÓNG GÓP CỦA MỘT BÃI LOẠI B          khoảng 1,9 triệu đồng mỗi tháng
```

Bãi loại B có biên mỏng hơn nhiều so với loại A. Điều này dẫn tới một kết luận về chiến lược: bãi ngoài trời nhỏ không nên là mục tiêu chính của lực lượng bán hàng có chi phí cao. Chúng nên được đưa lên hệ thống bằng cách tự đăng ký với gói thiết bị tối giản, hoặc chỉ ở cấp 1 và cấp 2 để tạo mật độ bản đồ, và chỉ nâng lên cấp 3 khi lưu lượng thực tế đủ để biện minh cho thiết bị.

### 5.3. Trường hợp C: chỗ đỗ nhỏ của hộ dân, bốn chỗ

```
GIẢ ĐỊNH
  Dung lượng cho thuê                       3 chỗ, khung giờ ban ngày
  Giá cho thuê theo tháng                   1 triệu đồng mỗi chỗ
  Doanh thu cho thuê                        3 triệu đồng mỗi tháng
  Thiết bị                                  không có

NỀN TẢNG THU
  Hoa hồng 20 phần trăm                     0,6 triệu đồng mỗi tháng

CHI PHÍ CỦA NỀN TẢNG
  Hạ tầng và hỗ trợ                         khoảng 0,1 triệu

BIÊN ĐÓNG GÓP CỦA MỘT CHỖ ĐỖ LOẠI C       khoảng 0,5 triệu đồng mỗi tháng
CHI PHÍ ĐƯA LÊN HỆ THỐNG                   gần bằng không nếu tự đăng ký
```

Loại C có biên tuyệt đối nhỏ nhưng tỷ suất rất cao và chi phí đưa lên gần bằng không, nên nó là công cụ tăng mật độ mạng lưới hiệu quả nhất về mặt vốn. Một trăm chỗ đỗ loại C trong một quận có thể tạo ra mật độ tương đương một bãi lớn, mà không cần đầu tư thiết bị nào.

### 5.4. So sánh ba loại và hàm ý chiến lược

| Loại | Biên đóng góp mỗi tháng | Chi phí đưa lên | Vai trò trong mạng lưới |
|---|---|---|---|
| A, hầm lớn | Khoảng 6,7 triệu | 8 tới 15 triệu | Trụ cột doanh thu, và là nơi dữ liệu chất lượng cao nhất |
| B, bãi ngoài trời trung bình | Khoảng 1,9 triệu | 5 tới 10 triệu | Bổ sung dung lượng, nên đưa lên bằng kênh tự đăng ký |
| C, chỗ nhỏ hộ dân | Khoảng 0,5 triệu | Gần bằng không | Tạo mật độ, phủ nơi bãi lớn không có, gần như không tốn vốn |

Kết luận về ưu tiên nguồn lực: đội bán hàng tập trung vào loại A, đặc biệt là hầm chung cư và toà nhà đang có nghĩa vụ tuân thủ quy định phòng cháy, vì đó là nơi vừa có biên cao vừa có động lực mạnh nhất. Loại B và C mở rộng bằng sản phẩm tự đăng ký và bằng lan truyền, không tiêu tốn nguồn lực bán hàng.

---

## 6. Kinh tế phía người dùng

### 6.1. Chi phí thu hút một người dùng

Đây là chỗ Parking HUB có lợi thế cấu trúc mà một ứng dụng thuần túy không có: kênh thu hút người dùng rẻ nhất chính là các bãi đã tham gia mạng lưới. Người đang đứng ở cổng một bãi là người đang có nhu cầu đỗ xe ngay lúc đó, nên tỷ lệ chuyển đổi từ kênh này cao hơn nhiều so với quảng cáo.

| Kênh | Cách làm | Đặc điểm chi phí |
|---|---|---|
| Tại bãi đã tham gia | Mã quét tại cổng và tại quầy bảo vệ, bảo vệ hướng dẫn, ưu đãi cho lượt đầu | Chi phí gần bằng không, đúng ngữ cảnh, tỷ lệ chuyển đổi cao nhất |
| Từ hầm chung cư đã tham gia | Thông báo tới cư dân qua ban quản trị | Chi phí gần bằng không, và đây là nhóm có nhu cầu lặp lại hàng ngày |
| Doanh nghiệp có đội xe | Bán hàng trực tiếp, một hợp đồng mang theo nhiều người dùng | Chi phí trên mỗi người dùng thấp vì đi theo lô |
| Lan truyền theo nhóm | Người dùng trong cùng toà nhà văn phòng giới thiệu nhau | Chi phí thấp, và có tính tập trung địa lý nên củng cố mật độ |
| Quảng cáo trả tiền | Chỉ dùng khi đã có mật độ bãi trong khu vực đó | Chi phí cao nhất, chỉ nên dùng để tăng tốc chỗ đã sẵn sàng |

Nguyên tắc: không chi tiền quảng cáo cho một khu vực mà mạng lưới chưa đủ mật độ. Người dùng đến từ quảng cáo, mở ứng dụng, thấy bãi gần nhất cách hai ki lô mét, và rời đi vĩnh viễn. Đây là cách đốt tiền nhanh nhất và cũng là sai lầm phổ biến nhất trong mô hình này.

### 6.2. Giá trị vòng đời của một người dùng

```
Người dùng loại một, đi làm cố định:
  Gói ngày làm việc, giá bãi khoảng 2 triệu đồng mỗi tháng
  Nền tảng chia khoảng 8 phần trăm                    160 nghìn mỗi tháng
  Giả định gắn bó 12 tháng                            khoảng 1,9 triệu đồng
  Cộng doanh thu từ các lượt gửi ngoài giờ làm        khoảng 0,3 triệu
  Giá trị vòng đời ước tính                           khoảng 2,2 triệu đồng

Người dùng loại hai, đi việc đột xuất:
  Khoảng 2 lượt mỗi tháng, phí giữ chỗ và chia doanh thu
  Nền tảng thu khoảng 15 nghìn mỗi lượt                30 nghìn mỗi tháng
  Giả định gắn bó 18 tháng                            khoảng 0,5 triệu đồng
```

Hai con số này giải thích vì sao nhóm đi làm cố định là nhóm phải chiếm được trước, dù nhóm đi việc đột xuất có số lượng lớn hơn. Nó cũng giải thích vì sao chiến lược onboard nên nhắm vào các hầm toà nhà văn phòng và hầm chung cư quanh khu vực làm việc, thay vì trải rộng theo bản đồ.

---

## 7. Đường tới điểm tự nuôi được

### 7.1. Cấu trúc chi phí cố định giai đoạn đầu

```
GIẢ ĐỊNH CHI PHÍ CỐ ĐỊNH MỖI THÁNG, GIAI ĐOẠN XÂY DỰNG
  Đội ngũ 8 người                           khoảng 200 triệu đồng
    (kỹ thuật, thị giác máy tính, sản phẩm, vận hành thực địa, kinh doanh)
  Hạ tầng máy chủ và dịch vụ                khoảng 15 triệu
  Chi phí vận hành khác                     khoảng 15 triệu
  Tổng                                      khoảng 230 triệu đồng mỗi tháng
```

### 7.2. Số bãi cần để chi phí cố định được trang trải

```
MỘT TỔ HỢP MẠNG LƯỚI ĐẠT ĐIỂM TRANG TRẢI CHI PHÍ CỐ ĐỊNH

  20 bãi loại A   x 6,7 triệu   =  134 triệu
  30 bãi loại B   x 1,9 triệu   =   57 triệu
  100 chỗ loại C  x 0,5 triệu   =   50 triệu
                                  -----------
  Tổng biên đóng góp                241 triệu đồng mỗi tháng

  So với chi phí cố định            230 triệu đồng mỗi tháng
```

Kết luận của mô hình: khoảng 50 bãi có thiết bị cộng khoảng 100 chỗ đỗ nhỏ trong một hoặc hai khu vực đô thị là mốc mà mô hình bắt đầu tự trang trải chi phí cố định. Đây là một con số ở tầm khả thi, không phải một con số cần hàng nghìn điểm mới có ý nghĩa. Đó là điểm mạnh cấu trúc của việc có doanh thu từ phía cung.

### 7.3. Độ nhạy của kết luận

| Nếu giả định này sai theo hướng xấu | Ảnh hưởng | Cách bù |
|---|---|---|
| Phí phần mềm chỉ đàm phán được một nửa mức đề xuất | Biên bãi loại A giảm khoảng 2,3 triệu, số bãi cần tăng khoảng 40 phần trăm | Tăng tỷ lệ chia doanh thu trên lượt mới, hoặc tập trung mạnh hơn vào mô đun an toàn nơi sức chi trả cao hơn |
| Doanh thu mới từ giờ thấp điểm chỉ đạt một nửa | Biên bãi loại A giảm khoảng 1,3 triệu | Đây là rủi ro thật và cần kiểm chứng sớm nhất, vì nó là luận điểm bán hàng chính. Kiểm chứng bằng một bãi thử nghiệm trong bốn tuần |
| Chi phí thiết bị mỗi bãi cao gấp rưỡi | Khấu hao tăng khoảng 0,4 triệu mỗi bãi | Tận dụng tối đa camera có sẵn của bãi, chỉ bổ sung camera cổng. Đàm phán mua thiết bị theo lô |
| Chi phí onboard mỗi bãi gấp đôi | Thời gian hoàn chi phí onboard tăng lên khoảng 4 tháng | Chuẩn hoá playbook, chuyển dần sang tự đăng ký cho loại B và C |
| Tỷ lệ giữ chỗ rồi không đến cao hơn dự kiến | Chủ bãi mất niềm tin vào cam kết của nền tảng | Phí giữ chỗ không hoàn lại, hạn mức giữ chỗ theo hồ sơ người dùng, giới hạn tỷ lệ dung lượng cho phép giữ trước |

---

## 8. Vì sao thu được tiền trong khi các bên đi trước không thu được

Bốn lý do, và cả bốn đều là lý do cấu trúc, không phải lý do về nỗ lực.

**Lý do một, bán trước cho phía cung một sản phẩm có giá trị độc lập.** Các nền tảng trước đó chỉ có một sản phẩm là sàn kết nối, nên họ phải chờ có cả hai phía mới có doanh thu. Parking HUB có một sản phẩm bán được cho chủ bãi từ ngày đầu, và chính việc bán sản phẩm đó tạo ra dữ liệu để sàn hoạt động.

**Lý do hai, giá trị mang tới chủ bãi đo được bằng tiền trong tháng đầu.** Chống thất thu là con số đối soát được. Đây là loại lập luận bán hàng khác hẳn lời hứa về khách hàng mới trong tương lai.

**Lý do ba, có một dòng doanh thu gắn với nghĩa vụ tuân thủ.** Mô đun an toàn cháy nổ không phải thứ chủ bãi cắt đầu tiên khi khó khăn, vì họ có nghĩa vụ pháp lý liên quan. Trong cấu trúc doanh thu, đây là dòng ổn định nhất.

**Lý do bốn, chỉ thu trên giá trị tạo thêm.** Việc không đòi phần trăm trên doanh thu vốn có của bãi làm giảm mạnh sức đề kháng trong đàm phán, và đây là nút thắt thực tế đã chặn nhiều nền tảng ở bước thứ nhất.

---

## 9. Rủi ro của mô hình và cách xử lý

| Rủi ro | Vì sao nghiêm trọng | Cách xử lý |
|---|---|---|
| Chủ bãi dùng hệ thống rồi đi vòng qua nền tảng, tự bán trực tiếp cho khách | Nền tảng mất phần chia doanh thu, chỉ còn phí phần mềm | Phần lớn doanh thu định kỳ nằm ở L1 và L2 nên vẫn giữ được. Gói tháng và ví của người dùng nằm trên nền tảng. Dữ liệu lịch sử và dự báo của bãi nằm trong hệ thống, đi ra là mất |
| Chủ bãi tự lắp camera AI của nhà cung cấp khác | Mất bãi và mất dữ liệu | Giá trị của Parking HUB không nằm ở camera mà ở mạng lưới: nguồn khách, dự báo, gói tháng, hợp đồng đội xe. Một hệ thống camera đơn lẻ không mang lại những thứ đó |
| Người dùng chỉ dùng để tìm rồi đỗ mà không đặt qua nền tảng | Không thu được phía cầu | Vào ra tự động và thanh toán không tiền mặt chỉ hoạt động khi đi qua nền tảng. Giá gói tháng và giá giờ thấp điểm chỉ có trên nền tảng |
| Mật độ mạng lưới không đạt ở khu vực nào | Người dùng không thấy giá trị, rời đi | Nguyên tắc không chi tiền thu hút người dùng ở khu vực chưa đủ mật độ. Dùng chỗ đỗ nhỏ của hộ dân để lấp mật độ với chi phí thấp |
| Vốn bị chôn vào thiết bị nếu cho thuê quá nhiều | Dòng tiền âm dù mô hình có lãi trên giấy | Chỉ cho thuê thiết bị trong giai đoạn thử nghiệm và với bãi có biên cao. Chuyển sang bán thiết bị hoặc thuê qua đối tác tài chính khi mở rộng |
| Cạnh tranh về giá từ một đơn vị lớn có sẵn tệp khách hàng | Bị ép giảm phí phần mềm và tỷ lệ chia | Cạnh tranh bằng dữ liệu và độ chính xác dự báo, không bằng giá. Đồng thời ưu tiên chiếm sớm những bãi có nghĩa vụ tuân thủ, vì đó là nơi quyết định không dựa hoàn toàn vào giá |
| Chi phí bán hàng cho từng bãi quá cao so với biên | Mở rộng không có lãi | Phân tuyến rõ: đội bán hàng chỉ đi bãi loại A, loại B và C đi bằng kênh tự đăng ký |
| Sự cố an toàn hoặc tranh chấp gây tổn hại uy tín | Mất niềm tin trên toàn mạng lưới, đặc biệt với phân khúc chỗ đỗ hộ dân | Quy trình bằng chứng hình ảnh, xác thực hai chiều, chính sách xử lý minh bạch, và không mở rộng phân khúc rủi ro trước khi quy trình đã chạy ổn |

---

## 10. Tầm nhìn doanh thu dài hạn

Ba hướng mở rộng, xếp theo mức độ gần với năng lực hiện có.

**Hướng một, dịch vụ cho xe đang gửi.** Xe đứng yên nhiều giờ trong bãi là cơ hội tự nhiên cho rửa xe, sạc điện, bảo dưỡng cơ bản. Đây là hướng mà kinh nghiệm và một phần lõi kỹ thuật sẵn có của đội về điều phối mạng lưới điểm dịch vụ chăm sóc xe phát huy trực tiếp.

**Hướng hai, mở rộng lớp cảm nhận sang các bài toán khác trong cùng khuôn viên.** Cùng một hạ tầng camera và thiết bị biên đã lắp, cùng một năng lực nhận diện biển số và phát hiện bất thường, có thể phục vụ kiểm soát ra vào, an ninh khuôn viên, và quản lý giao thông nội bộ của toà nhà. Doanh thu tăng thêm mà không cần lắp thêm thiết bị.

**Hướng ba, trở thành nguồn dữ liệu giao thông tĩnh cho đô thị.** Khi mạng lưới phủ đủ dày trong một thành phố, dữ liệu về cung, cầu và mức lấp đầy theo giờ trở thành đầu vào cho việc điều hành và quy hoạch. Hướng này ít doanh thu trực tiếp nhất trong ngắn hạn nhưng tạo vị thế bền nhất, và là hướng gắn chặt nhất với mục tiêu của cuộc thi.

Một ghi chú để đóng lại tài liệu này. Điều làm mô hình có thể sống không phải một luồng doanh thu lớn nào, mà là việc luồng doanh thu đầu tiên không phụ thuộc vào luồng thứ hai. Chủ bãi trả tiền cho vận hành và an toàn, việc đó tạo ra dữ liệu, dữ liệu tạo ra sản phẩm cho người lái xe, người lái xe tạo ra doanh thu mới cho chủ bãi, và doanh thu mới đó làm chủ bãi ở lại. Vòng này khép kín, và nó bắt đầu được từ một bãi duy nhất.
