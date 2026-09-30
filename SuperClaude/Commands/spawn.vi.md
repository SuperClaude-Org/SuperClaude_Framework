---
name: spawn
description: "Điều phối tác vụ hệ thống meta với phân rã và ủy quyền thông minh"
category: đặc biệt
complexity: cao
mcp-servers: []
personas: []
---

# /sc:spawn - Điều phối tác vụ hệ thống meta

## Kích hoạt
- Các hoạt động đa miền phức tạp đòi hỏi phân rã tác vụ thông minh
- Các hoạt động hệ thống quy mô lớn trải rộng trên nhiều lĩnh vực kỹ thuật
- Các hoạt động đòi hỏi sự phối hợp song song và quản lý phụ thuộc
- Điều phối cấp meta ngoài khả năng của các lệnh tiêu chuẩn

## Cách sử dụng
```
/sc:spawn [tác vụ phức tạp] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

## Luồng hành vi
1.  **Phân tích**: Phân tích cú pháp các yêu cầu hoạt động phức tạp và đánh giá phạm vi trên các miền
2.  **Phân rã**: Phân rã hoạt động thành các hệ thống phân cấp nhiệm vụ phụ được phối hợp
3.  **Điều phối**: Thực hiện các tác vụ bằng chiến lược phối hợp tối ưu (song song/tuần tự)
4.  **Giám sát**: Theo dõi tiến độ trên các hệ thống phân cấp nhiệm vụ với quản lý phụ thuộc
5.  **Tích hợp**: Tổng hợp kết quả và cung cấp tóm tắt điều phối toàn diện

Các hành vi chính:
- Phân rã tác vụ hệ thống meta với phân rã Epic → Story → Task → Subtask
- Lựa chọn chiến lược phối hợp thông minh dựa trên các đặc điểm hoạt động
- Quản lý hoạt động đa miền với các mẫu thực thi song song và tuần tự
- Phân tích phụ thuộc nâng cao và tối ưu hóa tài nguyên trên các hệ thống phân cấp nhiệm vụ
## Tích hợp MCP
- **Điều phối gốc**: Lệnh hệ thống meta sử dụng sự phối hợp gốc mà không có sự phụ thuộc của MCP
- **Tích hợp tiến bộ**: Phối hợp với thực thi có hệ thống để tăng cường tiến bộ
- **Tích hợp khung**: Tích hợp nâng cao với các lớp điều phối SuperClaude

## Phối hợp công cụ
- **TodoWrite**: Phân cấp nhiệm vụ và theo dõi tiến độ ở các cấp Epic → Story → Task
- **Read/Grep/Glob**: Phân tích hệ thống và ánh xạ phụ thuộc cho các hoạt động phức tạp
- **Edit/MultiEdit/Write**: Các hoạt động tệp được phối hợp với thực thi song song và tuần tự
- **Bash**: Phối hợp các hoạt động cấp hệ thống với quản lý tài nguyên thông minh

## Các mẫu chính
- **Phân rã có thứ bậc**: Các hoạt động cấp Epic → phối hợp Story → thực hiện Task → mức độ chi tiết của Subtask
- **Lựa chọn chiến lược**: Tuần tự (theo thứ tự phụ thuộc) → Song song (độc lập) → Thích ứng (động)
- **Phối hợp hệ thống meta**: Các hoạt động đa miền → tối ưu hóa tài nguyên → tích hợp kết quả
- **Nâng cao tiến bộ**: Thực thi có hệ thống → cổng chất lượng → xác thực toàn diện

## Ví dụ

### Triển khai tính năng phức tạp
```
/sc:spawn "triển khai hệ thống xác thực người dùng"
# Phân rã: Thiết kế cơ sở dữ liệu → API phụ trợ → Giao diện người dùng giao diện người dùng → Kiểm tra
# Phối hợp trên nhiều miền với quản lý phụ thuộc
```

### Hoạt động hệ thống quy mô lớn
```
/sc:spawn "di chuyển khối nguyên khối cũ sang các dịch vụ vi mô" --strategy adaptive --depth deep
# Hoạt động quy mô doanh nghiệp với sự điều phối tinh vi
# Phối hợp thích ứng dựa trên các đặc điểm hoạt động
```

### Cơ sở hạ tầng đa miền
```
/sc:spawn "thiết lập quy trình CI/CD với quét bảo mật"
# Hoạt động cơ sở hạ tầng trên toàn hệ thống bao gồm các miền DevOps, Bảo mật, Chất lượng
# Thực thi song song các thành phần độc lập với các cổng xác thực
```

## Giới hạn

**Sẽ:**
- Phân rã các hoạt động đa miền phức tạp thành các hệ thống phân cấp nhiệm vụ được phối hợp
- Cung cấp sự điều phối thông minh với các chiến lược phối hợp song song và tuần tự
- Thực hiện các hoạt động của hệ thống meta ngoài khả năng của các lệnh tiêu chuẩn

**Sẽ không:**
- Thay thế các lệnh dành riêng cho miền cho các hoạt động đơn giản
- Ghi đè các tùy chọn phối hợp hoặc chiến lược thực thi của người dùng
- Thực hiện các hoạt động mà không có phân tích và xác thực phụ thuộc phù hợp
