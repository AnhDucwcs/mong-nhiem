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

### 1.2 Tách Rời Hoàn Toàn Khỏi Tốc Độ Vẽ Giao Diện (Fixed-Timestep Accumulator Engine)
- **UI Render Loop:** Chạy theo chu kỳ vẽ của trình duyệt thông qua `requestAnimationFrame()` ($\sim 60\text{ fps} - 144\text{ fps}$). Render UI chỉ đọc trạng thái hiện tại của Host và vẽ lên Canvas; hoàn toàn độc lập với nhịp tính vật lý.
- **Bộ tích lũy thời gian thực (Time Accumulator):**
  $$\text{Accumulator} \mathrel{+}= \Delta t_{\text{frame}} \cdot \text{simSpeed}$$
  $$\text{Chạy } \text{updateSimulation}() \text{ khi } \text{Accumulator} \ge 50\text{ ms} \quad (\Delta t_{\text{sim}} = 0.05\text{ s})$$
- **Hệ Thống Tốc Độ Linh Hoạt (Speed Selector & Presets):**
  - **$0.25\times$:** $5\text{ ticks/s}$ ($200\text{ ms/tick}$) - Siêu chậm: Quan sát tỉ mỉ rình rập và né tránh zig-zag.
  - **$0.50\times$:** $10\text{ ticks/s}$ ($100\text{ ms/tick}$) - Chậm: Theo dõi quỹ đạo rượt đuổi và vồ mồi mượt mà.
  - **$0.75\times$:** $15\text{ ticks/s}$ ($66\text{ ms/tick}$) - Vừa phải: Kiểm tra vận động bầy đàn tự nhiên.
  - **$1.00\times$:** $20\text{ ticks/s}$ ($50\text{ ms/tick}$) - Chuẩn thời gian thực danh định ($1753\text{ ticks} \approx 87.6\text{ s}$).
  - **$2.00\times$:** $40\text{ ticks/s}$ ($25\text{ ms/tick}$) - Tua nhanh.
  - **$5.00\times$:** $100\text{ ticks/s}$ ($10\text{ ms/tick}$) - Siêu tốc: Đẩy nhanh tiến hóa quần thể.
  - **Thanh trượt liên tục (Continuous Slider):** Hỗ trợ dải tốc độ $0.10\times \to 5.00\times$.
- **Tính Bất Biến (Invariant):** Thay đổi tốc độ hiển thị **không làm thay đổi độ dịch chuyển hay lực tương tác trên mỗi tick** ($100\%$ deterministic replay).

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
| **Độ no bụng (Satiety)** | $S_i$ | $\%$ | $S_i = 100\% - H_i$ | $100\%$: no nê; $0\%$: đói kiệt quệ (hiển thị UI) |
| **Mức độ khát** | $T_i$ | $\%$ | $[0.0, 100.0]\%$ | $0\%$: đủ nước; $100\%$: khát khô |
| **Độ ẩm nước (Hydration)** | $W_i$ | $\%$ | $W_i = 100\% - T_i$ | $100\%$: đủ nước; $0\%$: khát khô (hiển thị UI) |
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

## 6. Cơ Chế Mùi Hương & Giác Quan Sinh Học Thực Tế

Khác với các hệ thống đồ chơi gán quyền "siêu cảm xạ" cho thỏ, Mộng Nhiễm tuân thủ nghiêm ngặt sinh thái học thực tế:

```
                  Gió thổi hướng theta_wind
                         =============>
             
  [THỎ (Con Mồi)] ----> (Vệt Hạt Mùi Phát Tán Xuôi Gió) ----> [SÓI (Kẻ Săn)]
  - Phát tán mùi tự nhiên                                      - Khứu giác vượt trội (R = 240px)
  - Chỉ nhìn bằng MẮT (R <= 110px)                            - Lần theo vệt mùi xuôi gió
  - KHÔNG ngửi được mùi dã thú                                 - Mắt hẹp hơn mũi (R = 150px)
```

### 6.1 Phát Tán Mùi Của Thỏ (Prey Scent Emission)
1. **Nguồn phát tán:** Mỗi cá thể thỏ vận động liên tục phát tán các hạt mùi sinh học (`scentParticles`) vào không khí theo chu kỳ ($3\text{ ticks/lần}$).
2. **Khuếch tán theo gió:** Hạt mùi dịch chuyển xuôi theo vector vận tốc gió:
   $$\mathbf{x}_{\text{scent}}(t + \Delta t) = \mathbf{x}_{\text{scent}}(t) + \mathbf{v}_{\text{wind}} \cdot \Delta t$$
3. **Triệt tiêu mùi trong Lùm Cây Che Phủ (Thicket Suppression):**
   - Khi thỏ ở ngoài đồng cỏ: Độ đậm đặc hạt mùi danh định $\alpha_0 = 0.65$.
   - Khi thỏ ẩn nấp trong lùm cây: Lớp tán lá dày hấp phụ mùi, độ phát tán giảm $75\%$ xuống $\alpha = 0.18$.
   - Tốc độ phân rã hạt mùi trong lùm cây tăng gấp đôi, làm vệt mùi đứt gãy nhanh chóng.

