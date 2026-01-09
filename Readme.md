# 🌸 Hệ thống Quản lý Kế hoạch GPA - Khoa học máy tính 🌸

## 📋 Mô tả
Web application màu hồng dễ thương giúp sinh viên ngành Khoa học máy tính quản lý và tính toán GPA của 150 tín chỉ trong chương trình học.

## ✨ Tính năng
- ✅ Hiển thị tất cả các môn học (150 tín chỉ)
- ✅ Điều chỉnh GPA dự tính cho từng môn học
- ✅ Nhập điểm thực tế khi hoàn thành môn
- ✅ Theo dõi trạng thái: ✓ Đạt kế hoạch / ✗ Chưa đạt kế hoạch / - Chưa hoàn thành
- ✅ Tự động tính toán GPA tổng thể (dự tính & thực tế)
- ✅ Hiển thị trạng thái đạt/không đạt mục tiêu (GPA ≥ 3.6)
- ✅ **Lưu dữ liệu vào file JSON** - Dữ liệu không mất khi tắt server!
- ✅ Reset về giá trị mặc định
- ✅ Export dữ liệu ra CSV
- ✅ Copy dữ liệu để dán vào Google Sheets

## 💾 Lưu trữ dữ liệu
Dữ liệu được lưu trong file **`courses_data.json`** tại thư mục gốc của project:
- **Tự động load** khi khởi động server
- **Ghi đè hoàn toàn** khi bấm "Lưu thay đổi"
- **Xóa file** khi bấm "Reset về mặc định"

## 🛠️ Cài đặt

### Yêu cầu
- Python 3.7+
- Trình duyệt web hiện đại (Chrome, Firefox, Edge, Safari)

### Các bước cài đặt

#### 1. Cài đặt các thư viện Python
```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install Flask==3.0.0
pip install flask-cors==4.0.0
```

#### 2. Cấu trúc thư mục
```
TUANPRO/
├── templates/
│   └── index.html        # Frontend
├── app.py                # Backend Flask
├── requirements.txt      # Dependencies
├── courses_data.json     # Dữ liệu (tự động tạo khi lưu)
└── README.md            # File này
```

#### 3. Chạy Backend Server
```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

Bạn sẽ thấy:
```
============================================================
🌸 KẾ HOẠCH GPA - KHOA HỌC MÁY TÍNH 2025 🌸
============================================================
🚀 Server đang chạy tại: http://localhost:5000
📊 Mở trình duyệt và truy cập: http://localhost:5000
💾 Dữ liệu được lưu trong file: courses_data.json
============================================================
```

#### 4. Mở Trình duyệt
Truy cập: `http://localhost:5000`

## 📖 Hướng dẫn sử dụng

### 1. Nhập kế hoạch GPA
- Nhập GPA dự tính vào cột "GPA dự tính" cho mỗi môn
- Đây là mục tiêu bạn muốn đạt được

### 2. Cập nhật điểm thực tế
- Khi thi xong môn, nhập điểm thực tế vào cột "Điểm thực tế"
- Hệ thống tự động:
  - Đánh dấu môn đã hoàn thành
  - So sánh với kế hoạch
  - Hiển thị trạng thái: ✓ Đạt KH hoặc ✗ Chưa đạt KH

### 3. Lưu thay đổi
- Nhấn nút **"💾 Lưu thay đổi"**
- Dữ liệu sẽ được ghi vào file `courses_data.json`
- Dữ liệu sẽ được giữ lại khi tắt/bật server

### 4. Theo dõi tiến độ
- **GPA Dự tính**: GPA nếu đạt theo kế hoạch
- **GPA Thực tế**: GPA từ các môn đã hoàn thành
- **Đã hoàn thành**: X/62 môn
- **Trạng thái**: ✅ ĐẠT hoặc ⚠️ Thiếu X điểm

### 5. Reset về mặc định
- Nhấn nút **"↺ Reset về mặc định"**
- Tất cả dữ liệu về giá trị ban đầu
- File JSON sẽ bị xóa

### 6. Export dữ liệu
- **Tải CSV**: Nhấn **"📥 Tải xuống CSV"**
- **Copy**: Nhấn **"📋 Copy để dán"** → Paste vào Google Sheets (Ctrl+V)

