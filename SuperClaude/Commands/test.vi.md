---
name: test
description: "Thực hiện các bài kiểm tra với phân tích phạm vi và báo cáo chất lượng tự động"
category: tiện ích
complexity: nâng cao
mcp-servers: [playwright]
personas: [qa-specialist]
---

# /sc:test - Kiểm tra và đảm bảo chất lượng

## Kích hoạt
- Yêu cầu thực hiện kiểm tra cho các bài kiểm tra đơn vị, tích hợp hoặc đầu cuối
- Nhu cầu phân tích phạm vi và xác thực cổng chất lượng
- Các kịch bản kiểm tra liên tục và chế độ theo dõi
- Yêu cầu phân tích và gỡ lỗi lỗi kiểm tra

## Cách sử dụng
```
/sc:test [mục tiêu] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

## Luồng hành vi
1.  **Khám phá**: Phân loại các bài kiểm tra có sẵn bằng cách sử dụng các mẫu và quy ước của trình chạy
2.  **Cấu hình**: Thiết lập môi trường kiểm tra và các tham số thực thi phù hợp
3.  **Thực thi**: Chạy các bài kiểm tra với giám sát và theo dõi tiến độ thời gian thực
4.  **Phân tích**: Tạo báo cáo phạm vi và chẩn đoán lỗi
5.  **Báo cáo**: Cung cấp các đề xuất có thể hành động và các chỉ số chất lượng

Các hành vi chính:
- Tự động phát hiện khung kiểm tra và cấu hình
- Tạo báo cáo phạm vi toàn diện với các chỉ số
- Kích hoạt MCP Playwright để kiểm tra trình duyệt đầu cuối
- Cung cấp phân tích lỗi kiểm tra thông minh
- Hỗ trợ chế độ theo dõi liên tục để phát triển

## Tích hợp MCP
- **MCP Playwright**: Tự động kích hoạt để kiểm tra trình duyệt `--type e2e`
- **Vai trò chuyên gia QA**: Được kích hoạt để phân tích kiểm tra và đánh giá chất lượng
- **Khả năng nâng cao**: Kiểm tra trên nhiều trình duyệt, xác thực trực quan, các chỉ số hiệu suất

## Phối hợp công cụ
- **Bash**: Thực thi trình chạy kiểm tra và quản lý môi trường
- **Glob**: Khám phá kiểm tra và đối sánh mẫu tệp
- **Grep**: Phân tích cú pháp kết quả và phân tích lỗi
- **Write**: Báo cáo phạm vi và tóm tắt kiểm tra

## Các mẫu chính
- **Khám phá kiểm tra**: Phân loại dựa trên mẫu → lựa chọn trình chạy phù hợp
- **Phân tích phạm vi**: Các chỉ số thực thi → báo cáo phạm vi toàn diện
- **Kiểm tra đầu cuối**: Tự động hóa trình duyệt → xác thực trên nhiều nền tảng
- **Chế độ theo dõi**: Giám sát tệp → thực hiện kiểm tra liên tục

## Ví dụ

### Thực hiện kiểm tra cơ bản
```
/sc:test
# Khám phá và chạy tất cả các bài kiểm tra với cấu hình tiêu chuẩn
# Tạo tóm tắt đạt/không đạt và phạm vi cơ bản
```

### Phân tích phạm vi được nhắm mục tiêu
```
/sc:test src/components --type unit --coverage
# Các bài kiểm tra đơn vị cho thư mục cụ thể với các chỉ số phạm vi chi tiết
```

### Kiểm tra trình duyệt
```
/sc:test --type e2e
# Kích hoạt MCP Playwright để kiểm tra trình duyệt toàn diện
# Khả năng tương thích trên nhiều trình duyệt và xác thực trực quan
```

### Chế độ theo dõi phát triển
```
/sc:test --watch --fix
# Kiểm tra liên tục với các bản sửa lỗi đơn giản tự động
# Phản hồi thời gian thực trong quá trình phát triển
```

## Giới hạn

**Sẽ:**
- Thực hiện các bộ kiểm tra hiện có bằng cách sử dụng trình chạy kiểm tra được định cấu hình của dự án
- Tạo báo cáo phạm vi và các chỉ số chất lượng
- Cung cấp phân tích lỗi kiểm tra thông minh với các đề xuất có thể hành động

**Sẽ không:**
- Tạo các trường hợp kiểm tra hoặc sửa đổi cấu hình khung kiểm tra
- Thực hiện các bài kiểm tra yêu cầu các dịch vụ bên ngoài mà không có thiết lập phù hợp
- Thực hiện các thay đổi phá hủy đối với các tệp kiểm tra mà không có sự cho phép rõ ràng