### 6.2 Khứu Giác Săn Mồi Của Sói (Wolf Olfactory Tracking)
Sói là loài săn mồi chuyên biệt khứu giác:
$$\text{Bán kính đánh hơi } R_{\text{olfactory}} = 240\text{ px} \quad > \quad \text{Bán kính thị giác } R_{\text{vision}} = 150\text{ px}$$
1. **Điều kiện ngửi thấy con mồi:**
   $$\|\mathbf{p}_{\text{rabbit}} - \mathbf{p}_{\text{wolf}}\| \le R_{\text{scent\_eff}} \quad \land \quad \cos(\theta_{\text{wolf}\to\text{rabbit}} - \theta_{\text{wind}}) < -0.30$$
   *(Sói phải đứng ở vị trí xuôi gió hứng luồng khí từ con mồi thổi tới).*
2. **Khắc chế khứu giác bằng lùm cây (Thicket Camouflage):**
   - Nếu thỏ đang ẩn nấp trong lùm cây, phạm vi đánh hơi hiệu dụng $R_{\text{scent\_eff}}$ bị bóp nghẹt xuống còn **$1/3$ tầm nhìn của sói**:
     $$R_{\text{scent\_eff}}^{\text{cover}} \approx \frac{1}{3} R_{\text{vision}} \approx 50.0\text{ px}$$
   - Điều này buộc sói phải tiếp cận cực gần mép bụi rậm mới phát hiện được con mồi ẩn nấp.
3. **Loại bỏ phễu mùi nhân tạo (Zero Artificial Scent Funnel):**
   - Sói là động vật thu nhận mùi (olfactory receiver), hoàn toàn **không phát tán luồng khí hay phễu mùi ra môi trường**.
   - Toàn bộ hình vẽ phễu mùi rẻ quạt màu đỏ gắn ở đầu sói đã bị bãi bỏ; giao diện chỉ hiển thị các hạt mùi sinh học của thỏ (`scentParticles`) trôi tự nhiên theo gió.

### 6.3 Giác Quan Của Thỏ (Prey Visual Detection)
- Thỏ là loài ăn thực vật, **hoàn toàn không có năng lực ngửi mùi dã thú từ xa**.
- Thỏ chỉ phát hiện sói thuần túy qua **Thị Giác Trực Tiếp**:
  $$d_{\text{rabbit}\to\text{wolf}} \le R_{\text{rabbit\_vision}} = 110\text{ px}$$
- Khi sói ở ngoài $110\text{ px}$, thỏ hoàn toàn không biết sự hiện diện của thú săn và tiếp tục gặm cỏ bình thản.

---

## 7. Động Lực Học Săn Bắt & Lẩn Tránh (Locomotion & Predation Dynamics)

### 7.1 Trạng Thái Săn Mồi Của Sói (Wolf Hunting FSM)
Sói vận hành với 3 trạng thái hành vi tự nhiên:

1. **`PATROL` (Tuần Tra Lãnh Thổ):**
   - Di chuyển đều ($v \approx 50\text{ px/s}$) quanh các điểm nóng sinh thái (phía Đông hồ và rặng đá).
   - Duy trì thể lực nước rút: $\text{Stamina} = 100\%$.
2. **`STALK` (Rình Rập & Phục Kích):**
   - Kích hoạt khi: Sói ngửi thấy hoặc nhìn thấy thỏ, **nhưng thỏ chưa nhìn thấy sói** ($d > 60\text{ px}$ và thỏ chưa hoảng loạn).
   - Hành vi: Sói hạ thấp trọng tâm, di chuyển chậm rãi và lén lút ($v \approx 25\text{ px/s}$), tận dụng các lùm cây che phủ để rút ngắn cự ly mà không gây tiếng động. Hồi phục thể lực nước rút ($+0.15\%/\text{tick}$).
3. **`CHASE / LUNGE` (Truy Đuổi Bứt Tốc & Vồ Mồi):**
   - Kích hoạt khi: Thỏ phát hiện sói bỏ chạy HOẶC cự ly áp sát đã vào tầm vồ mồi ($d \le 60\text{ px}$).
   - Vận tốc chạy thẳng: $v_{\text{wolf}} \approx 125\text{ px/s}$ (vượt trội thỏ).
   - **Cú vồ bứt tốc (Pounce Lunge):** Khi cự ly $d \le 42\text{ px}$ và $\text{Stamina} > 20\%$, sói tung cú vồ với gia tốc cực đại (hệ số bứt phá $\times 1.45$).
   - Nhược điểm vật lý: Quán tính khối lượng lớn, bán kính quay đầu rộng, khó bẻ lái đột ngột.

