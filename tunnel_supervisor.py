import subprocess
import time
import urllib.request
import urllib.error
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SUBDOMAIN = "terax-vidv2-webhook"
PORT = 8000
URL = f"https://{SUBDOMAIN}.loca.lt"

def start_tunnel():
    print(f"🚀 [Supervisor] Khởi động Localtunnel: {URL} (Port {PORT})...")
    # Using shell=True for windows npx command execution
    proc = subprocess.Popen(
        f"npx localtunnel --port {PORT} --subdomain {SUBDOMAIN}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return proc

def ping_tunnel():
    req = urllib.request.Request(
        URL,
        headers={
            'Bypass-Tunnel-Reminder': 'true',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as res:
            return res.status == 200
    except Exception as e:
        print(f"⚠️ [Supervisor] Ping lỗi: {e}")
        return False

def main():
    while True:
        proc = start_tunnel()
        time.sleep(6)  # Give localtunnel time to connect
        consecutive_failures = 0

        while True:
            # Check if subprocess exited unexpectedly
            if proc.poll() is not None:
                print("❌ [Supervisor] Tiến trình localtunnel đã thoát đột ngột. Khởi động lại...")
                break

            # Heartbeat ping
            ok = ping_tunnel()
            if ok:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(f"⚠️ [Supervisor] Cảnh báo rớt kết nối ({consecutive_failures}/2)")

            if consecutive_failures >= 2:
                print("🔄 [Supervisor] Mất kết nối liên tiếp 2 lần. Đang tự động kết nối lại tunnel...")
                try:
                    subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
                break

            time.sleep(15)  # Keepalive interval

        time.sleep(2)

if __name__ == "__main__":
    main()
