"""
generate_tts_vieneu.py
-----------------------
Module tạo giọng đọc Tiếng Việt cho 6 Frames video sử dụng AI VieNeu-TTS (hỗ trợ Voice Cloning).
- Nạp trực tiếp ref_audio để nhân bản chính xác giọng nói từ file mẫu.
- Tốc độ đọc mặc định: speed = 1.09 (vừa phải, rõ chữ, truyền cảm hứng và tự nhiên).
- update_durations.py sẽ tự động đồng bộ 100% hiệu ứng GSAP khớp từng mili-giây với tốc độ mới.
"""

import os
import sys
import re
import argparse
import subprocess
import numpy as np
import soundfile as sf

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

os.environ["HF_HOME"] = r"D:\dev-cache\huggingface"
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from vieneu import Vieneu
except ImportError:
    print("❌ Chưa tìm thấy thư viện `vieneu`. Hãy chạy bằng python trong virtualenv D:\\vidv2\\venv:")
    print(r"D:\vidv2\venv\Scripts\python generate_tts_vieneu.py")
    sys.exit(1)

def find_sample_voice(custom_path=None):
    """Tìm file giọng mẫu để nhân bản."""
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    sample_dir = r"D:\vidv2\voice_samples"
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            if f.lower().endswith((".wav", ".mp3")):
                return os.path.join(sample_dir, f)
    return None

def convert_to_mp3(input_wav, output_mp3, speed=1.09):
    """Chuyển đổi file WAV sang MP3 bằng ffmpeg kết hợp điều chỉnh tốc độ nói tự nhiên."""
    try:
        filter_str = f"atempo={speed}"
        subprocess.run([
            "ffmpeg", "-y", "-i", input_wav,
            "-filter:a", filter_str,
            "-codec:a", "libmp3lame", "-b:a", "192k",
            output_mp3
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(input_wav) and os.path.abspath(input_wav) != os.path.abspath(output_mp3):
            os.remove(input_wav)
    except Exception as e:
        pass

def split_text_into_chunks(text, max_words=12):
    """Chia văn bản dài thành các mệnh đề ngắn để tránh tràn bộ nhớ decoder."""
    raw_sentences = re.split(r'([.?!:])', text)
    sentences = []
    temp = ""
    for part in raw_sentences:
        if part in [".", "?", "!", ":"]:
            temp += part
            if temp.strip():
                sentences.append(temp.strip())
            temp = ""
        else:
            temp += part
    if temp.strip():
        sentences.append(temp.strip())
    
    final_chunks = []
    for s in sentences:
        words = s.split()
        if len(words) <= max_words:
            final_chunks.append(s)
        else:
            sub_parts = re.split(r'(,)', s)
            sub_temp = ""
            for p in sub_parts:
                if p == ",":
                    sub_temp += p
                    if sub_temp.strip():
                        final_chunks.append(sub_temp.strip())
                    sub_temp = ""
                else:
                    sub_temp += p
            if sub_temp.strip():
                final_chunks.append(sub_temp.strip())
    
    return [c for c in final_chunks if c.strip()]

def generate_audio_frames(output_dir, frames_text, voice_sample=None, preset_voice="Mai Anh", speed=1.09):
    """
    Tạo 6 file audio 01.mp3 -> 06.mp3 cho 6 frames với tốc độ chuẩn (mặc định speed=1.09).
    """
    os.makedirs(output_dir, exist_ok=True)
    print("🚀 Đang khởi tạo mô hình AI VieNeu-TTS...")
    tts = Vieneu()
    
    sample_path = find_sample_voice(voice_sample)
    
    if sample_path:
        print(f"🎙️ Nhân bản (Clone) chính xác từ file mẫu: {sample_path}")
        infer_kwargs = {"ref_audio": sample_path}
    else:
        print(f"ℹ️ Không có file mẫu, sử dụng giọng đọc có sẵn: {preset_voice}")
        infer_kwargs = {"voice": preset_voice}
    
    sample_rate = getattr(tts, 'sample_rate', 48000)
    silence_gap = np.zeros(int(sample_rate * 0.08), dtype=np.float32)

    print(f"🔊 Bắt đầu tạo 6 file audio (Tốc độ chuẩn x{speed}) vào: {output_dir}")
    for idx, full_text in enumerate(frames_text, start=1):
        filename_base = f"{idx:02d}"
        wav_path = os.path.join(output_dir, f"{filename_base}.wav")
        mp3_path = os.path.join(output_dir, f"{filename_base}.mp3")
        
        chunks = split_text_into_chunks(full_text)
        print(f"  ▶ Frame {idx}/6 ({len(chunks)} mệnh đề): {full_text[:50]}...")
        
        audio_segments = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            seg = tts.infer(text=chunk.strip(), **infer_kwargs)
            audio_segments.append(seg)
            audio_segments.append(silence_gap)
        
        if audio_segments:
            combined_audio = np.concatenate(audio_segments)
            tts.save(combined_audio, wav_path)
            convert_to_mp3(wav_path, mp3_path, speed=speed)
    
    print("🎉 Hoàn tất tạo toàn bộ 6 file âm thanh với tốc độ 1.09!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo 6 files audio cho video bằng VieNeu-TTS")
    parser.add_argument("--output-dir", required=True, help="Thư mục xuất audio")
    parser.add_argument("--sample", default=None, help="Đường dẫn file audio mẫu")
    parser.add_argument("--preset", default="Mai Anh", help="Tên giọng mặc định")
    parser.add_argument("--speed", type=float, default=1.09, help="Tốc độ nói (vd: 1.09)")
    args = parser.parse_args()
    
    test_texts = [
        "Vốn hóa PNJ bốc hơi hơn 4.200 tỷ đồng sau chuỗi bốn phiên giảm sàn liên tiếp.",
        "Đâu là bài học quản trị đằng sau biến động này?",
        "Vốn hóa là chỉ báo thị trường phản ánh kỳ vọng của nhà đầu tư.",
        "Tài chính cần theo dõi dòng tiền và kế hoạch vốn chặt chẽ.",
        "Ba bước hành động cho doanh nghiệp để ứng phó biến động.",
        "Tìm hiểu ngay giải pháp tối ưu quản trị cùng TeraX!"
    ]
    generate_audio_frames(args.output_dir, test_texts, voice_sample=args.sample, preset_voice=args.preset, speed=args.speed)
