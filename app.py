from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)


DATA_FILE = 'courses_data.json'


def create_course(id, code, name, credits, target, min_gpa, mustA, group):
    return {
        'id': id,
        'code': code,
        'name': name,
        'credits': credits,
        'target': target,
        'min': min_gpa,
        'mustA': mustA,
        'completed': False,
        'actualGPA': None,
        'group': group
    }

# Dữ liệu mặc định
def get_default_courses():
    return [
        
        create_course(1, 'POS104', 'Triết học Mác - Lênin', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(2, 'POS105', 'Kinh tế chính trị Mác - Lênin', 2, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(3, 'POS106', 'Chủ nghĩa xã hội khoa học', 2, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(4, 'POS107', 'Lịch sử Đảng Cộng sản Việt Nam', 2, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(5, 'POS103', 'Tư tưởng Hồ Chí Minh', 2, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(6, 'ENC120', 'Anh ngữ 1', 3, 3.0, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(7, 'ENC121', 'Anh ngữ 2', 3, 3.0, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(8, 'ENC122', 'Anh ngữ 3', 3, 3.0, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(9, 'ENC123', 'Anh ngữ 4', 3, 3.0, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(10, 'ENS192', 'Phát triển bền vững', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(11, 'LAW106', 'Pháp luật đại cương', 3, 2.5, 2.5, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(12, 'SKL115', 'Tư duy thiết kế dự án', 3, 4.0, 3.7, True, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(13, 'SKL116', 'Đổi mới sáng tạo và tư duy khởi nghiệp', 3, 4.0, 3.7, True, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(14, 'COS673', 'Nhập môn ngành Khoa học máy tính', 3, 4.0, 3.7, True, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(15, 'MAT101', 'Đại số tuyến tính', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(16, 'MAT118', 'Giải tích', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(17, 'MAT105', 'Xác suất thống kê', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        create_course(18, 'MAT104', 'Toán rời rạc', 3, 3.5, 3.0, False, 'I. KIẾN THỨC GIÁO DỤC ĐẠI CƯƠNG (50 TC)'),
        
        # II. KIẾN THỨC CHUYÊN NGHIỆP - BẮT BUỘC
        create_course(19, 'CMP1074', 'Cơ sở lập trình', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(20, 'CMP164', 'Kỹ thuật lập trình', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(21, 'CMP167', 'Lập trình hướng đối tượng', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(22, 'COS135', 'Nhập môn cơ sở dữ liệu', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(23, 'COS1002', 'Các hệ quản trị cơ sở dữ liệu', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(24, 'COS120', 'Cấu trúc dữ liệu và giải thuật', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(25, 'COS129', 'Điện toán đám mây', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(26, 'AIT1002', 'Nghệ thuật lập trình với hỗ trợ AI', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(27, 'AIT103', 'Lập trình cho trí tuệ nhân tạo', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(28, 'CMP177', 'Lập trình trên thiết bị di động', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(29, 'COS158', 'Lập trình DevOps', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(30, 'CMP172', 'Mạng máy tính', 3, 3.0, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(31, 'AIT1001', 'Cơ sở trí tuệ nhân tạo', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(32, 'CMP174', 'Bảo mật thông tin', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(33, 'AIT104', 'Máy học', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(34, 'CMP170', 'Lập trình trên môi trường Windows', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(35, 'CMP101', 'Công nghệ phần mềm', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(36, 'CMP1047', 'Phân tích và trực quan dữ liệu', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(37, 'AIT108', 'Xử lý ảnh và ứng dụng', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(38, 'COS159', 'Đồ họa ứng dụng trong KHMT', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(39, 'COS1010', 'Cơ sở công nghệ chuỗi khối', 3, 3.5, 3.0, False, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        
        # Thực hành
        create_course(40, 'COS321', 'TH Cấu trúc dữ liệu và giải thuật', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(41, 'COS323', 'TH Cơ sở dữ liệu', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(42, 'CMP3075', 'TH Cơ sở lập trình', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(43, 'CMP365', 'TH Kỹ thuật lập trình', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(44, 'CMP368', 'TH Lập trình hướng đối tượng', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(45, 'COS360', 'TH Lập trình DevOps', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(46, 'CMP3014', 'TH Lý thuyết đồ thị', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(47, 'CMP373', 'TH Mạng máy tính', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(48, 'CMP5089', 'Thực tập điện toán đám mây', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(49, 'AIT305', 'TH Lập trình cho AI', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(50, 'AIT3007', 'TH Nghệ thuật lập trình với AI', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(51, 'CMP371', 'TH Lập trình trên Windows', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(52, 'COS324', 'TH Quản trị cơ sở dữ liệu', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(53, 'CMP3055', 'TH Phân tích và trực quan dữ liệu', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(54, 'AIT306', 'TH Máy học', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(55, 'AIT307', 'TH Xử lý ảnh và ứng dụng', 1, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(56, 'CMP1020', 'Học sâu', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(57, 'COS5011', 'Thực tập cơ sở ngành KHMT', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(58, 'COS464', 'Đồ án chuyên ngành KHMT', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        create_course(59, 'COS570', 'Thực tập tốt nghiệp KHMT', 3, 4.0, 3.5, True, 'II.1. KIẾN THỨC BẮT BUỘC (91 TC)'),
        
        # II.2. TỰ CHỌN
        create_course(60, 'AIT109', 'Xử lý ngôn ngữ tự nhiên và ứng dụng', 3, 3.5, 3.0, False, 'II.2. KIẾN THỨC TỰ CHỌN (9 TC)'),
        create_course(61, 'CMP1049', 'Khai thác dữ liệu', 3, 3.5, 3.0, False, 'II.2. KIẾN THỨC TỰ CHỌN (9 TC)'),
        create_course(62, 'AIT123', 'Mô hình ngôn ngữ lớn', 3, 4.0, 3.5, True, 'II.2. KIẾN THỨC TỰ CHỌN (9 TC)')
    ]

#
def load_courses():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f" Đã load dữ liệu từ {DATA_FILE}")
                return data
        except Exception as e:
            print(f" Lỗi đọc file JSON: {e}")
            print(" Sử dụng dữ liệu mặc định")
            return get_default_courses()
    else:
        print(f" File {DATA_FILE} chưa tồn tại, sử dụng dữ liệu mặc định")
        return get_default_courses()


def save_courses(courses_data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(courses_data, f, ensure_ascii=False, indent=2)
        print(f" Đã lưu dữ liệu vào {DATA_FILE}")
        return True
    except Exception as e:
        print(f" Lỗi lưu file JSON: {e}")
        return False


courses_data = load_courses()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify(courses_data)


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    for course in courses_data:
        if course['id'] == course_id:
            if 'target' in data:
                course['target'] = float(data['target'])
            if 'completed' in data:
                course['completed'] = bool(data['completed'])
            if 'actualGPA' in data:
                course['actualGPA'] = float(data['actualGPA']) if data['actualGPA'] is not None else None
            return jsonify({'success': True, 'course': course})
    return jsonify({'success': False, 'message': 'Course not found'}), 404


@app.route('/api/save', methods=['POST'])
def save_all():
    success = save_courses(courses_data)
    if success:
        return jsonify({
            'success': True, 
            'message': 'Đã lưu dữ liệu vào file JSON',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({'success': False, 'message': 'Lỗi khi lưu dữ liệu'}), 500


@app.route('/api/calculate-gpa', methods=['GET'])
def calculate_gpa():
    total_points = 0
    total_credits = 0
    must_a_count = 0
    

    for course in courses_data:
        total_points += course['target'] * course['credits']
        total_credits += course['credits']
        if course['mustA']:
            must_a_count += 1
    
    overall_gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0
    

    actual_points = 0
    actual_credits = 0
    completed_count = 0
    not_as_planned_count = 0
    
    for course in courses_data:
        if course['completed'] and course['actualGPA'] is not None:
            actual_points += course['actualGPA'] * course['credits']
            actual_credits += course['credits']
            completed_count += 1
            

            if course['actualGPA'] < course['target']:
                not_as_planned_count += 1
    
    actual_gpa = round(actual_points / actual_credits, 2) if actual_credits > 0 else 0
    
    return jsonify({
        'overall_gpa': overall_gpa,
        'total_credits': total_credits,
        'total_points': round(total_points, 2),
        'must_a_count': must_a_count,
        'target_reached': overall_gpa >= 3.6,
        'actual_gpa': actual_gpa,
        'actual_credits': actual_credits,
        'completed_count': completed_count,
        'not_as_planned_count': not_as_planned_count
    })


@app.route('/api/reset', methods=['POST'])
def reset_courses():
    global courses_data
    courses_data = get_default_courses()
    

    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            print(f" Đã xóa file {DATA_FILE}")
        except Exception as e:
            print(f" Lỗi xóa file: {e}")
    
    return jsonify({'success': True, 'message': 'Đã reset về dữ liệu mặc định'})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = {
        'dai_cuong': {'credits': 0, 'gpa': 0, 'points': 0},
        'bat_buoc': {'credits': 0, 'gpa': 0, 'points': 0},
        'tu_chon': {'credits': 0, 'gpa': 0, 'points': 0}
    }
    
    for course in courses_data:
        points = course['target'] * course['credits']
        
        if 'ĐẠI CƯƠNG' in course['group']:
            stats['dai_cuong']['credits'] += course['credits']
            stats['dai_cuong']['points'] += points
        elif 'BẮT BUỘC' in course['group']:
            stats['bat_buoc']['credits'] += course['credits']
            stats['bat_buoc']['points'] += points
        else:
            stats['tu_chon']['credits'] += course['credits']
            stats['tu_chon']['points'] += points
    

    for key in stats:
        if stats[key]['credits'] > 0:
            stats[key]['gpa'] = round(stats[key]['points'] / stats[key]['credits'], 2)
    
    return jsonify(stats)

if __name__ == '__main__':
    print("="*60)
    print(" KẾ HOẠCH GPA - KHOA HỌC MÁY TÍNH 2025 ")
    print("="*60)
    print(" Server đang chạy tại: http://localhost:5000")
    print(" Mở trình duyệt và truy cập: http://localhost:5000")
    print(f" Dữ liệu được lưu trong file: {DATA_FILE}")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)