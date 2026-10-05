"""
append_outtro.py
────────────────
Tự động ghép nối video outtro mặc định (D:\\game\\outtro.mp4) vào cuối video được chỉ định.
- Sử dụng video outtro chuẩn hóa: D:\\vidv2\\assets\\outtro_1080x1920.mp4
- Ghép bằng ffmpeg concat cực nhanh (-c copy)
- Hỗ trợ gọi trực tiếp: python append_outtro.py <input_video> [output_video]
"""

import os
import sys
import tempfile
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

ORIGINAL_OUTTRO = r"D:\game\outtro.mp4"
STANDARDIZED_OUTTRO = r"D:\vidv2\assets\outtro_1080x1920.mp4"

def ensure_standardized_outtro():
    """Đảm bảo file outtro chuẩn hóa 1080x1920 @ 30fps 48kHz tồn tại."""
    if os.path.exists(STANDARDIZED_OUTTRO):
        return STANDARDIZED_OUTTRO

    if not os.path.exists(ORIGINAL_OUTTRO):
        print(f"❌ Không tìm thấy video outtro gốc tại {ORIGINAL_OUTTRO}")
        return None

    os.makedirs(os.path.dirname(STANDARDIZED_OUTTRO), exist_ok=True)
    print(f"🔄 Đang chuẩn hóa video outtro từ {ORIGINAL_OUTTRO}...")
    cmd = [
        "ffmpeg", "-y", "-i", ORIGINAL_OUTTRO,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        STANDARDIZED_OUTTRO
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Đã tạo video outtro chuẩn hóa: {STANDARDIZED_OUTTRO}")
    return STANDARDIZED_OUTTRO

def append_outtro(input_video_path, output_video_path=None):
    """
    Ghép video outtro vào cuối video input_video_path.
    Nếu output_video_path là None, sẽ ghi đè lên file input sau khi hoàn tất.
    """
    if not os.path.exists(input_video_path):
        print(f"❌ File không tồn tại: {input_video_path}")
        return False

    outtro_path = ensure_standardized_outtro()
    if not outtro_path:
        return False

    temp_output = None
    target_output = output_video_path or input_video_path

    if target_output == input_video_path:
        # Nếu ghi đè chính nó, cần xuất ra file tạm trước
        dir_name = os.path.dirname(input_video_path)
        base_name = os.path.basename(input_video_path)
        temp_output = os.path.join(dir_name, f"temp_with_outtro_{base_name}")
        final_dest = target_output
    else:
        temp_output = target_output
        final_dest = None

    # Tạo file danh sách cho concat demuxer
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        concat_list_path = f.name
        # Format ffmpeg concat yêu cầu dùng dấu gạch chéo xuôi
        input_norm = os.path.abspath(input_video_path).replace("\\", "/")
        outtro_norm = os.path.abspath(outtro_path).replace("\\", "/")
        f.write(f"file '{input_norm}'\n")
        f.write(f"file '{outtro_norm}'\n")

    try:
        print(f"🎬 Đang ghép outtro vào: {os.path.basename(input_video_path)}...")
        # Thử ghép nhanh bằng stream copy (-c copy)
        cmd_copy = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            temp_output
        ]
        res = subprocess.run(cmd_copy, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Nếu stream copy không thành công do codec khác biệt, fallback sang re-encode mượt mà
        if res.returncode != 0:
            print("⚠️ Stream copy không tương thích, chuyển sang ghép với filter_complex...")
            cmd_filter = [
                "ffmpeg", "-y",
                "-i", input_video_path,
                "-i", outtro_path,
                "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-ar", "48000",
                temp_output
            ]
            subprocess.run(cmd_filter, check=True)

        if final_dest:
            if os.path.exists(final_dest):
                os.remove(final_dest)
            os.rename(temp_output, final_dest)

        print(f"✅ Ghép outtro thành công: {target_output}")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi ghép outtro: {e}")
        if temp_output and os.path.exists(temp_output) and temp_output != target_output:
            try:
                os.remove(temp_output)
            except Exception:
                pass
        return False

    finally:
        if os.path.exists(concat_list_path):
            try:
                os.remove(concat_list_path)
            except Exception:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python append_outtro.py <input_video.mp4> [output_video.mp4]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    append_outtro(inp, out)
