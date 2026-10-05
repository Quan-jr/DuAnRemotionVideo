# 🎬 DỰ ÁN TỰ ĐỘNG HÓA VIDEO HYPERFRAMES (VIDV2)

## 📌 1. TỔNG QUAN DỰ ÁN & VAI TRÒ CỦA AGENT
Dự án này là hệ thống tự động sản xuất video ngắn dạng dọc (9:16, 1080x1920) phục vụ mạng xã hội (TikTok, Shorts, Reels) cho thương hiệu **TeraX**.
- **Luồng hoạt động:** n8n (hoặc webhook client) gửi bài viết HTML qua HTTP POST đến `webhook_server.py` (cổng 8000) $\to$ lưu vào thư mục `pending/` $\to$ **Antigravity Agent tự động đóng vai Builder** (thiết kế animation GSAP, tạo voice, cập nhật timing, render video) $\to$ chuyển video thành phẩm sang `completed/`.
- **Nguyên tắc quan trọng nhất:** Agent trực tiếp làm Builder xử lý mọi việc trong phiên làm việc, **tuyệt đối KHÔNG gọi API ngoài tốn phí và KHÔNG yêu cầu người dùng cung cấp GEMINI_API_KEY**.

---

## 🚀 2. PHẢN XẠ MẶC ĐỊNH KHI BẮT ĐẦU PHIÊN LÀM VIỆC (QUICK START)
Mỗi khi khởi động lại dự án hoặc người dùng nhắn *"Bắt đầu"*, *"Túc trực"* hoặc kiểm tra hệ thống:
1. Kiểm tra và khởi chạy `python webhook_server.py` (cổng 8000) nếu chưa chạy.
2. Kiểm tra và khởi chạy ngrok với static domain cố định: `ngrok http 8000 --url otter-saturday-viewing.ngrok-free.dev` (URL luôn cố định vĩnh viễn: `https://otter-saturday-viewing.ngrok-free.dev`).
3. Kiểm tra thư mục `D:\vidv2\pending\`.
4. Thiết lập lịch hẹn giờ (Cron schedule `* * * * *` qua công cụ `schedule`) để tự động quét thư mục `pending/` mỗi phút một lần.

---

## 🎙️ 3. QUY CHUẨN GIỌNG ĐỌC AI & CHUẨN HÓA KỊCH BẢN ÂM THANH (BẮT BUỘC)

### 3.1. Động cơ TTS & Nhân bản giọng (VieNeu-TTS)
* Sử dụng module `D:\vidv2\generate_tts_vieneu.py` (chạy với Python trong virtualenv `D:\vidv2\venv`).
* **Voice Cloning:** Tự động phát hiện và nhân bản giọng đọc từ file mẫu trong thư mục `D:\vidv2\voice_samples\` (ví dụ: `sample.wav`, `sample.mp3`...) thông qua tham số `ref_audio`. Nếu không có file mẫu thì dùng preset `Mai Anh` hoặc `Hải Đăng`.
* **Tốc độ đọc chuẩn (Speed):** Luôn cố định ở **`speed = 1.09`** (vừa vặn, rõ chữ, nhịp điệu cuốn hút, giữ nguyên cao độ tự nhiên).
* **Nhịp ngắt mệnh đề:** Rút ngắn khoảng lặng giữa các mệnh đề xuống **`0.06s - 0.08s`** để lời đọc dứt khoát, liền mạch.

### 3.2. Quy tắc viết kịch bản âm thanh: 100% THUẦN CHỮ (KHÔNG DÙNG KÝ TỰ ĐẶC BIỆT / GẠCH NỐI)
Khi viết kịch bản đưa vào mô hình TTS, **BẮT BUỘC phải chuyển đổi toàn bộ số, ký hiệu và từ viết tắt thành chữ tiếng Việt thuần túy, tuyệt đối không chèn ký tự lạ (`-`, `/`, `%`, `+`, `&`...)**:

* **Từ viết tắt & Chức danh (Cách nhau bằng khoảng trắng, KHÔNG dùng gạch nối `-`):**
  * `CEO` $\to$ viết thành: `C E O` (hoặc `giám đốc điều hành`)
  * `CFO` $\to$ viết thành: `C F O` (hoặc `giám đốc tài chính`)
  * `COO` $\to$ viết thành: `C O O` (hoặc `giám đốc vận hành`)
  * `PNJ` $\to$ viết thành: `P N J`
  * `FTC` $\to$ viết thành: `F T C`
  * `AI` $\to$ viết thành: `A I` (hoặc `trí tuệ nhân tạo`)
  * `TeraX` $\to$ đọc chuẩn `Te ra X` (tuyệt đối không đọc `.ai` hay `chấm AI`).
  * `VnExpress` $\to$ viết thành: `Vn Express`
  * `VnDirect` $\to$ viết thành: `Vn Direct`

* **Số tiền / Giá trị lớn:**
  * `4.200 tỷ đồng` $\to$ viết thành: `bốn nghìn hai trăm tỷ đồng`
  * `24.750 đồng` $\to$ viết thành: `hai mươi tư nghìn bảy trăm năm mươi đồng`
  * `7.071 tỷ đồng` $\to$ viết thành: `bảy nghìn không trăm bảy mươi mốt tỷ đồng`
  * `12.665 tỷ` $\to$ viết thành: `mười hai nghìn sáu trăm sáu mươi lăm tỷ đồng`
  * `41,5 tỷ đồng` $\to$ viết thành: `bốn mươi mốt phẩy năm tỷ đồng`

* **Phần trăm:**
  * `11,6%` $\to$ viết thành: `mười một phẩy sáu phần trăm`
  * `25%` $\to$ viết thành: `hai mươi lăm phần trăm`
  * `70%` $\to$ viết thành: `bảy mươi phần trăm`
  * `9,78%` $\to$ viết thành: `chín phẩy bảy mươi tám phần trăm`

* **Tỷ số tài chính & Phép đo:**
  * `P/E 12,17 lần` $\to$ viết thành: `P trên E mười hai phẩy mười bảy lần`
  * `EPS` $\to$ viết thành: `E P S`
  * `ROA`, `ROE` $\to$ viết thành: `R O A`, `R O E`

* **Thời gian & Số thứ tự:**
  * `phiên 1/10` $\to$ viết thành: `phiên ngày một tháng mười`
  * `9 tháng` $\to$ viết thành: `chín tháng`
  * `phiên thứ 4` $\to$ viết thành: `phiên thứ tư`
  * `chuỗi 8 phiên` $\to$ viết thành: `chuỗi tám phiên`

---

## 📋 4. QUY TRÌNH 10 BƯỚC CHUẨN XÂY DỰNG VIDEO HYPERFRAMES

Khi phát hiện file `.html` mới trong `D:\vidv2\pending\`:

### Bước 1: Phân tích bài viết & Lập kịch bản 6 Frames
Đọc file `.html` trong `pending/`. Trích xuất tiêu đề, xác định `slug` (dạng `ten-bai-viet-khong-dau`), và chia nội dung thành đúng **6 phân cảnh (Frames)**:
1. **Frame 1 (Hook / Nỗi đau):** Câu hỏi gây tò mò, mở đầu bối cảnh kịch tính.
2. **Frame 2 (Khái niệm cốt lõi / Điểm nghẽn):** Định nghĩa vấn đề hoặc khái niệm trọng tâm.
3. **Frame 3 (3 Trụ cột / 3 Tình huống / Giải pháp):** Phân tích chi tiết với 3 thẻ (cards) đánh số 1, 2, 3.
4. **Frame 4 (Chỉ số / Lưu ý / Cảnh báo):** Các con số thực tế kèm ghi chú quan trọng.
5. **Frame 5 (Quy trình / 3 Bước hành động):** 3 bước thực thi cụ thể (Bước 01, Bước 02, Bước 03).
6. **Frame 6 (Call to Action / TeraX):** Đúc kết thông điệp và nút CTA `Tìm hiểu ngay`.

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

### Bước 4: Tạo Voice đọc Tiếng Việt (VieNeu-TTS @ speed 1.09)
Chạy script `generate_tts_vieneu.py`:
```powershell
$env:HF_HOME="D:\dev-cache\huggingface"; $env:PYTHONIOENCODING="utf-8"
D:\vidv2\venv\Scripts\python -c "import generate_tts_vieneu; texts = [...]; generate_tts_vieneu.generate_audio_frames(r'D:\vidv2\hyperframes\videos\{slug}\public\audio', texts, speed=1.09)"
```
- Tự động xuất 6 file `01.mp3` $\to$ `06.mp3` với giọng đọc clone và tốc độ 1.09x.

### Bước 5: Viết `index.html` theo Chuẩn Thiết Kế Doanh Nghiệp TeraX
**Quy tắc thiết kế bất biến:**
- **Kích thước:** `1080px x 1920px` (9:16 dọc).
- **Màu sắc thương hiệu:**
  - Nền chính: Trắng tinh khiết `#ffffff` (hoặc `#fafafa`).
  - Màu nhấn (Accent): TeraX Orange `#F97316` (hoặc cam đậm `#EA580C`).
  - Màu chữ: Chữ chính xám đậm `#1f2937`, chữ phụ `#4b5563`, `#6b7280`.
  - Nền Card/Badge: `#f8fafc`, `#fff7ed`, viền `#e2e8f0` hoặc `#fed7aa`.
