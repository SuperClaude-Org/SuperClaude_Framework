---
name: document
description: "Tạo tài liệu tập trung cho các thành phần, hàm, API và tính năng"
category: tiện ích
complexity: cơ bản
mcp-servers: []
personas: []
---

# /sc:document - Tạo tài liệu tập trung

## Kích hoạt
- Yêu cầu tài liệu cho các thành phần, hàm hoặc tính năng cụ thể
- Nhu cầu tạo tài liệu API và tài liệu tham khảo
- Yêu cầu về nhận xét mã và tài liệu nội tuyến
- Yêu cầu tạo hướng dẫn sử dụng và tài liệu kỹ thuật

## Cách sử dụng
```
/sc:document [mục tiêu] [--type inline|external|api|guide] [--style brief|detailed]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra cấu trúc, giao diện và chức năng của thành phần mục tiêu
2.  **Xác định**: Xác định các yêu cầu về tài liệu và bối cảnh đối tượng mục tiêu
3.  **Tạo**: Tạo nội dung tài liệu phù hợp dựa trên loại và kiểu
4.  **Định dạng**: Áp dụng cấu trúc và các mẫu tổ chức nhất quán
5.  **Tích hợp**: Đảm bảo khả năng tương thích với hệ sinh thái tài liệu dự án hiện có

Các hành vi chính:
- Phân tích cấu trúc mã với trích xuất API và nhận dạng mẫu sử dụng
- Tạo tài liệu đa định dạng (nội tuyến, bên ngoài, tham chiếu API, hướng dẫn)
- Định dạng nhất quán và tích hợp tham chiếu chéo
- Các mẫu và quy ước tài liệu dành riêng cho ngôn ngữ

## Phối hợp công cụ
- **Read**: Phân tích thành phần và xem xét tài liệu hiện có
- **Grep**: Trích xuất tham chiếu và nhận dạng mẫu
- **Write**: Tạo tệp tài liệu với định dạng phù hợp
- **Glob**: Các dự án và tổ chức tài liệu nhiều tệp

## Các mẫu chính
- **Tài liệu nội tuyến**: Phân tích mã → tạo JSDoc/docstring → nhận xét nội tuyến
- **Tài liệu API**: Trích xuất giao diện → tài liệu tham khảo → ví dụ sử dụng
- **Hướng dẫn sử dụng**: Phân tích tính năng → nội dung hướng dẫn → hướng dẫn triển khai
- **Tài liệu bên ngoài**: Tổng quan về thành phần → thông số kỹ thuật chi tiết → hướng dẫn tích hợp

## Ví dụ

### Tài liệu mã nội tuyến
```
/sc:document src/auth/login.js --type inline
# Tạo nhận xét JSDoc với mô tả tham số và trả về
# Thêm tài liệu nội tuyến toàn diện cho các hàm và lớp
```

### Tạo tham chiếu API
```
/sc:document src/api --type api --style detailed
# Tạo tài liệu API toàn diện với các điểm cuối và lược đồ
# Tạo ví dụ sử dụng và hướng dẫn tích hợp
```

### Tạo hướng dẫn sử dụng
```
/sc:document payment-module --type guide --style brief
# Tạo tài liệu tập trung vào người dùng với các ví dụ thực tế
# Tập trung vào các mẫu triển khai và các trường hợp sử dụng phổ biến
```

### Tài liệu thành phần
```
/sc:document components/ --type external
# Tạo các tệp tài liệu bên ngoài cho thư viện thành phần
# Bao gồm các đạo cụ, ví dụ sử dụng và các mẫu tích hợp
```

## Giới hạn

**Sẽ:**
- Tạo tài liệu tập trung cho các thành phần và tính năng cụ thể
- Tạo nhiều định dạng tài liệu dựa trên nhu cầu của đối tượng mục tiêu
- Tích hợp với các hệ sinh thái tài liệu hiện có và duy trì tính nhất quán

**Sẽ không:**
- Tạo tài liệu mà không có phân tích mã và hiểu biết về ngữ cảnh phù hợp
- Ghi đè các tiêu chuẩn tài liệu hiện có hoặc các quy ước dành riêng cho dự án
- Tạo tài liệu tiết lộ các chi tiết triển khai nhạy cảm
