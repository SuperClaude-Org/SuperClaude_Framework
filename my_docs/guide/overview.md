### Tổng quan Framework SuperClaude

SuperClaude được xây dựng dựa trên một hệ thống các **tệp tin ngữ cảnh (context files)** bằng Markdown. Các tệp này không phải là code thực thi, mà là những **bộ hướng dẫn hành vi** cho AI (Claude Code). Chúng định nghĩa cách AI nên suy nghĩ, hành động và phản ứng trong các tình huống khác nhau. Framework được chia thành 5 phạm trù chính:

1.  **Core Files (Tệp Lõi):** Nền tảng triết lý và các quy tắc bất biến.
2.  **Agents (Tác tử):** Các "chuyên gia" ảo với kiến thức chuyên sâu về một lĩnh vực.
3.  **Modes (Chế độ):** Các "trạng thái" tư duy, thay đổi phong cách tương tác của AI.
4.  **Commands (Lệnh):** Các quy trình công việc (workflow) được định sẵn để tự động hóa các tác vụ phổ biến.
5.  **MCP (Meta-Context Protocols):** Các giao thức để tương tác với những công cụ chuyên biệt, cao cấp.

---

### I. Core Files (Tệp Lõi)

Đây là nền tảng của toàn bộ framework, thiết lập các nguyên tắc và quy tắc cơ bản mà AI phải luôn tuân thủ.

*   **`PRINCIPLES.md`**: Đặt ra triết lý kỹ thuật phần mềm cốt lõi. Nhấn mạnh vào các nguyên tắc như SOLID, DRY, KISS và tư duy hệ thống. AI được hướng dẫn phải đưa ra quyết định dựa trên bằng chứng và luôn cân nhắc các yếu-tố đánh đổi.
*   **`RULES.md`**: Bao gồm các quy tắc hành vi cụ thể, được phân cấp theo mức độ quan trọng (🔴 Critical, 🟡 Important, 🟢 Recommended). Các quy tắc này bao trùm từ quy trình làm việc, quản lý scope, cách tổ chức code, cho đến việc phải luôn trung thực và chuyên nghiệp. Ví dụ: "Luôn kiểm tra `git status` trước khi bắt đầu" hoặc "Không bao giờ để lại code `TODO`".
*   **`FLAGS.md`**: Định nghĩa các "cờ" (flags) để người dùng có thể kích hoạt các chế độ hoặc hành vi cụ thể một cách thủ công, ví dụ: `--brainstorm` để vào chế độ sáng tạo, hoặc `--safe-mode` để thực thi một cách thận trọng tối đa.

---

### II. Agents (Tác tử)

Agents là các "persona" (nhân cách) chuyên gia mà AI có thể "nhập vai". Mỗi agent có một lĩnh vực chuyên môn, một tư duy hành vi, và các hành động/kết quả đầu ra cụ thể. Việc này giúp AI cung cấp câu trả lời chất lượng và sâu sắc hơn trong từng lĩnh vực.

*   **`backend-architect.md`**: Chuyên gia thiết kế hệ thống backend, tập trung vào độ tin cậy, bảo mật và khả năng chịu lỗi.
*   **`frontend-architect.md`**: Chuyên gia giao diện người dùng, ưu tiên khả năng truy cập (accessibility), hiệu năng và trải nghiệm người dùng.
*   **`devops-architect.md`**: Chuyên gia tự động hóa hạ tầng và quy trình CI/CD.
*   **`security-engineer.md`**: Chuyên gia bảo mật, tư duy như một kẻ tấn công để tìm lỗ hổng.
*   **`quality-engineer.md`**: Chuyên gia đảm bảo chất lượng, tập trung vào chiến lược testing và phát hiện các trường hợp ngoại lệ (edge cases).
*   **`python-expert.md`**: Chuyên gia Python, cung cấp code chất lượng sản phẩm, an toàn và hiệu năng cao.
*   **`refactoring-expert.md`**: Chuyên gia tái cấu trúc code, giảm nợ kỹ thuật (technical debt).
*   **`system-architect.md`**: Chuyên gia kiến trúc hệ thống tổng thể, tập trung vào các quyết định dài hạn.
*   **`technical-writer.md`**: Chuyên gia viết tài liệu kỹ thuật, đảm bảo sự rõ ràng và dễ hiểu.
*   **`learning-guide.md`**: Hướng dẫn học tập, giải thích các khái niệm lập trình một cách tuần tự.
*   **`socratic-mentor.md`**: Một người thầy thông thái, sử dụng phương pháp hỏi-đáp Socratic để giúp người dùng tự khám phá kiến thức.
*   **`requirements-analyst.md`**: Chuyên gia phân tích yêu cầu, biến những ý tưởng mơ hồ thành các đặc tả cụ thể.
*   **`root-cause-analyst.md`**: Chuyên gia phân tích nguyên nhân gốc rễ, điều tra các vấn đề phức tạp.

---

### III. Modes (Chế độ)

Modes là các trạng thái hoạt động, thay đổi cách AI tương tác và xử lý thông tin. Chúng không gắn với một lĩnh vực chuyên môn như Agents, mà tập trung vào "phong cách" làm việc.

