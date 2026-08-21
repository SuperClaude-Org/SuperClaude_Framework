# Ví dụ 4: Tìm và Sửa một Lỗi (Bug) Phức tạp

**Bối cảnh:** Người dùng báo cáo một lỗi không thường xuyên xảy ra: thỉnh thoảng, giỏ hàng của họ tự động trống rỗng sau khi cập nhật thông tin cá nhân. Lỗi này khó tái tạo và không rõ nguyên nhân.

**Mục tiêu:** Sử dụng SuperClaude để điều tra một cách có hệ thống, tìm ra nguyên nhân gốc rễ và sửa lỗi.

---

### Bước 1: Bắt đầu Điều tra với `troubleshoot`

**Bạn (User) gõ:**

> `/sc:troubleshoot` Lỗi: "Giỏ hàng của người dùng đôi khi bị trống sau khi họ cập nhật thông tin cá nhân". Tôi nghi ngờ có vấn đề về quản lý state ở frontend hoặc race condition ở backend.

**SuperClaude phản hồi:**

> Đã nhận được báo cáo lỗi. Đây là một vấn đề phức tạp. Kích hoạt chuyên gia `@agent-root-cause-analyst` để tiến hành điều tra. Chúng ta sẽ tiếp cận một cách có hệ thống.
> 
> **Giả thuyết ban đầu:**
> 1.  **Frontend:** State của giỏ hàng (`cartState`) bị ghi đè hoặc reset ngoài ý muốn sau khi API cập nhật thông tin người dùng (`updateProfile`) trả về.
> 2.  **Backend:** API `updateProfile` có tác dụng phụ (side-effect) không mong muốn, làm thay đổi dữ liệu giỏ hàng của người dùng.
> 3.  **Timing/Race Condition:** Dữ liệu giỏ hàng được fetch lại ngay sau khi cập nhật profile, nhưng dữ liệu mới chưa kịp đồng bộ.

### Bước 2: Thu thập Bằng chứng một cách Hệ thống

**SuperClaude thực hiện các bước điều tra:**

> **Kế hoạch điều tra:**
> 
> 1.  **Phân tích Code Frontend:**
>     -   Tôi sẽ đọc code của component `ProfilePage.js` và store quản lý state (ví dụ: `userStore.js`, `cartStore.js`).
>     -   **Lệnh:** `read_many_files(paths=['src/pages/ProfilePage.js', 'src/stores/'])`
>     -   **Phát hiện:** `userStore.js` có một action `setUser` nhận toàn bộ object user từ API. Action này đã reset toàn bộ state của user, bao gồm cả `cartItems`, thay vì chỉ cập nhật các trường thông tin cá nhân.
> 
> 2.  **Kiểm tra Giả thuyết:**
>     -   Giả thuyết số 1 có vẻ đúng. Hành động `setUser` đã ghi đè lên state giỏ hàng đang có ở client bằng một mảng rỗng từ server (vì API `updateProfile` không trả về thông tin giỏ hàng).
> 
> 3.  **Xác nhận Nguyên nhân Gốc rễ:**
>     -   **Nguyên nhân:** Logic cập nhật state ở frontend quá "ngây thơ". Nó thay thế toàn bộ đối tượng `user` thay vì chỉ cập nhật các trường đã thay đổi, dẫn đến mất dữ liệu giỏ hàng tạm thời ở client.

### Bước 3: Đề xuất và Áp dụng Bản vá

**SuperClaude đề xuất giải pháp:**

> **Phân tích hoàn tất. Nguyên nhân gốc rễ đã được xác định.**
> 
> **Giải pháp:** Thay vì ghi đè toàn bộ, chúng ta nên cập nhật state một cách an toàn hơn bằng cách merge dữ liệu cũ và mới.
> 
> **Code cũ trong `userStore.js`:**
> ```javascript
> setUser(state, userData) {
>   state.currentUser = userData;
> }
> ```
> 
> **Code đề xuất sửa đổi:**
> ```javascript
> setUser(state, userData) {
>   state.currentUser = { ...state.currentUser, ...userData };
> }
> ```
> 
> Tôi có thể áp dụng thay đổi này ngay bây giờ không?

**Bạn (User) gõ:**

> Đồng ý. Hãy áp dụng nó.

*(SuperClaude sử dụng công cụ `replace` để cập nhật code)*

---

**Kết quả:** Thay vì mò mẫm trong vô vọng, bạn đã sử dụng một quy trình điều tra bài bản để tìm ra chính xác nguyên nhân của một lỗi phức tạp và sửa nó một cách an toàn, tự tin.