### 7.2 Động Lực Học Lẩn Tránh Của Thỏ (Rabbit Agility & Jinking)
1. **Vận tốc cơ sở:** $v_{\text{rabbit}} \approx 95\text{ px/s}$ (chạy thẳng chậm hơn sói).
2. **Kỹ thuật đổi hướng zig-zag liên tục (Rapid Jinking Agility):**
   - Mỗi chu kỳ $16 \sim 28\text{ ticks}$ khi bị truy đuổi, thỏ thực hiện một cú bẻ góc đột ngột $60^\circ \sim 80^\circ$ vuông góc với vector chạy trốn.
   - Nhờ quán tính nhỏ, thỏ đổi hướng tức thì, khiến cú vồ mồi thẳng của sói bị trượt qua mục tiêu (overshoot).
3. **Hành vi ẩn nấp đóng băng (Freeze in Cover):**
   - Khi thỏ chạy thoát vào lùm cây, nó tự động giảm tốc độ $55\%$, chuyển sang trạng thái bất động ép sát mặt đất (`Freeze Stealth`), triệt tiêu âm thanh và luồng khí phát tán.
4. **Ngưỡng săn bắt thành công (Predation Catch Threshold):**
   $$d \le R_{\text{catch}} = 16.0\text{ px}$$
   Khi chạm ngưỡng $16\text{ px}$, cú vồ mồi thành công: thỏ tử vong, sói reset cơn đói về $0\%$, nạp đầy năng lượng $100\%$ và tăng chỉ số chiến tích `killCount`.

### 7.3 Cơ Chế Chạy Trốn & Ưu Tiên Tìm Chỗ Trốn (Cover-Seeking Evasion & Escape Protocol)
Thỏ không chỉ bỏ chạy hỗn loạn ra khoảng trống vô định mà tuân thủ tập tính sinh tồn tự nhiên **chạy tìm nơi ẩn nấp**:
1. **Ngưỡng Báo Động Phân Hóa Theo Địa Hình:**
   - Khi ở địa hình quang đãng: thỏ phát hiện sói ở cự ly thị giác $110\text{ px}$ và lập tức kích hoạt bỏ chạy.
   - Khi đã nấp trong lùm cây (`inCover = true`): thỏ giữ trạng thái bất động (`Freeze Stealth`), ngưỡng bay trốn (flight threshold) rút ngắn xuống còn $42\text{ px}$. Thỏ sẽ không tự động phóng ra ngoài nếu sói chưa thực sự bước vào bụi rậm.
2. **Thuật Toán Tìm Nơi Trú Ẩn An Toàn Tối Ưu (Optimal Safe Cover Evaluation):**
   - Khi bị phát hiện, thỏ quét toàn bộ $7$ vị trí trú ẩn trên bản đồ (Hang Thỏ và $6$ lùm cây che phủ).
   - **Tiêu chí an toàn:** Nơi trú ẩn phải có góc hướng dạt xa sói ($\mathbf{u}_{\text{cover}} \cdot \mathbf{u}_{\text{away}} > -0.35$) và sói không đứng chặn đường ($d_{\text{wolf}\to\text{cover}} > 45\text{ px}$).
   - **Chấm điểm:** Ưu tiên khoảng cách gần, độ thẳng hàng với vector thoát hiểm và điểm thưởng cho Hang Thỏ ($+120\text{ pts}$).
3. **Tổng Hợp Vector Chạy Trốn (Combined Escape Steering):**
   - Hướng thoát hiểm $\mathbf{F}_{\text{flee}}$ kết hợp giữa lực đẩy xa dã thú ($\mathbf{u}_{\text{away}}$) và lực hút hướng tâm về lùm cây an toàn ($\mathbf{u}_{\text{cover}}$):
     $$\mathbf{F}_{\text{flee}} = w_{\text{away}} \cdot \mathbf{u}_{\text{away}} + w_{\text{cover}} \cdot \mathbf{u}_{\text{cover}}$$
     Trong đó, khi sói áp sát nguy cấp ($d \le 42\text{ px}$): $w_{\text{away}} = 0.65$ (ưu tiên né đòn vồ); khi ngoài cự ly vồ: $w_{\text{cover}} = 0.70$ (lao thẳng về lùm cây).
   - Cộng hưởng cú bẻ góc zig-zag ngẫu nhiên $60^\circ \sim 80^\circ$ trên từng nhịp $16 \sim 28\text{ ticks}$.
4. **Cắt Đuôi & Thoát Hiểm Thành Công (Predation Loss In Cover):**
   - Khi thỏ lặn vào phạm vi lùm cây ($d \le R_{\text{thicket}}$), vết mùi và hình ảnh bị triệt tiêu $75\%$.
   - Sói chỉ ngửi/nhìn thấy thỏ trong lùm cây ở cự ly $\le 48\text{ px}$. Nếu sói cách xa $> 50\text{ px}$, sói mất hoàn toàn tín hiệu con mồi, hủy trạng thái `CHASE` và quay về `PATROL`. Thỏ trốn thoát thành công và ghi nhận telemetry `[BẢN NĂNG SINH TỒN]`.

---

