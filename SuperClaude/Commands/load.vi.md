---
name: load
description: "Quản lý vòng đời phiên với tích hợp Serena MCP để tải ngữ cảnh dự án"
category: phiên
complexity: tiêu chuẩn
mcp-servers: [serena]
personas: []
---

# /sc:load - Tải ngữ cảnh dự án

## Kích hoạt
- Yêu cầu khởi tạo phiên và tải ngữ cảnh dự án
- Nhu cầu duy trì giữa các phiên và truy xuất bộ nhớ
- Yêu cầu kích hoạt dự án và quản lý ngữ cảnh
- Các kịch bản quản lý vòng đời phiên và tải điểm kiểm tra

## Cách sử dụng
```
/sc:load [mục tiêu] [--type project|config|deps|checkpoint] [--refresh] [--analyze]
```

## Luồng hành vi
1.  **Khởi tạo**: Thiết lập kết nối Serena MCP và quản lý ngữ cảnh phiên
2.  **Khám phá**: Phân tích cấu trúc dự án và xác định các yêu cầu tải ngữ cảnh
3.  **Tải**: Truy xuất bộ nhớ dự án, các điểm kiểm tra và dữ liệu duy trì giữa các phiên
4.  **Kích hoạt**: Thiết lập ngữ cảnh dự án và chuẩn bị cho quy trình phát triển
5.  **Xác thực**: Đảm bảo tính toàn vẹn của ngữ cảnh đã tải và sự sẵn sàng của phiên

Các hành vi chính:
- Tích hợp Serena MCP để quản lý bộ nhớ và duy trì giữa các phiên
- Kích hoạt dự án với tải và xác thực ngữ cảnh toàn diện
- Hoạt động quan trọng về hiệu suất với mục tiêu khởi tạo <500ms
- Quản lý vòng đời phiên với phối hợp điểm kiểm tra và bộ nhớ

## Tích hợp MCP
- **MCP Serena**: Tích hợp bắt buộc để kích hoạt dự án, truy xuất bộ nhớ và quản lý phiên
- **Hoạt động bộ nhớ**: Duy trì giữa các phiên, tải điểm kiểm tra và khôi phục ngữ cảnh
- **Hiệu suất quan trọng**: <200ms cho các hoạt động cốt lõi, <1 giây để tạo điểm kiểm tra

## Phối hợp công cụ
- **activate_project**: Kích hoạt dự án cốt lõi và thiết lập ngữ cảnh
- **list_memories/read_memory**: Truy xuất bộ nhớ và tải ngữ cảnh phiên
- **Read/Grep/Glob**: Phân tích cấu trúc dự án và khám phá cấu hình
- **Write**: Tài liệu ngữ cảnh phiên và tạo điểm kiểm tra

## Các mẫu chính
- **Kích hoạt dự án**: Phân tích thư mục → truy xuất bộ nhớ → thiết lập ngữ cảnh
- **Khôi phục phiên**: Tải điểm kiểm tra → xác thực ngữ cảnh → chuẩn bị quy trình làm việc
- **Quản lý bộ nhớ**: Duy trì giữa các phiên → tính liên tục của ngữ cảnh → hiệu quả phát triển
- **Hiệu suất quan trọng**: Khởi tạo nhanh → năng suất tức thì → sẵn sàng cho phiên

## Ví dụ

### Tải dự án cơ bản
```
/sc:load
# Tải ngữ cảnh dự án thư mục hiện tại với tích hợp bộ nhớ Serena
# Thiết lập ngữ cảnh phiên và chuẩn bị cho quy trình phát triển
```

### Tải dự án cụ thể
```
/sc:load /path/to/project --type project --analyze
# Tải dự án cụ thể với phân tích toàn diện
# Kích hoạt ngữ cảnh dự án và truy xuất bộ nhớ giữa các phiên
```

### Khôi phục điểm kiểm tra
```
/sc:load --type checkpoint --checkpoint session_123
# Khôi phục điểm kiểm tra cụ thể với ngữ cảnh phiên
# Tiếp tục phiên làm việc trước đó với bảo toàn ngữ cảnh đầy đủ
```

### Tải ngữ cảnh phụ thuộc
```
/sc:load --type deps --refresh
# Tải ngữ cảnh phụ thuộc với phân tích mới
# Cập nhật hiểu biết về dự án và ánh xạ phụ thuộc
```

## Giới hạn

**Sẽ:**
- Tải ngữ cảnh dự án bằng tích hợp Serena MCP để quản lý bộ nhớ
- Cung cấp quản lý vòng đời phiên với duy trì giữa các phiên
- Thiết lập kích hoạt dự án với tải ngữ cảnh toàn diện

**Sẽ không:**
- Sửa đổi cấu trúc hoặc cấu hình dự án mà không có sự cho phép rõ ràng
- Tải ngữ cảnh mà không có tích hợp và xác thực Serena MCP phù hợp
- Ghi đè ngữ cảnh phiên hiện có mà không bảo toàn điểm kiểm tra
