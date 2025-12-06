# Ví dụ 1: Lên kế hoạch cho Tính năng Mới - Hệ thống Xác thực Người dùng

**Bối cảnh:** Bạn cần xây dựng một hệ thống xác thực người dùng hoàn chỉnh nhưng chưa có đặc tả chi tiết, chỉ có ý tưởng ban đầu.

**Mục tiêu:** Sử dụng SuperClaude để biến ý tưởng thành một bản kế hoạch và thiết kế chi tiết.

---

### Bước 1: Khám phá Yêu cầu với `brainstorm`

**Bạn (User) gõ:**

> Tôi muốn xây dựng một hệ thống xác thực người dùng cho ứng dụng của mình, nhưng chưa biết bắt đầu từ đâu. Hãy giúp tôi `/sc:brainstorm` các yêu cầu.

**SuperClaude phản hồi:**

> Tuyệt vời. Kích hoạt `MODE_Brainstorming`. Để bắt đầu, chúng ta hãy cùng khám phá một vài khía cạnh chính:
> 
> 🤔 **Câu hỏi khám phá:**
> 1.  **Phương thức xác thực:** Bạn muốn hỗ trợ đăng nhập bằng email/mật khẩu, qua mạng xã hội (Google, Facebook), hay các phương thức không mật khẩu (passwordless) như magic link?
> 2.  **Luồng người dùng:** Quy trình sẽ bao gồm đăng ký, đăng nhập, quên mật khẩu, và xác thực email chứ?
> 3.  **Bảo mật:** Chúng ta có cần hỗ trợ xác thực hai yếu tố (2FA) không? Có yêu cầu đặc biệt nào về độ phức tạp của mật khẩu không?
> 4.  **Tích hợp:** Hệ thống này cần tích hợp với những dịch vụ nào khác trong ứng dụng của bạn?

*(Sau khi bạn trả lời các câu hỏi trên, SuperClaude đã có đủ thông tin để chuyển sang bước tiếp theo)*

### Bước 2: Tạo Quy trình (Workflow) từ các Yêu cầu

**SuperClaude tiếp tục:**

> Cảm ơn bạn đã cung cấp thông tin. Dựa trên thảo luận, tôi sẽ sử dụng `/sc:workflow` để tạo một kế hoạch triển khai có cấu trúc. Kích hoạt các chuyên gia `@agent-system-architect` và `@agent-security-engineer` để tư vấn.
> 
> **Kế hoạch triển khai được đề xuất:**
> 
> 📋 **Plan: Hệ thống Xác thực Người dùng**
> 
> → 🎯 **Giai đoạn 1: Thiết kế & Chuẩn bị**
>   → 📦 **Task 1.1:** Thiết kế Schema cho bảng `users` trong cơ sở dữ liệu.
>   → 📦 **Task 1.2:** Thiết kế các API Endpoints cho (đăng ký, đăng nhập, đăng xuất, quên mật khẩu).
>   → 📦 **Task 1.3:** Thiết kế giao diện người dùng (UI) cho các form.
> 
> → 🎯 **Giai đoạn 2: Triển khai Backend**
>   → 📦 **Task 2.1:** Implement API đăng ký với mã hóa mật khẩu (bcrypt).
>   → 📦 **Task 2.2:** Implement API đăng nhập với tạo JSON Web Token (JWT).
>   → 📦 **Task 2.3:** Implement logic gửi email xác thực.
> 
> → 🎯 **Giai đoạn 3: Triển khai Frontend & Tích hợp**
>   → 📦 **Task 3.1:** Xây dựng các UI component cho form.
>   → 📦 **Task 3.2:** Tích hợp API vào giao diện.
>   → 📦 **Task 3.3:** Quản lý trạng thái (state) của người dùng đã đăng nhập.

### Bước 3: Thiết kế chi tiết API

**Bạn (User) gõ:**

> Kế hoạch này rất tốt. Hãy tiếp tục với Task 1.2, dùng `/sc:design --type api` để tạo đặc tả chi tiết cho các endpoint.

**SuperClaude phản hồi:**

> Đã hiểu. Dưới đây là đặc tả API chi tiết theo chuẩn OpenAPI...
> *(SuperClaude sẽ tạo ra một file `api_spec.yaml` hoàn chỉnh)*

---

**Kết quả:** Từ một ý tưởng mơ hồ, bạn đã có trong tay một kế hoạch triển khai phân theo từng giai đoạn và một bản đặc tả API chi tiết, sẵn sàng cho việc bắt tay vào code.
