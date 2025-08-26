# Hướng dẫn sử dụng SuperClaude: Tổng quan về Lệnh và Cách thức Hoạt động

## SuperClaude hoạt động như thế nào?

Điều quan trọng cần nhớ là **SuperClaude không phải là một chương trình bạn chạy, mà là một bộ não mở rộng cho AI (Claude Code)**. Bạn "sử dụng" SuperClaude bằng cách tương tác với AI theo những cách đã được định nghĩa sẵn trong các tệp tin ngữ cảnh.

Có 3 cách chính để tận dụng sức mạnh của SuperClaude:

1.  **Sử dụng Command:** Gõ `/sc:[tên-lệnh]` để kích hoạt một quy trình làm việc (workflow) tự động. Đây là cách mạnh mẽ nhất để thực hiện các tác vụ phức tạp.
2.  **Triệu hồi Agent:** Gõ `@agent-[tên-chuyên-gia]` (ví dụ: `@agent-python-expert`) khi bạn cần sự tư vấn sâu về một lĩnh vực cụ thể.
3.  **Sử dụng Flag:** Thêm các cờ như `--safe` hoặc `--with-tests` vào sau lệnh để điều chỉnh hành vi của nó.

---

## Tổng quan về các Lệnh (Commands)

Các lệnh là trung tâm của SuperClaude, giúp tự động hóa các tác vụ từ đơn giản đến phức tạp. Dưới đây là tổng quan về các lệnh chính, được nhóm theo chức năng:

### Nhóm 1: Phân tích & Thiết kế

Đây là nhóm lệnh giúp bạn lên kế hoạch và định hình dự án.

*   `/sc:analyze`: Phân tích code toàn diện về chất lượng, bảo mật, hiệu năng và kiến trúc.
*   `/sc:design`: Thiết kế kiến trúc hệ thống, API, component hoặc cơ sở dữ liệu.
*   `/sc:estimate`: Cung cấp ước tính (thời gian, công sức, độ phức tạp) cho một tác vụ.
*   `/sc:brainstorm`: Kích hoạt một phiên làm việc tương tác để khám phá và làm rõ các yêu cầu từ những ý tưởng mơ hồ.
*   `/sc:workflow`: Tự động tạo ra một quy trình triển khai có cấu trúc từ tài liệu yêu cầu sản phẩm (PRD).

### Nhóm 2: Triển khai & Cải thiện

Nhóm lệnh này tập trung vào việc viết, xây dựng và nâng cao chất lượng code.

*   `/sc:implement`: Triển khai một tính năng mới (component, API, service). Lệnh này sẽ tự động điều phối các chuyên gia (agents) và công cụ (MCPs) phù hợp.
*   `/sc:build`: Biên dịch, xây dựng và đóng gói dự án của bạn.
*   `/sc:test`: Chạy các bộ kiểm thử (unit, integration, e2e) và phân tích độ bao phủ (coverage).
*   `/sc:improve`: Tự động áp dụng các cải tiến về chất lượng, hiệu năng, và khả năng bảo trì cho code.
*   `/sc:cleanup`: Dọn dẹp code, loại bỏ code không sử dụng (dead code) và tối ưu hóa cấu trúc dự án.

### Nhóm 3: Tài liệu & Giải thích

Nhóm lệnh giúp bạn hiểu và ghi lại kiến thức về dự án.

*   `/sc:document`: Tạo tài liệu tập trung cho một component, hàm, hoặc API cụ thể.
*   `/sc:explain`: Cung cấp lời giải thích rõ ràng về một đoạn code, một khái niệm, hoặc hành vi của hệ thống.
*   `/sc:index`: Tạo ra một cơ sở kiến thức hoặc tài liệu tổng thể cho toàn bộ dự án với khả năng tổ chức thông minh.

### Nhóm 4: Quản lý & Tiện ích

Các lệnh hỗ trợ cho quá trình làm việc hàng ngày.

*   `/sc:git`: Thực hiện các thao tác Git, với khả năng tự động tạo commit message thông minh.
*   `/sc:troubleshoot`: Chẩn đoán và giúp giải quyết các vấn đề trong code, build, hoặc khi triển khai.
*   `/sc:task` & `/sc:spawn`: Điều phối và thực thi các tác vụ cực kỳ phức tạp, có khả năng chia nhỏ công việc và giao cho nhiều agent xử lý song song.