## 8. Cân Bằng Sinh Thái Quần Thể (Lotka-Volterra Population Lifecycle)

Mô phỏng tích hợp mô hình động lực học quần thể phân hóa rõ rệt giữa loài $r$-strategist (thỏ) và loài $K$-strategist (sói):

### 8.1 Quần Thể Thỏ ($r$-strategist: Tăng Trưởng Nhanh, Chủ Động Kiếm Ăn)
- **Tử vong do đói khát (Starvation Mortality):**
  - Trao đổi chất cao: Nếu mức đói $H_i \ge 100\%$, sinh lực bắt đầu suy giảm nhanh ($-0.20\%/\text{tick}$). Khi $\Omega_i = 0$, cá thể tử vong và bị đào thải khỏi đàn.
- **Hành vi chủ động kiếm ăn (Active Foraging Hierarchy):**
  - Thỏ không di chuyển ngẫu nhiên vô định; mục tiêu sinh tồn cốt lõi là duy trì độ no để giao phối và phát triển bầy đàn:
    1. *Khát nước ($T_i > 45\%$):* Điều hướng trực tiếp tới bờ nông hồ nước trung tâm.
    2. *Đói / Hái lượm ($H_i > 18\%$):* Quét tìm bụi dâu chưa cạn kiệt hoặc vạt bồ công anh. Khi đói ($H_i > 35\%$), mở rộng phạm vi dò xét trên toàn bộ bản đồ.
    3. *No nê & Tụ đàn sinh sản ($H_i \le 18\% \land T_i \le 45\%$):* Tụ đàn về Hang Trú Ẩn $[320, 520]$ hoặc đồng cỏ ven hồ để chải lông, duy trì cự ly bầy đàn và ghép đôi.
- **Sinh sản tăng tốc (Accelerated Reproduction):**
  - Chu kỳ kiểm tra: Mỗi $140\text{ ticks}$ ($\approx 7\text{ s}$).
  - Điều kiện sinh sản:
    $$\bar{H}_{\text{colony}} < 50\% \quad \land \quad (\sum \text{Berry}_{\text{available}} \ge 15\text{ u} \lor \text{Herbs} \ge 20\text{ u}) \quad \land \quad N_{\text{rabbits}} < 36$$
  - Kích thước lứa sinh (Litter Size): Sinh $2$ thỏ con nếu đàn rất no ($\bar{H} < 30\%$) và tài nguyên dồi dào ($> 80\text{ u}$); sinh $1$ thỏ con nếu mức no trung bình.
  - Ghi nhận viễn thám: `LotkaVolterra: r-strategist accelerated reproduction`.

### 8.2 Quần Thể Sói ($K$-strategist: Bền Bỉ, Săn Mồi & Tái Cấu Trúc Đàn)
- **Sức chịu đựng cao:** Tốc độ trao đổi chất của sói bền hơn thỏ ($0.012\%/\text{tick}$ vs $0.018\%/\text{tick}$), có thể nhịn đói qua hàng ngàn tick mà không tử vong.
- **Tử vong do tuyệt diệt con mồi (Predator Starvation Extinction):**
  - Khi đàn thỏ bị tuyệt diệt hoàn toàn, sói không còn con mồi để săn bắt. Mức đói $H_{\text{wolf}}$ tăng chạm $100\%$ ($\text{Satiety} = 0\%$).
  - Sinh lực tụt dốc ($-0.08\%/\text{tick}$). Khi $\Omega_{\text{wolf}} = 0$, sói chết vì kiệt sức và bị loại khỏi bản đồ. Sói **tuyệt đối không thể tự tăng độ no khi không có thức ăn**.
- **Sinh sản tăng tốc & Quy mô đàn:**
  - Ngưỡng tích lũy calo giảm xuống $2$ lần săn bắt thành công (`killCount >= 2`).
  - Hạn mức tối đa đàn sói mở rộng lên tới $4$ con ($N_{\text{wolves}} \le 4$).
  - Cá thể sói con trưởng thành (`Wolf #02`, `Wolf #03`, `Wolf #04`) xuất hiện tại Cột Mốc Hang Sói $[910, 130]$, tuần tra và săn mồi độc lập.

### 8.3 Cơ Chế Mở Rộng Phạm Vi Dò Xét Khi Độ No Giảm Sút (Dynamic Sensory Expansion)
- **Sói (Predator):**
  - Khi no nê ($H \le 35\%$, độ no $\ge 65\%$): Tầm nhìn cơ sở $150\text{ px}$, bán kính ngửi mùi $240\text{ px}$, tuần tra bán kính hẹp quanh lãnh thổ.
  - Khi đói bụng ($H > 35\%$): Giác quan khứu giác và thị giác tăng cường độ nhạy bén tỷ lệ thuận với cơn đói:
    $$R_{\text{vision, effective}} = R_{\text{vision, base}} \times \left(1.0 + \min\left(0.50, \frac{H - 35}{65} \times 0.50\right) \times 0.80\right) \le 210\text{ px}$$
    $$R_{\text{scent, effective}} = R_{\text{scent, base}} \times \left(1.0 + \min\left(0.50, \frac{H - 35}{65} \times 0.50\right)\right) \le 360\text{ px}$$
  - Khi đói kiệt sức ($H > 50\%$): Quỹ đạo tuần tra mở rộng từ góc Đông Bắc quét sâu qua trung tâm đồng cỏ ven hồ ($[560 \pm 260, 340 \pm 170]$) để tích cực tầm soát con mồi.
