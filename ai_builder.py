import os
import sys
import time
import asyncio
import subprocess
from dotenv import load_dotenv

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# CẤU HÌNH
# ==========================================
VIDEOS_DIR = r"d:\vidv2\hyperframes\videos"
TTS_VOICE  = "vi-VN-HoaiMyNeural"

# System prompt: hướng dẫn Antigravity agent làm đúng chuẩn project
AGENT_SYSTEM_PROMPT = f"""
Bạn là một AI chuyên tạo video ngắn dạng 9:16 (1080x1920px) bằng Hyperframes.
Workspace tại: {VIDEOS_DIR}

Khi nhận nội dung HTML từ người dùng, bạn phải hoàn thành TOÀN BỘ các bước sau:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 1 — Phân tích & lên kịch bản
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Đọc HTML, xác định chủ đề, key messages
- Chia thành 5–8 cảnh (scenes) có logic rõ ràng:
  Hook → Khái niệm → Số liệu → Phân tích → Ứng dụng → Kết luận/CTA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 2 — Tạo thư mục project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Đặt tên project bằng slug tiếng Việt không dấu (ví dụ: trai-phieu-chinh-phu)
- Tạo cấu trúc:
  {VIDEOS_DIR}/[slug]/
  ├── compositions/frames/   ← frame HTML files
  ├── public/audio/          ← file mp3
  ├── index.html
  ├── package.json
  ├── meta.json
  ├── generate_tts.py
  └── update_durations.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 3 — Thiết kế từng frame HTML
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mỗi frame phải có:
- Background: WHITE (#ffffff) với accent màu cam #F97316 (TeraX brand)
- Font: 'Inter', sans-serif — title 70–96px, body 36–44px
- Layout: flex column, căn giữa, padding 60–80px, max-width 920px
- Thẻ <audio class="clip" data-start="0" data-duration="PLACEHOLDER" data-track-index="2" src="../../public/audio/[id].mp3">
- GSAP animation: fade-in, slide-in, scale theo thứ tự hợp lý
- KHÔNG dùng dark background trừ khi nội dung đặc biệt cần

Ví dụ cấu trúc frame:
<div data-composition-id="01-hook" class="frame-content" style="width:100%;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#ffffff;padding:80px 60px;">
  <h1 class="title" style="font-family:'Inter',sans-serif;font-size:96px;font-weight:800;color:#1f2937;opacity:0;">Tiêu đề</h1>
  <audio class="clip" data-start="0" data-duration="PLACEHOLDER" data-track-index="2" src="../../public/audio/01.mp3"></audio>
</div>
<script>
  (function() {{
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline();
    tl.to(".title", {{ opacity:1, y:0, duration:0.8, ease:"power3.out" }}, 0.5);
    window.__timelines["01-hook"] = tl;
  }})();
</script>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 4 — Tạo generate_tts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Script dùng edge-tts voice {TTS_VOICE}, viết text ra file tạm rồi xóa sau.
Có retry tối đa 5 lần nếu lỗi NoAudioReceived.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 5 — Tạo update_durations.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Script dùng ffprobe để đo duration thực tế, cập nhật data-duration trong frame HTML
và rebuild index.html với timing chính xác.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 6 — Tạo index.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 1080x1920, background #ffffff
- GSAP CDN từ jsdelivr
- Mỗi scene: data-start (ước tính), data-duration, data-track-index xen kẽ 0/1
- Transitions: fade out + fade in giữa các cảnh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 7 — Tạo package.json + meta.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
package.json dùng hyperframes@0.8.89

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 8 — Chạy generate_tts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chạy trong project_dir, chờ hoàn tất.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 9 — Chạy update_durations.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chạy trong project_dir, chờ hoàn tất.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BƯỚC 10 — Render video
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chạy: npm run render  (trong project_dir)
Video output tại: [project_dir]/renders/*.mp4

Sau khi xong, in ra đường dẫn file MP4 đã render.
"""


async def _run_agent(raw_html: str, project_slug: str = None):
    """Gọi Antigravity Agent để tạo toàn bộ video project."""
    from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

    config = LocalAgentConfig(
        system_instructions=AGENT_SYSTEM_PROMPT,
        capabilities=CapabilitiesConfig(),  # cho phép write file + run command
    )

    # Xây dựng prompt gửi đến agent
    slug_hint = f"\nTên project (slug): {project_slug}" if project_slug else ""
    user_prompt = f"""Hãy tạo video 9:16 từ nội dung HTML bên dưới.{slug_hint}
Thực hiện đầy đủ 10 bước như hướng dẫn trong system prompt.

===== NỘI DUNG HTML =====
{raw_html}
=========================
"""

    print("=" * 60)
    print("🤖 Antigravity Agent đang xử lý...")
    print("=" * 60)

    async with Agent(config) as agent:
        response = await agent.chat(user_prompt)

        # Stream output từ agent
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()

    print("\n" + "=" * 60)
    print("✅ Agent hoàn tất!")
    print("=" * 60)


def build_video_from_html(raw_html: str, project_slug: str = None):
    """Entry point đồng bộ — gọi từ webhook_server hoặc CLI."""
    try:
        asyncio.run(_run_agent(raw_html, project_slug))
    except ImportError:
        print("❌ LỖI: Chưa cài google-antigravity SDK.")
        print("   Chạy: pip install google-antigravity")
    except Exception as e:
        print(f"❌ LỖI khi chạy agent: {e}")
        raise


if __name__ == "__main__":
    # Test trực tiếp từ command line
    import argparse

    parser = argparse.ArgumentParser(description="Tạo video từ HTML bằng Antigravity Agent")
    parser.add_argument("--file", help="Đường dẫn file HTML/TXT đầu vào")
    parser.add_argument("--slug", help="Tên project (slug, không dấu)")
    args = parser.parse_args()

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            html_content = f.read()
        build_video_from_html(html_content, args.slug)
    elif os.path.exists("webhook_data.txt"):
        with open("webhook_data.txt", "r", encoding="utf-8") as f:
            html_content = f.read()
        build_video_from_html(html_content)
    else:
        print("Dùng: python ai_builder.py --file content.html --slug ten-video")
        print("Hoặc tạo file webhook_data.txt rồi chạy lại.")
