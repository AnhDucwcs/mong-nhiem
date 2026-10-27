# Mộng Nhiễm Living World: World Design, Scenario & Epistemic Specification
*Authoritative Technical & Scientific Contract (v2.0)*

---

## 1. Thời Gian Mô Phỏng, Fixed Timestep & Độc Lập Render UI

### 1.1 Chu Kỳ Thời Gian Vật Lý Cố Định (`simulation_dt`)
Mô phỏng vật lý và trạng thái sinh học vận hành trên một bước thời gian cố định (**Fixed Timestep**):
$$\Delta t_{\text{sim}} = 0.05\text{ s} \quad (20\text{ simulation ticks / second})$$
Mọi phương trình vi phân biến đổi trạng thái được tích phân số học (Euler integration) theo $\Delta t_{\text{sim}}$:
$$\mathbf{x}(t + \Delta t_{\text{sim}}) = \mathbf{x}(t) + \mathbf{v}(t) \cdot \Delta t_{\text{sim}}$$
$$E_i(t + \Delta t_{\text{sim}}) = E_i(t) + \dot{E}_i \cdot \Delta t_{\text{sim}}$$

### 1.2 Tách Rời Hoàn Toàn Khỏi Tốc Độ Vẽ Giao Diện (Decoupled UI Render)
- **UI Render Loop:** Chạy theo chu kỳ vẽ của trình duyệt thông qua `requestAnimationFrame()` ($\sim 60\text{ fps}$ hoặc tần số quét màn hình). Render UI chỉ đọc trạng thái hiện tại của Host và vẽ lên Canvas; không tham gia biến đổi trạng thái vật lý.
- **Nút Điều Khiển Tốc Độ ($1\times, 2\times, 5\times$):**
  - Tốc độ $1\times$: Tính toán $1$ physics tick mỗi frame.
  - Tốc độ $2\times$: Tính toán $2$ physics ticks mỗi frame.
  - Tốc độ $5\times$: Tính toán $5$ physics ticks mỗi frame.
- **Tính Bất Biến (Invariant):** Việc tăng tốc độ giao diện **không làm thay đổi $\Delta t_{\text{sim}}$**. Tỉ số vi phân toán học hoàn toàn bất biến; kết quả mô phỏng giữa $1\times$ và $5\times$ là tất định ($100\%$ deterministic replay).

---

## 2. Bảng Đơn Vị Đo Lường Toàn Diện Của Biến Số & Hệ Số

