# 🎬 DỰ ÁN TỰ ĐỘNG HÓA VIDEO HYPERFRAMES (VIDV2)

## 📌 1. TỔNG QUAN DỰ ÁN & VAI TRÒ CỦA AGENT
Dự án này là hệ thống tự động sản xuất video ngắn dạng dọc (9:16, 1080x1920) phục vụ mạng xã hội (TikTok, Shorts, Reels) cho thương hiệu **TeraX**.
- **Luồng hoạt động:** n8n (hoặc webhook client) gửi bài viết HTML qua HTTP POST đến `webhook_server.py` (cổng 8000) $\to$ lưu vào thư mục `pending/` $\to$ **Antigravity Agent tự động đóng vai Builder** (thiết kế animation GSAP, tạo voice, cập nhật timing, render video) $\to$ chuyển video thành phẩm sang `completed/`.
- **Nguyên tắc quan trọng nhất:** Agent trực tiếp làm Builder xử lý mọi việc trong phiên làm việc, **tuyệt đối KHÔNG gọi API ngoài tốn phí và KHÔNG yêu cầu người dùng cung cấp GEMINI_API_KEY**.

---

## 🚀 2. PHẢN XẠ MẶC ĐỊNH KHI BẮT ĐẦU PHIÊN LÀM VIỆC (QUICK START)
Mỗi khi khởi động lại dự án hoặc người dùng nhắn *"Bắt đầu"*, *"Túc trực"* hoặc kiểm tra hệ thống:
1. Kiểm tra xem `python webhook_server.py` (cổng 8000) có đang chạy không.
2. Kiểm tra thư mục `D:\vidv2\pending\`.
3. Thiết lập lịch hẹn giờ (Cron schedule `* * * * *` qua công cụ `schedule`) để tự động quét thư mục `pending/` mỗi phút một lần.

---

## 📋 3. QUY TRÌNH 10 BƯỚC CHUẨN XÂY DỰNG VIDEO HYPERFRAMES

Khi phát hiện file `.html` mới trong `D:\vidv2\pending\`:

### Bước 1: Phân tích bài viết & Lập kịch bản 6 Frames
Đọc file `.html` trong `pending/`. Trích xuất tiêu đề, xác định `slug` (dạng `ten-bai-viet-khong-dau`), và chia nội dung thành đúng **6 phân cảnh (Frames)**:
1. **Frame 1 (Hook / Nỗi đau):** Câu hỏi gây tò mò, mở đầu bối cảnh kịch tính.
2. **Frame 2 (Khái niệm cốt lõi / Điểm nghẽn):** Định nghĩa vấn đề hoặc khái niệm trọng tâm.
3. **Frame 3 (3 Trụ cột / 3 Tình huống / Giải pháp):** Phân tích chi tiết với 3 thẻ (cards).
4. **Frame 4 (Chỉ số / Lưu ý / Cảnh báo):** Các con số thực tế hoặc sai lầm cần tránh.
5. **Frame 5 (Quy trình / 3 Bước hành động):** Hướng dẫn thực thi từng bước.
6. **Frame 6 (Call to Action / TeraX):** Đúc kết thông điệp và kêu gọi hành động cho doanh nghiệp.

### Bước 2: Khởi tạo thư mục dự án Hyperframes
Tạo cấu trúc thư mục tại `D:\vidv2\hyperframes\videos\{slug}\`:
```
hyperframes/videos/{slug}/
├── public/
│   └── audio/
├── renders/
├── meta.json
├── package.json
├── hyperframes.json
├── index.html
└── update_durations.py
```

### Bước 3: Cấu hình `package.json`, `meta.json`, `hyperframes.json`
- `package.json`:
  ```json
  {
    "name": "{slug}",
    "version": "1.0.0",
    "private": true,
    "scripts": {
      "dev": "hyperframes dev",
      "check": "hyperframes check",
      "render": "hyperframes render"
    },
    "devDependencies": {
      "@hyperframes/cli": "latest"
    }
  }
  ```
- `meta.json`:
  ```json
  {
    "title": "{Tiêu đề video}",
    "description": "Video ngắn tự động bởi TeraX Builder",
    "fps": 30,
    "width": 1080,
    "height": 1920
  }
  ```
- `hyperframes.json`:
  ```json
  {
    "width": 1080,
    "height": 1920,
    "fps": 30
  }
  ```

### Bước 4: Tạo Voice đọc Tiếng Việt (Edge-TTS)
Dùng Python script chạy ngầm `edge-tts` với giọng `vi-VN-HoaiMyNeural` (hoặc `vi-VN-NamMinhNeural`):
- Xuất 6 file audio: `public/audio/01.mp3` $\to$ `06.mp3` tương ứng với 6 frames.
- Giữ tốc độ chuẩn (`+0%`) hoặc tăng nhẹ (`+10%` nếu kịch bản dài).

### Bước 5: Viết `index.html` theo Chuẩn Thiết Kế TeraX
**Quy tắc thiết kế bất biến:**
- **Kích thước:** `1080px x 1920px` (9:16 dọc).
- **Màu sắc thương hiệu:**
  - Nền chính: Trắng tinh khiết `#ffffff` (hoặc `#fafafa`). Tuyệt đối không dùng nền tối.
  - Màu nhấn (Accent): TeraX Orange `#F97316` (hoặc cam đỏ `#EA580C`).
  - Màu chữ: Chữ chính xám đậm `#1f2937`, chữ phụ `#6b7280`.
  - Nền Card/Badge: `#f3f4f6`, `#f8fafc`, viền `#e5e7eb`, bóng đổ nhẹ `box-shadow: 0 4px 20px rgba(0,0,0,0.06)`.
