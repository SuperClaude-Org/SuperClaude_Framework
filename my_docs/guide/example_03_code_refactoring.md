# Ví dụ 3: Tái cấu trúc (Refactor) và Cải thiện Code Legacy

**Bối cảnh:** Bạn đang phải làm việc với một module code cũ (`legacy_payment.js`). Nó hoạt động nhưng rất khó đọc, khó bảo trì, và có nhiều đoạn code lặp lại.

**Mục tiêu:** Sử dụng SuperClaude để tự động phân tích, tái cấu trúc và dọn dẹp module này một cách an toàn.

---

### Bước 1: Phân tích Chất lượng Code

**Bạn (User) gõ:**

> Module `src/services/legacy_payment.js` này rất phức tạp. Hãy `/sc:analyze` nó và cho tôi biết các vấn đề chính về chất lượng code.

**SuperClaude phản hồi:**

> Đã hiểu. Kích hoạt lệnh `/sc:analyze --focus quality` trên tệp `src/services/legacy_payment.js`. Chuyên gia `@agent-quality-engineer` sẽ vào cuộc.
> 
> **Kết quả phân tích:**
> 
> 📊 **Báo cáo Chất lượng Code:**
> - **Độ phức tạp Cyclomatic:** Rất cao (25). Cho thấy các hàm có quá nhiều luồng logic lồng nhau.
> - **Trùng lặp Code:** Phát hiện 3 khối code giống hệt nhau (khoảng 15 dòng) xử lý việc định dạng số tiền.
> - **Khả năng bảo trì:** Chỉ số thấp (45/100) do các hàm quá dài và tên biến không rõ ràng.
> - **Vấn đề chính:** Hàm `processPayment` đang làm quá nhiều việc (lấy thông tin người dùng, xác thực thẻ, xử lý thanh toán, gửi email). Vi phạm nguyên tắc Đơn trách nhiệm (Single Responsibility Principle).

### Bước 2: Yêu cầu Cải thiện Tự động

**Bạn (User) gõ:**

> Cảm ơn. Báo cáo rất chi tiết. Bây giờ, hãy `/sc:improve` file này. Tôi muốn ưu tiên sự an toàn, đảm bảo không làm thay đổi hành vi hiện tại của nó.

**SuperClaude phản hồi:**

> Rõ ràng. Tôi sẽ thực hiện lệnh `/sc:improve --safe`. Chế độ an toàn sẽ đảm bảo rằng các bài kiểm thử (test) hiện có phải được chạy và vượt qua trước và sau khi tái cấu trúc. Chuyên gia `@agent-refactoring-expert` sẽ chỉ đạo quá trình này.
> 
> **Kế hoạch cải thiện:**
> 
> 1.  **Chạy Pre-flight Check:** Chạy toàn bộ test liên quan đến `legacy_payment.js` để đảm bảo trạng thái ban đầu ổn định.
> 2.  **Trích xuất Hàm (Extract Function):** Khối code định dạng số tiền sẽ được trích xuất ra một hàm tiện ích riêng tên là `formatCurrency`.
> 3.  **Tách Hàm (Decompose Function):** Hàm `processPayment` khổng lồ sẽ được chia thành các hàm nhỏ hơn, rõ ràng hơn:
>     -   `getUserDetails(userId)`
>     -   `validateCard(cardInfo)`
>     -   `executeTransaction(amount, card)`
>     -   `sendConfirmationEmail(user, transactionId)`
> 4.  **Đổi tên Biến:** Các biến như `val`, `p`, `dat` sẽ được đổi thành `amount`, `paymentData`, `transactionDate` cho dễ hiểu.
> 5.  **Chạy Post-flight Check:** Chạy lại toàn bộ bộ test để xác nhận không có hồi quy (regression).

*(SuperClaude tự động áp dụng các thay đổi trên vào file)*

### Bước 3: Dọn dẹp và Hoàn tất

**SuperClaude hoàn thành:**

> Quá trình tái cấu trúc đã hoàn tất và tất cả các bài kiểm thử đều đã vượt qua. File `legacy_payment.js` giờ đây đã gọn gàng và dễ bảo trì hơn. Tôi cũng đã thêm một vài bình luận (comment) để giải thích các luồng xử lý phức tạp.
> 
> Bạn có muốn tôi tiếp tục với `/sc:cleanup --type imports` để dọn dẹp các import không cần thiết không?

---

**Kết quả:** Module code cũ khó bảo trì đã được tự động biến đổi thành code sạch, có cấu trúc tốt, tuân thủ các nguyên tắc thiết kế phần mềm và quan trọng nhất là vẫn đảm bảo hoạt động đúng như ban đầu.