- **Thỏ (Prey):**
  - Khi đói ($H > 25\%$): Cảnh giác thị giác mở rộng từ $95\text{ px}$ lên tới $138\text{ px}$ (Scout từ $130\text{ px}$ lên $188\text{ px}$).
  - Khi $H > 35\%$: Vùng quét tìm thức ăn mở rộng không giới hạn ($250\text{ px} \to \text{Toàn bản đồ}$), chủ động tìm tới các bụi dâu hoặc bồ công anh còn trữ lượng.

---

## 9. Phân Định Sức Chứa Hang Trú Ẩn & Vai Trò Alpha Scout

### 9.1 Sức Chứa Hang ($C_{\text{burrow}} = 16$), Cơ Chế Chui Vào Hang & Giao Thức Tràn
- **Sức chứa giới hạn:** Hang chỉ chứa tối đa $C_{\text{burrow}} = 16$ cá thể thỏ.
- **Cơ chế chủ động chạy vào hang khi bị sói săn bắt (Burrow Sanctuary Escape):**
  1. *Cảnh báo bầy đàn (Acoustic Foot-Thumping Alarm):* Khi sói phát hiện hoặc lao vào rượt đuổi một cá thể thỏ, thỏ dậm chân cảnh báo nguy hiểm. Các cá thể lân cận trong bán kính $135\text{ px}$ lập tức chuyển sang trạng thái cảnh giác cao độ (`seesWolf = true`).
  2. *Định hướng trú ẩn tối cao:* Nếu hang còn chỗ ($N_{\text{sheltered}} < 16$) và hướng chạy không bị sói chặn ngang mặt ($\text{alignment} > -0.55$), thỏ ưu tiên tuyệt đối ($+450\text{ điểm}$, trọng số hướng tâm $85\%$) bứt tốc chạy thẳng về phía Hang Trú Ẩn $[320, 520]$.
  3. *Hành động chui vào hang (Burrow Dive):* Khi tiếp cận miệng hang ($d \le R_{\text{burrow}} + 10\text{ px} \approx 42\text{ px}$), thỏ lập tức lặn sâu vào lòng đất (`isSheltered = true`, `state = 'SHELTERED'`).
  4. *Miễn nhiễm hoàn toàn trước thú săn:* Cá thể trong hang được bảo vệ $100\%$ dưới lòng đất; sói không thể nhìn, ngửi hay chạm tới thỏ. Sói đến miệng hang sẽ mất dấu con mồi, hủy lệnh `CHASE` và quay về `PATROL`.
  5. *Quan sát an toàn & Rời hang:* Khi sói đã rời xa bán kính an toàn ($d_{\text{wolf}} > 160\text{ px}$) và hết thời gian cảnh giới ngầm ($\approx 8 - 14\text{ s}$), thỏ an toàn bước ra khỏi miệng hang để tiếp tục gặm dâu và ăn cỏ.
- **Giao thức điều phối tràn (Overflow Protocol):**
  - Khi hang đã đầy $16/16$ cá thể: Những cá thể thỏ đến sau hoặc ở quá xa hang tự động kích hoạt điều phối tràn, chuyển hướng chạy tản mác vào $6$ lùm cây rậm rạp gần nhất để ẩn nấp tĩnh (Freeze Stealth), tránh tập trung đông đúc trước cửa hang.

### 9.2 Phân Quyền Hữu Hạn Của Alpha Scout
- **Không phải điều khiển tập trung:** Scout là một cá thể thỏ có trí khôn và giác quan định hướng, không sở hữu quyền năng điều khiển toạ độ vật lý của các cá thể khác.
- **Cơ chế phát tín hiệu dẫn đường (Directive Stigmergy):**
  - Scout dẫn đầu đường đi bằng cách di chuyển và phát pheromone/tiếng kêu trong bán kính $R_{\text{broadcast}} = 200\text{ px}$.
  - Các cá thể xung quanh phản hồi theo quy tắc boids đàn (Flock alignment & cohesion).
  - Bản năng sinh tồn cá thể (`flee_predator`) luôn được ưu tiên cao nhất: nếu sói áp sát một con thỏ, con thỏ đó sẽ lập tức bỏ chạy zig-zag, bất chấp chỉ thị của Scout.

---

## 10. Kiến Trúc Giao Diện Công Thái Học & HMI Bảng Điều Khiển

Tuân thủ triết lý tối giản và công thái học nhận thức (UI/UX Pro Max):

