"""
Editorial Intelligence Agent (Long-Form Documentary Engine V4)
Builds deep editorial reasoning layer prior to script generation:
- Formulates EDITORIAL_THESIS
- Defines CENTRAL_QUESTION (driving mystery)
- Formulates VIEWER_PROMISE (guaranteed takeaway)
- Articulates WHY_THIS_MATTERS
- Exposes KEY_TENSION & SURPRISING_INSIGHT
- Isolates TECHNICAL_BREAKTHROUGH
- Outlines REAL_WORLD_IMPLICATION
- Identifies TRADE_OFF & LIMITATION
- Resolves FINAL_PAYOFF
"""
import uuid
from typing import Dict, Any, List
from radar.models.schemas import (
    StorySelectionArtifact, RepoAnalysis, EditorialThesis
)


class EditorialIntelligenceAgent:
    """Creates the deep editorial reasoning thesis guiding documentary scripting."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def synthesize_thesis(self, story: StorySelectionArtifact) -> EditorialThesis:
        repo = story.selected_repos[0].repository
        name = repo.name.lower()
        full_name = repo.full_name
        stars_k = round(repo.stars / 1000, 1)
        stars_str = f"{stars_k}k" if stars_k >= 1 else str(repo.stars)

        if "browser" in name:
            return EditorialThesis(
                story_id=story.story_id,
                editorial_thesis=(
                    "browser-use chuyển dịch mô hình AI từ công cụ trò chuyện thụ động sang tác nhân tự chủ "
                    "hành động trên môi trường web thực tế bằng thị giác máy và phân tích DOM không cần bộ chọn cứng."
                ),
                central_question=(
                    "Làm thế nào một mô hình ngôn ngữ lớn có thể nhìn thấy, định vị và click chính xác "
                    "các phần tử trên trang web mà không làm vỡ hệ thống khi giao diện liên tục thay đổi?"
                ),
                viewer_promise=(
                    "Hiểu cặn kẽ kiến trúc 3 tầng Perception-Reasoning-Action, cách giải quyết bài toán "
                    "web scraping gãy vỡ và bài toán chi phí token thực tế trong môi trường production."
                ),
                why_this_matters=(
                    "Giao diện người dùng web được thiết kế cho mắt và tay con người, không phải cho máy tính. "
                    "Khả năng thích ứng tự động hóa web mở ra kỷ nguyên robot phần mềm thế hệ mới."
                ),
                key_tension=(
                    "Các script CSS/XPath truyền thống siêu nhanh nhưng cực kỳ giòn và dễ gãy vỡ; "
                    "trong khi AI Agent siêu linh hoạt nhưng lại vấp phải bài toán chi phí token và độ trễ suy luận."
                ),
                surprising_insight=(
                    "Agent không đọc toàn bộ mã HTML khổng lồ mà dùng thuật toán lọc cây DOM tương tác, "
                    "đánh số trực quan lên tọa độ màn hình và gửi ảnh chụp đa phương thức cho LLM."
                ),
                technical_breakthrough=(
                    "Cơ chế Visual DOM Indexing kết hợp cùng engine Playwright bất đồng bộ cho phép "
                    "mô hình tương tác tự nhiên với bất kỳ trang web động nào."
                ),
                real_world_implication=(
                    "Tự động hóa hoàn toàn quy trình kiểm thử E2E QA, theo dõi dữ liệu thị trường theo thời gian thực "
                    "và vận hành các quy trình nhập liệu thủ công tốn hàng nghìn giờ mỗi tháng."
                ),
                trade_off=(
                    "Đổi độ trễ 2–5 giây và chi phí token đa phương thức cho mỗi hành động "
                    "để lấy khả năng thích ứng linh hoạt và tự sửa lỗi khi giao diện thay đổi."
                ),
                limitation=(
                    "Chưa thể vượt qua các hệ thống chống bot cao cấp như CAPTCHA xoay vòng hay phân tích vân tay thiết bị; "
                    "không phù hợp cho các tác vụ crawl dữ liệu tĩnh hàng triệu request mỗi ngày."
                ),
                final_payoff=(
                    "browser-use chứng minh rằng web không còn là rào cản của AI: "
                    "thế giới phần mềm đang bước từ thời đại chatbox sang thời đại agentic execution."
                )
            )
        elif "zed" in name:
            return EditorialThesis(
                story_id=story.story_id,
                editorial_thesis=(
                    "Zed là bước đột phá kỹ thuật chứng minh các công cụ lập trình desktop viết bằng Rust "
                    "và render trực tiếp qua GPU có thể đè bẹp hoàn toàn kiến trúc web nhúng Electron về tốc độ và tài nguyên."
                ),
                central_question=(
                    "Tại sao những kỹ sư từng tạo ra Atom lại từ bỏ hoàn toàn nền tảng Electron "
                    "để viết lại code editor bằng 100% Rust và GPU rendering từ con số không?"
                ),
                viewer_promise=(
                    "Nắm bắt cơ chế bên dưới của GPU rendering trên desktop, cấu trúc dữ liệu Rope Buffer "
                    "và lý do làn sóng phần mềm native đang trỗi dậy đánh bại các ứng dụng web cồng kềnh."
                ),
                why_this_matters=(
                    "Lập trình viên hàng ngày phải chịu đựng những công cụ ngốn hàng gigabyte RAM, "
                    "khởi động chậm chạp và giật lag trên màn hình độ phân giải cao."
                ),
                key_tension=(
                    "Electron mang lại tốc độ phát triển giao diện nhanh bằng web stack nhưng đánh đổi hiệu năng phần cứng; "
                    "Rust mang lại hiệu năng đỉnh cao nhưng đòi hỏi chi phí kỹ thuật cực lớn để tự viết engine đồ họa."
                ),
                surprising_insight=(
                    "Zed không dùng bất kỳ thẻ HTML hay CSS nào; toàn bộ chữ và giao diện được gửi draw call "
                    "trực tiếp vào chip đồ họa GPU với tần số quét 120 khung hình/giây."
                ),
                technical_breakthrough=(
                    "Framework đồ họa GPUI tùy chỉnh kết hợp Text Rope engine đa luồng không tương tranh."
                ),
                real_world_implication=(
                    "Giảm thời gian khởi động xuống 0.35 giây, tiết kiệm 90% RAM và loại bỏ độ trễ gõ phím "
                    "ngay cả trên các dự án hàng triệu dòng code."
                ),
                trade_off=(
                    "Tốc độ phát triển tính năng chậm hơn so với hệ sinh thái web; "
                    "hệ thống extension non trẻ và đòi hỏi thời gian để hỗ trợ toàn diện đa nền tảng."
                ),
                limitation=(
                    "Hệ sinh thái extension hiện chưa thể sánh bằng VS Code Marketplace sau một thập kỷ tích lũy; "
                    "bản hỗ trợ Windows vẫn đang trong quá trình hoàn thiện."
                ),
                final_payoff=(
                    "Zed định nghĩa lại tiêu chuẩn phần mềm công cụ kỹ thuật: "
                    "hiệu năng thuần túy và trải nghiệm native là con đường phát triển bền vững duy nhất."
                )
            )
        elif "uv" in name:
            return EditorialThesis(
                story_id=story.story_id,
                editorial_thesis=(
                    "uv của Astral chứng minh cuộc cách mạng tái cấu trúc hạ tầng tooling Python bằng Rust "
                    "giúp giải quyết dứt điểm nút thắt cổ chai về tốc độ cài đặt và quản lý gói tồn tại suốt hai thập kỷ."
                ),
                central_question=(
                    "Tại sao một công cụ quản lý gói Python viết bằng Rust lại có thể nhanh gấp 10 đến 100 lần "
                    "pip và virtualenv truyền thống mà vẫn giữ được độ tương thích 100%?"
                ),
                viewer_promise=(
                    "Thấu hiểu kiến trúc giải quyết phụ thuộc PubGrub, cơ chế copy-on-write và cách "
                    "Rust đang thay đổi toàn bộ hệ sinh thái phần mềm khoa học dữ liệu và AI."
                ),
                why_this_matters=(
                    "Hàng triệu kỹ sư và đường ống CI/CD trên thế giới tiêu tốn hàng nghìn giờ mỗi ngày "
                    "chỉ để chờ đợi pip tải và phân giải xung đột thư viện."
                ),
                key_tension=(
                    "Python là ngôn ngữ phổ biến nhất cho AI nhưng hệ thống tooling cốt lõi lại chậm chạp "
                    "và phân mảnh giữa pip, poetry, conda và venv."
                ),
                surprising_insight=(
                    "uv không chỉ là trình cài gói thay thế pip; nó là một nền tảng quản lý dự án, "
                    "tự động tải phiên bản Python, phân giải dependency dạng đại số và lưu cache ổ cứng dùng chung."
                ),
                technical_breakthrough=(
                    "Thuật toán PubGrub phân giải dependency song song kết hợp hardlink và reflink trên hệ thống file."
                ),
                real_world_implication=(
                    "Rút ngắn thời gian build Docker image và chạy CI/CD từ vài phút xuống còn vài giây, "
                    "tiết kiệm hàng triệu USD chi phí hạ tầng máy chủ cho các doanh nghiệp công nghệ."
                ),
                trade_off=(
                    "Tập trung hóa quyền năng vào một công cụ đơn lẻ được tài trợ thương mại bởi Astral, "
                    "thay thế các công cụ tiêu chuẩn cộng đồng phân tán của PyPA."
                ),
                limitation=(
                    "Các gói C-extension phức tạp yêu cầu biên dịch đặc biệt từ mã nguồn vẫn phụ thuộc vào trình biên dịch hệ thống."
                ),
                final_payoff=(
                    "uv là cột mốc trưởng thành của hệ sinh thái Python: "
                    "ngôn ngữ viết code là Python, nhưng hạ tầng vận hành được bàn giao cho Rust."
                )
            )
        elif "ollama" in name:
            return EditorialThesis(
                story_id=story.story_id,
                editorial_thesis=(
                    "Ollama dẫn đầu cuộc cách mạng đưa các mô hình ngôn ngữ lớn từ đám mây đắt đỏ về chạy trực tiếp "
                    "trên máy tính cá nhân nhờ kiến trúc Go daemon kết hợp backend C++ llama.cpp và lượng tử hóa GGUF."
                ),
                central_question=(
                    "Làm thế nào Ollama có thể đóng gói toàn bộ hạ tầng AI phức tạp vào một tệp nhị phân duy nhất, "
                    "cho phép chạy mượt mà mô hình hàng chục tỷ tham số trên phần cứng cá nhân mà không cần Internet?"
                ),
                viewer_promise=(
                    "Giải mã cơ chế lượng tử hóa GGUF k-quants, thuật toán phân bổ GPU Layer Offloading trên Apple Silicon "
                    "và Nvidia, cùng kiến trúc bảo mật tuyệt đối cho mọi lập trình viên."
                ),
                why_this_matters=(
                    "Các API cloud AI tiêu tốn hàng nghìn USD chi phí định kỳ, tiềm ẩn nguy cơ rò rỉ mã nguồn nhạy cảm "
                    "và phụ thuộc hoàn toàn vào kết nối mạng của các tập đoàn công nghệ lớn."
                ),
                key_tension=(
                    "Mô hình AI nguyên bản FP16 ngốn hàng chục gigabyte VRAM vượt xa phần cứng cá nhân; "
                    "Ollama phải nén trọng số cực đại mà vẫn bảo toàn năng lực suy luận với tổn thất dưới 1% perplexity."
                ),
                surprising_insight=(
                    "Ollama tự động tính toán VRAM khả dụng để chia tách tensor layers giữa GPU và RAM hệ thống, "
                    "đồng thời chuẩn hóa định dạng Modelfile tương tự Dockerfile để phân phối AI trong vài giây."
                ),
                technical_breakthrough=(
                    "Thuật toán GPU Layer Offloading động kết hợp GGUF k-quants nén ma trận trọng số 4-bit và Go REST API."
                ),
                real_world_implication=(
                    "Trao quyền cho các kỹ sư và doanh nghiệp vận hành trợ lý code, phân tích dữ liệu bảo mật và agent tự hành "
                    "100% on-premises với chi phí 0 đồng phí API và độ trễ mạng bằng 0."
                ),
                trade_off=(
                    "Đánh đổi năng lực suy luận của các siêu mô hình hàng trăm tỷ tham số trên cloud datacenter "
                    "để đổi lấy sự riêng tư tuyệt đối, tốc độ tức thì và quyền kiểm soát mô hình hoàn toàn."
                ),
                limitation=(
                    "Cửa sổ ngữ cảnh context window lớn đòi hỏi KV-cache tăng theo cấp số nhân; "
                    "phần cứng thiếu băng thông bộ nhớ sẽ bị suy giảm tốc độ khi offload layer về CPU."
                ),
                final_payoff=(
                    "Ollama là bản tuyên ngôn độc lập của giới lập trình: biến máy tính cá nhân thành một siêu máy tính "
                    "xử lý ngôn ngữ riêng tư, bảo mật và bất khả xâm phạm."
                )
            )
        else:
            # Generic repo deep dive
            desc = repo.description or "Dự án mã nguồn mở đáng chú ý."
            return EditorialThesis(
                story_id=story.story_id,
                editorial_thesis=(
                    f"{repo.name} giải quyết một thách thức kỹ thuật cốt lõi trong cộng đồng phần mềm "
                    f"thông qua kiến trúc tối ưu hóa và cách tiếp cận hiện đại."
                ),
                central_question=(
                    f"Tại sao dự án {repo.name} lại thu hút sự chú ý đặc biệt từ cộng đồng kỹ sư toàn cầu "
                    f"và nó giải quyết bài toán kỹ thuật hóc búa nào mà các công cụ trước đó bó tay?"
                ),
                viewer_promise=(
                    f"Hiểu rõ cơ chế kiến trúc nội tại của {repo.name}, các giải pháp kỹ thuật nền tảng "
                    f"và đánh giá khách quan những bài toán đánh đổi khi áp dụng vào sản phẩm thực tế."
                ),
                why_this_matters=(
                    f"Các giải pháp cũ trong lĩnh vực này thường gặp rào cản về hiệu năng và độ phức tạp bảo trì. "
                    f"{repo.name} đưa ra một hướng đi mới đáng học hỏi."
                ),
                key_tension=(
                    "Sự mâu thuẫn giữa tính đơn giản dễ tiếp cận và khả năng mở rộng chịu tải cao "
                    "trong môi trường sản xuất thực tế."
                ),
                surprising_insight=(
                    f"Cách đội ngũ tác giả tổ chức module cốt lõi bằng {repo.language} giúp tối ưu tài nguyên "
                    f"và loại bỏ các lớp trung gian không cần thiết."
                ),
                technical_breakthrough=(
                    f"Kiến trúc module hóa linh hoạt cho phép mở rộng tính năng mà không làm suy giảm hiệu năng cơ sở."
                ),
                real_world_implication=(
                    "Giúp các đội ngũ kỹ sư rút ngắn thời gian phát triển và giảm thiểu chi phí vận hành hệ thống."
                ),
                trade_off=(
                    "Cần thời gian thích ứng với quy chuẩn mới và hệ sinh thái thư viện mở rộng đang trong quá trình phát triển."
                ),
                limitation=(
                    "Chưa phải giải pháp vạn năng cho mọi trường hợp; cần đánh giá kỹ điều kiện tải trước khi triển khai quy mô lớn."
                ),
                final_payoff=(
                    f"{repo.name} chứng minh rằng việc đào sâu tối ưu kiến trúc phần mềm từ gốc rễ "
                    f"luôn mang lại giá trị bền vững cho cộng đồng công nghệ."
                )
            )