- **Typography:** Font Google `'Inter', sans-serif`.
- **Cấu trúc Audio bắt buộc (Tránh lỗi `media_missing_id`):**
  Mỗi thẻ `<audio class="clip">` **bắt buộc phải có thuộc tính `id`**:
  ```html
  <audio id="audio-01" class="clip" src="./public/audio/01.mp3" data-start="0.00" data-duration="6.00"></audio>
  <audio id="audio-02" class="clip" src="./public/audio/02.mp3" data-start="6.00" data-duration="7.00"></audio>
  ...
  ```
- **Cấu trúc Frame:** 6 thẻ div riêng biệt `#frame1` đến `#frame6` với class `frame`:
  ```css
  .frame {
    position: absolute;
    inset: 0;
    width: 1080px;
    height: 1920px;
    display: none;
    flex-direction: column;
    justify-content: space-between;
    padding: 100px 70px;
    box-sizing: border-box;
  }
  ```
- **Hiệu ứng GSAP:** Dùng timeline duy nhất. Tại thời điểm bắt đầu của mỗi frame, set `display: "flex"` và animate các phần tử con (`from({ opacity: 0, y: 30, stagger: 0.15 })`), kết thúc frame set `display: "none"`.

### Bước 6: Đồng bộ Thời lượng chính xác (`update_durations.py`)
Viết và chạy script Python dùng `ffprobe` đọc thời lượng thực tế của từng file `01.mp3` $\to$ `06.mp3`:
- Tính mảng `DURATIONS` và `START_TIMES`.
- Tự động thay thế mảng timing trong Javascript và các thuộc tính `data-start`, `data-duration` trong các thẻ `<audio>`.
- Cập nhật tổng thời lượng cho timeline GSAP và tag `<div id="hyperframe" data-duration="...">`.

### Bước 7: Kiểm tra Lỗi (`npm run check`)
Chạy lệnh `npm run check` trong thư mục video. Bắt buộc:
- **0 errors, 0 warnings**.
- Nếu có cảnh báo về id audio hoặc duration, sửa lại ngay trước khi render.

### Bước 8: Render Video (`npm run render`)
Chạy `npm run render`. Video sẽ được xuất ra thư mục `renders/{slug}.mp4`.

### Bước 9: Bàn giao thành phẩm vào `completed/`
1. Copy file `renders/{slug}.mp4` sang `D:\vidv2\completed\{slug}.mp4`.
2. Di chuyển file bài viết `.html` tương ứng từ `D:\vidv2\pending\` sang `D:\vidv2\completed\`.

### Bước 10: Báo cáo kết quả
Thông báo ngắn gọn cho người dùng về video vừa hoàn thành (tên video, thời lượng, dung lượng, đường dẫn đến thư mục [completed/](file:///D:/vidv2/completed)).

---

## 🛠️ 4. XỬ LÝ LỖI PHỔ BIẾN
1. **Lỗi `media_missing_id`:** Luôn thêm `id="audio-01"`, `id="audio-02"`... vào các thẻ `<audio>`.
2. **Lỗi `out_of_bounds_clip`:** Tổng thời lượng `data-duration` của container `<div id="hyperframe">` phải lớn hơn hoặc bằng thời điểm kết thúc của file audio cuối cùng.
3. **Lỗi ffmpeg không tìm thấy:** Đảm bảo `ffmpeg` và `ffprobe` đã được thêm vào Windows PATH.
