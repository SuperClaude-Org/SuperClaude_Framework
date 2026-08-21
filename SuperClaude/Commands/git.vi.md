---
name: git
description: "Các thao tác Git với thông báo commit thông minh và tối ưu hóa quy trình làm việc"
category: tiện ích
complexity: cơ bản
mcp-servers: []
personas: []
---

# /sc:git - Các thao tác Git

## Kích hoạt
- Các thao tác kho lưu trữ Git: status, add, commit, push, pull, branch
- Cần tạo thông báo commit thông minh
- Yêu cầu tối ưu hóa quy trình làm việc của kho lưu trữ
- Quản lý nhánh và các thao tác hợp nhất

## Cách sử dụng
```
/sc:git [thao tác] [đối số] [--smart-commit] [--interactive]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra trạng thái kho lưu trữ và các thay đổi trong thư mục làm việc
2.  **Xác thực**: Đảm bảo thao tác phù hợp với ngữ cảnh Git hiện tại
3.  **Thực thi**: Chạy lệnh Git với tự động hóa thông minh
4.  **Tối ưu hóa**: Áp dụng các thông báo commit thông minh và các mẫu quy trình làm việc
5.  **Báo cáo**: Cung cấp trạng thái và hướng dẫn các bước tiếp theo

Các hành vi chính:
- Tạo các thông báo commit thông thường dựa trên phân tích thay đổi
- Áp dụng các quy ước đặt tên nhánh nhất quán
- Xử lý các xung đột hợp nhất với giải pháp có hướng dẫn
- Cung cấp các bản tóm tắt trạng thái rõ ràng và các đề xuất quy trình làm việc

## Phối hợp công cụ
- **Bash**: Thực thi lệnh Git và các thao tác kho lưu trữ
- **Read**: Phân tích trạng thái kho lưu trữ và xem xét cấu hình
- **Grep**: Phân tích cú pháp nhật ký và phân tích trạng thái
- **Write**: Tạo thông báo commit và tài liệu

## Các mẫu chính
- **Commit thông minh**: Phân tích các thay đổi → tạo thông báo commit thông thường
- **Phân tích trạng thái**: Trạng thái kho lưu trữ → các đề xuất có thể hành động
- **Chiến lược nhánh**: Đặt tên nhất quán và thực thi quy trình làm việc
- **Phục hồi lỗi**: Giải quyết xung đột và hướng dẫn khôi phục trạng thái

## Ví dụ

### Phân tích trạng thái thông minh
```
/sc:git status
# Phân tích trạng thái kho lưu trữ với tóm tắt thay đổi
# Cung cấp các bước tiếp theo và các đề xuất quy trình làm việc
```

### Commit thông minh
```
/sc:git commit --smart-commit
# Tạo thông báo commit thông thường từ phân tích thay đổi
# Áp dụng các phương pháp hay nhất và định dạng nhất quán
```

### Các thao tác tương tác
```
/sc:git merge feature-branch --interactive
# Hợp nhất có hướng dẫn với hỗ trợ giải quyết xung đột
```

## Giới hạn

**Sẽ:**
- Thực thi các thao tác Git với tự động hóa thông minh
- Tạo các thông báo commit thông thường từ phân tích thay đổi
- Cung cấp tối ưu hóa quy trình làm việc và hướng dẫn các phương pháp hay nhất

**Sẽ không:**
- Sửa đổi cấu hình kho lưu trữ mà không có sự cho phép rõ ràng
- Thực hiện các thao tác phá hủy mà không có xác nhận
- Xử lý các hợp nhất phức tạp yêu cầu can thiệp thủ công