- **Typography:** Font Google `'Inter', sans-serif`.
- **Quy tắc viết hoa (Sentence Case - Bắt buộc):** Chỉ viết hoa chữ cái đầu tiên của câu/tiêu đề, các từ phía sau đều viết chữ thường (ví dụ: *"Vốn hóa PNJ bốc hơi hơn 4.200 tỷ, bài học quản trị là gì?"*). Tuyệt đối KHÔNG viết hoa mọi chữ cái đầu (Title Case) và KHÔNG viết hoa toàn bộ (ALL CAPS), trừ từ viết tắt chuẩn (TeraX, AI, CEO, CFO, PNJ...).
- **Header & Footer bắt buộc cho cả 6 frames:**
  - **Header:** `.brand-badge` (chủ đề) + `.code-tag` (tag phân loại).
  - **Footer:** `.footer-brand` (`TeraX Insights` / `TeraX Platform`) + `.footer-page` (`01 / 06` $\to$ `06 / 06`).
- **Nút CTA ở Frame 6:** Đặt là `Tìm hiểu ngay` (tuyệt đối không dùng `terax.ai`).
- **Thẻ container gốc và Audio:**
  ```html
  <div id="root" data-composition-id="main" data-start="0" data-duration="..." data-width="1080" data-height="1920">
    <audio id="audio-01" class="clip" src="./public/audio/01.mp3" data-start="0.00" data-duration="..."></audio>
    ...
  ```
