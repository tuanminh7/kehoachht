from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import google.generativeai as genai
import PyPDF2
import base64
import io
import re
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# debug
print(" Đang load file .env...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f" Đường dẫn .env: {env_path}")
print(f" File tồn tại: {os.path.exists(env_path)}")

load_dotenv(dotenv_path=env_path, verbose=True)

app = Flask(__name__)
CORS(app)

DATA_FILE = 'courses_data.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
LEARNING_DATA_FILE = 'learning_sessions.json'

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print(f" API Key loaded: {' Có' if GEMINI_API_KEY else ' Không'}")
if GEMINI_API_KEY:
    print(f" Độ dài key: {len(GEMINI_API_KEY)} ký tự")

if not GEMINI_API_KEY:
    print("\n HƯỚNG DẪN FIX:")
    print("1. Mở file .env")
    print("2. Thêm dòng: GEMINI_API_KEY=your_actual_key")
    print("3. Lưu và chạy lại\n")
    GEMINI_API_KEY = input("Hoặc nhập API key tạm thời ngay bây giờ: ").strip()
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY không được để trống!")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
genai.configure(api_key=GEMINI_API_KEY)

# route 3
#########################
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file):
    """Trích xuất text từ PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Lỗi đọc PDF: {e}")
        return None

def load_learning_sessions():
    """Load dữ liệu học tập"""
    if os.path.exists(LEARNING_DATA_FILE):
        try:
            with open(LEARNING_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"sessions": []}
    return {"sessions": []}

def save_learning_sessions(data):
    """Lưu dữ liệu học tập"""
    try:
        with open(LEARNING_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi lưu file: {e}")
        return False
######################################################################
def call_gemini_api(text_content, num_questions=10):
    """Gọi Gemini API để tóm tắt và tạo câu hỏi"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
Bạn là trợ lý giáo dục thông minh. Phân tích nội dung bài học sau và thực hiện 2 nhiệm vụ:

NHIỆM VỤ 1: Tóm tắt nội dung chính trong 300-500 từ, bao gồm:
- Các khái niệm quan trọng
- Kiến thức cốt lõi
- Ứng dụng thực tế

NHIỆM VỤ 2: Tạo {num_questions} câu hỏi trắc nghiệm ABCD với:
- Độ khó: trung bình đến khó
- 4 đáp án mỗi câu (A, B, C, D)
- Đáp án đúng rõ ràng
- Câu hỏi bao quát nội dung chính

NỘI DUNG BÀI HỌC:
{text_content[:8000]}

QUAN TRỌNG: 
1. Trả về ĐÚNG định dạng JSON (không thêm markdown, backticks hay text khác)
2. KHÔNG sử dụng ký tự ** hay *** trong nội dung
3. Sử dụng ngắt dòng \\n thay vì xuống dòng thật
4. Format JSON phải hợp lệ và có thể parse được

{{
  "summary": "Nội dung tóm tắt ở đây...",
  "questions": [
    {{
      "id": 1,
      "question": "Câu hỏi số 1?",
      "options": ["A. Đáp án A", "B. Đáp án B", "C. Đáp án C", "D. Đáp án D"],
      "correct": 0,
      "explanation": "Giải thích tại sao đáp án A đúng"
    }}
  ]
}}
"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        if result_text.startswith('```'):
            parts = result_text.split('```')
            if len(parts) >= 2:
                result_text = parts[1]
                # Loại bỏ 'json' ở đầu nếu có
                if result_text.strip().startswith('json'):
                    result_text = result_text.strip()[4:]
        
        # Loại bỏ các ký tự markdown còn sót lại
        result_text = re.sub(r'\*\*\*+', '', result_text)  # 
        result_text = re.sub(r'\*\*', '', result_text)     # Loại bỏ **
        result_text = re.sub(r'#{1,6}\s*', '', result_text)  # Loại bỏ # ## ###...
        result_text = result_text.strip()
        result = json.loads(result_text)
        if 'summary' in result:
            result['summary'] = clean_text(result['summary'])
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Lỗi parse JSON: {e}")
        print(f"Nội dung nhận được:\n{result_text[:500]}...")
        return None
    except Exception as e:
        print(f"Lỗi Gemini API: {e}")
        return None


def clean_text(text):
    """Làm sạch text từ markdown và format lại"""
    text = re.sub(r'\*\*\*+', '', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)  
    
    return text.strip()


def display_summary(summary):
    """Hiển thị summary với format đẹp"""
    formatted = summary.replace('\\n', '\n')
    return formatted

#

@app.route('/')
def home():
    """Trang chủ mới"""
    return render_template('base.html')

@app.route('/gpa-planner')
def gpa_planner():
    """Trang quản lý GPA (trang index.html cũ)"""
    return render_template('index.html')

@app.route('/learning')
def learning():
    """Trang AI Learning"""
    return render_template('learning.html')

@app.route('/learning-stats')
def learning_stats():
    """Trang thống kê học tập"""
    return render_template('learning_stats.html')



