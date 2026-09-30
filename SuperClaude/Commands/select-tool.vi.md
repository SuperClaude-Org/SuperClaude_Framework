---
name: select-tool
description: "Lựa chọn công cụ MCP thông minh dựa trên chấm điểm độ phức tạp và phân tích hoạt động"
category: đặc biệt
complexity: cao
mcp-servers: [serena, morphllm]
personas: []
---

# /sc:select-tool - Lựa chọn công cụ MCP thông minh

## Kích hoạt
- Các hoạt động yêu cầu lựa chọn công cụ MCP tối ưu giữa Serena và Morphllm
- Các quyết định của hệ thống meta cần phân tích độ phức tạp và đối sánh khả năng
- Các quyết định định tuyến công cụ yêu cầu sự đánh đổi giữa hiệu suất và độ chính xác
- Các hoạt động được hưởng lợi từ việc đánh giá khả năng của công cụ thông minh

## Cách sử dụng
```
/sc:select-tool [hoạt động] [--analyze] [--explain]
```

## Luồng hành vi
1.  **Phân tích cú pháp**: Phân tích loại hoạt động, phạm vi, số lượng tệp và các chỉ số phức tạp
2.  **Chấm điểm**: Áp dụng chấm điểm độ phức tạp đa chiều trên các yếu tố hoạt động khác nhau
3.  **Đối sánh**: So sánh các yêu cầu hoạt động với các khả năng của Serena và Morphllm
4.  **Lựa chọn**: Chọn công cụ tối ưu dựa trên ma trận chấm điểm và các yêu cầu về hiệu suất
5.  **Xác thực**: Xác minh tính chính xác của lựa chọn và cung cấp các chỉ số tin cậy

Các hành vi chính:
- Chấm điểm độ phức tạp dựa trên số lượng tệp, loại hoạt động, ngôn ngữ và các yêu cầu của khung
- Đánh giá hiệu suất đánh giá sự đánh đổi giữa tốc độ và độ chính xác để lựa chọn tối ưu
- Ma trận logic quyết định với các ánh xạ trực tiếp và các quy tắc định tuyến dựa trên ngưỡng
- Đối sánh khả năng của công cụ cho Serena (các hoạt động ngữ nghĩa) so với Morphllm (các hoạt động mẫu)

## Tích hợp MCP
- **MCP Serena**: Tối ưu cho các hoạt động ngữ nghĩa, chức năng LSP, điều hướng ký hiệu và ngữ cảnh dự án
- **MCP Morphllm**: Tối ưu cho các chỉnh sửa dựa trên mẫu, các phép biến đổi hàng loạt và các hoạt động quan trọng về tốc độ
- **Ma trận quyết định**: Định tuyến thông minh dựa trên chấm điểm độ phức tạp và các đặc điểm hoạt động

## Phối hợp công cụ
- **get_current_config**: Phân tích cấu hình hệ thống để đánh giá khả năng của công cụ
- **execute_sketched_edit**: Kiểm tra và xác thực hoạt động để đảm bảo tính chính xác của lựa chọn
- **Read/Grep**: Phân tích ngữ cảnh hoạt động và xác định yếu tố phức tạp
- **Tích hợp**: Logic lựa chọn tự động được sử dụng bởi các lệnh tái cấu trúc, chỉnh sửa, triển khai và cải tiến

## Các mẫu chính
- **Ánh xạ trực tiếp**: Các hoạt động ký hiệu → Serena, Chỉnh sửa mẫu → Morphllm, Các hoạt động bộ nhớ → Serena
- **Ngưỡng độ phức tạp**: Điểm > 0,6 → Serena, Điểm < 0,4 → Morphllm, 0,4-0,6 → Dựa trên tính năng
- **Sự đánh đổi hiệu suất**: Yêu cầu về tốc độ → Morphllm, Yêu cầu về độ chính xác → Serena
- **Chiến lược dự phòng**: Chuỗi suy giảm Serena → Morphllm → các công cụ gốc

## Ví dụ

### Hoạt động tái cấu trúc phức tạp
```
/sc:select-tool "đổi tên hàm trên 10 tệp" --analyze
# Phân tích: Độ phức tạp cao (nhiều tệp, các hoạt động ký hiệu)
# Lựa chọn: MCP Serena (khả năng LSP, hiểu biết ngữ nghĩa)
```

### Chỉnh sửa hàng loạt dựa trên mẫu
```
/sc:select-tool "cập nhật console.log thành logger.info trên toàn bộ dự án" --explain
# Phân tích: Chuyển đổi dựa trên mẫu, ưu tiên tốc độ
# Lựa chọn: MCP Morphllm (đối sánh mẫu, các hoạt động hàng loạt)
```

### Hoạt động quản lý bộ nhớ
```
/sc:select-tool "lưu ngữ cảnh dự án và các khám phá"
# Ánh xạ trực tiếp: Các hoạt động bộ nhớ → MCP Serena
# Cơ sở lý luận: Ngữ cảnh dự án và duy trì giữa các phiên
```

## Giới hạn

**Sẽ:**
- Phân tích các hoạt động và cung cấp lựa chọn công cụ tối ưu giữa Serena và Morphllm
- Áp dụng chấm điểm độ phức tạp dựa trên số lượng tệp, loại hoạt động và các yêu cầu
- Cung cấp thời gian quyết định dưới 100ms với độ chính xác lựa chọn > 95%

**Sẽ không:**
- Ghi đè các thông số kỹ thuật công cụ rõ ràng khi người dùng có sở thích rõ ràng
- Lựa chọn các công cụ mà không có phân tích độ phức tạp và đối sánh khả năng phù hợp
- Ảnh hưởng đến các yêu cầu về hiệu suất vì sự tiện lợi hoặc tốc độ
