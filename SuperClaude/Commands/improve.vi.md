---
name: improve
description: "Áp dụng các cải tiến có hệ thống để nâng cao chất lượng, hiệu suất và khả năng bảo trì của mã"
category: quy trình làm việc
complexity: tiêu chuẩn
mcp-servers: [sequential, context7]
personas: [architect, performance, quality, security]
---

# /sc:improve - Cải thiện mã

## Kích hoạt
- Yêu cầu nâng cao chất lượng mã và tái cấu trúc
- Nhu cầu tối ưu hóa hiệu suất và giải quyết điểm nghẽn
- Cải thiện khả năng bảo trì và giảm nợ kỹ thuật
- Áp dụng các phương pháp hay nhất và thực thi các tiêu chuẩn mã hóa

## Cách sử dụng
```
/sc:improve [mục tiêu] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra mã nguồn để tìm cơ hội cải tiến và các vấn đề về chất lượng
2.  **Lập kế hoạch**: Chọn phương pháp cải tiến và kích hoạt các vai trò có liên quan để có chuyên môn
3.  **Thực thi**: Áp dụng các cải tiến có hệ thống với các phương pháp hay nhất dành riêng cho từng lĩnh vực
4.  **Xác thực**: Đảm bảo các cải tiến duy trì chức năng và đáp ứng các tiêu chuẩn chất lượng
5.  **Tài liệu**: Tạo tóm tắt cải tiến và các đề xuất cho công việc trong tương lai

Các hành vi chính:
- Phối hợp nhiều vai trò (kiến trúc sư, hiệu suất, chất lượng, bảo mật) dựa trên loại cải tiến
- Tối ưu hóa dành riêng cho khung thông qua tích hợp Context7 để có các phương pháp hay nhất
- Phân tích có hệ thống thông qua MCP tuần tự cho các cải tiến đa thành phần phức tạp
- Tái cấu trúc an toàn với khả năng xác thực và khôi phục toàn diện

## Tích hợp MCP
- **MCP tuần tự**: Tự động kích hoạt để phân tích và lập kế hoạch cải tiến đa bước phức tạp
- **MCP Context7**: Các phương pháp hay nhất và các mẫu tối ưu hóa dành riêng cho khung
- **Phối hợp vai trò**: Kiến trúc sư (cấu trúc), Hiệu suất (tốc độ), Chất lượng (khả năng bảo trì), Bảo mật (an toàn)

## Phối hợp công cụ
- **Read/Grep/Glob**: Phân tích mã và xác định cơ hội cải tiến
- **Edit/MultiEdit**: Sửa đổi mã an toàn và tái cấu trúc có hệ thống
- **TodoWrite**: Theo dõi tiến độ cho các hoạt động cải tiến nhiều tệp phức tạp
- **Task**: Ủy quyền cho các quy trình cải tiến quy mô lớn yêu cầu phối hợp có hệ thống

## Các mẫu chính
- **Cải thiện chất lượng**: Phân tích mã → xác định nợ kỹ thuật → ứng dụng tái cấu trúc
- **Tối ưu hóa hiệu suất**: Phân tích hồ sơ → xác định điểm nghẽn → triển khai tối ưu hóa
- **Nâng cao khả năng bảo trì**: Phân tích cấu trúc → giảm độ phức tạp → cải thiện tài liệu
- **Tăng cường bảo mật**: Phân tích lỗ hổng → ứng dụng mẫu bảo mật → xác minh xác thực

## Ví dụ

### Nâng cao chất lượng mã
```
/sc:improve src/ --type quality --safe
# Phân tích chất lượng có hệ thống với ứng dụng tái cấu trúc an toàn
# Cải thiện cấu trúc mã, giảm nợ kỹ thuật, nâng cao khả năng đọc
```

### Tối ưu hóa hiệu suất
```
/sc:improve api-endpoints --type performance --interactive
# Vai trò hiệu suất phân tích các điểm nghẽn và các cơ hội tối ưu hóa
# Hướng dẫn tương tác cho các quyết định cải thiện hiệu suất phức tạp
```

### Cải thiện khả năng bảo trì
```
/sc:improve legacy-modules --type maintainability --preview
# Vai trò kiến trúc sư phân tích cấu trúc và đề xuất các cải tiến về khả năng bảo trì
# Chế độ xem trước hiển thị các thay đổi trước khi ứng dụng để xem xét
```

### Tăng cường bảo mật
```
/sc:improve auth-service --type security --validate
# Vai trò bảo mật xác định các lỗ hổng và áp dụng các mẫu bảo mật
# Xác thực toàn diện đảm bảo các cải tiến bảo mật có hiệu quả
```

## Giới hạn

**Sẽ:**
- Áp dụng các cải tiến có hệ thống với chuyên môn và xác thực dành riêng cho từng lĩnh vực
- Cung cấp phân tích toàn diện với sự phối hợp của nhiều vai trò và các phương pháp hay nhất
- Thực hiện tái cấu trúc an toàn với khả năng khôi phục và bảo toàn chất lượng

**Sẽ không:**
- Áp dụng các cải tiến rủi ro mà không có phân tích và xác nhận của người dùng phù hợp
- Thực hiện các thay đổi về kiến trúc mà không hiểu đầy đủ tác động của hệ thống
- Ghi đè các tiêu chuẩn mã hóa đã được thiết lập hoặc các quy ước dành riêng cho dự án
