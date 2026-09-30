---
name: cleanup
description: "Dọn dẹp mã một cách có hệ thống, xóa mã chết và tối ưu hóa cấu trúc dự án"
category: quy trình làm việc
complexity: tiêu chuẩn
mcp-servers: [sequential, context7]
personas: [architect, quality, security]
---

# /sc:cleanup - Dọn dẹp mã và dự án

## Kích hoạt
- Yêu cầu bảo trì mã và giảm nợ kỹ thuật
- Nhu cầu xóa mã chết và tối ưu hóa import
- Yêu cầu cải thiện và tổ chức cấu trúc dự án
- Các sáng kiến ​​cải thiện vệ sinh và chất lượng mã nguồn

## Cách sử dụng
```
/sc:cleanup [mục tiêu] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]
```

## Luồng hành vi
1.  **Phân tích**: Đánh giá các cơ hội dọn dẹp và các cân nhắc về an toàn trên phạm vi mục tiêu
2.  **Lập kế hoạch**: Chọn phương pháp dọn dẹp và kích hoạt các vai trò có liên quan để có chuyên môn về lĩnh vực
3.  **Thực thi**: Áp dụng dọn dẹp có hệ thống với khả năng phát hiện và xóa mã chết thông minh
4.  **Xác thực**: Đảm bảo không mất chức năng thông qua kiểm tra và xác minh an toàn
5.  **Báo cáo**: Tạo tóm tắt dọn dẹp với các đề xuất để bảo trì liên tục

Các hành vi chính:
- Phối hợp nhiều vai trò (kiến trúc sư, chất lượng, bảo mật) dựa trên loại dọn dẹp
- Các mẫu dọn dẹp dành riêng cho khung thông qua tích hợp MCP Context7
- Phân tích có hệ thống thông qua MCP tuần tự cho các hoạt động dọn dẹp phức tạp
- Phương pháp tiếp cận ưu tiên an toàn với khả năng sao lưu và khôi phục

## Tích hợp MCP
- **MCP tuần tự**: Tự động kích hoạt để phân tích và lập kế hoạch dọn dẹp đa bước phức tạp
- **MCP Context7**: Các mẫu dọn dẹp và các phương pháp hay nhất dành riêng cho khung
- **Phối hợp vai trò**: Kiến trúc sư (cấu trúc), Chất lượng (nợ), Bảo mật (thông tin xác thực)

## Phối hợp công cụ
- **Read/Grep/Glob**: Phân tích mã và phát hiện mẫu để tìm cơ hội dọn dẹp
- **Edit/MultiEdit**: Sửa đổi mã an toàn và tối ưu hóa cấu trúc
- **TodoWrite**: Theo dõi tiến độ cho các hoạt động dọn dẹp nhiều tệp phức tạp
- **Task**: Ủy quyền cho các quy trình dọn dẹp quy mô lớn yêu cầu phối hợp có hệ thống

## Các mẫu chính
- **Phát hiện mã chết**: Phân tích sử dụng → xóa an toàn với xác thực phụ thuộc
- **Tối ưu hóa import**: Phân tích phụ thuộc → xóa và tổ chức import không sử dụng
- **Dọn dẹp cấu trúc**: Phân tích kiến trúc → tổ chức tệp và cải tiến mô-đun
- **Xác thực an toàn**: Kiểm tra trước/trong/sau → duy trì chức năng trong suốt quá trình dọn dẹp

## Ví dụ

### Dọn dẹp mã an toàn
```
/sc:cleanup src/ --type code --safe
# Dọn dẹp thận trọng với xác thực an toàn tự động
# Xóa mã chết trong khi vẫn giữ nguyên tất cả chức năng
```

### Tối ưu hóa import
```
/sc:cleanup --type imports --preview
# Phân tích và hiển thị dọn dẹp import không sử dụng mà không thực thi
# Tối ưu hóa nhận biết khung thông qua các mẫu Context7
```

### Dọn dẹp dự án toàn diện
```
/sc:cleanup --type all --interactive
# Dọn dẹp đa miền với hướng dẫn của người dùng cho các quyết định phức tạp
# Kích hoạt tất cả các vai trò để phân tích toàn diện
```

### Dọn dẹp dành riêng cho khung
```
/sc:cleanup components/ --aggressive
# Dọn dẹp kỹ lưỡng với các mẫu khung Context7
# Phân tích tuần tự để quản lý phụ thuộc phức tạp
```

## Giới hạn

**Sẽ:**
- Dọn dẹp mã một cách có hệ thống, xóa mã chết và tối ưu hóa cấu trúc dự án
- Cung cấp xác thực an toàn toàn diện với khả năng sao lưu và khôi phục
- Áp dụng các thuật toán dọn dẹp thông minh với khả năng nhận dạng mẫu dành riêng cho khung

**Sẽ không:**
- Xóa mã mà không có phân tích và xác thực an toàn kỹ lưỡng
- Ghi đè các loại trừ dọn dẹp dành riêng cho dự án hoặc các ràng buộc về kiến trúc
- Áp dụng các hoạt động dọn dẹp làm ảnh hưởng đến chức năng hoặc gây ra lỗi
