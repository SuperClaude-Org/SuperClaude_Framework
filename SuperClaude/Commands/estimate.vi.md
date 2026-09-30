---
name: estimate
description: "Cung cấp các ước tính phát triển cho các tác vụ, tính năng hoặc dự án với phân tích thông minh"
category: đặc biệt
complexity: tiêu chuẩn
mcp-servers: [sequential, context7]
personas: [architect, performance, project-manager]
---

# /sc:estimate - Ước tính phát triển

## Kích hoạt
- Lập kế hoạch phát triển yêu cầu ước tính thời gian, công sức hoặc độ phức tạp
- Quyết định về phạm vi dự án và phân bổ nguồn lực
- Phân tích tính năng cần phương pháp ước tính có hệ thống
- Yêu cầu phân tích khoảng tin cậy và đánh giá rủi ro

## Cách sử dụng
```
/sc:estimate [mục tiêu] [--type time|effort|complexity] [--unit hours|days|weeks] [--breakdown]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra phạm vi, các yếu tố phức tạp, các phụ thuộc và các mẫu khung
2.  **Tính toán**: Áp dụng phương pháp ước tính với các điểm chuẩn lịch sử và chấm điểm độ phức tạp
3.  **Xác thực**: Đối chiếu các ước tính với các mẫu dự án và chuyên môn về lĩnh vực
4.  **Trình bày**: Cung cấp phân tích chi tiết với các khoảng tin cậy và đánh giá rủi ro
5.  **Theo dõi**: Ghi lại độ chính xác của ước tính để cải tiến phương pháp liên tục

Các hành vi chính:
- Phối hợp nhiều vai trò (kiến trúc sư, hiệu suất, quản lý dự án) dựa trên phạm vi ước tính
- Tích hợp MCP tuần tự để phân tích có hệ thống và đánh giá độ phức tạp
- Tích hợp MCP Context7 cho các mẫu dành riêng cho khung và các điểm chuẩn lịch sử
- Phân tích phân tích thông minh với các khoảng tin cậy và các yếu tố rủi ro

## Tích hợp MCP
- **MCP tuần tự**: Phân tích ước tính đa bước phức tạp và đánh giá độ phức tạp có hệ thống
- **MCP Context7**: Các mẫu ước tính dành riêng cho khung và dữ liệu điểm chuẩn lịch sử
- **Phối hợp vai trò**: Kiến trúc sư (độ phức tạp của thiết kế), Hiệu suất (nỗ lực tối ưu hóa), Quản lý dự án (tiến trình)

## Phối hợp công cụ
- **Read/Grep/Glob**: Phân tích mã nguồn để đánh giá độ phức tạp và đánh giá phạm vi
- **TodoWrite**: Phân tích ước tính và theo dõi tiến độ cho các quy trình ước tính phức tạp
- **Task**: Ủy quyền nâng cao để ước tính đa miền yêu cầu phối hợp có hệ thống
- **Bash**: Phân tích dự án và đánh giá phụ thuộc để chấm điểm độ phức tạp chính xác

## Các mẫu chính
- **Phân tích phạm vi**: Yêu cầu dự án → các yếu tố phức tạp → các mẫu khung → đánh giá rủi ro
- **Phương pháp ước tính**: Dựa trên thời gian → Dựa trên công sức → Dựa trên độ phức tạp → Các phương pháp dựa trên chi phí
- **Đánh giá đa miền**: Độ phức tạp của kiến trúc → Yêu cầu về hiệu suất → Tiến trình dự án
- **Khung xác thực**: Điểm chuẩn lịch sử → xác thực chéo → khoảng tin cậy → theo dõi độ chính xác

## Ví dụ

### Ước tính phát triển tính năng
```
/sc:estimate "hệ thống xác thực người dùng" --type time --unit days --breakdown
# Phân tích có hệ thống: Thiết kế cơ sở dữ liệu (2 ngày) + API phụ trợ (3 ngày) + Giao diện người dùng giao diện người dùng (2 ngày) + Kiểm tra (1 ngày)
# Tổng cộng: 8 ngày với khoảng tin cậy 85%
```

### Đánh giá độ phức tạp của dự án
```
/sc:estimate "di chuyển khối nguyên khối sang các dịch vụ vi mô" --type complexity --breakdown
# Phân tích độ phức tạp của kiến trúc với các yếu tố rủi ro và ánh xạ phụ thuộc
# Phối hợp nhiều vai trò để đánh giá toàn diện
```

### Nỗ lực tối ưu hóa hiệu suất
```
/sc:estimate "tối ưu hóa hiệu suất ứng dụng" --type effort --unit hours
# Phân tích vai trò hiệu suất với các so sánh điểm chuẩn
# Phân tích nỗ lực theo danh mục tối ưu hóa và tác động dự kiến
```

## Giới hạn

**Sẽ:**
- Cung cấp các ước tính phát triển có hệ thống với các khoảng tin cậy và đánh giá rủi ro
- Áp dụng phối hợp nhiều vai trò để phân tích độ phức tạp toàn diện
- Tạo phân tích phân tích chi tiết với các so sánh điểm chuẩn lịch sử

**Sẽ không:**
- Đảm bảo độ chính xác của ước tính mà không có phân tích và xác thực phạm vi phù hợp
- Cung cấp các ước tính mà không có chuyên môn về lĩnh vực và đánh giá độ phức tạp phù hợp
- Ghi đè các điểm chuẩn lịch sử mà không có sự biện minh và phân tích rõ ràng
