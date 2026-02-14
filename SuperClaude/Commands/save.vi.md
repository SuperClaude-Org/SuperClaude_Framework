---
name: save
description: "Quản lý vòng đời phiên với tích hợp Serena MCP để duy trì ngữ cảnh phiên"
category: phiên
complexity: tiêu chuẩn
mcp-servers: [serena]
personas: []
---

# /sc:save - Duy trì ngữ cảnh phiên

## Kích hoạt
- Hoàn thành phiên và nhu cầu duy trì ngữ cảnh dự án
- Yêu cầu quản lý bộ nhớ giữa các phiên và tạo điểm kiểm tra
- Các kịch bản lưu trữ khám phá và bảo toàn sự hiểu biết về dự án
- Yêu cầu quản lý vòng đời phiên và theo dõi tiến độ

## Cách sử dụng
```
/sc:save [--type session|learnings|context|all] [--summarize] [--checkpoint]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra tiến độ phiên và xác định những khám phá đáng được lưu giữ
2.  **Duy trì**: Lưu ngữ cảnh phiên và những điều đã học được bằng cách sử dụng quản lý bộ nhớ Serena MCP
3.  **Điểm kiểm tra**: Tạo các điểm khôi phục cho các phiên phức tạp và theo dõi tiến độ
4.  **Xác thực**: Đảm bảo tính toàn vẹn của dữ liệu phiên và khả năng tương thích giữa các phiên
5.  **Chuẩn bị**: Chuẩn bị ngữ cảnh phiên để tiếp tục liền mạch trong các phiên trong tương lai

Các hành vi chính:
- Tích hợp Serena MCP để quản lý bộ nhớ và duy trì giữa các phiên
- Tự động tạo điểm kiểm tra dựa trên tiến độ phiên và các tác vụ quan trọng
- Bảo toàn ngữ cảnh phiên với khám phá toàn diện và lưu trữ mẫu
- Học hỏi giữa các phiên với những hiểu biết sâu sắc về dự án và các quyết định kỹ thuật được tích lũy

## Tích hợp MCP
- **MCP Serena**: Tích hợp bắt buộc để quản lý phiên, các hoạt động bộ nhớ và duy trì giữa các phiên
- **Hoạt động bộ nhớ**: Lưu trữ ngữ cảnh phiên, tạo điểm kiểm tra và lưu trữ khám phá
- **Hiệu suất quan trọng**: <200ms cho các hoạt động bộ nhớ, <1 giây để tạo điểm kiểm tra

## Phối hợp công cụ
- **write_memory/read_memory**: Duy trì và truy xuất ngữ cảnh phiên cốt lõi
- **think_about_collected_information**: Phân tích phiên và nhận dạng khám phá
- **summarize_changes**: Tạo tóm tắt phiên và tài liệu tiến độ
- **TodoRead**: Theo dõi hoàn thành nhiệm vụ để kích hoạt điểm kiểm tra tự động

## Các mẫu chính
- **Bảo toàn phiên**: Phân tích khám phá → duy trì bộ nhớ → tạo điểm kiểm tra
- **Học hỏi giữa các phiên**: Tích lũy ngữ cảnh → lưu trữ mẫu → nâng cao hiểu biết về dự án
- **Theo dõi tiến độ**: Hoàn thành nhiệm vụ → điểm kiểm tra tự động → tính liên tục của phiên
- **Lập kế hoạch khôi phục**: Bảo toàn trạng thái → xác thực điểm kiểm tra → sẵn sàng khôi phục

## Ví dụ

### Lưu phiên cơ bản
```
/sc:save
# Lưu các khám phá và ngữ cảnh của phiên hiện tại vào Serena MCP
# Tự động tạo điểm kiểm tra nếu phiên vượt quá 30 phút
```

### Điểm kiểm tra phiên toàn diện
```
/sc:save --type all --checkpoint
# Bảo toàn phiên hoàn chỉnh với điểm kiểm tra khôi phục
# Bao gồm tất cả những điều đã học, ngữ cảnh và tiến độ để khôi phục phiên
```

### Tạo tóm tắt phiên
```
/sc:save --summarize
# Tạo tóm tắt phiên với tài liệu khám phá
# Cập nhật các mẫu học hỏi giữa các phiên và những hiểu biết sâu sắc về dự án
```

### Chỉ duy trì khám phá
```
/sc:save --type learnings
# Chỉ lưu các mẫu và thông tin chi tiết mới được khám phá trong phiên
# Cập nhật hiểu biết về dự án mà không cần bảo toàn toàn bộ phiên
```

## Giới hạn

**Sẽ:**
- Lưu ngữ cảnh phiên bằng tích hợp Serena MCP để duy trì giữa các phiên
- Tạo các điểm kiểm tra tự động dựa trên tiến độ phiên và hoàn thành nhiệm vụ
- Bảo tồn các khám phá và các mẫu để nâng cao hiểu biết về dự án

**Sẽ không:**
- Hoạt động mà không có tích hợp Serena MCP phù hợp và quyền truy cập bộ nhớ
- Lưu dữ liệu phiên mà không có xác thực và xác minh tính toàn vẹn
- Ghi đè ngữ cảnh phiên hiện có mà không bảo toàn điểm kiểm tra phù hợp
