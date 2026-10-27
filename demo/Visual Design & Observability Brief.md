# Mộng Nhiễm Demo — Visual Design & Observability Brief

## 1. Mục tiêu thiết kế

Thiết kế giao diện demo Mộng Nhiễm theo hướng **Abstract Top-Down Living World**: một thế giới mô phỏng nhìn từ trên xuống, được biểu diễn bằng các hình khối hình học và những nhóm điểm nhỏ, thay vì đồ họa sinh thái chi tiết hoặc hình ảnh động vật chân thực.

Đây không phải một trò chơi sinh tồn thông thường. Mục tiêu là giúp người xem quan sát một thế giới đang vận hành, nhận biết những thay đổi trong thế giới, hiểu những vấn đề mà các thực thể đang gặp phải, đánh giá các quyết định và theo dõi hậu quả của chúng. Giao diện phải thể hiện được giá trị của Mộng Nhiễm thông qua các sự kiện có thể kiểm chứng, không chỉ thông qua hiệu ứng hình ảnh.

Ưu tiên theo thứ tự:
1. Khả năng quan sát toàn bộ thế giới và những biến động quan trọng.
2. Khả năng hiểu trạng thái, hành vi và mối quan hệ giữa các thực thể.
3. Khả năng quan sát sự khác biệt giữa trạng thái thực và thông tin mà thực thể đang biết.
4. Khả năng theo dõi quyết định, sự can thiệp của Mộng Nhiễm và hậu quả thực tế.
5. Tính thẩm mỹ, chuyển động mượt và trải nghiệm tương tác.

## 2. Ngôn ngữ đồ họa của thế giới

### Góc nhìn và hình thức

- Sử dụng góc nhìn top-down 2D trực tiếp từ trên xuống.
- Thế giới được vẽ bằng hình học đơn giản: hình tròn, chấm nhỏ, đường viền, vùng màu và các đa giác cơ bản.
- Không sử dụng mô hình động vật chi tiết, sprite hoạt hình phức tạp hoặc phong cách photorealistic.
- Không cần mô phỏng từng chiếc lá, cọng cỏ hay chi tiết bề mặt.
- Tập trung vào bố cục rõ ràng, tương phản màu hợp lý, chuyển động dễ theo dõi và khả năng biểu diễn mật độ của quần thể.
- Có thể sử dụng hiệu ứng chuyển động nhẹ, vùng sáng, đường đi và lớp phủ trạng thái, nhưng tránh hiệu ứng trang trí làm nhiễu dữ liệu.

Phong cách mong muốn nằm giữa bản đồ mô phỏng khoa học và một thế giới nhân tạo có tính thẩm mỹ. Nó phải tối giản nhưng không khô khan, dễ đọc nhưng vẫn tạo cảm giác một hệ thống sống đang vận hành.

### Biểu diễn môi trường và tài nguyên

Sử dụng các vùng màu hoặc hình khối để biểu diễn địa hình, khu vực sinh sống, nước, vật cản và tài nguyên.

Ví dụ:
- Cây thông thường: hình tròn hoặc cụm hình tròn màu xanh.
- Cây berry: cụm xanh có một số chấm đỏ để phân biệt.
- Nguồn nước: vùng màu xanh lam; diện tích, độ đậm hoặc một chỉ báo nhỏ thể hiện lượng nước còn lại.
- Đá và vật cản: hình đa giác hoặc hình vuông màu trung tính.
- Vùng nguy hiểm: đường viền hoặc lớp phủ bán trong suốt.
- Tài nguyên cạn kiệt: số lượng dấu hiệu tài nguyên giảm hoặc trạng thái hiển thị chuyển đổi rõ ràng.

Tài nguyên phải thay đổi trực quan khi trạng thái mô phỏng thay đổi. Ví dụ, nếu thức ăn bị tiêu thụ, các dấu hiệu thức ăn phải giảm; nếu nguồn nước cạn, mức nước hoặc chỉ báo tương ứng phải thay đổi.

Không chỉ thay đổi con số trong bảng dữ liệu trong khi bản đồ vẫn giữ nguyên hình ảnh cũ.

### Biểu diễn cá thể và quần thể