*   **`MODE_Brainstorming.md`**: Kích hoạt tư duy sáng tạo, khám phá. AI sẽ đặt nhiều câu hỏi gợi mở thay vì đưa ra giải pháp ngay.
*   **`MODE_Introspection.md`**: Chế độ "tự vấn". AI sẽ phân tích lại chuỗi suy nghĩ của chính mình để tìm ra các mẫu, tối ưu hóa quyết định và học hỏi từ lỗi sai.
*   **`MODE_Orchestration.md`**: Chế độ "điều phối". AI sẽ tập trung vào việc lựa chọn công cụ tối ưu nhất cho từng tác vụ và tối đa hóa hiệu quả tài nguyên, đặc biệt là khi thực thi song song.
*   **`MODE_Task_Management.md`**: Kích hoạt tư duy quản lý công việc có cấu trúc. AI sẽ chia nhỏ các tác vụ phức tạp theo một hệ thống phân cấp (Plan → Phase → Task → Todo) và sử dụng bộ nhớ (memory) để theo dõi tiến độ.
*   **`MODE_Token_Efficiency.md`**: Chế độ "tiết kiệm token". AI sẽ sử dụng một hệ thống ký hiệu và từ viết tắt để giao tiếp một cách cô đọng nhưng vẫn rõ ràng, giúp giảm 30-50% lượng token sử dụng.

---

### IV. Commands (Lệnh)

Đây là các quy trình công việc (workflows) được định nghĩa trước, kích hoạt bằng lệnh `/sc:[command]`. Mỗi lệnh là một chuỗi các bước được cấu trúc sẵn để giải quyết một tác vụ phát triển phần mềm cụ thể.

*   **Phân tích & Thiết kế:**
    *   `analyze`: Phân tích code toàn diện về chất lượng, bảo mật, hiệu năng.
    *   `design`: Thiết kế kiến trúc hệ thống, API, hoặc component.
    *   `estimate`: Cung cấp ước tính về thời gian, công sức cho một tác vụ.
*   **Triển khai & Cải thiện:**
    *   `implement`: Triển khai tính năng mới, tự động kích hoạt các Agents và MCPs phù hợp.
    *   `build`: Biên dịch và đóng gói dự án.
    *   `test`: Chạy test và phân tích độ bao phủ (coverage).
    *   `improve`: Cải thiện code về chất lượng, hiệu năng, hoặc khả năng bảo trì.
    *   `cleanup`: Dọn dẹp code, xóa code chết, tối ưu cấu trúc dự án.
*   **Tài liệu & Giải thích:**
    *   `document`: Tạo tài liệu cho component, API.
    *   `explain`: Giải thích code, khái niệm hoặc hành vi hệ thống.
    *   `index`: Tạo tài liệu và cơ sở kiến thức toàn diện cho dự án.
*   **Quản lý & Điều phối:**
    *   `brainstorm`: Khám phá yêu cầu một cách tương tác.
    *   `workflow`: Tạo một quy trình triển khai có cấu trúc từ các tài liệu yêu cầu (PRD).
    *   `task`: Quản lý và thực thi các tác vụ phức tạp, có khả năng điều phối nhiều agents.
    *   `spawn`: "Sinh" ra một quy trình điều phối cấp cao để xử lý các tác vụ cực kỳ phức tạp.
*   **Tiện ích & Vòng đời:**
    *   `git`: Thực hiện các thao tác Git với các tin nhắn commit thông minh.
    *   `troubleshoot`: Chẩn đoán và giải quyết sự cố.
    *   `load` & `save`: Quản lý vòng đời của một phiên làm việc, lưu và tải lại ngữ cảnh dự án.
    *   `reflect`: Tự đánh giá và xác thực lại công việc đã làm.
    *   `select-tool`: Lựa chọn công cụ MCP tối ưu một cách thông minh.

---

### V. MCP (Meta-Context Protocols)

MCP là các giao thức ngữ cảnh cấp cao, định nghĩa cách AI nên tương tác với các công cụ chuyên biệt (được gọi là MCP Servers). Mỗi tệp MCP giải thích khi nào nên chọn một công cụ và cách nó phối hợp với các công cụ khác.

*   **`MCP_Context7.md`**: Dùng để tra cứu tài liệu chính thức của các thư viện và framework.
*   **`MCP_Magic.md`**: Dùng để tạo các thành phần giao diện người dùng (UI components) hiện đại.
*   **`MCP_Morphllm.md`**: Dùng cho các tác vụ chỉnh sửa code hàng loạt dựa trên mẫu (pattern-based).
*   **`MCP_Playwright.md`**: Dùng cho các tác vụ tự động hóa trình duyệt và kiểm thử E2E.
*   **`MCP_Sequential.md`**: Kích hoạt một bộ máy suy luận đa bước để phân tích các vấn đề phức tạp.
*   **`MCP_Serena.md`**: Dùng cho việc hiểu ngữ nghĩa của code (ví dụ: đổi tên biến/hàm trên toàn dự án) và quản lý bộ nhớ phiên làm việc.

Tóm lại, SuperClaude là một hệ thống được thiết kế cực kỳ bài bản, biến AI từ một công cụ trả lời đơn thuần thành một đối tác phát triển phần mềm thực thụ, có khả năng tư duy, lập kế hoạch, và thực thi một cách chuyên nghiệp và hiệu quả.
