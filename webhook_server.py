"""
webhook_server.py
─────────────────
Nhận POST từ n8n → ghi HTML vào thư mục pending/
Antigravity IDE sẽ tự động pick up và xử lý theo cron.

POST http://localhost:8000/
Body: JSON { "content": "<html>...", "slug": "ten-video" }
   hoặc: Text/HTML thô
"""

import http.server
import socketserver
import json
import os
import re
import sys
import time
import unicodedata
from dotenv import load_dotenv

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

PORT       = 8000
PENDING_DIR = r"d:\vidv2\pending"


def make_slug(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:50] or f"video_{int(time.time())}"


def extract_slug_from_html(html: str) -> str:
    match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', html, re.IGNORECASE | re.DOTALL)
    if match:
        title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        return make_slug(title)
    return f"video_{int(time.time())}"


class WebhookHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        pending = os.listdir(PENDING_DIR) if os.path.exists(PENDING_DIR) else []
        self.wfile.write(f"🎬 Video Builder Webhook — port {PORT}\nPending: {pending}".encode())

    def do_POST(self):
        try:
            length   = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(length)

            raw_html    = ""
            project_slug = None

            try:
                data        = json.loads(raw_data.decode('utf-8'))
                raw_html    = data.get("content") or data.get("html") or data.get("body") or json.dumps(data, ensure_ascii=False)
                project_slug = data.get("slug") or data.get("project_slug")
            except (json.JSONDecodeError, UnicodeDecodeError):
                raw_html    = raw_data.decode('utf-8', errors='replace')

            if not project_slug:
                project_slug = extract_slug_from_html(raw_html)

            # ─── Ghi vào pending/ ───
            os.makedirs(PENDING_DIR, exist_ok=True)
            pending_file = os.path.join(PENDING_DIR, f"{project_slug}.html")
            with open(pending_file, "w", encoding="utf-8") as f:
                f.write(raw_html)

            print(f"[Webhook] ✅ Đã ghi: {pending_file} ({len(raw_html)} ký tự) - Sẵn sàng cho Antigravity Agent xử lý")

            # ─── Phản hồi ngay lập tức ───
            body = json.dumps({
                "status"       : "received",
                "project_slug" : project_slug,
                "pending_file" : pending_file,
                "message"      : "Đã nhận file và AI Builder đang tự động tạo video dưới nền."
            }, ensure_ascii=False).encode('utf-8')

            self.send_response(202)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            print(f"[Webhook] ❌ LỖI: {e}")
            err = json.dumps({"status": "error", "message": str(e)}).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(err)


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads     = True
    allow_reuse_address = True


if __name__ == '__main__':
    os.makedirs(PENDING_DIR, exist_ok=True)
    httpd = ThreadingHTTPServer(('', PORT), WebhookHandler)
    print(f"🚀 Webhook Server: http://localhost:{PORT}")
    print(f"📁 Pending dir   : {PENDING_DIR}")
    print(f"   n8n POST JSON : {{\"content\": \"<html>...\", \"slug\": \"ten-video\"}}")
    print("Ctrl+C để dừng\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