Mỗi cá thể là một dấu hiệu hình học nhỏ có vị trí độc lập. Một quần thể gồm nhiều dấu hiệu tương tự cùng tồn tại và di chuyển trong bản đồ.

Ví dụ:
- Thỏ: các chấm nhỏ màu nâu vàng.
- Sói: các chấm nhỏ màu xám.
- Cá thể đặc biệt: kích thước lớn hơn, hình dạng khác hoặc có vòng đánh dấu.
- Cá thể đang được chọn: có đường viền nổi bật, không làm thay đổi màu sắc gốc dùng để nhận diện loài.
- Cá thể bị thương, đói hoặc đang gặp nguy hiểm: hiển thị trạng thái bằng một dấu hiệu phụ, biểu tượng nhỏ hoặc đường viền trạng thái.

Các quy ước hình ảnh phải nhất quán. Màu sắc chủ yếu nhận diện loại thực thể; hình dạng hoặc dấu hiệu phụ nhận diện vai trò và trạng thái. Không nên dùng một màu duy nhất để đồng thời biểu thị quá nhiều thông tin.

### Chuyển động

Chuyển động là một phần quan trọng của khả năng quan sát, không chỉ là hiệu ứng trang trí.

Cần biểu diễn được:
- Cá thể di chuyển, dừng lại, tìm kiếm tài nguyên và thay đổi hướng.
- Các cá thể hình thành, duy trì hoặc tách khỏi một nhóm.
- Quần thể phân tán khi tài nguyên cạn hoặc nguy hiểm xuất hiện.
- Các nhóm tập trung tại nguồn thức ăn hoặc nước.
- Các cá thể phản ứng với nhau và với những thay đổi trong môi trường.

Chuyển động phải phản ánh trạng thái mô phỏng thực tế. Không tạo chuyển động ngẫu nhiên chỉ để làm bản đồ trông sống động.

Với số lượng cá thể lớn, ưu tiên hiệu năng và khả năng nhìn thấy xu hướng của cả quần thể. Không cần hiển thị chi tiết mọi cá thể cùng lúc.

## 3. Bố cục giao diện

Bố cục nên có ba khu vực chính.

### A. World Map — khu vực trung tâm

Đây là vùng chiếm diện tích lớn nhất màn hình, khoảng 65–75% không gian làm việc tùy kích thước cửa sổ.

Nội dung:
- Toàn cảnh thế giới và địa hình.
- Vị trí các tài nguyên, cá thể và quần thể.
- Chuyển động hiện tại.
- Các vùng nguy hiểm hoặc vùng ảnh hưởng của sự kiện.
- Đường di chuyển hoặc đường đi dự kiến khi cần thiết.
- Dấu hiệu trực quan cho các sự kiện quan trọng.
- Công cụ chọn thực thể, phóng to, thu nhỏ và di chuyển bản đồ nếu cần.

Người xem phải có thể quan sát được các biến động tổng thể mà không phải mở nhiều bảng thông tin.

Có thể cung cấp các lớp hiển thị bật/tắt:
- Thực thể và quần thể.
- Tài nguyên.
- Mối nguy và vùng ảnh hưởng.
- Đường đi và hành vi dự kiến.
- Vùng quan sát hoặc phạm vi nhận thức.
- Các sự kiện và hành động của Mộng Nhiễm.

Không bật mọi lớp cùng lúc theo mặc định.

### B. Inspector — thông tin của thực thể được chọn

Khi người xem chọn một cá thể, quần thể, nguồn tài nguyên hoặc khu vực, hiển thị thông tin chi tiết trong một bảng bên cạnh bản đồ.

Đối với cá thể:
- ID và loại thực thể.
- Vai trò, nếu có.
- Vị trí và trạng thái hiện tại.
- Các thuộc tính liên quan như mức năng lượng, đói, sức khỏe hoặc khả năng hành động.
- Mục tiêu hoặc hành động hiện tại.
- Những quan sát gần đây.
- Ký ức hoặc thông tin có liên quan đến quyết định hiện tại.
- Những gì thực thể biết, tin hoặc chưa biết.
- Các hành động đang chờ thực hiện, nếu có.

