"""
sync_to_postgres.py
───────────────────
Tự động đồng bộ các video thành phẩm từ completed/vid sang PostgreSQL (DB: terax).
- Quét các video trong D:\\vidv2\\completed\\vid
- Trích xuất metadata (thời lượng, kích thước, fps, độ phân giải qua ffprobe)
- Lưu thông tin và dữ liệu nhị phân (BYTEA) vào bảng `videos`
- Chế độ chạy 1 lần: python sync_to_postgres.py --once
- Chế độ chạy chu kỳ liên tục: python sync_to_postgres.py --loop --interval 30
"""

import os
import sys
import time
import argparse
import subprocess
import json
import psycopg2
from psycopg2 import sql

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# Cấu hình mặc định
VIDEOS_DIR = r"D:\vidv2\completed\vid"

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": int(os.environ.get("PGPORT", 5432)),
    "database": os.environ.get("PGDATABASE", "terax"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "")
}

def get_connection():
    """Tạo kết nối tới cơ sở dữ liệu PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Khởi tạo bảng `videos` nếu chưa tồn tại."""
    query = """
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE NOT NULL,
        file_path TEXT NOT NULL,
        file_size_mb NUMERIC(10, 2),
        duration_sec NUMERIC(8, 2),
        fps INT DEFAULT 30,
        width INT DEFAULT 1080,
        height INT DEFAULT 1920,
        video_data BYTEA,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_videos_slug ON videos(slug);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
    print("✅ Đã khởi tạo schema bảng `videos` trên PostgreSQL (DB: terax).")

def get_video_metadata(file_path):
    """Sử dụng ffprobe để lấy thông tin chi tiết về video."""
    duration = 0.0
    width = 1080
    height = 1920
    fps = 30

    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(res.stdout)

        if "format" in data and "duration" in data["format"]:
            duration = round(float(data["format"]["duration"]), 2)

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                width = int(stream.get("width", 1080))
                height = int(stream.get("height", 1920))
                r_frame_rate = stream.get("r_frame_rate", "30/1")
                if "/" in r_frame_rate:
                    num, den = r_frame_rate.split("/")
                    fps = round(float(num) / float(den))
                break
    except Exception as e:
        print(f"⚠️ Không thể đọc metadata bằng ffprobe cho {file_path}: {e}")

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps
    }

def sync_single_video(file_path, store_binary=True):
    """
    Đồng bộ một file video vào PostgreSQL.
    Trả về True nếu đồng bộ mới, False nếu đã tồn tại.
    """
    if not os.path.exists(file_path):
        return False

    filename = os.path.basename(file_path)
    slug = os.path.splitext(filename)[0]
    title = slug.replace("-", " ").title()

    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Kiểm tra xem video đã được lưu vào DB chưa
            cur.execute("SELECT id FROM videos WHERE slug = %s", (slug,))
            if cur.fetchone() is not None:
                return False  # Đã có trong DB

            print(f"🔄 Đang đồng bộ video mới: {filename} ({file_size_mb} MB)...")
            metadata = get_video_metadata(file_path)

            video_bytes = None
            if store_binary:
                with open(file_path, "rb") as f:
                    video_bytes = f.read()

            cur.execute(
                """
                INSERT INTO videos (
                    title, slug, file_path, file_size_mb, duration_sec,
                    fps, width, height, video_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO NOTHING;
                """,
                (
                    title, slug, os.path.abspath(file_path), file_size_mb,
                    metadata["duration"], metadata["fps"], metadata["width"],
                    metadata["height"], psycopg2.Binary(video_bytes) if video_bytes else None
                )
            )
        conn.commit()

    print(f"✨ [HOÀN TẤT ĐỒNG BỘ] {slug} -> DB terax | {file_size_mb} MB | {metadata['duration']}s | {metadata['width']}x{metadata['height']}")
    return True

def scan_and_sync(watch_dir=VIDEOS_DIR, store_binary=True):
    """Quét toàn bộ thư mục và đồng bộ các video chưa có trong DB theo thứ tự mới nhất."""
    if not os.path.exists(watch_dir):
        print(f"⚠️ Thư mục không tồn tại: {watch_dir}")
        return 0

    files = [
        f for f in os.listdir(watch_dir)
        if f.lower().endswith(".mp4") and not f.startswith(".")
    ]
    if not files:
        return 0

    # Sắp xếp file theo thời gian chỉnh sửa mới nhất lên đầu
    files_with_mtime = [
        (f, os.path.getmtime(os.path.join(watch_dir, f)))
        for f in files
    ]
    files_with_mtime.sort(key=lambda x: x[1], reverse=True)

    synced_count = 0
    for filename, _ in files_with_mtime:
        full_path = os.path.join(watch_dir, filename)
        if sync_single_video(full_path, store_binary=store_binary):
            synced_count += 1

    return synced_count

def run_loop(watch_dir=VIDEOS_DIR, interval=30, store_binary=True):
    """Chạy vòng lặp quét định kỳ theo chu kỳ interval giây."""
    print(f"👀 Bắt đầu giám sát thư mục: {watch_dir}")
    print(f"⏱️ Chu kỳ quét: mỗi {interval} giây")
    init_db()

    while True:
        try:
            count = scan_and_sync(watch_dir, store_binary=store_binary)
            if count > 0:
                print(f"🎉 Đã đồng bộ thành công {count} video mới vào PostgreSQL.")
        except Exception as e:
            print(f"⚠️ Lỗi trong chu kỳ quét: {e}")
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Đồng bộ video hoàn thành sang PostgreSQL.")
    parser.add_argument("--once", action="store_true", help="Chạy quét 1 lần rồi thoát.")
    parser.add_argument("--loop", action="store_true", help="Chạy chu kỳ liên tục.")
    parser.add_argument("--interval", type=int, default=30, help="Chu kỳ quét (giây). Mặc định: 30s.")
    parser.add_argument("--no-binary", action="store_true", help="Chỉ lưu metadata, không lưu dữ liệu binary (BYTEA).")
    parser.add_argument("--dir", type=str, default=VIDEOS_DIR, help="Thư mục video cần quét.")

    args = parser.parse_args()
    store_binary = not args.no_binary

    if args.loop:
        run_loop(watch_dir=args.dir, interval=args.interval, store_binary=store_binary)
    else:
        init_db()
        count = scan_and_sync(watch_dir=args.dir, store_binary=store_binary)
        print(f"🏁 Đã hoàn thành quét. Số video mới được đồng bộ: {count}")

if __name__ == "__main__":
    main()
