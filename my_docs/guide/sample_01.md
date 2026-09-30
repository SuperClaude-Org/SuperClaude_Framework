## Guide Thực Chiến: Xây Dựng API Blog với SuperClaude

### Giai đoạn 1: Lên Kế Hoạch và Thiết Kế

**Mục tiêu:** Từ một ý tưởng "API cho blog", chúng ta sẽ định hình rõ ràng các tính năng, kiến trúc và kế hoạch thực hiện.

**Bước 1.1: Brainstorming để làm rõ ý tưởng**
Sử dụng `/sc:brainstorm` để SuperClaude đặt câu hỏi và giúp bạn suy nghĩ về các khía cạnh của dự án.

*   **Ví dụ:**
    ```bash
    /sc:brainstorm "Tôi muốn xây dựng một API cho blog"
    ```
    *   **Kết quả mong đợi:** SuperClaude sẽ hỏi: "Tuyệt vời! Hãy cùng khám phá nhé. API này cần những tính năng chính nào? Ví dụ: lấy danh sách bài viết, xem chi tiết một bài, tạo bài mới? Dữ liệu cho một bài viết sẽ gồm những trường nào (tiêu đề, nội dung, tác giả)?"

**Bước 1.2: Phân tích và định hình yêu cầu**
Sau khi có ý tưởng rõ hơn, hãy giao cho `@agent-requirements-analyst` để hệ thống hóa các yêu cầu.

*   **Ví dụ:**
    ```bash
    @agent-requirements-analyst "Dựa trên cuộc thảo luận vừa rồi, hãy tạo một bản đặc tả yêu cầu (specification) cho API blog. Cần có 2 endpoint: GET /posts và GET /posts/:id. Dữ liệu bài viết gồm id, title, và content."
    ```
    *   **Kết quả mong đợi:** Agent sẽ tạo ra một tài liệu ngắn gọn, rõ ràng về các yêu cầu chức năng và phi chức năng.

**Bước 1.3: Thiết kế kiến trúc**
Sử dụng `/sc:design` để phác thảo kiến trúc và cấu trúc thư mục.

*   **Ví dụ:**
    ```bash
    /sc:design "Thiết kế cấu trúc thư mục cho dự án API blog bằng Express. Cần có thư mục cho routes, controllers và một file server.js chính."
    ```
    *   **Kết quả mong đợi:** SuperClaude sẽ đề xuất một cấu trúc thư mục hợp lý và giải thích vai trò của từng thành phần.

**Bước 1.4: Lập kế hoạch triển khai**
Cuối cùng, dùng `/sc:workflow` để tạo một danh sách công việc (checklist) chi tiết.

*   **Ví dụ:**
    ```bash
    /sc:workflow "Tạo kế hoạch các bước để triển khai API blog"
    ```
    *   **Kết quả mong đợi:** Một checklist dạng:
        1.  Khởi tạo dự án Node.js (`npm init`).
        2.  Cài đặt Express.
        3.  Tạo file `server.js`.
        4.  Tạo router cho `/posts`.
        5.  Viết logic để trả về dữ liệu giả (mock data).
        6.  Viết unit test.

---

### Giai đoạn 2: Triển Khai (Viết Code)

**Mục tiêu:** Hiện thực hóa bản thiết kế thành code chạy được.

**Bước 2.1: Viết code cho các endpoint**
Sử dụng `/sc:implement` để viết phần logic chính.

*   **Ví dụ:**
    ```bash
    /sc:implement "Trong file routes/posts.js, hãy viết code cho Express router xử lý 2 endpoint GET /posts và GET /posts/:id. Tạm thời sử dụng một mảng JSON giả lập làm dữ liệu."
    ```
    *   **Kết quả mong đợi:** SuperClaude sẽ tạo ra đoạn code hoàn chỉnh cho file router, kèm theo một mảng dữ liệu giả.

**Bước 2.2: Kết nối các thành phần**

*   **Ví dụ:**
    ```bash
    /sc:implement "Trong file server.js, hãy import router từ routes/posts.js và sử dụng nó với tiền tố /api."
    ```

---

### Giai đoạn 3: Kiểm Thử

**Mục tiêu:** Đảm bảo API hoạt động đúng như mong đợi.

**Bước 3.1: Lên chiến lược kiểm thử**
Hỏi ý kiến chuyên gia `@agent-quality-engineer`.

*   **Ví dụ:**
    ```bash
    @agent-quality-engineer "Tôi nên dùng thư viện nào để viết unit test cho API Express này? Jest và Supertest có phải là lựa chọn tốt không?"
    ```

**Bước 3.2: Viết code test**
Sử dụng `/sc:test` để tạo các kịch bản kiểm thử.

*   **Ví dụ:**
    ```bash
    /sc:test "Viết một file test bằng Jest và Supertest cho posts.js. Kịch bản đầu tiên cần kiểm tra endpoint GET /posts trả về status 200 và một mảng. Kịch bản thứ hai kiểm tra GET /posts/1 trả về một đối tượng."
    ```
    *   **Kết quả mong đợi:** Một file `posts.test.js` với code đầy đủ để chạy.

---

### Giai đoạn 4: Cải Tiến và Tái Cấu Trúc

**Mục tiêu:** Nâng cao chất lượng code sau khi các tính năng đã chạy đúng.

**Bước 4.1: Phân tích chất lượng code**
Sử dụng `/sc:analyze` để tìm các điểm có thể cải thiện.

*   **Ví dụ:**
    ```bash
    /sc:analyze routes/posts.js --focus quality
    ```
    *   **Kết quả mong đợi:** SuperClaude có thể đề xuất: "Dữ liệu giả đang được định nghĩa ngay trong file router. Điều này làm giảm khả năng bảo trì. Nên tách nó ra một file riêng."

**Bước 4.2: Áp dụng cải tiến**
Sử dụng `/sc:improve` hoặc giao cho `@agent-refactoring-expert`.

*   **Ví dụ:**
    ```bash
    /sc:improve "Tách mảng dữ liệu giả từ file routes/posts.js ra một file mới là data/mockPosts.js, sau đó import nó trở lại."
    ```

---

### Giai đoạn 5: Hoàn Thiện

**Mục tiêu:** Viết tài liệu và lưu lại công việc.

**Bước 5.1: Viết tài liệu API**
Sử dụng `/sc:document`.

*   **Ví dụ:**
    ```bash
    /sc:document routes/posts.js --type api --format markdown
    ```
    *   **Kết quả mong đợi:** Một file Markdown mô tả các endpoint, phương thức, tham số và dữ liệu trả về mẫu.

**Bước 5.2: Commit code**
Sử dụng `/sc:git` để tạo commit message chất lượng.

*   **Ví dụ:**
    ```bash
    /sc:git commit --smart-commit
    ```
    *   **Kết quả mong đợi:** SuperClaude sẽ phân tích các thay đổi và đề xuất một commit message có ý nghĩa (ví dụ: "Feat: Implement API endpoints for fetching posts").

Bằng cách đi theo quy trình thực chiến này, bạn đã áp dụng một cách hệ thống các công cụ của SuperClaude để xây dựng một tính năng hoàn chỉnh từ đầu đến cuối.