Đối với quần thể:
- Quy mô hiện tại.
- Số lượng sinh, chết hoặc di cư trong một khoảng thời gian.
- Mức tài nguyên liên quan.
- Khu vực phân bố.
- Xu hướng biến động.
- Các vai trò đặc biệt bên trong quần thể.
- Những vấn đề đang ảnh hưởng đến nhóm.

Đối với tài nguyên:
- Lượng hiện có và sức chứa tối đa, nếu có.
- Tốc độ tiêu thụ hoặc phục hồi.
- Các thực thể đang sử dụng tài nguyên.
- Các sự kiện có thể làm thay đổi nguồn tài nguyên.

Không cần hiển thị mọi trường dữ liệu ngay lập tức. Ưu tiên trạng thái quan trọng nhất, sau đó cung cấp các mục mở rộng khi người xem cần tìm hiểu sâu hơn.

### C. Event & Decision Panel — diễn biến và quyết định

Đây là khu vực cho phép người xem hiểu điều gì đang xảy ra và tại sao nó đáng chú ý.

Hiển thị một dòng thời gian các sự kiện quan trọng, chẳng hạn:
- Nguồn nước bắt đầu suy giảm.
- Một quần thể phát hiện thiếu thức ăn.
- Một cá thể phát hiện nguy hiểm.
- Một quyết định được đề xuất.
- Một hành động bị từ chối hoặc điều chỉnh bởi cơ chế kiểm soát.
- Một hành động được thực thi.
- Kết quả thực tế sau hành động.
- Một sai lệch giữa thông tin mà thực thể tin tưởng và trạng thái thực được phát hiện.

Mỗi sự kiện nên có:
- Thời điểm.
- Thực thể liên quan.
- Mô tả ngắn gọn.
- Nguyên nhân hoặc dữ kiện kích hoạt, nếu đã xác định.
- Quyết định hoặc hành động liên quan.
- Trạng thái xử lý và kết quả quan sát được.

Cho phép chọn một sự kiện để định vị thực thể liên quan trên bản đồ, mở Inspector hoặc xem chuỗi sự kiện dẫn đến kết quả đó.

Không trình bày log kỹ thuật thành một khối văn bản dài khó đọc. Dùng các mục có cấu trúc, trạng thái rõ ràng và liên kết được với những gì đang xảy ra trên bản đồ.

## 4. Những thông tin cần thiết để người xem tự đưa ra quyết định

Giao diện không nên chỉ kể lại những gì hệ thống đã làm. Nó cần cung cấp đủ bằng chứng để người xem đánh giá tình hình và lựa chọn can thiệp.

### Tình trạng chung của thế giới

Một thanh thông tin gọn ở phía trên bản đồ nên hiển thị các chỉ số tổng hợp có ý nghĩa với kịch bản hiện tại, chẳng hạn:
- Thời gian mô phỏng hoặc world tick.
- Quy mô từng quần thể.
- Lượng thức ăn và nước còn lại.
- Số thực thể đang gặp nguy hiểm.
- Số sự kiện chưa được xử lý.
- Tình trạng tổng thể của hệ sinh thái.

Chỉ hiển thị các chỉ số có thật trong bộ mô phỏng. Không tạo các điểm số sức khỏe hệ sinh thái hoặc xác suất thành công nếu chưa có định nghĩa và phương pháp tính rõ ràng.

### Tình hình và xu hướng

Giá trị hiện tại chưa đủ để ra quyết định. Cần hiển thị một lượng thông tin lịch sử ngắn để người xem biết tình hình đang tốt lên hay xấu đi.

Ví dụ:
- Biểu đồ số lượng thỏ theo thời gian.
- Lượng thức ăn và nước còn lại.
- Tỷ lệ sinh và tử.
- Số lượng cá thể đang đói hoặc bị thương.
- Diễn biến của một chỉ số trước và sau sự kiện.

Không cần hiển thị tất cả biểu đồ cùng lúc. Chọn biểu đồ theo kịch bản hoặc theo thực thể đang được xem.

### Mối nguy và mức độ bất định

Khi có nguy cơ, người xem cần biết:
- Nguy cơ là gì.
- Ai hoặc khu vực nào bị ảnh hưởng.
- Dữ kiện nào hỗ trợ nhận định đó.
- Thực thể nào đã phát hiện nguy cơ.
- Thực thể nào chưa phát hiện.
- Thông tin nào còn thiếu hoặc chưa được xác minh.

