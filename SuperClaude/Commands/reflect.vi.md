---
name: reflect
description: "Phản ánh và xác thực nhiệm vụ bằng khả năng phân tích của Serena MCP"
category: đặc biệt
complexity: tiêu chuẩn
mcp-servers: [serena]
personas: []
---

# /sc:reflect - Phản ánh và xác thực nhiệm vụ

## Kích hoạt
- Hoàn thành nhiệm vụ yêu cầu xác thực và đánh giá chất lượng
- Phân tích tiến độ phiên và phản ánh công việc đã hoàn thành
- Học hỏi và nắm bắt thông tin chi tiết giữa các phiên để cải thiện dự án
- Các cổng chất lượng yêu cầu xác minh tuân thủ nhiệm vụ toàn diện

## Cách sử dụng
```
/sc:reflect [--type task|session|completion] [--analyze] [--validate]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra trạng thái nhiệm vụ hiện tại và tiến độ phiên bằng các công cụ phản ánh của Serena
2.  **Xác thực**: Đánh giá sự tuân thủ nhiệm vụ, chất lượng hoàn thành và việc đáp ứng yêu cầu
3.  **Phản ánh**: Áp dụng phân tích sâu thông tin đã thu thập và thông tin chi tiết về phiên
4.  **Tài liệu**: Cập nhật siêu dữ liệu phiên và nắm bắt thông tin chi tiết học được
5.  **Tối ưu hóa**: Cung cấp các đề xuất để cải tiến quy trình và nâng cao chất lượng

Các hành vi chính:
- Tích hợp Serena MCP để phân tích phản ánh toàn diện và xác thực nhiệm vụ
- Cầu nối giữa các mẫu TodoWrite và các khả năng phân tích nâng cao của Serena
- Tích hợp vòng đời phiên với duy trì giữa các phiên và nắm bắt học hỏi
- Các hoạt động quan trọng về hiệu suất với phản ánh và xác thực cốt lõi <200ms
## Tích hợp MCP
- **MCP Serena**: Tích hợp bắt buộc để phân tích phản ánh, xác thực nhiệm vụ và siêu dữ liệu phiên
- **Công cụ phản ánh**: think_about_task_adherence, think_about_collected_information, think_about_whether_you_are_done
- **Hoạt động bộ nhớ**: Duy trì giữa các phiên với read_memory, write_memory, list_memories
- **Hiệu suất quan trọng**: <200ms cho các hoạt động phản ánh cốt lõi, <1 giây để tạo điểm kiểm tra

## Phối hợp công cụ
- **TodoRead/TodoWrite**: Cầu nối giữa quản lý tác vụ truyền thống và phân tích phản ánh nâng cao
- **think_about_task_adherence**: Xác thực phương pháp tiếp cận hiện tại so với các mục tiêu của dự án và các mục tiêu của phiên
- **think_about_collected_information**: Phân tích công việc của phiên và tính đầy đủ của việc thu thập thông tin
- **think_about_whether_you_are_done**: Đánh giá các tiêu chí hoàn thành nhiệm vụ và xác định công việc còn lại
- **Công cụ bộ nhớ**: Cập nhật siêu dữ liệu phiên và nắm bắt học hỏi giữa các phiên

## Các mẫu chính
- **Xác thực nhiệm vụ**: Phương pháp tiếp cận hiện tại → căn chỉnh mục tiêu → xác định độ lệch → điều chỉnh hướng đi
- **Phân tích phiên**: Thu thập thông tin → đánh giá tính đầy đủ → đánh giá chất lượng → nắm bắt thông tin chi tiết
- **Đánh giá hoàn thành**: Đánh giá tiến độ → tiêu chí hoàn thành → công việc còn lại → xác thực quyết định
- **Học hỏi giữa các phiên**: Thông tin chi tiết phản ánh → duy trì bộ nhớ → nâng cao hiểu biết về dự án

## Ví dụ

### Phản ánh tuân thủ nhiệm vụ
```
/sc:reflect --type task --analyze
# Xác thực phương pháp tiếp cận hiện tại so với các mục tiêu của dự án
# Xác định các sai lệch và cung cấp các đề xuất điều chỉnh hướng đi
```

### Phân tích tiến độ phiên
```
/sc:reflect --type session --validate
# Phân tích toàn diện công việc của phiên và thu thập thông tin
# Đánh giá chất lượng và xác định khoảng trống để cải thiện dự án
```

### Xác thực hoàn thành
```
/sc:reflect --type completion
# Đánh giá các tiêu chí hoàn thành nhiệm vụ so với tiến độ thực tế
# Xác định sự sẵn sàng để hoàn thành nhiệm vụ và xác định các trình chặn còn lại
```

## Giới hạn

**Sẽ:**
- Thực hiện phản ánh và xác thực nhiệm vụ toàn diện bằng các công cụ phân tích Serena MCP
- Kết nối các mẫu TodoWrite với các khả năng phản ánh nâng cao để quản lý tác vụ nâng cao
- Cung cấp khả năng nắm bắt học hỏi giữa các phiên và tích hợp vòng đời phiên

**Sẽ không:**
- Hoạt động mà không có tích hợp Serena MCP phù hợp và quyền truy cập công cụ phản ánh
- Ghi đè các quyết định hoàn thành nhiệm vụ mà không có xác thực tuân thủ và chất lượng phù hợp
- Bỏ qua các kiểm tra tính toàn vẹn của phiên và các yêu cầu duy trì giữa các phiên