| Đại Lượng | Ký Hiệu | Đơn Vị Đo | Phạm Vi Giá Trị | Định Nghĩa & Ý Nghĩa |
| :--- | :--- | :--- | :--- | :--- |
| **Toạ độ không gian** | $x, y$ | $\text{px}$ (pixel) | $x \in [0, W], y \in [0, H]$ | Toạ độ 2D thực trên canvas mô phỏng |
| **Vận tốc thực** | $v_x, v_y$ | $\text{px/s}$ | $\|v\| \le 120\text{ px/s}$ | Vận tốc chuyển động thực tế trong 1 giây |
| **Vận tốc tick** | $v_{\text{tick}}$ | $\text{px/tick}$ | $v_{\text{tick}} = v \cdot \Delta t$ | Độ dịch chuyển trong 1 bước mô phỏng ($\le 6\text{ px/tick}$) |
| **Bán kính vật thể** | $r_i, R$ | $\text{px}$ | $r_{\text{rabbit}} = 4.8$, $r_{\text{scout}} = 6.5$, $r_{\text{wolf}} = 8.5$ | Bán kính va chạm vật lý |
| **Năng lượng thể lực** | $E_i$ | $\%$ | $[0.0, 100.0]\%$ | Năng lượng dự trữ của cá thể |
| **Mức độ đói** | $H_i$ | $\%$ | $[0.0, 100.0]\%$ | $0\%$: no căng; $100\%$: đói kiệt sức |
| **Mức độ khát** | $T_i$ | $\%$ | $[0.0, 100.0]\%$ | $0\%$: đủ nước; $100\%$: khát khô |
| **Sinh lực / Máu** | $\Omega_i$ | $\%$ | $[0.0, 100.0]\%$ | Khi $\Omega_i = 0$, cá thể tử vong |
| **Tốc độ hao năng lượng** | $\alpha_E$ | $\%/\text{s}$ | $0.40\%/\text{s}$ ($0.02\%/\text{tick}$) | Năng lượng tiêu hao tĩnh cơ bản |
| **Hệ số hao theo vận tốc** | $\beta_E$ | $\%/\text{px}$ | $0.005\%/\text{px}$ | Năng lượng tiêu hao thêm khi di chuyển |
| **Tốc độ tăng đói** | $\alpha_H$ | $\%/\text{s}$ | $0.70\%/\text{s}$ ($0.035\%/\text{tick}$) | Tốc độ tiêu hóa tự nhiên |
| **Tốc độ tăng khát** | $\alpha_T$ | $\%/\text{s}$ | $0.60\%/\text{s}$ ($0.030\%/\text{tick}$) | Tốc độ mất nước tự nhiên |
| **Trữ lượng tài nguyên** | $r$ | $\text{u}$ (units) | $0.0 \sim 300.0\text{ u}$ | Đơn vị dinh dưỡng / nước sinh học |
| **Tốc độ hồi tài nguyên** | $\dot{r}_{\text{regen}}$ | $\text{u/s}$ | $0.50\text{ u/s}$ ($0.025\text{ u/tick}$) | Tốc độ chín của dâu / nạp nước hồ danh định |
| **Tốc độ gặm/uống** | $\dot{c}_{\text{eat}}$ | $\text{u/s}$ | $2.0\text{ u/s}$ ($0.10\text{ u/tick}$) | Lượng thức ăn tiêu thụ khi thỏ đứng cạnh bụi |
| **Vận tốc gió** | $v_{\text{wind}}$ | $\text{km/h}$ | $0 \sim 40\text{ km/h}$ | Vận tốc gió khí quyển |
| **Hướng gió** | $\theta_{\text{wind}}$ | $\text{rad}$ | $[0, 2\pi)$ | Hướng luồng gió thổi |

---

## 3. Định Nghĩa Ngưỡng Nhìn Trước 4 Bước (4-Step Action Lookahead)

Ngưỡng nhìn trước trong quy chế an toàn của Mộng Nhiễm được định nghĩa chính xác là:
$$\mathbf{H}_{\text{lookahead}} = 4\text{ Action Steps (Bước hành động kế hoạch của SLM)}$$
Không phải 4 tick mô phỏng ($\Delta t_{\text{sim}} \times 4 = 0.2\text{ s}$ là quá ngắn, chưa phản ánh được ý đồ di chuyển).

### 3.1 Cấu Trúc Kế Hoạch Của SLM
Khi SLM được kích hoạt, nó xuất ra một chuỗi gồm 4 waypoint không gian:
$$\mathcal{P}_{\text{plan}} = \langle \mathbf{w}_1, \mathbf{w}_2, \mathbf{w}_3, \mathbf{w}_4 \rangle, \quad \mathbf{w}_k \in \mathbb{R}^2$$
Mỗi bước hành động $\mathbf{w}_k$ có thời lượng dự kiến $t_{\text{step}} = 1.0\text{ s}$ ($20\text{ simulation ticks}$). Tổng chân trời nhìn trước là:
$$T_{\text{horizon}} = 4 \times 1.0\text{ s} = 4.0\text{ s} \quad (80\text{ simulation ticks})$$

### 3.2 Quy Trình Thẩm Định Của Hạt Nhân Mộng Nhiễm
Trước khi commit kế hoạch vào bộ điều khiển thực:
1. **Nội suy quỹ đạo:** Host nội suy đường đi dự kiến của thỏ: $\mathbf{p}_{\text{scout}}(\tau)$ với $\tau \in [t, t + 4.0\text{ s}]$.
2. **Chiếu vị trí chướng ngại & thú săn:** Host dự phóng quỹ đạo của Sói: $\mathbf{p}_{\text{wolf}}(\tau)$ dựa trên vận tốc hiện tại.
3. **Tính khoảng cách động thực tế:**
   $$d_{\text{min}} = \min_{\tau \in [t, t + 4.0\text{ s}]} \|\mathbf{p}_{\text{scout}}(\tau) - \mathbf{p}_{\text{wolf}}(\tau)\|$$