@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload PDF và xử lý bằng Gemini"""
    try:
        # Kiểm tra file
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'message': 'Không có file được upload'}), 400
        
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Chỉ chấp nhận file PDF'}), 400
        
       
        course_code = request.form.get('course_code', 'UNKNOWN')
        course_name = request.form.get('course_name', 'Unknown Course')
        num_questions = int(request.form.get('num_questions', 10))
        
       
        if num_questions < 5 or num_questions > 20:
            return jsonify({'success': False, 'message': 'Số câu hỏi phải từ 5-20'}), 400
        
       
        pdf_text = extract_text_from_pdf(file)
        if not pdf_text:
            return jsonify({'success': False, 'message': 'Không thể đọc nội dung PDF'}), 400
        
        if len(pdf_text) < 100:
            return jsonify({'success': False, 'message': 'Nội dung PDF quá ngắn'}), 400
        
      
        gemini_result = call_gemini_api(pdf_text, num_questions)
        if not gemini_result:
            return jsonify({'success': False, 'message': 'Lỗi xử lý AI, vui lòng thử lại'}), 500
        
        
        sessions_data = load_learning_sessions()
        new_session = {
            'id': len(sessions_data['sessions']) + 1,
            'course_code': course_code,
            'course_name': course_name,
            'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': gemini_result.get('summary', ''),
            'questions': gemini_result.get('questions', []),
            'num_questions': num_questions,
            'user_answers': None,
            'score': None,
            'submitted': False
        }
        
        sessions_data['sessions'].append(new_session)
        save_learning_sessions(sessions_data)
        
        return jsonify({
            'success': True,
            'session': new_session,
            'message': 'Xử lý thành công!'
        })
        
    except Exception as e:
        print(f"Lỗi upload: {e}")
        return jsonify({'success': False, 'message': f'Lỗi server: {str(e)}'}), 500

@app.route('/api/submit-test', methods=['POST'])
def submit_test():
    """Nộp bài test và chấm điểm"""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_answers = data.get('answers')  # List: [0, 2, 1, ...]
        
        if not session_id or user_answers is None:
            return jsonify({'success': False, 'message': 'Thiếu dữ liệu'}), 400
        
       
        sessions_data = load_learning_sessions()
        session = None
        
        for s in sessions_data['sessions']:
            if s['id'] == session_id:
                session = s
                break
        
        if not session:
            return jsonify({'success': False, 'message': 'Session không tồn tại'}), 404
        
       
        questions = session['questions']
        correct_count = 0
        results = []
        
        for i, question in enumerate(questions):
            user_ans = user_answers[i] if i < len(user_answers) else -1
            correct_ans = question['correct']
            is_correct = user_ans == correct_ans
            
            if is_correct:
                correct_count += 1
            
            results.append({
                'question_id': question['id'],
                'user_answer': user_ans,
                'correct_answer': correct_ans,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
       
        total_questions = len(questions)
        score = round((correct_count / total_questions) * 10, 2)
        
       
        session['user_answers'] = user_answers
        session['score'] = score
        session['correct_count'] = correct_count
        session['submitted'] = True
        session['submit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        save_learning_sessions(sessions_data)
        
        return jsonify({
            'success': True,
            'score': score,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'percentage': round((correct_count / total_questions) * 100, 1),
            'results': results
        })
        
    except Exception as e:
        print(f"Lỗi submit: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/learning-sessions', methods=['GET'])
def get_learning_sessions():
    """Lấy danh sách tất cả sessions"""
    try:
        sessions_data = load_learning_sessions()
        return jsonify(sessions_data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/learning-session/<int:session_id>', methods=['GET'])
def get_learning_session(session_id):
    """Lấy thông tin 1 session cụ thể"""
    try:
        sessions_data = load_learning_sessions()
        
        for session in sessions_data['sessions']:
            if session['id'] == session_id:
                return jsonify({'success': True, 'session': session})
        
        return jsonify({'success': False, 'message': 'Session không tồn tại'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/learning-stats', methods=['GET'])
def get_learning_stats():
    """Tính toán thống kê học tập"""
    try:
        sessions_data = load_learning_sessions()
        sessions = sessions_data['sessions']
        
        if not sessions:
            return jsonify({
                'total_sessions': 0,
                'completed_sessions': 0,
                'average_score': 0,
                'scores_over_time': [],
                'score_distribution': {'0-4': 0, '5-6': 0, '7-8': 0, '9-10': 0},
                'courses_count': {}
            })
        
       
        completed = [s for s in sessions if s.get('submitted', False)]
        total_score = sum([s['score'] for s in completed])
        avg_score = round(total_score / len(completed), 2) if completed else 0
        
       
        scores_over_time = [
            {
                'date': s.get('submit_time', s['upload_time']),
                'score': s.get('score', 0),
                'course': s['course_code']
            }
            for s in completed
        ]
        
       
        score_dist = {'0-4': 0, '5-6': 0, '7-8': 0, '9-10': 0}
        for s in completed:
            score = s['score']
            if score < 5:
                score_dist['0-4'] += 1
            elif score < 7:
                score_dist['5-6'] += 1
            elif score < 9:
                score_dist['7-8'] += 1
            else:
                score_dist['9-10'] += 1
        
       
        courses_count = {}
        for s in sessions:
            code = s['course_code']
            courses_count[code] = courses_count.get(code, 0) + 1
        
        return jsonify({
            'total_sessions': len(sessions),
            'completed_sessions': len(completed),
            'average_score': avg_score,
            'scores_over_time': scores_over_time,
            'score_distribution': score_dist,
            'courses_count': courses_count
        })
        
    except Exception as e:
        print(f"Lỗi stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Xóa 1 session"""
    try:
        sessions_data = load_learning_sessions()
        sessions_data['sessions'] = [s for s in sessions_data['sessions'] if s['id'] != session_id]
        save_learning_sessions(sessions_data)
        
        return jsonify({'success': True, 'message': 'Đã xóa session'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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
##############################################################################################3

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

#######
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