1. **Bộ Điều Khiển Tốc Độ Thông Minh (Adaptive Speed Popover):**
   - Nút trigger hiển thị tốc độ thực tế tức thời (`1.00x ▾`) với font Fira Code monospace.
   - Trình đơn thả xuống tích hợp 2 cơ chế tương tác:
     - **Thanh trượt liên tục (Continuous Range Slider):** Kéo thả mượt mà từ $0.10\times$ đến $5.00\times$.
     - **Lưới chọn nhanh 6 mức (Preset Chips):** $0.25\times$ (Siêu chậm), $0.50\times$ (Chậm), $0.75\times$ (Mượt), $1.00\times$ (Chuẩn), $2.00\times$ (Tua nhanh), $5.00\times$ (Siêu tốc).
     - **Phản hồi thời gian thực:** Cập nhật ngay số tick tính toán trên giây ($\text{ticks/s}$) và ghi chú mục đích quan sát.
2. **Menu Dropdown `Can Thiệp ▾` (Operator Interventions):**
   - Đóng gói toàn bộ 7 tác vụ can thiệp vào một trình đơn thả xuống có kiểm soát:
     - `Đổi Hướng Gió (90°)`: Thay đổi vector khuếch tán mùi tức thời.
     - `Bật/Tắt Mưa Rào`: Giảm tầm nhìn và xóa sạch vệt mùi trên mặt đất.
     - `Khí Hậu: Hạn Hán Vi Phân`: Mô phỏng hạn hán tự nhiên làm bay hơi tài nguyên.
     - `Thả Sói Phục Kích`: Kiểm tra phản ứng đa mối đe dọa.
     - `Lệnh Bầy Đàn: Bật/Tắt Nghỉ Ngơi`: Phát chỉ thị toàn bầy đàn dừng di chuyển, ưu tiên hồi phục thể lực nếu không bị đói.
     - `Standby (Chờ Can Thiệp)`: Can thiệp khẩn cấp đưa hệ sinh thái về trạng thái an toàn.
3. **Menu Dropdown `Lớp Bản Đồ ▾` (Viewport Layer Filtering):**
   - Đóng gói 9 công tắc hiển thị lớp vào dropdown dạng checkbox: Bãi Cỏ, Tầm Nhìn, Vệt Mùi, Khí Quyển, Mối Nguy, Trục Toạ Độ, Lưới Kiến Trúc, Hang & Lùm Cây, Rặng Đá.
   - Giải phóng hoàn toàn thanh chip nổi phía trên canvas, tạo không gian quan sát chuẩn học thuật.
4. **Đồng Hồ Đo Sinh Học Trực Quan (Intuitive Physiological Gauges) & Trạng Thái Cá Thể:**
   - Sửa đổi toàn diện các chỉ số: hiển thị **Độ No (Satiety)** và **Độ Ẩm Nước (Hydration)** từ $100\% \to 0\%$, đi kèm màu sắc tương thích (Xanh lục khi no $> 50\%$, Vàng hổ phách khi thiếu $25-50\%$, Đỏ báo động kiệt sức $< 25\%$).
   - Triệt tiêu hoàn toàn nghịch lý hiển thị "đói tăng nhưng nhãn ghi no".
   - **Chỉ Báo Bứt Tốc & Huy Hiệu Trạng Thái:** Hiển thị số lượt bứt tốc khả dụng (`Bứt tốc: 3/3 lần` vs `Chỉ còn 1 lần bứt tốc!` vs `⚠️ Kiệt Sức!`), huy hiệu trạng thái (`HOẠT ĐỘNG`, `💤 ĐANG NGHỈ NGƠI`, `⚠️ KIỆT SỨC`, `⚡ RƯỢT ĐUỔI / BỎ CHẠY`), và nút can thiệp cá thể `💤 Nghỉ Ngơi / ⚡ Đánh Thức`.
5. **Telemetry Strip Đa Quần Thể:**
   - Bổ sung bộ đếm `Đàn Sói` trực quan cạnh `Đàn Thỏ` và `Trữ Lượng Dâu` để theo dõi cân bằng Lotka-Volterra theo thời gian thực.
   - Giữ nguyên hiển thị quang đãng danh định `☀️ BAN NGÀY` (tạm dừng chu kỳ ngày/đêm theo yêu cầu).

---

## 11. Kịch Bản Kiểm Chứng Định Lượng

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

---

## 12. Cơ Chế Năng Lượng Chuyển Hóa, Giới Hạn Bứt Tốc & Chế Độ Nghỉ Ngơi

### 12.1 Tạm Dừng Chu Kỳ Ngày / Đêm (Day/Night Pause)
Theo yêu cầu thiết kế giao diện và kiểm thử nhận thức, chu kỳ sáng / tối được vô hiệu hóa hoàn toàn:
- Môi trường duy trì điều kiện chiếu sáng quang đãng danh định ($100\%$ daylight visibility).
- Triệt tiêu các lớp overlay làm tối canvas vào ban đêm, giúp theo dõi sát sao biểu hiện vận động và thể lực của từng cá thể.

