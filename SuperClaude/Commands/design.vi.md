---
name: design
description: "Thiết kế kiến trúc hệ thống, API và giao diện thành phần với các thông số kỹ thuật toàn diện"
category: tiện ích
complexity: cơ bản
mcp-servers: []
personas: []
---

# /sc:design - Thiết kế hệ thống và thành phần

## Kích hoạt
- Yêu cầu lập kế hoạch kiến trúc và thiết kế hệ thống
- Nhu cầu đặc tả API và thiết kế giao diện
- Yêu cầu thiết kế thành phần và đặc tả kỹ thuật
- Yêu cầu thiết kế lược đồ cơ sở dữ liệu và mô hình dữ liệu

## Cách sử dụng
```
/sc:design [mục tiêu] [--type architecture|api|component|database] [--format diagram|spec|code]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra các yêu cầu mục tiêu và bối cảnh hệ thống hiện có
2.  **Lập kế hoạch**: Xác định phương pháp và cấu trúc thiết kế dựa trên loại và định dạng
3.  **Thiết kế**: Tạo các thông số kỹ thuật toàn diện với các phương pháp hay nhất trong ngành
4.  **Xác thực**: Đảm bảo thiết kế đáp ứng các yêu cầu và tiêu chuẩn về khả năng bảo trì
5.  **Tài liệu**: Tạo tài liệu thiết kế rõ ràng với các sơ đồ và thông số kỹ thuật

Các hành vi chính:
- Phương pháp thiết kế theo yêu cầu với các cân nhắc về khả năng mở rộng
- Tích hợp các phương pháp hay nhất trong ngành cho các giải pháp có thể bảo trì
- Đầu ra đa định dạng (sơ đồ, thông số kỹ thuật, mã) dựa trên nhu cầu
- Xác thực dựa trên kiến trúc và các ràng buộc của hệ thống hiện có

## Phối hợp công cụ
- **Read**: Phân tích yêu cầu và kiểm tra hệ thống hiện có
- **Grep/Glob**: Phân tích mẫu và điều tra cấu trúc hệ thống
- **Write**: Tài liệu thiết kế và tạo đặc tả
- **Bash**: Tích hợp công cụ thiết kế bên ngoài khi cần thiết

## Các mẫu chính
- **Thiết kế kiến trúc**: Yêu cầu → cấu trúc hệ thống → lập kế hoạch khả năng mở rộng
- **Thiết kế API**: Đặc tả giao diện → các mẫu RESTful/GraphQL → tài liệu
- **Thiết kế thành phần**: Yêu cầu chức năng → thiết kế giao diện → hướng dẫn triển khai
- **Thiết kế cơ sở dữ liệu**: Yêu cầu dữ liệu → thiết kế lược đồ → mô hình hóa mối quan hệ

## Ví dụ

### Thiết kế kiến trúc hệ thống
```
/sc:design user-management-system --type architecture --format diagram
# Tạo kiến trúc hệ thống toàn diện với các mối quan hệ thành phần
# Bao gồm các cân nhắc về khả năng mở rộng và các phương pháp hay nhất
```

### Thiết kế đặc tả API
```
/sc:design payment-api --type api --format spec
# Tạo đặc tả API chi tiết với các điểm cuối và mô hình dữ liệu
# Tuân theo các nguyên tắc thiết kế RESTful và các tiêu chuẩn ngành
```

### Thiết kế giao diện thành phần
```
/sc:design notification-service --type component --format code
# Thiết kế giao diện thành phần với các hợp đồng và phụ thuộc rõ ràng
# Cung cấp hướng dẫn triển khai và các mẫu tích hợp
```

### Thiết kế lược đồ cơ sở dữ liệu
```
/sc:design e-commerce-db --type database --format diagram
# Tạo lược đồ cơ sở dữ liệu với các mối quan hệ và ràng buộc thực thể
# Bao gồm các cân nhắc về chuẩn hóa và hiệu suất
```

## Giới hạn

**Sẽ:**
- Tạo các thông số kỹ thuật thiết kế toàn diện với các phương pháp hay nhất trong ngành
- Tạo ra nhiều định dạng đầu ra (sơ đồ, thông số kỹ thuật, mã) dựa trên yêu cầu
- Xác thực các thiết kế dựa trên các tiêu chuẩn về khả năng bảo trì và khả năng mở rộng

**Sẽ không:**
- Tạo mã triển khai thực tế (sử dụng /sc:implement để triển khai)
- Sửa đổi kiến trúc hệ thống hiện có mà không có sự chấp thuận thiết kế rõ ràng
- Tạo các thiết kế vi phạm các ràng buộc kiến trúc đã được thiết lập