## 🎨 Giao diện

Giao diện màu **hồng pastel** dễ thương với:
- Background gradient hồng
- Header màu hồng đậm
- Buttons màu hồng với hover effect
- Emoji hoa sakura 🌸
- Stat cards với số liệu màu hồng

## 🎯 API Endpoints

### GET /
Serve trang web frontend

### GET /api/courses
Lấy danh sách tất cả các môn học
```json
[
  {
    "id": 1,
    "code": "POS104",
    "name": "Triết học Mác - Lênin",
    "credits": 3,
    "target": 3.5,
    "min": 3.0,
    "mustA": false,
    "completed": false,
    "actualGPA": null,
    "group": "I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)"
  }
]
```

### PUT /api/courses/:id
Cập nhật thông tin môn học (trong memory)
```json
{
  "target": 3.8,
  "completed": true,
  "actualGPA": 3.5
}
```

### POST /api/save
**Lưu toàn bộ dữ liệu vào file JSON**
```json
Response:
{
  "success": true,
  "message": "Đã lưu dữ liệu vào file JSON",
  "timestamp": "2025-01-09 15:30:45"
}
```

### GET /api/calculate-gpa
Tính toán GPA tổng thể
```json
{
  "overall_gpa": 3.62,
  "total_credits": 150,
  "actual_gpa": 3.55,
  "actual_credits": 45,
  "completed_count": 15,
  "not_as_planned_count": 2,
  "target_reached": true
}
```

### POST /api/reset
Reset về dữ liệu mặc định và xóa file JSON

### GET /api/statistics
Lấy thống kê theo nhóm môn

## 📊 Cấu trúc dữ liệu

### File courses_data.json
```json
[
  {
    "id": 1,
    "code": "POS104",
    "name": "Triết học Mác - Lênin",
    "credits": 3,
    "target": 3.5,
    "min": 3.0,
    "mustA": false,
    "completed": false,
    "actualGPA": null,
    "group": "I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)"
  },
  ...
]
```

### Các trường quan trọng
- `target`: GPA dự tính (có thể chỉnh sửa)
- `actualGPA`: GPA thực tế (null nếu chưa thi)
- `completed`: Đã hoàn thành hay chưa
- `mustA`: Môn bắt buộc đạt A (38 môn)
- `credits`: Số tín chỉ

## 🔧 Troubleshooting

### Lỗi: Cannot connect to server
- Kiểm tra backend đã chạy: `python app.py`
- Kiểm tra port 5000 có bị chiếm không

### Lỗi: File JSON không lưu
- Kiểm tra quyền ghi file trong thư mục
- Xem log trong terminal khi chạy server

### Dữ liệu bị mất
- Kiểm tra file `courses_data.json` có tồn tại không
- Nếu không có → Server sẽ dùng dữ liệu mặc định
- Nhớ bấm "Lưu thay đổi" sau khi chỉnh sửa!

### Muốn backup dữ liệu
- Copy file `courses_data.json` ra nơi khác
- Hoặc dùng nút "Export CSV"

## 🚀 Tính năng có thể thêm

- [ ] Biểu đồ trực quan (Chart.js)
- [ ] Lọc và tìm kiếm môn học
- [ ] Kế hoạch theo học kỳ
- [ ] Gợi ý thông minh
- [ ] Dark mode 🌙
- [ ] Mobile responsive
- [ ] Multiple users (login system)
- [ ] Export PDF report

## 💡 Tips

1. **Backup thường xuyên**: Copy file `courses_data.json` để backup
2. **Sử dụng CSV**: Export CSV để mở trong Excel/Google Sheets
3. **Theo dõi tiến độ**: Cập nhật điểm ngay sau khi thi để theo dõi GPA thực tế
4. **Cảnh báo sớm**: Nếu có môn "✗ Chưa đạt KH", hãy cố gắng cải thiện môn tiếp theo

## 📝 License
MIT License

## 👨‍💻 Tác giả
Hệ thống quản lý kế hoạch GPA cho sinh viên Khoa học máy tính
Phiên bản: 2.0 - JSON Storage Edition 🌸