### 12.2 Chuyển Hóa Năng Lượng & Ràng Buộc Dinh Dưỡng Thực Tế (Nutrition Gate)
Năng lượng thể lực ($E_i \in [0, 100]\%$) không thể tự sinh ra từ hư vô mà bắt buộc phải chuyển hóa từ dinh dưỡng thức ăn trong cơ thể (ATP Synthesis):
1. **Tiêu hao năng lượng:**
   - **Trạng thái bình thường (`NORMAL` / `PATROL` / `STALK`):** Vận động nhẹ tiêu hao cực thấp ($\dot{E}_{\text{base}} = -0.004\% \sim -0.005\%/\text{tick}$).
   - **Bứt tốc rượt đuổi / bỏ chạy (`CHASE` / `FLEE`):** Tiêu hao thể lực cực mạnh ($\dot{E}_{\text{sprint}} = -0.18\% \sim -0.25\%/\text{tick}$).
2. **Ràng buộc dinh dưỡng khi hồi phục (Nutrition Gate Invariant):**
   - Năng lượng **CHỈ CÓ THỂ HỒI PHỤC KHI CÁ THỂ KHÔNG BỊ ĐÓI**:
     $$H_i < 60\% \quad (S_i = \text{Satiety} > 40\%)$$
   - Nếu $H_i \ge 60\%$ (đói bụng kiệt quệ): Cơ thể không còn calo dự trữ để tái tạo ATP; quá trình hồi phục năng lượng bị chặn hoàn toàn ($\dot{E}_{\text{regen}} = 0$).
3. **Tốc độ hồi phục theo trạng thái:**
   - **Bình thường:** Hồi phục chậm ($\dot{E}_{\text{regen}} = +0.02\%/\text{tick}$) nếu $H_i < 50\%$.
   - **Nghỉ ngơi (`REST`):** Đứng yên, tập trung toàn bộ trao đổi chất để hồi phục nhanh ($\dot{E}_{\text{rest}} = +0.14\%/\text{tick}$) nếu $H_i < 60\%$.
   - **Gặm dâu / Uống nước:** Bổ sung calo trực tiếp giúp nạp ngay $+0.04\% \sim +0.08\%$ năng lượng.

### 12.3 Giới Hạn Bứt Tốc Dưới 40% Năng Lượng & Phạt Kiệt Sức
Triệt tiêu hoàn toàn hiện tượng phi thực tế "cạn kiệt thể lực nhưng vẫn chạy như bay":
1. **Ngưỡng Năng Lượng $E_i < 40\%$:**
   - Khi năng lượng tụt xuống dưới $40\%$, cá thể (cả thỏ lẫn sói) **chỉ còn duy nhất 1 lần bứt tốc cuối cùng**:
     $$E_i < 40\% \implies \text{sprintsRemaining} = \min(\text{sprintsRemaining}, 1)$$
2. **Hết lượt bứt tốc HOẶC Năng lượng $E_i < 15\%$ (Trạng Thái Kiệt Sức - `isExhausted`):**
   - Khi dùng hết cú bứt tốc duy nhất hoặc năng lượng tụt dưới $15\%$, cá thể rơi vào trạng thái **Kiệt Sức**:
     $$\text{isExhausted} = \text{true}$$
   - **Phạt vận tốc thực tế ($\sim 60\%$ Speed Penalty):**
     - Sói kiệt sức: Gia tốc truy đuổi bị giảm từ $1.15 \to 0.42$ ($63\%$ penalty). Sói thở dốc, bước chân nặng nề, không thể lao vào vồ mồi.
     - Thỏ kiệt sức: Lực chạy trốn bị giảm từ $0.85 \to 0.32$ ($62\%$ penalty). Thỏ mất khả năng bẻ góc zig-zag tốc độ cao.
     - Nếu năng lượng chạm đáy $0\%$, việc tiếp tục gắng gượng chạy trốn sẽ bào mòn trực tiếp sinh lực máu ($\Omega_i \mathrel{-}= 0.10\%/\text{tick}$).

### 12.4 Chế Độ Nghỉ Ngơi (Resting System & Operator Control)
1. **Nghỉ ngơi tự nhiên (Autonomous Rest):**
   - Khi $E_i < 25\%$ nhưng không bị đói ($H_i < 60\%$) và ở trong vùng an toàn (trong lùm cây hoặc cạnh hang đối với thỏ, không thấy con mồi đối với sói), cá thể tự động chuyển sang `REST`.
   - Khi năng lượng hồi phục đạt $E_i \ge 85\% \sim 90\%$, cá thể tự động thức dậy trở lại hoạt động bình thường.
   - Thỏ đang ngủ nếu phát hiện sói áp sát trong cự ly $110\text{ px}$ sẽ lập tức hoảng sợ thức giấc để bỏ chạy.
