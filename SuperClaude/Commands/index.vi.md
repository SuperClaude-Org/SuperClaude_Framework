---
name: index
description: "Tạo tài liệu dự án và cơ sở kiến thức toàn diện với tổ chức thông minh"
category: đặc biệt
complexity: tiêu chuẩn
mcp-servers: [sequential, context7]
personas: [architect, scribe, quality]
---

# /sc:index - Tài liệu dự án

## Kích hoạt
- Yêu cầu tạo và bảo trì tài liệu dự án
- Nhu cầu tạo và tổ chức cơ sở kiến thức
- Yêu cầu phân tích cấu trúc và tài liệu API
- Yêu cầu nâng cao khả năng tham chiếu chéo và điều hướng

## Cách sử dụng
```
/sc:index [mục tiêu] [--type docs|api|structure|readme] [--format md|json|yaml]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra cấu trúc dự án và xác định các thành phần tài liệu chính
2.  **Tổ chức**: Áp dụng các mẫu tổ chức thông minh và các chiến lược tham chiếu chéo
3.  **Tạo**: Tạo tài liệu toàn diện với các mẫu dành riêng cho khung
4.  **Xác thực**: Đảm bảo tính đầy đủ của tài liệu và các tiêu chuẩn chất lượng
5.  **Bảo trì**: Cập nhật tài liệu hiện có trong khi vẫn giữ lại các bổ sung và tùy chỉnh thủ công

Các hành vi chính:
- Phối hợp nhiều vai trò (kiến trúc sư, người ghi chép, chất lượng) dựa trên phạm vi và độ phức tạp của tài liệu
- Tích hợp MCP tuần tự để phân tích có hệ thống và các quy trình tài liệu toàn diện
- Tích hợp MCP Context7 cho các mẫu dành riêng cho khung và các tiêu chuẩn tài liệu
- Tổ chức thông minh với khả năng tham chiếu chéo và bảo trì tự động

## Tích hợp MCP
- **MCP tuần tự**: Phân tích dự án đa bước phức tạp và tạo tài liệu có hệ thống
- **MCP Context7**: Các mẫu tài liệu dành riêng cho khung và các tiêu chuẩn đã được thiết lập
- **Phối hợp vai trò**: Kiến trúc sư (cấu trúc), Người ghi chép (nội dung), Chất lượng (xác thực)

## Phối hợp công cụ
- **Read/Grep/Glob**: Phân tích cấu trúc dự án và trích xuất nội dung để tạo tài liệu
- **Write**: Tạo tài liệu với tổ chức thông minh và tham chiếu chéo
- **TodoWrite**: Theo dõi tiến độ cho các quy trình tài liệu đa thành phần phức tạp
- **Task**: Ủy quyền nâng cao cho tài liệu quy mô lớn yêu cầu phối hợp có hệ thống

## Các mẫu chính
- **Phân tích cấu trúc**: Kiểm tra dự án → nhận dạng thành phần → tổ chức logic → tham chiếu chéo
- **Các loại tài liệu**: Tài liệu API → Tài liệu cấu trúc → README → Các phương pháp tiếp cận cơ sở kiến thức
- **Xác thực chất lượng**: Đánh giá tính đầy đủ → xác minh tính chính xác → tuân thủ tiêu chuẩn → lập kế hoạch bảo trì
- **Tích hợp khung**: Các mẫu Context7 → các tiêu chuẩn chính thức → các phương pháp hay nhất → xác thực tính nhất quán

## Ví dụ

### Tài liệu cấu trúc dự án
```
/sc:index project-root --type structure --format md
# Tài liệu cấu trúc dự án toàn diện với tổ chức thông minh
# Tạo cấu trúc có thể điều hướng với các tham chiếu chéo và các mối quan hệ thành phần
```

### Tạo tài liệu API
```
/sc:index src/api --type api --format json
# Tài liệu API với phân tích và xác thực có hệ thống
# Các vai trò người ghi chép và chất lượng đảm bảo tính đầy đủ và chính xác
```

### Tạo cơ sở kiến thức
```
/sc:index . --type docs
# Tạo cơ sở kiến thức tương tác với các mẫu dành riêng cho dự án
# Vai trò kiến trúc sư cung cấp tổ chức cấu trúc và tham chiếu chéo
```

## Giới hạn

**Sẽ:**
- Tạo tài liệu dự án toàn diện với tổ chức thông minh và tham chiếu chéo
- Áp dụng phối hợp nhiều vai trò để phân tích có hệ thống và xác thực chất lượng
- Cung cấp các mẫu dành riêng cho khung và các tiêu chuẩn tài liệu đã được thiết lập

**Sẽ không:**
- Ghi đè tài liệu thủ công hiện có mà không có sự cho phép cập nhật rõ ràng
- Tạo tài liệu mà không có phân tích và xác thực cấu trúc dự án phù hợp
- Bỏ qua các tiêu chuẩn tài liệu hoặc các yêu cầu về chất lượng đã được thiết lập
