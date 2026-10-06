> ## Feature: Context-aware Parking Matching — Traffic, Flood & Camera Intelligence
>
> Hệ thống hiện đã có **Parking Matching**: từ vị trí/điểm đến của user, tìm các bãi phù hợp dựa trên các yếu tố hiện có như loại xe, khoảng cách, giá, availability và các điều kiện của parking.
>
> Tôi muốn nghiên cứu và mở rộng Matching để xét thêm **điều kiện thực tế trên đường đi đến từng bãi**, đặc biệt là traffic và ngập lụt tại TP.HCM. Lý do rất thực tế: *“hồi chiều trời mưa”* 🌧️, bãi gần nhất chưa chắc là bãi đến nhanh hoặc an toàn nhất.
>
> ### 1. Target flow
>
> Không chọn ngay 3 bãi gần nhất theo khoảng cách chim bay. Distance chỉ dùng để lấy một tập candidate ban đầu.
>
> ```text
> User location / Destination
>          ↓
> Existing Parking Matching
>          ↓
> Candidate parkings (~10–30)
>          ↓
> Hard filter
> vehicle compatibility / opening / availability / ...
>          ↓
> Route từ user → từng parking
>          ↓
> ┌────────────┬────────────┬─────────────┐
> │  Traffic   │   Flood    │   Weather   │
> └────────────┴────────────┴─────────────┘
>          ↓
> Route Risk / Travel Cost
>          ↓
> Existing Parking Score + Route Score
>          ↓
> Top 3 Parking
> ```
>
> Cần **giữ Parking Score và Route Score tách biệt**. Một parking có thể rất phù hợp nhưng route tới đó đang kẹt hoặc ngập.
>
> ---
>
> ### 2. Traffic Intelligence
>
> Nghiên cứu bổ sung traffic state cho từng route/road segment:
>
> - dữ liệu traffic nếu lấy được từ nguồn TP.HCM;
> - congestion / traffic warning;
> - incident, road closure, road work, diversion nếu nguồn có;
> - camera giao thông làm nguồn realtime bổ sung.
>
> Output cuối không cần quá phức tạp:
>
> ```text
> FREE / MODERATE / CONGESTED / BLOCKED / UNKNOWN
> ```
>
> và có thể chuyển thành `traffic_penalty` cho từng road edge.
>
> Không yêu cầu CV giải quyết hoàn hảo case đèn đỏ ngay. Nếu một snapshot thấy nhiều xe thì có thể nhầm với congestion. Phase sau có thể dùng temporal evidence: nhiều snapshot liên tiếp vẫn đông → khả năng congestion cao; đông/thưa theo chu kỳ → khả năng do traffic light.
>
> ---
>
> ### 3. Flood Intelligence — mô hình 3 tầng
>
> Historical flood data coi như **đã có**.
>
> Không được hiểu “đường từng ngập” = “đường đang ngập”. Historical chỉ là **prior risk**.
>
> ```text
>                 FLOOD RISK
>
> Historical       Realtime Evidence       Weather
>     │                    │                  │
> điểm từng ngập        Camera AI          mưa hiện tại
> tần suất              report/API         cường độ mưa
> mức độ cũ             current evidence   nowcast
>     │                    │                  │
>     └────────────────────┼──────────────────┘
>                          ↓
>                   Current Flood Risk
>                          ↓
>              penalty / block road edge
> ```
>
> Có thể conceptualize:
>
> ```text
> P(flood_now) =
>     f(historical_risk,
>       camera_evidence,
>       rainfall_now,
>       other_realtime_evidence)
> ```
>
> Ngập nhẹ → tăng route cost.  
> Ngập đáng kể → penalty mạnh.  
> Ngập nghiêm trọng → có thể block edge.
>
> ---
>
> ### 4. Camera TP.HCM
>
> Hưng đã POC được nguồn camera từ trang giao thông TP.HCM:
>
> - lấy được danh sách camera toàn TP.HCM;
> - có vị trí/metadata camera;
> - lấy được snapshot hiện tại.
>
> Vì vậy không cần nghiên cứu lại từ đầu chuyện *có lấy được camera hay không*. Hãy tập trung vào cách integrate camera vào routing/matching.
>
> Với mỗi candidate route:
>
> ```text
> Route geometry
>      ↓
> Find cameras near/on route
>      ↓
> Get latest snapshots
>      ↓
> Camera AI
>      ↓
> flood + traffic evidence
>      ↓
> map evidence → road segment
> ```
>
> Camera không nằm chính xác trên route hoặc không nhìn được road segment tương ứng thì không nên dùng evidence một cách mù quáng. Cần xem xét distance, hướng camera nếu có và confidence.
>
> ---
>
> ### 5. Multi-camera AI
>
> Nếu route đi qua nhiều camera, ví dụ 9 camera, **không nhất thiết gửi 9 request AI riêng**.
>
> Ghép snapshot thành một mosaic:
>
> ```text
> ┌───────┬───────┬───────┐
> │ CAM 1 │ CAM 2 │ CAM 3 │
> ├───────┼───────┼───────┤
> │ CAM 4 │ CAM 5 │ CAM 6 │
> ├───────┼───────┼───────┤
> │ CAM 7 │ CAM 8 │ CAM 9 │
> └───────┴───────┴───────┘
> ```
>
> Đánh số camera trực tiếp trên ảnh và gửi **một image request cho vision model/VLM**.
>
> Mong muốn structured output dạng:
>
> ```json
> {
>   "1": {
>     "flood": "none",
>     "traffic": "moderate",
>     "confidence": 0.91
>   },
>   "2": {
>     "flood": "light",
>     "traffic": "congested",
>     "confidence": 0.82
>   }
> }
> ```
>
> Có thể dùng cascade:
>
> ```text
> 9 snapshots
>      ↓
> 3×3 mosaic → AI
>      ↓
> high-confidence cameras → accept
>      ↓
> uncertain camera
>      ↓
> resend riêng full-resolution
> ```
>
> Cần benchmark mosaic so với individual image vì dấu hiệu ngập nhẹ có thể nhỏ: mặt nước, bánh xe chìm, reflection, mép nước...
>
> Camera AI nên đóng vai trò **sensor**, không phải router. AI trả observation/confidence; routing engine quyết định penalty.
>
> ---
>
> ### 6. Weather — ưu tiên nghiên cứu kỹ
>
> Không muốn weather kiểu:
>
> ```text
> Ho Chi Minh City: Rain
> ```
>
> vì TP.HCM có thể Bình Thạnh mưa rất lớn trong khi khu vực gần đó chưa mưa.
>
> Mong muốn dữ liệu dạng:
>
> ```text
> rain(lat, lng, time)
> ```
>
> Ưu tiên nghiên cứu:
>
> - precipitation/rainfall theo tọa độ;
> - rainfall intensity (`mm/h`);
> - radar precipitation nếu có;
> - short-term precipitation nowcast;
> - khả năng dự báo 15–60 phút tới.
>
> Weather phải được map vào **route segments**, không chỉ user location.
>
> Xa hơn có thể xét cả ETA:
>
> ```text
> User hiện tại
>       ↓
> segment X sau ~12 phút
>       ↓
> rain(segment_X, now + 12 min)
> ```
>
> Weather chủ yếu tác động vào `flood_risk`, `traffic_risk` và uncertainty của travel time, thay vì đơn giản block route.
>
> ---
>
> ### 7. Integration với Matching hiện tại
>
> Không rewrite thuật toán Matching đang có.
>
> Hãy đọc codebase trước và xác định:
>
> 1. Candidate parking hiện được tạo ở đâu.
> 2. Hard filters hiện tại là gì.
> 3. Parking score/ranking hiện tính thế nào.
> 4. Routing engine/OSM hiện nằm ở layer nào.
> 5. Availability và ETA hiện được xử lý thế nào.
> 6. Điểm thích hợp để inject `RouteContext`.
>
> Có thể hướng tới abstraction:
>
> ```text
> RouteContext
> ├── base_travel_time
> ├── distance
> ├── traffic_score
> ├── flood_risk
> ├── weather_risk
> ├── incidents
> ├── blocked
> └── confidence
> ```
>
> Sau đó:
>
> ```text
> Existing Parking Score
>          +
> RouteContext
>          ↓
> Final Matching Score
> ```
>
> Hard constraints vẫn phải tách khỏi weighted score. Ví dụ đường bị đóng/ngập nghiêm trọng thì không nên chỉ `-20 points`; route đó phải bị loại hoặc reroute.
>
> ---
>
> ### 8. Việc cần agent thực hiện
>
> Trước mắt **chưa code ngay**. Hãy:
>
> 1. Đọc và mô tả flow Matching hiện tại.
> 2. Xác định các module/file cần thay đổi để thêm Route Intelligence mà ít ảnh hưởng hệ thống cũ nhất.
> 3. Đánh giá dữ liệu camera mà Hưng đã POC và cách map camera → OSM road/route.
> 4. Nghiên cứu nguồn traffic TP.HCM có thể sử dụng.
> 5. Nghiên cứu nguồn weather/rainfall/nowcast có độ phân giải không gian đủ tốt cho TP.HCM.
> 6. Thiết kế flood model 3 tầng: historical + camera/realtime + weather.
> 7. Đề xuất schema/cache/update frequency cho traffic, camera, weather và flood.
> 8. Đề xuất cách merge các signal vào Matching hiện tại.
> 9. Phân chia rõ **MVP / Phase 2 / nice-to-have**, tránh over-engineering.
>
> Output mong muốn là **technical assessment + integration proposal**, kèm diagram/flow và các file/module dự kiến thay đổi. Chưa implementation cho đến khi architecture được review.