4. **Quyết định Gating:**
   - Nếu $d_{\text{min}} < D_{\text{safety}} = 35.0\text{ px}$: Kích hoạt `ReflexBreaker`.
   - **Ghi log Host Arbitration:** Ghi rõ mã vi phạm `VIOLATION_PREDATOR_PROXIMITY`, giá trị kiểm tra động đo được ($d_{\text{min}} = 28.4\text{ px} < 35.0\text{ px}$), và cưỡng chế quỹ đạo fallback an toàn sang lùm cây che phủ gần nhất.

---

## 4. Phân Biệt Biến Cố: Shock Injection vs Environmental Simulation

Để đảm bảo tính trung thực khoa học, hệ thống phân biệt tường minh 2 cơ chế biến cố:

```
+-------------------------------------------------------------------------+
|                  PHÂN LOẠI BIẾN CỐ TÀI NGUYÊN                           |
+------------------------------------+------------------------------------+
| A. SHOCK INJECTION                 | B. ENVIRONMENTAL SIMULATION        |
| (Can Thiệp Thử Nghiệm Sốc)         | (Mô Phỏng Biến Đổi Khí Hậu)        |
+------------------------------------+------------------------------------+
| - Tác nhân: Người vận hành cưỡng   | - Tác nhân: Vi khí hậu tự nhiên    |
|   chế đặt giá trị tức thời.        |   (Hạn hán, nắng nóng, mưa).       |
| - Quy luật:                        | - Quy luật vi phân theo Delta t:   |
|   r_target <- 0u tại tick t0.      |   dr/dt = -k_drought * r - sum(c)  |
| - Mục đích: Stress test phản ứng   | - Mục đích: Tái hiện sinh thái tự  |
|   khẩn cấp của SLM & ReflexBreaker |   nhiên, cho phép trinh sát nhận   |
|   khi tài nguyên đột ngột cạn.     |   biết xu hướng suy giảm dần.      |
+------------------------------------+------------------------------------+
```

- **Shock Injection (Ép Cạn Lương):** Nút UI `Shock: Ép Cạn Lương (0u)` lập tức gán `bush.amount = 0`. Dùng để kiểm tra khả năng phát hiện lỗi nhận thức và chuyển hướng khẩn cấp.
- **Environmental Simulation (Hạn Hán Vi Phân):** Nút UI `Khí Hậu: Hạn Hán Vi Phân` chuyển môi trường sang chế độ hạn hán:
  - Tốc độ hồi phục: $\dot{r}_{\text{regen}} = 0.0\text{ u/s}$.
  - Tốc độ suy giảm tự nhiên do nhiệt: $\dot{r}_{\text{evap}} = -0.60\text{ u/s}$ ($-0.03\text{ u/tick}$).
  - Trữ lượng giảm liên tục từ $100\text{ u} \to 80\text{ u} \to 50\text{ u} \to 0\text{ u}$ trong vòng $\sim 160\text{ s}$ mô phỏng.

---

## 5. Ký Ức Scout (FactCard-02) & Nguồn Gốc Bất Đối Xứng Nhận Thức

Spec giải thích chính xác vì sao ký ức của Scout có giá trị $80\text{ u}$:

1. **Khởi nguyên tại $t_0$ (`tick = 0`):**
   - Trữ lượng thực tế của Bụi dâu Bắc khi đó là $80\text{ u}$.
   - Thỏ đầu đàn (Alpha Scout) tiến hành quan sát trực tiếp trong tầm nhìn ($d \le R_{\text{vision}} = 140\text{ px}$).
   - Host sinh thẻ ký ức AutoDream `FACT-02`:
     ```json
     {
       "id": "FACT-02",
       "subject": "berry_north",
       "observed_amount": 80.0,
       "observed_at_tick": 0,
       "status": "ABUNDANT_FORAGE",
       "initial_confidence": 1.0
     }
     ```
2. **Di chuyển rời vùng quan sát tại $t = 2.0\text{ s}$ (`tick = 40`):**
   - Scout dẫn bầy di chuyển về phía Bãi Cỏ Trung Tâm gặm cỏ non ($d_{\text{scout}\to\text{bush}} \approx 280\text{ px} > R_{\text{vision}}$).
   - Bụi dâu Bắc nằm ngoài nón quan sát. Hệ thống KHÔNG tự động cập nhật trạng thái từ xa (không có thần giao cách cảm).