Phải phân biệt nguy cơ đã được xác nhận với nguy cơ mới chỉ là giả thuyết. Không biến một suy đoán của SLM thành sự thật của thế giới.

### Quyết định và phương án can thiệp

Cho phép người xem chọn một thực thể hoặc khu vực, xem tình trạng liên quan rồi thực hiện những can thiệp phù hợp với kịch bản, ví dụ:
- Bổ sung thức ăn hoặc nước.
- Tạo hoặc đóng một lối đi.
- Đánh dấu một khu vực nguy hiểm.
- Tạo một biến cố môi trường.
- Gửi một mục tiêu hoặc chỉ thị cho thực thể được chọn.
- Tạm dừng mô phỏng để kiểm tra trước khi tiếp tục.

Đối với mỗi hành động, cần làm rõ:
- Hành động sẽ tác động đến đối tượng nào.
- Điều kiện hoặc tài nguyên cần thiết.
- Hậu quả dự kiến, nếu mô hình thực sự có thể ước lượng.
- Những rủi ro hoặc tác động phụ đã biết.
- Kết quả thực tế sau khi hành động được thực hiện.

Không nên đưa ra một con số dự đoán chính xác nếu mô hình không có cơ sở để tính toán con số đó.

Người xem phải có thể so sánh tình hình trước và sau can thiệp để đánh giá quyết định có thực sự hiệu quả hay không.

## 5. Phân biệt trạng thái thực và thông tin của tác tử

Đây là yêu cầu quan trọng đối với demo Mộng Nhiễm.

Trạng thái thực của thế giới phải được quản lý riêng với thông tin mà từng cá thể hoặc quần thể nắm giữ.

Ví dụ, nguồn nước đã cạn nhưng một nhóm thỏ vẫn tin rằng nguồn nước còn tồn tại. Trong Inspector của nhóm thỏ, người xem có thể thấy thông tin mà nhóm đang sử dụng; trên bản đồ và bảng trạng thái thực, người xem thấy nguồn nước đã cạn.

Giao diện nên có một cách chuyển đổi hoặc so sánh rõ ràng giữa:
- Ground Truth: trạng thái thực được bộ mô phỏng xác nhận.
- Agent Belief: thông tin, niềm tin hoặc nhận định của thực thể.
- Observations: những gì thực thể đã quan sát.
- Decision: quyết định được đề xuất dựa trên thông tin hiện có.
- Execution Result: hành động thực tế và kết quả đã được xác nhận.

Chỉ hiển thị thông tin mà hệ thống thực sự ghi nhận được. Không bịa ký ức, quan sát hoặc trạng thái nội bộ để làm demo trông thông minh hơn.

## 6. Hiển thị vai trò của Mộng Nhiễm

Mộng Nhiễm phải được thể hiện thông qua các sự kiện có thể truy vết, không phải bằng một bảng thông báo chung chung rằng hệ thống đang hoạt động tốt.

Nếu cơ chế tương ứng đã được triển khai, giao diện có thể cho thấy:
- Một hành động được đề xuất.
- Trạng thái và điều kiện liên quan được kiểm tra.
- Một ràng buộc bị vi phạm hoặc một nguy cơ được phát hiện.
- Hành động bị chặn, điều chỉnh hoặc cho phép.
- Hành động cuối cùng được thực thi.
- Trạng thái thực sau khi thực thi.
- Các sự kiện tiếp theo mà hệ thống tiếp tục theo dõi.

Phân biệt rõ hành động do SLM đề xuất, hành động được Mộng Nhiễm chấp thuận hoặc can thiệp, và hành động thực tế đã được thực thi.

Không gọi một đề xuất là hành động đã thực hiện. Không gọi một cảnh báo là một sự cố đã được ngăn chặn thành công nếu không có bằng chứng về kết quả.

Nếu hệ thống có thể giải thích dữ kiện và các bước kiểm tra của một quyết định, hãy hiển thị chúng thành một Decision Trace có cấu trúc. Không giả vờ hiển thị toàn bộ suy nghĩ nội bộ của SLM.

## 7. Điều khiển mô phỏng và kiểm tra tình huống

