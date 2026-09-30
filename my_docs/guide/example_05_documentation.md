# Ví dụ 5: Tạo Tài liệu Toàn diện cho Dự án

**Bối cảnh:** Dự án của bạn đã gần hoàn thành về mặt tính năng, nhưng gần như không có tài liệu (documentation), gây khó khăn cho việc bàn giao và bảo trì.

**Mục tiêu:** Sử dụng SuperClaude để tự động quét toàn bộ dự án và tạo ra một bộ tài liệu hoàn chỉnh.

---

### Bước 1: Khởi tạo Quy trình Tạo Tài liệu

**Bạn (User) gõ:**

> Dự án này cần được tài liệu hóa. Hãy `/sc:index` toàn bộ project và tạo ra các tài liệu cần thiết, bao gồm README, tài liệu API và hướng dẫn sử dụng.

**SuperClaude phản hồi:**

> Đã nhận yêu cầu. Bắt đầu quy trình tạo tài liệu toàn diện. Tôi sẽ điều phối các chuyên gia `@agent-system-architect` để phân tích cấu trúc và `@agent-technical-writer` để tạo nội dung.
> 
> **Kế hoạch tạo tài liệu:**
> 
> 1.  **Phân tích Tổng thể:** Quét toàn bộ cây thư mục để hiểu cấu trúc, các công nghệ sử dụng (framework, ngôn ngữ), và các thành phần chính.
> 2.  **Tạo README.md:** Tạo một file `README.md` chất lượng cao ở thư mục gốc, bao gồm:
>     -   Mô tả dự án.
>     -   Các công nghệ sử dụng.
>     -   Hướng dẫn cài đặt (cách clone, cài dependencies).
>     -   Hướng dẫn chạy dự án (dev, prod, test).
>     -   Mô tả cấu trúc thư mục chính.
> 3.  **Tạo Tài liệu API:**
>     -   Quét thư mục `src/api` hoặc `src/routes`.
>     -   Tự động tạo tài liệu cho từng endpoint, bao gồm: phương thức HTTP, URL, tham số, body request, và các phản hồi mẫu (success, error).
>     -   Lưu kết quả vào `Docs/api-reference.md`.
> 4.  **Tạo Tài liệu cho Component Frontend:**
>     -   Quét thư mục `src/components`.
>     -   Đối với mỗi component, tạo tài liệu về các `props` nó nhận, các `events` nó phát ra, và ví dụ sử dụng.
>     -   Lưu kết quả vào `Docs/component-guide.md`.

### Bước 2: SuperClaude Tự động Tạo Nội dung

**SuperClaude bắt đầu thực thi kế hoạch và tạo các file:**

> **Đang tiến hành...**
> 
> -   **`@agent-system-architect`:** Đã phân tích xong cấu trúc. Dự án sử dụng React và Express. Các module chính là `auth`, `products`, và `orders`.
> -   **`@agent-technical-writer`:**
>     -   **Đã tạo `README.md`:** Bao gồm các hướng dẫn chi tiết.
>     -   **Đang tạo `Docs/api-reference.md`:** Đã quét 15 endpoints. Bắt đầu viết tài liệu cho nhóm endpoint `/auth/...`
>     -   **Đang tạo `Docs/component-guide.md`:** Đã quét 25 components. Bắt đầu viết tài liệu cho `Button.jsx` và `ProductCard.jsx`.

*(Quá trình này có thể mất vài phút tùy thuộc vào độ lớn của dự án. SuperClaude sẽ tự động đọc các file code để hiểu logic và sinh ra tài liệu tương ứng)*

### Bước 3: Hoàn tất và Rà soát

**SuperClaude hoàn thành:**

> Quá trình tạo tài liệu đã hoàn tất. Tôi đã tạo và cập nhật các tệp sau:
> -   `README.md`
> -   `Docs/api-reference.md`
> -   `Docs/component-guide.md`
> 
> Các tài liệu này được tạo ra từ việc phân tích code, bao gồm các ví dụ sử dụng thực tế. Vui lòng rà soát lại và cho tôi biết nếu bạn muốn bổ sung hoặc chỉnh sửa phần nào.

---

**Kết quả:** Từ một dự án không có tài liệu, bạn đã có một bộ tài liệu chuyên nghiệp và toàn diện chỉ với một vài câu lệnh. Điều này giúp tăng tốc độ onboarding cho thành viên mới và đơn giản hóa quá trình bảo trì trong tương lai.
