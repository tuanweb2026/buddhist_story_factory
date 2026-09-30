# Buddhist Story Factory (Xưởng Sản Xuất Video Truyện Phật Giáo Tự Động)

Hệ thống tự động hóa chuyển đổi văn bản và sách PDF Phật giáo thành video hoàn chỉnh với chuẩn điện ảnh màn ảnh rộng 16:9 (1920x1080), lồng tiếng truyền cảm Microsoft Neural Voice (Hoài My) và mỹ thuật Phật giáo / Thiền tông thanh tịnh.

---

## 🌟 Các Tính Năng Nổi Bật

1. **Chuẩn Màn Ảnh Rộng 16:9 Widescreen (1920x1080)**:
   - Tối ưu hóa cho YouTube, TV và các nền tảng video dài.
   - Hiệu ứng chuyển động máy quay Ken Burns (Slow Pan/Zoom) tạo chiều sâu điện ảnh.
2. **Mỹ Thuật Phật Giáo Đỉnh Cao**:
   - **Tranh màu nước nguyên bản**: Khai thác trực tiếp kho tranh minh họa thủ công từ các ấn phẩm Phật giáo kinh điển.
   - **Tranh thủy mặc Thiền tông (Sumi-e Zen Art)**: Tái hiện không gian thiền môn, trà đạo, vườn sỏi thanh tịnh.
3. **Lồng Tiếng Truyền Cảm Microsoft Neural Voice**:
   - Giọng nữ đọc tiếng Việt chuẩn `vi-VN-HoaiMyNeural` ấm áp, an lạc.
   - Hệ thống tự động xử lý câu dài, ngắt nhịp tự nhiên và cơ chế dự phòng `vi-VN-NamMinhNeural` đảm bảo 100% không gián đoạn.
4. **Chuẩn Lời Kể Văn Xuôi Tự Nhiên**:
   - Tự động loại bỏ hoàn toàn các ký hiệu phân mảnh như `"Cảnh 1:", "Cảnh 2:"` giúp câu chuyện liền mạch như một cuốn phim tài liệu/audiobook chân thực.
5. **Hệ Thống Phụ Đề Sang Trọng**:
   - Tự động canh giữa, xuống dòng thông minh và phủ trên thanh nền mờ bo góc (translucent lower-third) giúp người xem dễ theo dõi.

---

## 📚 Các Tuyển Tập Đã Sản Xuất

### 1. Tuyển tập "Những Mẩu Truyện Cuộc Sống Lòng Yêu Thương - Tập 3" (Tu Viện Chơn Như)
- **Tập hợp 6 chương trọn vẹn (95 phân cảnh chi tiết)**:
  - **Chương 1:** Thầy Cứu Nhái (17 cảnh - 2:13)
  - **Chương 2:** Thầy Cứu Chuột (17 cảnh - 1:57)
  - **Chương 3:** Chú Bé An (17 cảnh - 2:00)
  - **Chương 4:** Người Trộm Điều (16 cảnh - 1:48)
  - **Chương 5:** Đám Cỏ Đậu (12 cảnh - 1:20)
  - **Chương 6:** Chuyện Ly Nước (16 cảnh - 1:44)
- **Bản phim tổng hợp (Full Movie):** `data/buddhist_production/LongYeuThuong_Full_Movie_16x9.mp4` (Thời lượng 11 phút 01 giây).

### 2. Tuyển tập "101 Câu Chuyện Thiền" (101 Zen Stories - Trần Trúc Lâm Dịch)
- **Tập 1: Một Cốc Trà (A Cup of Tea)**: 12 cảnh minh họa phong cách tranh thủy mặc thiền tông Nhật Bản (85 giây).
- Kế hoạch 9 tập tiếp theo: *Thật Vậy Sao?, Những Cuộn Sóng Lớn, Mặt Trăng Không Thể Bị Đánh Cắp, Con Đường Bùn Lầy, Ngụ Ngôn Quả Dâu Rừng, Tiếng Vỗ Của Một Bàn Tay, Kẻ Cướp Trở Thành Môn Đồ, Cửa Thiên Đường, Hãy Tự Mở Kho Báu Của Mình*.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Dựng video theo kịch bản phân cảnh 16:9
```bash
# Dựng một chương truyện bất kỳ
python3 build_widescreen_chapter.py --script data/chapters/chapter1_script.json

# Dựng cho series Thiền tông với thư mục xuất tùy biến
python3 build_widescreen_chapter.py --script data/zen_scripts/story_01_mot_coc_tra.json --output_base data/zen_production/episodes
```

### 2. Dựng nhanh qua PDF Story Engine
```bash
# Xuất định dạng 16:9 Landscape
python3 pdf_story_engine.py --pdf "data/pdf/kinh_phap_cu_sample.pdf" --orientation landscape

# Xuất định dạng 9:16 Portrait (Shorts/Reels/TikTok)
python3 pdf_story_engine.py --pdf "data/pdf/kinh_phap_cu_sample.pdf" --orientation portrait
```

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
buddhist_story_factory/
├── build_widescreen_chapter.py  # Production Engine dựng video màn ảnh rộng 16:9
├── pdf_story_engine.py          # Pipeline phân tích PDF và tạo video tự động
├── cli.py                       # CLI điều khiển chung
├── prepare_chapters_4_5_6.py    # Script cắt crop tranh và chuẩn bị phân cảnh
├── data/
│   ├── book_illustrations/      # Kho tranh màu nước nguyên bản từ sách
│   ├── chapters/                # Kịch bản JSON các chương Lòng Yêu Thương
│   ├── zen_scripts/             # Kịch bản JSON các tập 101 Câu Chuyện Thiền
│   ├── buddhist_production/     # Kết quả video series Lòng Yêu Thương
│   └── zen_production/          # Kết quả video series 101 Câu Chuyện Thiền
└── README.md
```
