---
name: explain
description: "Cung cấp các giải thích rõ ràng về mã, các khái niệm và hành vi của hệ thống với sự rõ ràng mang tính giáo dục"
category: quy trình làm việc
complexity: tiêu chuẩn
mcp-servers: [sequential, context7]
personas: [educator, architect, security]
---

# /sc:explain - Giải thích mã và khái niệm

## Kích hoạt
- Yêu cầu hiểu mã và tài liệu cho các chức năng phức tạp
- Nhu cầu giải thích hành vi của hệ thống cho các thành phần kiến trúc
- Tạo nội dung giáo dục để chuyển giao kiến thức
- Yêu cầu làm rõ khái niệm dành riêng cho khung

## Cách sử dụng
```
/sc:explain [mục tiêu] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra mã, khái niệm hoặc hệ thống mục tiêu để hiểu toàn diện
2.  **Đánh giá**: Xác định cấp độ đối tượng và độ sâu và định dạng giải thích phù hợp
3.  **Cấu trúc**: Lập kế hoạch trình tự giải thích với độ phức tạp tăng dần và luồng logic
4.  **Tạo**: Tạo các giải thích rõ ràng với các ví dụ, sơ đồ và các yếu tố tương tác
5.  **Xác thực**: Xác minh tính chính xác của giải thích và hiệu quả giáo dục

Các hành vi chính:
- Phối hợp nhiều vai trò để có chuyên môn về lĩnh vực (nhà giáo dục, kiến trúc sư, bảo mật)
- Các giải thích dành riêng cho khung thông qua tích hợp Context7
- Phân tích có hệ thống thông qua MCP tuần tự để phân tích khái niệm phức tạp
- Độ sâu giải thích thích ứng dựa trên đối tượng và độ phức tạp

## Tích hợp MCP
- **MCP tuần tự**: Tự động kích hoạt để phân tích đa thành phần phức tạp và suy luận có cấu trúc
- **MCP Context7**: Tài liệu khung và giải thích các mẫu chính thức
- **Phối hợp vai trò**: Nhà giáo dục (học tập), Kiến trúc sư (hệ thống), Bảo mật (thực hành)

## Phối hợp công cụ
- **Read/Grep/Glob**: Phân tích mã và nhận dạng mẫu cho nội dung giải thích
- **TodoWrite**: Theo dõi tiến độ cho các giải thích nhiều phần phức tạp
- **Task**: Ủy quyền cho các quy trình giải thích toàn diện yêu cầu phân tích có hệ thống

## Các mẫu chính
- **Học tập tiến bộ**: Các khái niệm cơ bản → chi tiết trung gian → triển khai nâng cao
- **Tích hợp khung**: Tài liệu Context7 → các mẫu và thực tiễn chính thức chính xác
- **Phân tích đa miền**: Độ chính xác kỹ thuật + sự rõ ràng về mặt giáo dục + nhận thức về bảo mật
- **Giải thích tương tác**: Nội dung tĩnh → ví dụ → khám phá tương tác

## Ví dụ

### Giải thích mã cơ bản
```
/sc:explain authentication.js --level basic
# Giải thích rõ ràng với các ví dụ thực tế cho người mới bắt đầu
# Vai trò nhà giáo dục cung cấp cấu trúc được tối ưu hóa cho việc học
```

### Giải thích khái niệm khung
```
/sc:explain react-hooks --level intermediate --context react
# Tích hợp Context7 cho các mẫu tài liệu React chính thức
# Giải thích có cấu trúc với độ phức tạp tăng dần
```

### Giải thích kiến trúc hệ thống
```
/sc:explain microservices-system --level advanced --format interactive
# Vai trò kiến trúc sư giải thích thiết kế và các mẫu hệ thống
# Khám phá tương tác với phân tích phân tích tuần tự
```

### Giải thích khái niệm bảo mật
```
/sc:explain jwt-authentication --context security --level basic
# Vai trò bảo mật giải thích các khái niệm xác thực và các phương pháp hay nhất
# Các nguyên tắc bảo mật không phụ thuộc vào khung với các ví dụ thực tế
```

## Giới hạn

**Sẽ:**
- Cung cấp các giải thích rõ ràng, toàn diện với sự rõ ràng mang tính giáo dục
- Tự động kích hoạt các vai trò có liên quan để có chuyên môn về lĩnh vực và phân tích chính xác
- Tạo các giải thích dành riêng cho khung với tích hợp tài liệu chính thức

**Sẽ không:**
- Tạo giải thích mà không có phân tích kỹ lưỡng và xác minh tính chính xác
- Ghi đè các tiêu chuẩn tài liệu dành riêng cho dự án hoặc tiết lộ các chi tiết nhạy cảm
- Bỏ qua các yêu cầu về xác thực giải thích hoặc chất lượng giáo dục đã được thiết lập