2. **Can thiệp điều khiển (Operator Action):**
   - **Can thiệp cá thể:** Nút `💤 Nghỉ Ngơi` / `⚡ Đánh Thức` trên Inspector panel cho phép người vận hành cưỡng chế cá thể được chọn vào hoặc thoát khỏi chế độ dưỡng sức.
   - **Chỉ thị quần thể:** Nút `Lệnh Bầy Đàn: Bật/Tắt Nghỉ Ngơi` trong dropdown `Can Thiệp ▾` phát lệnh trên toàn đàn thỏ, buộc cả bầy dừng kiếm ăn và tập trung nạp lại thể lực.
3. **Hiển thị trực quan:**
   - Cá thể đang nghỉ ngơi hiển thị ký hiệu `zZ` bồng bềnh màu xanh lam phía trên đầu.
   - Cá thể kiệt sức hiển thị dấu báo hiệu `⚡0` màu đỏ hồng.

---

## 13. Vật Cản Địa Hình Tuyệt Đối (Rặng Đá, Lòng Hồ Sâu) & Kiểm Soát Vận Tốc Thực

### 13.1 Vật Cản Địa Hình Tuyệt Đối & Chống Dịch Chuyển Tức Thời (Anti-Teleport Collision Resolution)
Để loại bỏ triệt để hiện tượng đi xuyên vật cản (clipping) hoặc bị bắn văng/dịch chuyển tức thời (teleportation) do lỗi chiếu bán kính elip:
1. **Rặng Đá Granit (Step-Back Boundary Resolution):**
   - Mỗi khối đá được mô hình hóa dưới dạng elip quay góc $\theta$ với bán trục $r_x, r_y$:
     $$\mathbf{x}_{\text{local}} = \mathbf{R}(-\theta) \cdot (\mathbf{x}_{\text{ent}} - \mathbf{x}_{\text{rock}})$$
     $$q = \left(\frac{x_{\text{local}}}{r_x + r_{\text{ent}}}\right)^2 + \left(\frac{y_{\text{local}}}{r_y + r_{\text{ent}}}\right)^2$$
   - Khi $q < 1.0$ (chạm đá):
     - **Thuật toán Step-Back:** Vị trí cá thể lập tức được hoàn nguyên về bước trước đó ($\mathbf{x}_{\text{prev}}$). Nếu không có tọa độ trước, chiếu tọa độ theo phương trình chuẩn tắc:
       $$\alpha = \text{atan2}(y_{\text{local}} \cdot a, x_{\text{local}} \cdot b), \quad x_{\text{target}} = a \cos\alpha, \quad y_{\text{target}} = b \sin\alpha$$
       Giới hạn khoảng cách tuyệt đối trong kích thước đá ($\le 65\text{ px}$), triệt tiêu $100\%$ hiện tượng phóng đại tọa độ.
     - Phản lực mềm ($v \mathrel{*}= -0.2$) giúp cá thể dội nhẹ và trượt men theo rìa ngoài của đá.
2. **Lòng Hồ Nước Sâu (Impassable Deep Water Basin):**
   - Hồ nước trung tâm có bán kính tổng $R = 105\text{ px}$.
   - **Vùng bờ nông ($r \in [68\text{ px}, 120\text{ px}]$):** Nơi các cá thể đứng uống nước. Thỏ sinh sản và bầy đàn ban đầu được khởi tạo an toàn ở vùng đồng cỏ ngoài hồ ($d > 115\text{ px}$).
   - **Lòng hồ nước sâu ($r \le R_{\text{deep}} = 105 \times 0.65 = 68.25\text{ px}$):** Cấm đi vào; nếu tiếp cận sẽ bị hoàn nguyên bước và phản hồi trượt tiếp tuyến men theo mép bờ hồ.

### 13.2 Giới Hạn Vận Tốc Sinh Học Thực Tế (Strict Velocity Clamping)
Triệt tiêu hiện tượng sói hay thỏ bị kéo về với tốc độ phi lý sau va chạm:
- **Sói:** $v_{\max} = 3.0\text{ px/tick}$ khi tuần tra/bình thường; $v_{\max} = 5.2\text{ px/tick}$ khi rượt đuổi; $v_{\max} = 1.5\text{ px/tick}$ khi kiệt sức.
- **Thỏ:** $v_{\max} = 2.4\text{ px/tick}$ khi gặm cỏ; $v_{\max} = 4.4\text{ px/tick}$ khi bỏ chạy; $v_{\max} = 1.4\text{ px/tick}$ khi kiệt sức.
- Vận tốc di chuyển trở về lãnh thổ không bao giờ được vượt quá tốc độ săn bắt danh định.

### 13.3 Trạng Thái Hố Sụt Karst (Deferred Hazard Status)
- Theo chỉ thị của người vận hành, cơ chế Hố sụt (Sinkhole) và nhãn chữ liên quan tạm thời được gỡ bỏ hoàn toàn khỏi bản đồ mô phỏng để tinh gọn không gian quan sát hành vi bầy đàn thuần túy. Cơ chế này sẽ được hoàn thiện và tái tích hợp ở giai đoạn sau.
