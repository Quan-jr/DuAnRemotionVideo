import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import generate_tts_vieneu

texts = [
    "Doanh nghiệp của bạn đang lưu trữ tài liệu, hay vô tình xây dựng những nghĩa địa dữ liệu số đắt đỏ?",
    "Quản trị ngữ cảnh tài liệu là việc lưu trữ hồ sơ gắn liền với các mối liên kết nghiệp vụ như mã thiết bị, đơn hàng và hợp đồng, biến dữ liệu chết thành tài sản sống.",
    "Ba định danh kết nối then chốt gồm có: mã vật tư đồng bộ chuỗi cung ứng, mã lệnh bảo trì kiểm soát chi phí thực tế, và mã thiết bị theo dõi toàn diện vòng đời tài sản.",
    "Khi tài liệu có ngữ cảnh, hiệu suất nhân sự tăng tới chín mươi mốt phần trăm, giảm mười lăm phẩy một phần trăm tồn kho dư thừa và loại bỏ hoàn toàn rủi ro thanh toán trùng lặp.",
    "Ba bước hành động cụ thể: một là chuẩn hóa hệ thống mã định danh, hai là thiết lập cơ chế đối chiếu ba lớp tự động, và ba là số hóa quy trình phê duyệt đa chiều.",
    "Xóa bỏ ốc đảo thông tin và làm chủ tri thức doanh nghiệp với Te ra X. Tìm hiểu ngay hôm nay!"
]

output_dir = r"D:\vidv2\hyperframes\videos\quan-tri-ngu-canh-tai-lieu-la-gi-va-vi-sao-doanh-nghiep-can-quan-tam\public\audio"
generate_tts_vieneu.generate_audio_frames(output_dir, texts, speed=1.09)
