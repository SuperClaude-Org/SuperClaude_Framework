---
name: brainstorm
description: "Khám phá yêu cầu tương tác thông qua đối thoại Socratic và khám phá có hệ thống"
category: điều phối
complexity: nâng cao
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---

# /sc:brainstorm - Khám phá yêu cầu tương tác

> **Ghi chú khung ngữ cảnh**: Tệp này cung cấp các hướng dẫn hành vi cho Claude Code khi người dùng nhập các mẫu `/sc:brainstorm`. Đây KHÔNG phải là một lệnh có thể thực thi - đó là một trình kích hoạt ngữ cảnh kích hoạt các mẫu hành vi được xác định bên dưới.

## Kích hoạt
- Các ý tưởng dự án mơ hồ đòi hỏi sự khám phá có cấu trúc
- Nhu cầu khám phá yêu cầu và phát triển đặc tả
- Yêu cầu xác thực khái niệm và đánh giá tính khả thi
- Các kịch bản động não và tinh chỉnh lặp đi lặp lại giữa các phiên

## Mẫu kích hoạt ngữ cảnh
```
/sc:brainstorm [chủ đề/ý tưởng] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```
**Cách sử dụng**: Nhập mẫu này vào cuộc trò chuyện Claude Code của bạn để kích hoạt chế độ hành vi động não với khám phá có hệ thống và phối hợp nhiều vai trò.

## Luồng hành vi
1.  **Khám phá**: Chuyển đổi các ý tưởng mơ hồ thông qua đối thoại Socratic và đặt câu hỏi có hệ thống
2.  **Phân tích**: Phối hợp nhiều vai trò để có chuyên môn về lĩnh vực và phân tích toàn diện
3.  **Xác thực**: Áp dụng đánh giá tính khả thi và xác thực yêu cầu trên các lĩnh vực
4.  **Chỉ định**: Tạo các thông số kỹ thuật cụ thể với khả năng duy trì giữa các phiên
5.  **Bàn giao**: Tạo các bản tóm tắt có thể hành động sẵn sàng để triển khai hoặc phát triển thêm

Các hành vi chính:
- Điều phối nhiều vai trò trên các lĩnh vực kiến trúc, phân tích, giao diện người dùng, phụ trợ, bảo mật
- Phối hợp MCP nâng cao với định tuyến thông minh để phân tích chuyên biệt
- Thực thi có hệ thống với việc tăng cường đối thoại tiến bộ và khám phá song song
- Duy trì giữa các phiên với tài liệu khám phá yêu cầu toàn diện

## Tích hợp MCP
- **MCP Sequential**: Suy luận đa bước phức tạp để khám phá và xác thực có hệ thống
- **MCP Context7**: Đánh giá tính khả thi và phân tích mẫu dành riêng cho khung
- **MCP Magic**: Tính khả thi của UI/UX và phân tích tích hợp hệ thống thiết kế
- **MCP Playwright**: Xác thực trải nghiệm người dùng và kiểm tra mẫu tương tác
- **MCP Morphllm**: Phân tích nội dung quy mô lớn và chuyển đổi dựa trên mẫu
- **MCP Serena**: Duy trì giữa các phiên, quản lý bộ nhớ và tăng cường ngữ cảnh dự án

## Phối hợp công cụ
- **Read/Write/Edit**: Tài liệu yêu cầu và tạo đặc tả
- **TodoWrite**: Theo dõi tiến độ để khám phá đa pha phức tạp
- **Task**: Ủy quyền nâng cao cho các đường khám phá song song và phối hợp nhiều tác nhân
- **WebSearch**: Nghiên cứu thị trường, phân tích đối thủ cạnh tranh và xác thực công nghệ
- **sequentialthinking**: Suy luận có cấu trúc để phân tích các yêu cầu phức tạp

## Các mẫu chính
- **Đối thoại Socratic**: Khám phá theo hướng câu hỏi → khám phá yêu cầu có hệ thống
- **Phân tích đa lĩnh vực**: Chuyên môn đa chức năng → đánh giá tính khả thi toàn diện
- **Phối hợp tiến bộ**: Khám phá có hệ thống → tinh chỉnh và xác thực lặp đi lặp lại
- **Tạo đặc tả**: Yêu cầu cụ thể → bản tóm tắt triển khai có thể hành động

## Ví dụ

### Khám phá sản phẩm có hệ thống
```
/sc:brainstorm "Công cụ quản lý dự án được hỗ trợ bởi AI" --strategy systematic --depth deep
# Phân tích đa vai trò: kiến trúc sư (thiết kế hệ thống), nhà phân tích (tính khả thi), quản lý dự án (yêu cầu)
# MCP tuần tự cung cấp khung khám phá có cấu trúc
```

### Khám phá tính năng linh hoạt
```
/sc:brainstorm "các tính năng cộng tác thời gian thực" --strategy agile --parallel
# Các đường khám phá song song với các vai trò giao diện người dùng, phụ trợ và bảo mật
# MCP Context7 và Magic để phân tích khung và mẫu giao diện người dùng
```

### Xác thực giải pháp doanh nghiệp
```
/sc:brainstorm "nền tảng phân tích dữ liệu doanh nghiệp" --strategy enterprise --validate
# Xác thực toàn diện với các vai trò bảo mật, devops và kiến trúc sư
# MCP Serena để duy trì giữa các phiên và theo dõi các yêu cầu của doanh nghiệp
```

### Tinh chỉnh giữa các phiên
```
/sc:brainstorm "chiến lược kiếm tiền từ ứng dụng di động" --depth normal
# MCP Serena quản lý ngữ cảnh giữa các phiên và tinh chỉnh lặp đi lặp lại
# Tăng cường đối thoại tiến bộ với những hiểu biết sâu sắc dựa trên bộ nhớ
```

## Giới hạn

**Sẽ:**
- Chuyển đổi các ý tưởng mơ hồ thành các thông số kỹ thuật cụ thể thông qua khám phá có hệ thống
- Phối hợp nhiều vai trò và máy chủ MCP để phân tích toàn diện
- Cung cấp tính liên tục giữa các phiên và tăng cường đối thoại tiến bộ

**Sẽ không:**
- Đưa ra quyết định triển khai mà không khám phá các yêu cầu phù hợp
- Ghi đè tầm nhìn của người dùng bằng các giải pháp quy định trong giai đoạn khám phá
- Bỏ qua khám phá có hệ thống cho các dự án đa miền phức tạp
