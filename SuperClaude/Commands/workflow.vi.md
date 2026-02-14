---
name: workflow
description: "Tạo quy trình triển khai có cấu trúc từ PRD và các yêu cầu tính năng"
category: điều phối
complexity: nâng cao
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---

# /sc:workflow - Trình tạo quy trình triển khai

## Kích hoạt
- Phân tích đặc tả PRD và tính năng để lập kế hoạch triển khai
- Tạo quy trình làm việc có cấu trúc cho các dự án phát triển
- Phối hợp nhiều vai trò cho các chiến lược triển khai phức tạp
- Quản lý quy trình làm việc và ánh xạ phụ thuộc giữa các phiên

## Cách sử dụng
```
/sc:workflow [tệp-prd|mô-tả-tính-năng] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

## Luồng hành vi
1.  **Phân tích**: Phân tích cú pháp các đặc tả PRD và tính năng để hiểu các yêu cầu triển khai
2.  **Lập kế hoạch**: Tạo cấu trúc quy trình làm việc toàn diện với ánh xạ phụ thuộc và điều phối tác vụ
3.  **Phối hợp**: Kích hoạt nhiều vai trò để có chuyên môn về lĩnh vực và chiến lược triển khai
4.  **Thực thi**: Tạo các quy trình làm việc từng bước có cấu trúc với sự phối hợp tác vụ tự động
5.  **Xác thực**: Áp dụng các cổng chất lượng và đảm bảo tính đầy đủ của quy trình làm việc trên các miền

Các hành vi chính:
- Điều phối nhiều vai trò trên các lĩnh vực kiến trúc, giao diện người dùng, phụ trợ, bảo mật và devops
- Phối hợp MCP nâng cao với định tuyến thông minh để phân tích quy trình làm việc chuyên biệt
- Thực thi có hệ thống với việc tăng cường quy trình làm việc tiến bộ và xử lý song song
- Quản lý quy trình làm việc giữa các phiên với theo dõi phụ thuộc toàn diện

## Tích hợp MCP
- **MCP tuần tự**: Phân tích quy trình làm việc đa bước phức tạp và lập kế hoạch triển khai có hệ thống
- **MCP Context7**: Các mẫu quy trình làm việc dành riêng cho khung và các phương pháp hay nhất để triển khai
- **MCP Magic**: Tạo quy trình làm việc UI/UX và các chiến lược tích hợp hệ thống thiết kế
- **MCP Playwright**: Tích hợp quy trình kiểm tra và tự động hóa đảm bảo chất lượng
- **MCP Morphllm**: Chuyển đổi quy trình làm việc quy mô lớn và tối ưu hóa dựa trên mẫu
- **MCP Serena**: Duy trì quy trình làm việc giữa các phiên, quản lý bộ nhớ và ngữ cảnh dự án

## Phối hợp công cụ
- **Read/Write/Edit**: Phân tích PRD và tạo tài liệu quy trình làm việc
- **TodoWrite**: Theo dõi tiến độ để thực hiện quy trình làm việc đa pha phức tạp
- **Task**: Ủy quyền nâng cao để tạo quy trình làm việc song song và phối hợp nhiều tác nhân
- **WebSearch**: Nghiên cứu công nghệ, xác thực khung và phân tích chiến lược triển khai
- **sequentialthinking**: Suy luận có cấu trúc để phân tích phụ thuộc quy trình làm việc phức tạp

## Các mẫu chính
- **Phân tích PRD**: Phân tích cú pháp tài liệu → trích xuất yêu cầu → phát triển chiến lược triển khai
- **Tạo quy trình làm việc**: Phân rã tác vụ → ánh xạ phụ thuộc → lập kế hoạch triển khai có cấu trúc
- **Phối hợp đa miền**: Chuyên môn đa chức năng → các chiến lược triển khai toàn diện
- **Tích hợp chất lượng**: Xác thực quy trình làm việc → các chiến lược kiểm tra → lập kế hoạch triển khai

## Ví dụ

### Quy trình làm việc PRD có hệ thống
```
/sc:workflow ClaudeDocs/PRD/feature-spec.md --strategy systematic --depth deep
# Phân tích PRD toàn diện với tạo quy trình làm việc có hệ thống
# Phối hợp nhiều vai trò để có chiến lược triển khai hoàn chỉnh
```

### Quy trình làm việc tính năng linh hoạt
```
/sc:workflow "hệ thống xác thực người dùng" --strategy agile --parallel
# Tạo quy trình làm việc linh hoạt với phối hợp tác vụ song song
# MCP Context7 và Magic cho các mẫu quy trình làm việc của khung và giao diện người dùng
```

### Lập kế hoạch triển khai doanh nghiệp
```
/sc:workflow enterprise-prd.md --strategy enterprise --validate
# Quy trình làm việc quy mô doanh nghiệp với xác thực toàn diện
# Các vai trò bảo mật, devops và kiến trúc sư để đảm bảo tuân thủ và khả năng mở rộng
```

### Quản lý quy trình làm việc giữa các phiên
```
/sc:workflow project-brief.md --depth normal
# MCP Serena quản lý ngữ cảnh và tính bền vững của quy trình làm việc giữa các phiên
# Tăng cường quy trình làm việc tiến bộ với những hiểu biết sâu sắc dựa trên bộ nhớ
```

## Giới hạn

**Sẽ:**
- Tạo các quy trình triển khai toàn diện từ các đặc tả PRD và tính năng
- Phối hợp nhiều vai trò và máy chủ MCP để có các chiến lược triển khai hoàn chỉnh
- Cung cấp khả năng quản lý quy trình làm việc giữa các phiên và tăng cường tiến bộ

**Sẽ không:**
- Thực hiện các tác vụ triển khai thực tế ngoài việc lập kế hoạch và chiến lược quy trình làm việc
- Ghi đè các quy trình phát triển đã được thiết lập mà không có phân tích và xác thực phù hợp
- Tạo quy trình làm việc mà không có phân tích yêu cầu và ánh xạ phụ thuộc toàn diện
