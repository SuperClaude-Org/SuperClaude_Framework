---
name: troubleshoot
description: "Chẩn đoán và giải quyết các sự cố trong mã, bản dựng, triển khai và hành vi của hệ thống"
category: tiện ích
complexity: cơ bản
mcp-servers: []
personas: []
---

# /sc:troubleshoot - Chẩn đoán và giải quyết sự cố

## Kích hoạt
- Yêu cầu điều tra lỗi mã và lỗi thời gian chạy
- Nhu cầu phân tích và giải quyết lỗi bản dựng
- Yêu cầu chẩn đoán và tối ưu hóa vấn đề về hiệu suất
- Phân tích sự cố triển khai và gỡ lỗi hành vi của hệ thống

## Cách sử dụng
```
/sc:troubleshoot [sự cố] [--type bug|build|performance|deployment] [--trace] [--fix]
```

## Luồng hành vi
1.  **Phân tích**: Kiểm tra mô tả sự cố và thu thập thông tin trạng thái hệ thống có liên quan
2.  **Điều tra**: Xác định các nguyên nhân gốc rễ tiềm ẩn thông qua phân tích mẫu có hệ thống
3.  **Gỡ lỗi**: Thực hiện các quy trình gỡ lỗi có cấu trúc bao gồm kiểm tra nhật ký và trạng thái
4.  **Đề xuất**: Xác thực các phương pháp giải quyết với đánh giá tác động và đánh giá rủi ro
5.  **Giải quyết**: Áp dụng các bản sửa lỗi phù hợp và xác minh hiệu quả của giải pháp

Các hành vi chính:
- Phân tích nguyên nhân gốc rễ có hệ thống với kiểm tra giả thuyết và thu thập bằng chứng
- Khắc phục sự cố đa miền (mã, bản dựng, hiệu suất, triển khai)
- Các phương pháp gỡ lỗi có cấu trúc với phân tích sự cố toàn diện
- Áp dụng bản sửa lỗi an toàn với xác minh và tài liệu

## Phối hợp công cụ
- **Read**: Phân tích nhật ký và kiểm tra trạng thái hệ thống
- **Bash**: Thực thi lệnh chẩn đoán và điều tra hệ thống
- **Grep**: Phát hiện mẫu lỗi và phân tích nhật ký
- **Write**: Báo cáo chẩn đoán và tài liệu giải quyết

## Các mẫu chính
- **Điều tra lỗi**: Phân tích lỗi → kiểm tra dấu vết ngăn xếp → kiểm tra mã → xác thực bản sửa lỗi
- **Khắc phục sự cố bản dựng**: Phân tích nhật ký bản dựng → kiểm tra phụ thuộc → xác thực cấu hình
- **Chẩn đoán hiệu suất**: Phân tích chỉ số → xác định điểm nghẽn → đề xuất tối ưu hóa
- **Sự cố triển khai**: Phân tích môi trường → xác minh cấu hình → xác thực dịch vụ

## Ví dụ

### Điều tra lỗi mã
```
/sc:troubleshoot "Ngoại lệ con trỏ null trong dịch vụ người dùng" --type bug --trace
# Phân tích có hệ thống bối cảnh lỗi và dấu vết ngăn xếp
# Xác định nguyên nhân gốc rễ và cung cấp các đề xuất sửa lỗi được nhắm mục tiêu
```

### Phân tích lỗi bản dựng
```
/sc:troubleshoot "Lỗi biên dịch TypeScript" --type build --fix
# Phân tích nhật ký bản dựng và cấu hình TypeScript
# Tự động áp dụng các bản sửa lỗi an toàn cho các sự cố biên dịch phổ biến
```

### Chẩn đoán vấn đề về hiệu suất
```
/sc:troubleshoot "Thời gian phản hồi API bị suy giảm" --type performance
# Phân tích chỉ số hiệu suất và xác định điểm nghẽn
# Cung cấp các đề xuất tối ưu hóa và hướng dẫn giám sát
```

### Giải quyết sự cố triển khai
```
/sc:troubleshoot "Dịch vụ không khởi động trong môi trường sản xuất" --type deployment --trace
# Phân tích môi trường và cấu hình
# Xác minh có hệ thống các yêu cầu và phụ thuộc triển khai
```

## Giới hạn

**Sẽ:**
- Thực hiện chẩn đoán sự cố có hệ thống bằng các phương pháp gỡ lỗi có cấu trúc
- Cung cấp các phương pháp giải quyết đã được xác thực với phân tích sự cố toàn diện
- Áp dụng các bản sửa lỗi an toàn với xác minh và tài liệu giải quyết chi tiết

**Sẽ không:**
- Áp dụng các bản sửa lỗi rủi ro mà không có phân tích và xác nhận của người dùng phù hợp
- Sửa đổi các hệ thống sản xuất mà không có sự cho phép rõ ràng và xác thực an toàn
- Thực hiện các thay đổi về kiến trúc mà không hiểu đầy đủ tác động của hệ thống
