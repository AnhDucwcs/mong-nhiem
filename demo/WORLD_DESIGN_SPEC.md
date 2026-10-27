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

---

## 8. Cân Bằng Sinh Thái Quần Thể (Lotka-Volterra Population Lifecycle)

Mô phỏng tích hợp mô hình động lực học quần thể phân hóa rõ rệt giữa loài $r$-strategist (thỏ) và loài $K$-strategist (sói):

### 8.1 Quần Thể Thỏ ($r$-strategist: Tăng Trưởng Nhanh, Tử Vong Nhanh)
- **Tử vong do đói khát (Starvation Mortality):**
  - Trao đổi chất cao: Nếu mức đói $H_i \ge 100\%$, sinh lực bắt đầu suy giảm nhanh ($-0.25\%/\text{tick}$). Khi $\Omega_i = 0$, cá thể tử vong và bị đào thải khỏi đàn.
- **Sinh sản nhanh (Rapid Reproduction):**
  - Điều kiện: Cứ mỗi $320\text{ ticks}$ ($\approx 16\text{ s}$), nếu:
    $$\bar{H}_{\text{colony}} < 45\% \quad \land \quad \sum \text{Berry}_{\text{available}} > 25\text{ u} \quad \land \quad N_{\text{rabbits}} < 30$$
  - Thỏ mẹ tại Hang Trú Ẩn sẽ sinh thêm 1 thỏ con mới ($E = 90\%, H = 20\%, \Omega = 100\%$).
  - Ghi nhận viễn thám: `LotkaVolterra: r-strategist population growth`.

### 8.2 Quần Thể Sói ($K$-strategist: Bền Bỉ, Tái Cấu Trúc Chậm)
- **Sức chịu đựng cao:** Tốc độ tiêu hóa của sói chậm gấp $4$ lần thỏ, có thể nhịn đói qua hàng ngàn tick mà không tử vong.
- **Sinh sản dựa trên năng lượng tích lũy:**
  - Sói chỉ sinh sản khi tích lũy đủ calo từ $3$ lần săn mồi thành công (`killCount >= 3`).
  - Khi thỏa mãn điều kiện và đàn sói $< 2$ con: Một cá thể sói con trưởng thành (`Wolf #02`) sẽ gia nhập bản đồ tại vùng rừng phía Đông.

---

## 9. Phân Định Sức Chứa Hang Trú Ẩn & Vai Trò Alpha Scout

### 9.1 Sức Chứa Hang ($C_{\text{burrow}} = 16$) & Giao Thức Tràn Sang Lùm Cây
- Hang chỉ chứa tối đa $16$ cá thể thỏ.
- Với quy mô đàn khởi điểm $24$ cá thể (hoặc khi tăng đàn), $8$ cá thể ngoài định mức không thể vào hang khi có chuông báo động.
- **Giao thức điều phối tràn (Overflow Protocol):**
  1. $16$ cá thể gần hang nhất được cấp quyền trú ẩn an toàn tuyệt đối bên trong hang.
  2. Các cá thể còn lại tự động tính toán khoảng cách tới $6$ lùm cây che phủ gần nhất và chạy tản mác vào lùm cây, kích hoạt ẩn nấp $85\%$.
  3. Phân tán rải rác triệt tiêu rủi ro bị sói gom bắt cả bầy tại cửa hang.

### 9.2 Phân Quyền Hữu Hạn Của Alpha Scout
- **Không phải điều khiển tập trung:** Scout là một cá thể thỏ có trí khôn và giác quan định hướng, không sở hữu quyền năng điều khiển toạ độ vật lý của các cá thể khác.
- **Cơ chế phát tín hiệu dẫn đường (Directive Stigmergy):**
  - Scout dẫn đầu đường đi bằng cách di chuyển và phát pheromone/tiếng kêu trong bán kính $R_{\text{broadcast}} = 200\text{ px}$.
  - Các cá thể xung quanh phản hồi theo quy tắc boids đàn (Flock alignment & cohesion).
  - Bản năng sinh tồn cá thể (`flee_predator`) luôn được ưu tiên cao nhất: nếu sói áp sát một con thỏ, con thỏ đó sẽ lập tức bỏ chạy zig-zag, bất chấp chỉ thị của Scout.

---

## 10. Kiến Trúc Giao Diện Công Thái Học & HMI Bảng Điều Khiển

Tuân thủ triết lý tối giản và công thái học nhận thức (Cognitive Ergonomics):

1. **Menu Dropdown `Can Thiệp ▾` (Operator Interventions):**
   - Đóng gói toàn bộ 6 tác vụ can thiệp vào một trình đơn thả xuống có kiểm soát:
     - `Đổi Hướng Gió (90°)`: Thay đổi vector khuếch tán mùi tức thời.
     - `Bật/Tắt Mưa Rào`: Giảm tầm nhìn và xóa sạch vệt mùi trên mặt đất.
     - `Shock: Ép Cạn Lương (0u)`: Cưỡng bức tài nguyên về 0 để thử thách SLM.
     - `Shock: Thả Thêm Sói`: Kiểm tra phản ứng đa mối đe dọa.
     - `Shock: Xóa Sổ Đàn Sói`: Đưa hệ sinh thái về trạng thái an toàn.
     - `Standby (Chờ Can Thiệp)`: Reset trạng thái can thiệp.
2. **Menu Dropdown `Lớp Bản Đồ ▾` (Viewport Layer Filtering):**
   - Đóng gói 9 công tắc hiển thị lớp vào dropdown dạng checkbox: Bãi Cỏ, Tầm Nhìn, Vệt Mùi, Khí Quyển, Mối Nguy, Trục Toạ Độ, Lưới Kiến Trúc, Hang & Lùm Cây, Rặng Đá.
   - Giải phóng hoàn toàn thanh chip nổi phía trên canvas, tạo không gian quan sát chuẩn học thuật.
3. **Telemetry Strip Đa Quần Thể:**
   - Bổ sung bộ đếm `Đàn Sói` trực quan cạnh `Đàn Thỏ` và `Trữ Lượng Dâu` để theo dõi cân bằng Lotka-Volterra theo thời gian thực.

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