Giao diện nên có một thanh điều khiển nhỏ, dễ sử dụng:
- Play/Pause.
- Tốc độ mô phỏng.
- Reset về trạng thái ban đầu.
- Chọn kịch bản.
- Tạo một biến cố được định nghĩa trước.
- Bật/tắt các lớp thông tin trên bản đồ.
- Xem lại hoặc tua đến các mốc sự kiện nếu cơ chế lưu lịch sử hỗ trợ.

Nên có một số tình huống mẫu để người xem dễ kiểm tra các khả năng của hệ thống. Ví dụ:
1. Nguồn thức ăn cạn dần và quần thể phải thích nghi.
2. Một mối nguy xuất hiện nhưng không phải mọi cá thể đều nhận biết được.
3. Người dùng can thiệp và tạo ra một hậu quả ngoài dự kiến.
4. Một hành động được đề xuất nhưng bị cơ chế an toàn từ chối.
5. Một quyết định ban đầu không hiệu quả, khiến hệ thống phải tiếp tục quan sát và xử lý tình huống mới.

Các tình huống phải xuất phát từ hành vi thực tế của mô phỏng. Không dùng hoạt ảnh hoặc kịch bản dựng sẵn để giả lập một năng lực mà backend chưa có.

## 8. Nguyên tắc triển khai

Đây là một demo tập trung vào khả năng quan sát và kiểm chứng, không phải một hệ sinh thái hoàn chỉnh.

- Dùng bộ mô phỏng xác định các trạng thái vật lý, tài nguyên và những quy luật thông thường.
- Không gọi SLM cho từng cá thể hoặc từng bước di chuyển nếu không cần thiết.
- Chỉ kích hoạt các cơ chế nhận thức ở những tình huống có ý nghĩa.
- Tách dữ liệu mô phỏng khỏi lớp đồ họa.
- Giao diện phải đọc trạng thái và sự kiện từ backend thực tế.
- Không giả lập log, quyết định, cảnh báo hoặc kết quả thành công để lấp chỗ trống.
- Nếu một khả năng chưa được triển khai, hãy để nó ở trạng thái chưa hỗ trợ hoặc đánh dấu rõ là bản minh họa.
- Ưu tiên một số ít tình huống được triển khai hoàn chỉnh hơn là nhiều tính năng chỉ có bề ngoài.

Có thể dùng HTML Canvas và JavaScript cho bản demo ban đầu nếu phù hợp với cấu trúc hiện tại. Không cần thêm framework đồ họa nặng trừ khi có lý do rõ ràng.

## 9. Tiêu chí nghiệm thu giao diện

Bản demo đạt yêu cầu khi người xem có thể:
1. Nhận biết các loại thực thể và tài nguyên mà không cần đọc tài liệu dài.
2. Quan sát được quần thể thay đổi về số lượng, vị trí và hành vi.
3. Nhận ra một biến cố và xác định đối tượng chịu ảnh hưởng.
4. So sánh trạng thái thực với thông tin mà một thực thể đang biết.
5. Tìm hiểu nguyên nhân của một quyết định thông qua dữ kiện và sự kiện có liên quan.
6. Thực hiện một can thiệp, tiếp tục mô phỏng và quan sát hậu quả.
7. Xác định hành động nào do SLM đề xuất, Mộng Nhiễm đã kiểm tra hoặc can thiệp, và kết quả nào thực sự được xác nhận.
8. Kiểm tra được chuỗi sự kiện từ biến cố ban đầu đến hậu quả cuối cùng.

Trước khi triển khai, hãy kiểm tra API và mã nguồn hiện có của Mộng Nhiễm. Lập bảng đối chiếu giữa năng lực thực tế, dữ liệu backend có thể cung cấp và thông tin giao diện cần hiển thị. Không giả định một module hoặc API tồn tại chỉ vì nó được nhắc đến trong tài liệu.

Hãy ưu tiên xây dựng một lát cắt hoàn chỉnh: bản đồ tối giản, một vài loại thực thể, một biến cố có ý nghĩa, bảng Inspector, dòng sự kiện và một can thiệp có thể quan sát hậu quả. Sau khi lát cắt này hoạt động đúng với backend thực tế, mới mở rộng số lượng quần thể, loại biến cố và biểu đồ.