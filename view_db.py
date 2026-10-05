"""
view_db.py
──────────
Xem nhanh danh sách video đã lưu trong PostgreSQL (DB: terax)
Cách chạy: python view_db.py
"""

import sys
import psycopg2

sys.stdout.reconfigure(encoding='utf-8')

def view_videos():
    try:
        conn = psycopg2.connect(dbname="terax", user="postgres", password="", host="localhost", port=5432)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, title, slug, file_size_mb, duration_sec, width, height, length(video_data), synced_at
            FROM videos
            ORDER BY id ASC;
        """)
        rows = cur.fetchall()
        
        if not rows:
            print("📭 Chưa có video nào trong bảng `videos`.")
            return

        print("\n" + "="*110)
        print(f"🎬 DANH SÁCH VIDEO TRONG POSTGRESQL (DATABASE: terax) — TỔNG: {len(rows)} VIDEO")
        print("="*110)
        header = f"{'ID':<4} | {'Slug / Tên video':<45} | {'Size':<8} | {'Thời lượng':<10} | {'Độ phân giải':<12} | {'Dung lượng BYTEA':<18}"
        print(header)
        print("-" * 110)
        
        for r in rows:
            vid_id = r[0]
            slug = r[2] if len(r[2]) <= 44 else r[2][:41] + "..."
            size = f"{r[3]} MB"
            duration = f"{r[4]}s"
            res = f"{r[5]}x{r[6]}"
            bytea_size = f"{r[7]:,} bytes" if r[7] else "0 bytes"
            print(f"{vid_id:<4} | {slug:<45} | {size:<8} | {duration:<10} | {res:<12} | {bytea_size:<18}")
        
        print("="*110 + "\n")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi khi đọc database: {e}")

if __name__ == "__main__":
    view_videos()