3. **Độ tin cậy suy giảm theo thời gian (Stale Memory Decay):**
   $$\text{Confidence}(t) = \exp(-\lambda_{\text{decay}} \cdot (t - t_{\text{observed}})), \quad \lambda_{\text{decay}} = 0.003\text{ s}^{-1}$$
4. **Phát sinh Bất Đối Xứng Nhận Thức (Epistemic Skew):**
   - Tại `tick = 142`: Biến cố khiến Bụi dâu Bắc cạn về $0\text{ u}$.
   - **Thực tế khách quan (Ground Truth):** $0\text{ u}$.
   - **Niềm tin của Scout (Agent Belief):** Vẫn lưu `FACT-02` ($80\text{ u}$) với độ tin cậy $\approx 0.78$. Scout chỉ phát hiện sự thật khi di chuyển trở lại vào bán kính $R_{\text{vision}} \le 140\text{ px}$.

---

## 6. Mô Hình Mùi Hương Tối Giản: Nón Mùi Hướng Gió (Directional Scent Cone)

Loại bỏ hoàn toàn các phương trình đạo hàm riêng $2\text{D}$ phức tạp (YAGNI). Hệ thống sử dụng mô hình hình học nón tán xạ theo hướng gió:

```
                       Gió thổi hướng theta_wind
                             =============>
                 
                     \   VÙNG PHÁT TÁN MÙI DÃ THÚ   /
                      \  (Directional Scent Cone)  /
                       \                          /
                        \       (Downwind)       /
                         \                      /
                          +--------------------+
                          |  SÓI (Nguồn Mùi)   |
                          +--------------------+
                                   ||
                               (Upwind)  <- Vùng ngược gió KHÔNG có mùi
```

### 6.1 Công Thức Hình Học Của Nón Mùi
1. **Nguồn mùi:** Vị trí Sói $\mathbf{p}_{\text{wolf}} = [x_w, y_w]$.
2. **Bán kính khuếch tán cơ sở:** $R_{\text{base}} = 60\text{ px}$.
3. **Chiều dài nón xuôi gió:**
   $$L_{\text{cone}} = R_{\text{base}} + \gamma_w \cdot v_{\text{wind}} = 60 + 4.0 \times 14 = 116\text{ px}$$
4. **Góc mở của nón:** $\alpha_{\text{half}} = 35^\circ$ ($0.61\text{ rad}$) quanh trục hướng gió $\theta_{\text{wind}}$.

### 6.2 Điều Kiện Thỏ Phát Hiện Mùi (Host Invariant Check - $O(1)$)
Thỏ $i$ tại $\mathbf{p}_i$ phát hiện mùi sói khi và chỉ khi:
$$\|\mathbf{p}_i - \mathbf{p}_{\text{wolf}}\| \le L_{\text{cone}} \quad \land \quad |\text{atan2}(y_i - y_w, x_i - x_w) - \theta_{\text{wind}}| \le \alpha_{\text{half}}$$
- **Ngược gió (Upwind):** Thỏ đứng ngược chiều gió so với sói sẽ hoàn toàn không ngửi thấy mùi, tạo điều kiện cho sói áp sát nếu thỏ bị che khuất tầm nhìn.
- **Xuôi gió (Downwind):** Thỏ ngửi thấy mùi từ cự ly $116\text{ px}$, tự động cảnh báo sớm bầy đàn mà chưa cần nhìn thấy sói.

---

## 7. Phân Định Thực Thể: Quần Thể Thỏ vs Thực Thể Độc Lập Sói

1. **Quần Thể Thỏ (Rabbit Colony - `colony_01`):**
   - Gồm chính xác **24 cá thể sinh học**:
     - 1 Alpha Scout (Thỏ đầu đàn trinh sát & giữ quyền giao tiếp SLM).
     - 7 Foragers (Thỏ hái lượm kiếm ăn).
     - 16 Flock members (Thành viên đàn thông thường).
   - Chia sẻ chung một không gian tín hiệu và mục tiêu sinh tồn bầy đàn.
