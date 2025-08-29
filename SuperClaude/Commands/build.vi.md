---
name: build
description: "Xây dựng, biên dịch và đóng gói các dự án với khả năng xử lý lỗi và tối ưu hóa thông minh"
category: tiện ích
complexity: nâng cao
mcp-servers: [playwright]
personas: [devops-engineer]
---

# /sc:build - Xây dựng và đóng gói dự án

## Kích hoạt
- Yêu cầu biên dịch và đóng gói dự án cho các môi trường khác nhau
- Nhu cầu tối ưu hóa bản dựng và tạo tạo phẩm
- Gỡ lỗi trong quá trình xây dựng
- Yêu cầu chuẩn bị triển khai và đóng gói tạo phẩm

## Cách sử dụng
```
/sc:build [mục tiêu] [--type dev|prod|test] [--clean] [--optimize] [--verbose]
```

## Luồng hành vi
1.  **Phân tích**: Cấu trúc dự án, cấu hình bản dựng và tệp kê khai phụ thuộc
2.  **Xác thực**: Môi trường xây dựng, các phụ thuộc và các thành phần chuỗi công cụ bắt buộc
3.  **Thực thi**: Quá trình xây dựng với giám sát thời gian thực và phát hiện lỗi
4.  **Tối ưu hóa**: Xây dựng các tạo phẩm, áp dụng các tối ưu hóa và giảm thiểu kích thước gói
5.  **Đóng gói**: Tạo các tạo phẩm triển khai và báo cáo xây dựng toàn diện

Các hành vi chính:
- Điều phối xây dựng theo cấu hình với xác thực phụ thuộc
- Phân tích lỗi thông minh với hướng dẫn giải quyết có thể hành động
- Tối ưu hóa theo môi trường cụ thể (cấu hình dev/prod/test)
- Báo cáo xây dựng toàn diện với các chỉ số thời gian và phân tích tạo phẩm

## Tích hợp MCP
- **MCP Playwright**: Tự động kích hoạt để xác thực bản dựng và kiểm tra giao diện người dùng trong quá trình xây dựng
- **Vai trò Kỹ sư DevOps**: Được kích hoạt để tối ưu hóa bản dựng và chuẩn bị triển khai
- **Khả năng nâng cao**: Tích hợp quy trình xây dựng, giám sát hiệu suất, xác thực tạo phẩm

## Phối hợp công cụ
- **Bash**: Thực thi hệ thống xây dựng và quản lý quy trình
- **Read**: Phân tích cấu hình và kiểm tra tệp kê khai
- **Grep**: Phân tích cú pháp lỗi và phân tích nhật ký xây dựng
- **Glob**: Khám phá và xác thực tạo phẩm
- **Write**: Báo cáo xây dựng và tài liệu triển khai

## Các mẫu chính
- **Bản dựng môi trường**: dev/prod/test → cấu hình và tối ưu hóa phù hợp
- **Phân tích lỗi**: Lỗi xây dựng → phân tích chẩn đoán và hướng dẫn giải quyết
- **Tối ưu hóa**: Phân tích tạo phẩm → giảm kích thước và cải thiện hiệu suất
- **Xác thực**: Xác minh bản dựng → cổng chất lượng và sẵn sàng triển khai

## Ví dụ

### Xây dựng dự án tiêu chuẩn
```
/sc:build
# Xây dựng toàn bộ dự án bằng cấu hình mặc định
# Tạo các tạo phẩm và báo cáo xây dựng toàn diện
```

### Xây dựng tối ưu hóa sản xuất
```
/sc:build --type prod --clean --optimize
# Xây dựng sản xuất sạch với các tối ưu hóa nâng cao
# Thu nhỏ, loại bỏ mã không dùng đến và chuẩn bị triển khai
```

### Xây dựng thành phần được nhắm mục tiêu
```
/sc:build frontend --verbose
# Xây dựng thành phần dự án cụ thể với đầu ra chi tiết
# Giám sát tiến độ thời gian thực và thông tin chẩn đoán
```

### Xây dựng phát triển với xác thực
```
/sc:build --type dev --validate
# Xây dựng phát triển với xác thực Playwright
# Tích hợp kiểm tra giao diện người dùng và xác minh bản dựng
```

## Giới hạn

**Sẽ:**
- Thực thi các hệ thống xây dựng dự án bằng các cấu hình hiện có
- Cung cấp phân tích lỗi toàn diện và các đề xuất tối ưu hóa
- Tạo các tạo phẩm sẵn sàng triển khai với báo cáo chi tiết

**Sẽ không:**
- Sửa đổi cấu hình hệ thống xây dựng hoặc tạo tập lệnh xây dựng mới
- Cài đặt các phụ thuộc xây dựng hoặc công cụ phát triển bị thiếu
- Thực hiện các hoạt động triển khai ngoài việc chuẩn bị tạo phẩm
