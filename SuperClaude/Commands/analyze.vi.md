---
name: analyze
description: "Phân tích mã toàn diện trên các lĩnh vực chất lượng, bảo mật, hiệu suất và kiến trúc"
category: tiện ích
complexity: cơ bản
mcp-servers: []
personas: []
---

# /sc:analyze - Phân tích mã và Đánh giá chất lượng

## Kích hoạt
- Yêu cầu đánh giá chất lượng mã cho các dự án hoặc các thành phần cụ thể
- Nhu cầu quét lỗ hổng bảo mật và xác thực tuân thủ
- Xác định điểm nghẽn hiệu suất và lập kế hoạch tối ưu hóa
- Yêu cầu xem xét kiến trúc và đánh giá nợ kỹ thuật

## Cách sử dụng
```
/sc:analyze [mục tiêu] [--focus quality|security|performance|architecture] [--depth quick|deep] [--format text|json|report]
```

## Luồng hành vi
1.  **Khám phá**: Phân loại các tệp nguồn bằng cách phát hiện ngôn ngữ và phân tích dự án
2.  **Quét**: Áp dụng các kỹ thuật phân tích dành riêng cho từng lĩnh vực và đối sánh mẫu
3.  **Đánh giá**: Tạo các phát hiện được ưu tiên với xếp hạng mức độ nghiêm trọng và đánh giá tác động
4.  **Đề xuất**: Tạo các đề xuất có thể hành động với hướng dẫn triển khai
5.  **Báo cáo**: Trình bày phân tích toàn diện với các số liệu và lộ trình cải tiến

Các hành vi chính:
- Phân tích đa lĩnh vực kết hợp phân tích tĩnh và đánh giá theo kinh nghiệm
- Khám phá tệp thông minh và nhận dạng mẫu theo ngôn ngữ cụ thể
- Ưu tiên các phát hiện và đề xuất dựa trên mức độ nghiêm trọng
- Báo cáo toàn diện với các số liệu, xu hướng và thông tin chi tiết có thể hành động

## Phối hợp công cụ
- **Glob**: Khám phá tệp và phân tích cấu trúc dự án
- **Grep**: Phân tích mẫu và các thao tác tìm kiếm mã
- **Read**: Kiểm tra mã nguồn và phân tích cấu hình
- **Bash**: Thực thi và xác thực công cụ phân tích bên ngoài
- **Write**: Tạo báo cáo và tài liệu hóa các số liệu

## Các mẫu chính
- **Phân tích lĩnh vực**: Chất lượng/Bảo mật/Hiệu suất/Kiến trúc → đánh giá chuyên biệt
- **Nhận dạng mẫu**: Phát hiện ngôn ngữ → kỹ thuật phân tích phù hợp
- **Đánh giá mức độ nghiêm trọng**: Phân loại sự cố → các đề xuất được ưu tiên
- **Tạo báo cáo**: Kết quả phân tích → tài liệu có cấu trúc

## Ví dụ

### Phân tích dự án toàn diện
```
/sc:analyze
# Phân tích đa lĩnh vực của toàn bộ dự án
# Tạo báo cáo toàn diện với các phát hiện chính và lộ trình
```

### Đánh giá bảo mật tập trung
```
/sc:analyze src/auth --focus security --depth deep
# Phân tích bảo mật sâu các thành phần xác thực
# Đánh giá lỗ hổng với hướng dẫn khắc phục chi tiết
```

### Phân tích tối ưu hóa hiệu suất
```
/sc:analyze --focus performance --format report
# Xác định điểm nghẽn hiệu suất
# Tạo báo cáo HTML với các đề xuất tối ưu hóa
```

### Kiểm tra chất lượng nhanh
```
/sc:analyze src/components --focus quality --depth quick
# Đánh giá chất lượng nhanh thư mục thành phần
# Xác định các "code smell" và các vấn đề về khả năng bảo trì
```

## Giới hạn

**Sẽ:**
- Thực hiện phân tích mã tĩnh toàn diện trên nhiều lĩnh vực
- Tạo ra các phát hiện được xếp hạng theo mức độ nghiêm trọng với các đề xuất có thể hành động
- Cung cấp các báo cáo chi tiết với các số liệu và hướng dẫn cải tiến

**Sẽ không:**
- Thực hiện phân tích động yêu cầu biên dịch mã hoặc môi trường thời gian chạy
- Sửa đổi mã nguồn hoặc áp dụng các bản sửa lỗi mà không có sự đồng ý rõ ràng của người dùng
- Phân tích các phụ thuộc bên ngoài ngoài các mẫu nhập và sử dụng