2. **Thực Thể Sói (Apex Predator - `wolf_01`):**
   - Là **Thực thể ngoại lai độc lập**, KHÔNG thuộc quần thể thỏ.
   - Vận hành bằng máy trạng thái hữu hạn riêng biệt (Host FSM):
     - `PATROL`: Tuần tra vòng tròn kiểm soát lãnh thổ phía Đông hồ ($[810, 270]$).
     - `STALK`: Khi phát hiện thỏ ngoài lùm cây ở cự ly $\le 160\text{ px}$, sói giảm tốc ($v = 40\text{ px/s}$) tiếp cận lén lút.
     - `CHASE`: Khi cự ly $\le 90\text{ px}$, sói tăng tốc tối đa ($v = 110\text{ px/s}$) đuổi bắt con mồi gần nhất.

---

## 8. Quy Chuẩn Sức Chứa Hang Thỏ ($C_{\text{burrow}} = 16$ vs $N = 24$)

Hang trú ẩn có sức chứa $C_{\text{burrow}} = 16$, trong khi bầy đàn có $24$ cá thể $\to$ Khi có biến cố báo động khẩn cấp, **8 cá thể chắc chắn không thể vào hang**.

### 8.1 Thuật Toán Xếp Hàng Ưu Tiên Vào Hang
Khi báo động `ALARM_EVACUATE` được kích hoạt:
1. **Tiêu chí ưu tiên 1 (Khoảng cách tiếp cận):** Cá thể nào tiếp cận miệng hang trước ($d_i \le R_{\text{entrance}} = 11\text{ px}$) sẽ được Host xác nhận vào hang trước (FIFO).
2. **Tiêu chí ưu tiên 2 (Cứu trợ cá thể kiệt sức):** Cá thể có năng lượng thấp ($E_i < 40\%$) được bầy đàn nhường lối vào cửa hang nhanh hơn.
3. **Đóng cửa hang:** Khi số lượng trong hang đạt $16/16$, cờ trạng thái hang chuyển thành `STATUS: FULL`.

### 8.2 Giao Thức Phân Tán Cho 8 Cá Thể Còn Lại
- Cá thể nào tiếp cận hang sau khi hang đã đầy hoặc nhận thấy cự ly tới hang quá xa ($> 200\text{ px}$) sẽ **tự động kích hoạt hành vi phân tán vào Lùm Cây Che Phủ (`Thickets`)**:
  - Tìm lùm cây gần nhất trong 6 lùm cây trên bản đồ.
  - Khi tiến vào lùm cây ($d \le R_{\text{thicket}}$), cờ $\kappa_i = 1$ kích hoạt hệ số ẩn nấp $80\% - 85\%$.
  - Tầm nhìn của sói đối với cá thể trong lùm cây bị bóp nghẹt từ $160\text{ px} \to 48\text{ px}$, giúp 8 cá thể còn lại sống sót an toàn mà không bị dồn ứ chết chùm trước cửa hang.

---

## 9. Phân Quyền & Vai Trò Của Alpha Scout

Alpha Scout **không phải là bộ điều khiển tập trung vĩ mô (Centralized Omniscient Controller)**. Phạm vi quyền hạn được phân tầng rõ rệt:

1. **Cấp Cá Thể (Self-Cognition):**
   - Scout có nhận thức giác quan riêng ($R_{\text{vision}} = 140\text{ px}$, nón khứu giác).
   - Là cá thể DUY NHẤT trong đàn được liên kết phiên suy luận SLM khi gặp biến cố bất thường (Surprise trigger).
   - SLM đưa ra quyết định có cấu trúc: `INTENT: EXPLORE_WEST` hoặc `INTENT: RETREAT`.
2. **Cấp Truyền Tin (Directive Signal Broadcast):**
   - Scout không trực tiếp điều khiển toạ độ $(x_j, y_j)$ của 23 con thỏ khác.
   - Scout chỉ có quyền phát **Tín Hiệu Chỉ Thị (Directive Signal)** trong bán kính truyền thanh/mùi pheromone:
     $$R_{\text{broadcast}} = 200\text{ px}$$
   - Nội dung tín hiệu là các token mục tiêu vĩ mô: `DIRECTIVE_FORAGE [point]` hoặc `DIRECTIVE_EVACUATE`.