### Nhóm 5: Quản lý Phiên làm việc (Session)

Các lệnh này giúp AI "ghi nhớ" công việc của bạn giữa các phiên làm việc.

*   `/sc:load`: Tải lại ngữ cảnh của một dự án khi bạn bắt đầu một phiên làm việc mới.
*   `/sc:save`: Lưu lại ngữ cảnh, các khám phá và tiến độ của phiên làm việc hiện tại.
*   `/sc:reflect`: Yêu cầu AI tự "nhìn lại" và đánh giá công việc đã làm trong một tác vụ hoặc phiên.

Bằng cách kết hợp các lệnh, tác tử và cờ, bạn có thể hướng dẫn AI thực hiện các công việc phức tạp một cách hiệu quả và có cấu trúc.

---

## Mẹo sử dụng hiệu quả

*   **Bắt đầu rộng, sau đó thu hẹp:** Đối với các tác vụ lớn, hãy bắt đầu bằng các lệnh có phạm vi rộng như `/sc:brainstorm` hoặc `/sc:workflow` để xác định yêu cầu. Sau đó, sử dụng `/sc:implement` cho từng phần cụ thể.
*   **Kết hợp các lệnh:** Bạn có thể tạo ra một chuỗi công việc mạnh mẽ. Ví dụ: yêu cầu AI `/sc:analyze` để tìm các vấn đề, sau đó dùng `/sc:improve` để khắc phục chúng.
*   **Triệu hồi chuyên gia khi cần:** Khi bạn cần chất lượng code cao nhất cho một phần cụ thể (ví dụ: bảo mật), hãy gọi trực tiếp chuyên gia đó: `Tôi muốn @agent-security-engineer xem xét lại hàm đăng nhập này`.
*   **Tận dụng quản lý phiên:** Với các dự án lớn, hãy dùng `/sc:save` và `/sc:load` thường xuyên. Điều này giúp AI không cần phải phân tích lại toàn bộ dự án mỗi khi bạn quay lại, tiết kiệm thời gian và chi phí.
*   **An toàn là trên hết:** Khi thực hiện các thay đổi quan trọng, hãy thêm cờ `--safe` để AI thực hiện các bước kiểm tra bổ sung và yêu cầu xác nhận trước khi hành động.

---

## Câu hỏi thường gặp (FAQ)

**H: SuperClaude có phải là một ứng dụng tôi cần cài đặt và chạy không?**

Đ: Không. SuperClaude là một bộ các tệp tin ngữ cảnh được cài đặt để định hướng cho AI bạn đang sử dụng. Bạn không chạy SuperClaude, bạn "trò chuyện" với nó thông qua các lệnh và tác tử.

**H: Làm cách nào để xem tất cả các lệnh có sẵn?**

Đ: Bản hướng dẫn này là một khởi đầu tốt. Để xem danh sách đầy đủ, bạn có thể xem cấu trúc thư mục `SuperClaude/Commands`. Mỗi tệp `.md` trong đó tương ứng với một lệnh.

**H: Điều gì xảy ra nếu tôi đưa ra một yêu cầu mơ hồ?**

Đ: Framework được thiết kế để xử lý việc này. AI có khả năng sẽ tự động chuyển sang `MODE_Brainstorming`, đặt các câu hỏi gợi mở để giúp bạn làm rõ yêu cầu của mình trước khi hành động.

**H: Tôi có thể tạo lệnh hoặc agent của riêng mình không?**

Đ: Có. Framework được thiết kế để mở rộng. Bạn có thể thêm các tệp `.md` mới vào thư mục `~/.claude/commands/sc/` (cho lệnh) hoặc `~/.claude/agents/` (cho agent) theo định dạng đã có.

**H: Lệnh `/sc:implement` có thực sự viết code cho tôi không?**

Đ: Có. Nó không chỉ viết code, mà còn điều phối các agent chuyên gia (backend, frontend, security) để đảm bảo code được tạo ra tuân thủ các tiêu chuẩn tốt nhất, có kiểm thử và tài liệu đi kèm nếu được yêu cầu.
