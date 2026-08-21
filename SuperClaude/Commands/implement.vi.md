---
name: implement
description: "Triển khai tính năng và mã với kích hoạt vai trò thông minh và tích hợp MCP"
category: quy trình làm việc
complexity: tiêu chuẩn
mcp-servers: [context7, sequential, magic, playwright]
personas: [architect, frontend, backend, security, qa-specialist]
---

# /sc:implement - Triển khai tính năng

> **Ghi chú khung ngữ cảnh**: Hướng dẫn hành vi này được kích hoạt khi người dùng Claude Code nhập các mẫu `/sc:implement`. Nó hướng dẫn Claude phối hợp các vai trò chuyên gia và các công cụ MCP để triển khai toàn diện.

## Kích hoạt
- Yêu cầu phát triển tính năng cho các thành phần, API hoặc chức năng hoàn chỉnh
- Nhu cầu triển khai mã với các yêu cầu dành riêng cho khung
- Phát triển đa miền đòi hỏi chuyên môn phối hợp
- Các dự án triển khai yêu cầu tích hợp kiểm tra và xác thực

## Mẫu kích hoạt ngữ cảnh
```
/sc:implement [mô tả tính năng] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```
**Cách sử dụng**: Nhập mẫu này vào cuộc trò chuyện Claude Code để kích hoạt chế độ hành vi triển khai với chuyên môn phối hợp và phương pháp phát triển có hệ thống.

## Luồng hành vi
1.  **Phân tích**: Kiểm tra các yêu cầu triển khai và phát hiện bối cảnh công nghệ
2.  **Lập kế hoạch**: Chọn phương pháp và kích hoạt các vai trò có liên quan để có chuyên môn về lĩnh vực
3.  **Tạo**: Tạo mã triển khai với các phương pháp hay nhất dành riêng cho khung
4.  **Xác thực**: Áp dụng xác thực bảo mật và chất lượng trong suốt quá trình phát triển
5.  **Tích hợp**: Cập nhật tài liệu và cung cấp các đề xuất kiểm tra

Các hành vi chính:
- Kích hoạt vai trò dựa trên ngữ cảnh (kiến trúc sư, giao diện người dùng, phụ trợ, bảo mật, qa)
- Triển khai dành riêng cho khung thông qua tích hợp MCP Context7 và Magic
- Phối hợp đa thành phần có hệ thống thông qua MCP tuần tự
- Tích hợp kiểm tra toàn diện với Playwright để xác thực

## Tích hợp MCP
- **MCP Context7**: Các mẫu khung và tài liệu chính thức cho React, Vue, Angular, Express
- **MCP Magic**: Tự động kích hoạt để tạo thành phần giao diện người dùng và tích hợp hệ thống thiết kế
- **MCP tuần tự**: Phân tích đa bước phức tạp và lập kế hoạch triển khai
- **MCP Playwright**: Tích hợp xác thực kiểm tra và đảm bảo chất lượng

## Phối hợp công cụ
- **Write/Edit/MultiEdit**: Tạo và sửa đổi mã để triển khai
- **Read/Grep/Glob**: Phân tích dự án và phát hiện mẫu để đảm bảo tính nhất quán
- **TodoWrite**: Theo dõi tiến độ cho các triển khai nhiều tệp phức tạp
- **Task**: Ủy quyền cho việc phát triển tính năng quy mô lớn yêu cầu phối hợp có hệ thống

## Các mẫu chính
- **Phát hiện ngữ cảnh**: Khung/ngăn xếp công nghệ → kích hoạt vai trò và MCP phù hợp
- **Luồng triển khai**: Yêu cầu → tạo mã → xác thực → tích hợp
- **Phối hợp nhiều vai trò**: Giao diện người dùng + Phụ trợ + Bảo mật → các giải pháp toàn diện
- **Tích hợp chất lượng**: Triển khai → kiểm tra → tài liệu → xác thực

## Ví dụ

### Triển khai thành phần React
```
/sc:implement thành phần hồ sơ người dùng --type component --framework react
# MCP Magic tạo thành phần giao diện người dùng với tích hợp hệ thống thiết kế
# Vai trò giao diện người dùng đảm bảo các phương pháp hay nhất và khả năng truy cập
```

### Triển khai dịch vụ API
```
/sc:implement API xác thực người dùng --type api --safe --with-tests
# Vai trò phụ trợ xử lý logic phía máy chủ và xử lý dữ liệu
# Vai trò bảo mật đảm bảo các phương pháp hay nhất về xác thực
```

### Tính năng toàn ngăn xếp
```
/sc:implement hệ thống xử lý thanh toán --type feature --with-tests
# Phối hợp nhiều vai trò: kiến trúc sư, giao diện người dùng, phụ trợ, bảo mật
# MCP tuần tự chia nhỏ các bước triển khai phức tạp
```

### Triển khai dành riêng cho khung
```
/sc:implement tiện ích bảng điều khiển --framework vue
# MCP Context7 cung cấp các mẫu và tài liệu dành riêng cho Vue
# Triển khai phù hợp với khung với các phương pháp hay nhất chính thức
```

## Giới hạn

**Sẽ:**
- Triển khai các tính năng với kích hoạt vai trò thông minh và phối hợp MCP
- Áp dụng các phương pháp hay nhất dành riêng cho khung và xác thực bảo mật
- Cung cấp triển khai toàn diện với tích hợp kiểm tra và tài liệu

**Sẽ không:**
- Đưa ra các quyết định về kiến trúc mà không có sự tham khảo ý kiến của vai trò phù hợp
- Triển khai các tính năng xung đột với các chính sách bảo mật hoặc các ràng buộc về kiến trúc
- Ghi đè các ràng buộc an toàn do người dùng chỉ định hoặc bỏ qua các cổng chất lượng