3. **Cấp Tự Trị Bầy Đàn (Flock Local Autonomy):**
   - Mỗi con thỏ trong 23 con còn lại tự vận hành bộ boids vi phân của riêng nó:
     $$\mathbf{a}_i = w_1 \mathbf{a}_{\text{directive}} + w_2 \mathbf{a}_{\text{cohesion}} + w_3 \mathbf{a}_{\text{separation}} + w_4 \mathbf{a}_{\text{obstacle\_avoid}}$$
   - Nếu một con thỏ ở ngoài bán kính $R_{\text{broadcast}}$, nó hoàn toàn KHÔNG biết chỉ thị mới của Scout và tiếp tục gặm cỏ theo quán tính cục bộ.
   - Nếu một con thỏ bị Sói chặn đầu, luật sinh tồn cá thể (`flee_predator`) sẽ ghi đè $100\%$ lên directive của Scout.

---

## 10. Kịch Bản Kiểm Chứng Định Lượng

### Kịch Bản A: Shock Injection vs Phát Hiện Lệch Nhận Thức
1. **T0 ($t = 0.0\text{ s}$, Tick 0):** Quần thể thỏ tại Bãi Cỏ Ven Hồ $[520, 360]$. Bụi dâu Bắc có trữ lượng $80\text{ u}$. Scout trinh sát ghi nhận `FACT-02: bush_north = 80u`.
2. **T1 ($t = 5.0\text{ s}$, Tick 100):** Operator bấm `Shock: Ép Cạn Lương (0u)` tại Bụi dâu Bắc. Host gán tức thời `amount = 0u`.
3. **T2 ($t = 5.05\text{ s}$, Tick 101):** Bất đối xứng nhận thức xuất hiện:
   $$\text{GroundTruth}(\text{Bush\_N}) = 0\text{ u} \quad \ne \quad \text{Belief}_{\text{scout}}(\text{Bush\_N}) = 80\text{ u}$$
4. **T3 ($t = 8.2\text{ s}$, Tick 164):** Scout dẫn đầu tiến vào chu vi Bụi dâu Bắc ($d = 39.2\text{ px} \le R_{\text{bush}} = 42\text{ px}$).
5. **T4 ($t = 8.25\text{ s}$, Tick 165):** Cảm biến mắt của Scout phát hiện thực tế $0\text{ u}$. Surprise Spike vượt ngưỡng:
   $$\Delta_{\text{surprise}} = |80 - 0| = 80 > \tau_{\text{threshold}} (30)$$
   Kích hoạt $1$ phiên gọi SLM duy nhất ($142\text{ tokens}$).
6. **T5 ($t = 8.35\text{ s}$, Tick 167):** SLM phát lệnh đổi hướng `MOVE_TO bush_west [260, 230]`. Cập nhật `FACT-02: bush_north = 0u (DEPLETED)`.

### Kịch Bản B: Phục Kích Của Sói & Can Thiệp Reflex Breaker
1. **T0 ($t = 10.0\text{ s}$, Tick 200):** Sói xuất hiện tại $[620, 280]$ ẩn sau rặng đá NE.
2. **T1 ($t = 10.5\text{ s}$, Tick 210):** Scout đề xuất kế hoạch 4 bước di chuyển:
   $$\mathcal{P}_{\text{plan}} = \langle [560, 320], [600, 300], [640, 280], [680, 260] \rangle$$
3. **T2 ($t = 10.55\text{ s}$, Tick 211):** Mộng Nhiễm Kernel thực hiện Trajectory Lookahead horizon 4 bước ($4.0\text{ s}$).
   Host tính khoảng cách tối thiểu động:
   $$d_{\text{min}} = \min_{\tau} \|\mathbf{p}_{\text{scout}}(\tau) - \mathbf{p}_{\text{wolf}}(\tau)\| = 23.6\text{ px} < D_{\text{safety}} (35.0\text{ px})$$
4. **T3 ($t = 10.6\text{ s}$, Tick 212):** `ReflexBreaker` **INTERCEPT**:
   - Chặn đứng kế hoạch của SLM.
   - Ghi nhật ký Panel C: `REJECT: Path breaches predator safety margin (measured d_min = 23.6px < 35.0px)`.
   - Cưỡng chế phát tín hiệu khẩn cấp: 16 con thỏ gần nhất sơ tán về Hang $[320, 520]$, các con còn lại tản vào Lùm Cây $[730, 470]$.