- **GSAP Registration:**
  ```js
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
  ```

### Bước 6: Đồng bộ Thời lượng chính xác (`update_durations.py`)
Chạy script `python update_durations.py` trong thư mục video để `ffprobe` tự động quét thời lượng thực tế của `01.mp3` $\to$ `06.mp3`, cập nhật chính xác `DURATIONS`, `START_TIMES`, `data-start`, `data-duration` và thuộc tính `data-duration` của `#root`.

### Bước 7: Kiểm tra Lỗi (`npx hyperframes check`)
Chạy lệnh `npx hyperframes check` trong thư mục video. Bắt buộc:
- **0 errors, 0 warnings** (pass contrast WCAG AA).

### Bước 8: Render Video (`npx hyperframes render`) & Ghép Outtro
1. Đảm bảo set `$env:TEMP="D:\dev-cache\temp"; $env:TMP="D:\dev-cache\temp"`.
2. Chạy `npx hyperframes render`. Video xuất ra tại `renders/{slug}_*.mp4`.
3. Ghép nối outtro:
   `python D:\vidv2\append_outtro.py "renders/{slug}_*.mp4"`

### Bước 9: Bàn giao thành phẩm vào `completed/`
1. Copy file video đã ghép outtro sang `D:\vidv2\completed\vid\{slug}.mp4`.
2. Di chuyển file bài viết `.html` sang `D:\vidv2\completed\html\{slug}.html`.

### Bước 10: Báo cáo kết quả
Thông báo ngắn gọn cho người dùng về video hoàn thành (tên video, thời lượng, dung lượng, đường dẫn đến completed).

---

## 🛠️ 5. XỬ LÝ LỖI PHỔ BIẾN
1. **Lỗi `media_missing_id`:** Luôn thêm `id="audio-01"`, `id="audio-02"`... vào các thẻ `<audio>`.
2. **Lỗi `out_of_bounds_clip` / Video bị cắt ngắn:** Luôn chạy `update_durations.py` để thuộc tính `data-duration` của `<div id="root">` cập nhật đúng tổng thời lượng của 6 audio clips.
3. **Lỗi thiếu ổ đĩa C:** Luôn set `$env:TEMP="D:\dev-cache\temp"; $env:TMP="D:\dev-cache\temp"` trước khi render.
