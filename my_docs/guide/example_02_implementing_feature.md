# Ví dụ 2: Triển khai API Backend cho Tính năng Xác thực

**Bối cảnh:** Bạn đã có một bản thiết kế API chi tiết (từ Ví dụ 1) và giờ muốn triển khai phần backend.

**Mục tiêu:** Sử dụng SuperClaude để viết code backend cho các API, đảm bảo code an toàn, chất lượng và có kiểm thử (test).

---

### Bước 1: Yêu cầu Triển khai với các Tiêu chuẩn Cao

**Bạn (User) gõ:**

> Dựa trên bản đặc tả API đã có, hãy `/sc:implement` các endpoint cho việc đăng ký và đăng nhập. Yêu cầu:
> - Sử dụng Node.js và Express.
> - Phải có đầy đủ unit test.
> - Tuân thủ các tiêu chuẩn bảo mật tốt nhất.

**SuperClaude phản hồi:**

> Đã nhận yêu cầu. Kích hoạt lệnh `/sc:implement --type api --with-tests`. 
> 
> Để đảm bảo chất lượng và bảo mật, tôi sẽ điều phối các chuyên gia sau:
> - `@agent-backend-architect`: Chịu trách nhiệm cấu trúc code và logic chính.
> - `@agent-security-engineer`: Đảm bảo các biện pháp bảo mật được áp dụng đúng đắn.
> - `@agent-quality-engineer`: Thiết kế và viết các unit test.

### Bước 2: SuperClaude Thực hiện và Tường thuật

**SuperClaude bắt đầu quá trình triển khai và cập nhật tiến độ:**

> **Tiến trình triển khai:**
> 
> 1.  **`@agent-backend-architect`:**
>     -   Tạo cấu trúc thư mục cho routes, controllers, và models.
>     -   Thiết lập server Express cơ bản.
>     -   Viết logic chính cho `auth.controller.js`.
> 
> 2.  **`@agent-security-engineer`:**
>     -   **Rà soát:** Yêu cầu tích hợp `bcrypt` để mã hóa mật khẩu trước khi lưu vào CSDL.
>     -   **Rà soát:** Thêm middleware sử dụng `express-validator` để xác thực và làm sạch dữ liệu đầu vào (input validation) cho email và mật khẩu.
>     -   **Rà soát:** Đảm bảo JWT được tạo với secret key từ biến môi trường và có thời gian hết hạn hợp lý.
> 
> 3.  **`@agent-quality-engineer`:**
>     -   Thiết lập môi trường test với `jest` và `supertest`.
>     -   Viết các file test cho từng endpoint (`auth.test.js`):
>         -   Test trường hợp đăng ký thành công.
>         -   Test trường hợp đăng ký với email đã tồn tại.
>         -   Test trường hợp đăng nhập với thông tin chính xác và nhận được token.
>         -   Test trường hợp đăng nhập sai mật khẩu.
> 
> 4.  **Tổng hợp & Hoàn thiện:**
>     -   Tạo file `.env.example` với các biến môi trường cần thiết.
>     -   Tạo file `README.md` hướng dẫn cách chạy và kiểm thử API.

*(SuperClaude sẽ tự động tạo và sửa các file cần thiết)*

### Bước 3: Chạy Kiểm thử để Xác thực

**SuperClaude hoàn tất và đề xuất bước tiếp theo:**

> Quá trình triển khai đã hoàn tất. Các file đã được tạo và chỉnh sửa. Tôi sẽ chạy lệnh `/sc:test` để xác thực rằng tất cả các kiểm thử đều vượt qua.

*(SuperClaude chạy test và hiển thị kết quả pass 100%)*

---

**Kết quả:** Bạn nhận được code backend hoàn chỉnh cho các API xác thực. Code không chỉ hoạt động đúng logic mà còn được cấu trúc tốt, an toàn, và có bộ unit test đầy đủ để đảm bảo chất lượng và dễ dàng bảo trì sau này.
