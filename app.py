from flask import Flask, json, render_template, jsonify, request, redirect, url_for, flash
from datetime import datetime
from db_connector import get_db_connection
import mysql.connector
import traceback
import json

app = Flask(__name__)
app.config['DEBUG'] = True  # Bật chế độ debug
SETTINGS_FILE = 'settings.json'
# Đọc cài đặt từ file JSON
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "classSize": 40,
            "minAge": 15,
            "maxAge": 20
        }

# Sử dụng before_first_request để khởi tạo cài đặt
@app.before_request
def initialize_settings():
    global classSize, minAge, maxAge
    settings = load_settings()  # Đọc giá trị từ file JSON
    classSize = settings["classSize"]
    minAge = settings["minAge"]
    maxAge = settings["maxAge"]
    print(f"Settings loaded: {settings}")  # In ra để kiểm tra




@app.route('/update_setting', methods=['POST'])
def update_setting():
    global classSize, minAge, maxAge

    try:
        # Lấy dữ liệu từ yêu cầu POST
        data = request.get_json()
        name = data.get("name")
        
        # Cập nhật biến toàn cục
        if name == "classSize":
            classSize = int(data.get("value"))
        elif name == "ageSettings":
            # Nếu gửi cả minAge và maxAge
            minAge = int(data.get("minAge"))
            maxAge = int(data.get("maxAge"))
        else:
            return jsonify({"status": "error", "message": "Invalid setting name"}), 400

        # Lưu thay đổi vào file JSON
        save_settings({
            "classSize": classSize,
            "minAge": minAge,
            "maxAge": maxAge
        })

        return jsonify({"status": "success", "name": name, "minAge": minAge, "maxAge": maxAge})

    except Exception as e:
        print(f"Error updating setting: {e}")
        return jsonify({"status": "error", "message": "Failed to update setting"}), 500

    

@app.route('/get_settings', methods=['GET'])
def get_settings():
    return jsonify({
        "classSize": classSize,
        "minAge": minAge,
        "maxAge": maxAge
    })

def save_settings(data):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
        raise



@app.route('/submit', methods=['POST'])
def submit():
    print("POST request received at /submit")  # In ra khi nhận được yêu cầu
    # Lấy dữ liệu từ form
    ho_ten = request.form['ho_ten']
    gioi_tinh = request.form['gioi_tinh']
    ngay_sinh = request.form['ngay_sinh']
    dia_chi = request.form['dia_chi']
    so_dien_thoai = request.form['so_dien_thoai']
    email = request.form['email']
    
    if not ho_ten or not gioi_tinh or not ngay_sinh or not dia_chi or not so_dien_thoai or not email:
        return "Vui lòng điền đầy đủ thông tin!", 400
    # Chuyển đổi chuỗi ngày sinh thành đối tượng datetime
    try:
        ngay_sinh = datetime.strptime(ngay_sinh, '%Y-%m-%d')
    except ValueError:
        return "Ngày sinh không hợp lệ.", 400

    # Lấy ngày hiện tại
    ngay_hien_tai = datetime.now()

    # Tính tuổi
    tuoi = ngay_hien_tai.year - ngay_sinh.year - ((ngay_hien_tai.month, ngay_hien_tai.day) < (ngay_sinh.month, ngay_sinh.day))

    # Kiểm tra điều kiện tuổi
    if tuoi < minAge or tuoi > maxAge:
        return "Độ tuổi của học sinh không hợp lệ, vui lòng nhập lại", 400
    
    # Kết nối đến cơ sở dữ liệu
    conn = get_db_connection()
    cursor = conn.cursor()

    # Thực hiện câu lệnh INSERT
    query = "INSERT INTO hoc_sinh (FullName, GioiTinh, NgaySinh, DiaChi, SDT, Email) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (ho_ten, gioi_tinh, ngay_sinh, dia_chi, so_dien_thoai, email)
    try:
        cursor.execute(query, values)
        conn.commit()
        return '', 200  # Trả về mã trạng thái 200 nếu thành công
    except Exception as e:
        conn.rollback()
        return str(e), 500  # Trả về mã trạng thái 500 nếu có lỗi
    finally:
        cursor.close()
        conn.close()

    
#     1223234




# Route để tìm kiếm sinh viên
@app.route('/search_student', methods=['GET'])
def search_student():
    query = request.args.get('query')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if query:
        # Tìm kiếm dữ liệu trong cơ sở dữ liệu
        cursor.execute("""
            SELECT MaHS, FullName, GioiTinh, YEAR(NgaySinh) AS NamSinh, DiaChi
            FROM hoc_sinh
            WHERE FullName LIKE %s
        """, (f"%{query}%",))
        results = cursor.fetchall()
        
        # Trả về kết quả dưới dạng JSON
        return jsonify(results)
    else:
        return jsonify([])

@app.route('/add_class_list', methods=['POST'])
def add_class_list():
    # Lấy dữ liệu từ request
    data = request.get_json()
    TenLop = data['TenLop']
    MaHS_list = data['MaHS']  # Mảng mã học sinh đã chọn

    # Kết nối đến cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    # Mảng để lưu kết quả thông báo
    results = []

    try:
        # Duyệt qua từng mã học sinh trong mảng MaHS_list
        for MaHS in MaHS_list:
            # Gọi stored procedure AddStudentToClass với từng MaHS và TenLop
            cursor.callproc('AddStudentToClass', [MaHS, TenLop, classSize])

            # Lấy kết quả trả về từ stored procedure
            for result in cursor.stored_results():
                message = result.fetchone()[0]  # Giả sử message là cột đầu tiên trong kết quả
                results.append({'MaHS': MaHS, 'message': message})
                
        connection.commit()  # Commit các thay đổi vào cơ sở dữ liệu sau khi gọi stored procedure

        # Trả về kết quả với mã HTTP 200
        return jsonify(results), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()



    ### Point index xuất danh sách học sinh
@app.route('/get-students', methods=['GET'])
def get_students():
    # Lấy tham số từ request
    ten_lop = request.args.get('ten_lop')
    ten_mh = request.args.get('ten_mh')
    hoc_ky = request.args.get('hoc_ky')
    nam_hoc = request.args.get('nam_hoc')

    # Kiểm tra xem các tham số có hợp lệ không
    if not (ten_lop and ten_mh and hoc_ky and nam_hoc):
        return jsonify({'error': 'Thiếu tham số!'}), 400

    try:
        # Kết nối đến cơ sở dữ liệu
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Lấy kết quả dưới dạng dictionary

        # Gọi stored procedure 'TimThongTinHocSinh' với các tham số từ request
        cursor.callproc('TimThongTinHocSinh', [ten_lop, ten_mh, nam_hoc, hoc_ky])

        # Mảng để lưu kết quả thông báo
        students = []

        # Lấy kết quả trả về từ stored procedure
        for result in cursor.stored_results():
            # Mỗi result chứa dữ liệu trả về, như ma_hoc_sinh, ten_hoc_sinh
            rows = result.fetchall()

            # Duyệt qua từng học sinh trong kết quả trả về
            for index, row in enumerate(rows):
                # Đảm bảo các cột từ stored procedure khớp với tên trong mã
                student = {
                    "ma_hoc_sinh": row['ma_hoc_sinh'],
                    "stt": index + 1,  # STT là chỉ số trong danh sách
                    "ten_hoc_sinh": row['ten_hoc_sinh'],  # Tên học sinh
                    "diem_15_phut": None,  # Điểm 15 phút (có thể cần lấy thêm từ bảng điểm nếu có)
                    "diem_1_tiet": None,    # Điểm 1 tiết (có thể cần lấy thêm từ bảng điểm nếu có)
                    "diem_thi": None,       # Điểm thi (có thể cần lấy thêm từ bảng điểm nếu có)
                    
                }                

                
                students.append(student)

        # Kiểm tra nếu có học sinh
        if students:
            return jsonify(students)
        else:
            return jsonify({'message': 'Không có dữ liệu phù hợp.'}), 404

    except mysql.connector.Error as e:
        # Xử lý lỗi kết nối hoặc truy vấn
        print(f"Error: {e}")
        return jsonify({"error": "Không thể lấy dữ liệu. Vui lòng kiểm tra lại!"}), 500

    finally:
        # Đảm bảo đóng kết nối và con trỏ sau khi sử dụng
        cursor.close()
        connection.close()
   ######## Lưu điểm sau khi xuất danh sách học sinh
@app.route('/save-student-grades', methods=['POST'])
def save_student_grades():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        students = data.get('students')

        # Kết nối database và sử dụng cursor như dictionary
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Sử dụng MySQLCursorDict

        for student in students:
            ma_hoc_sinh = student.get('ma_hoc_sinh')
            diem_15_phut = student.get('diem_15_phut')
            diem_1_tiet = student.get('diem_1_tiet')
            diem_thi = student.get('diem_thi')
            ten_mh = student.get('ten_mh')
            hoc_ky = student.get('hoc_ky')

            # Kiểm tra bảng điểm học sinh đã có chưa
            cursor.execute("""
                SELECT MaBD FROM bang_diem 
                WHERE ma_hoc_sinh = %s AND HocKy = %s
            """, (ma_hoc_sinh, hoc_ky))
            ma_bang_diem = cursor.fetchone()

            # Nếu không có bảng điểm, tạo bảng điểm mới
            if not ma_bang_diem:
                cursor.execute("""
                    INSERT INTO bang_diem (ma_hoc_sinh, HocKy) 
                    VALUES (%s, %s)
                """, (ma_hoc_sinh, hoc_ky))
                connection.commit()  # Commit để tạo bảng điểm mới

                # Lấy mã bảng điểm mới
                cursor.execute("""
                    SELECT MaBD FROM bang_diem 
                    WHERE ma_hoc_sinh = %s AND HocKy = %s
                """, (ma_hoc_sinh, hoc_ky))
                ma_bang_diem = cursor.fetchone()  # Lấy lại MaBD của bảng điểm mới
                ma_bang_diem = ma_bang_diem['MaBD']  # Truy cập theo tên cột

            else:
                ma_bang_diem = ma_bang_diem['MaBD']  # Truy cập MaBD từ tuple dưới dạng dictionary

            # Lấy mã môn học từ tên môn học
            cursor.execute("""
                SELECT MaMH FROM mon_hoc WHERE TenMH = %s
            """, (ten_mh,))
            ma_mon_hoc = cursor.fetchone()
            if ma_mon_hoc:
                ma_mon_hoc = ma_mon_hoc['MaMH']
            else:
                flash(f"Môn học {ten_mh} không tồn tại.", "error")
                return jsonify({'error': f"Môn học {ten_mh} không tồn tại!"}), 400

            # Kiểm tra số lượng điểm 15 phút cho môn học này
            if diem_15_phut:
                cursor.execute("""
                    SELECT COUNT(*) FROM bang_diem_chi_tiet 
                    WHERE ma_bang_diem = %s AND LoaiDiem = '15 phút' AND ma_mon_hoc = %s
                """, (ma_bang_diem, ma_mon_hoc))
                existing_diem_15_phut = cursor.fetchone()['COUNT(*)']
                if existing_diem_15_phut >= 5:
                    return jsonify({'error': f"Học sinh đã có đủ 5 giá trị điểm 15 phút cho môn học {ten_mh}!"}), 400

            # Kiểm tra số lượng điểm 1 tiết cho môn học này
            if diem_1_tiet:
                cursor.execute("""
                    SELECT COUNT(*) FROM bang_diem_chi_tiet 
                    WHERE ma_bang_diem = %s AND LoaiDiem = '1 tiết' AND ma_mon_hoc = %s
                """, (ma_bang_diem, ma_mon_hoc))
                existing_diem_1_tiet = cursor.fetchone()['COUNT(*)']
                if existing_diem_1_tiet >= 3:
                    return jsonify({'error': f"Học sinh đã có đủ 3 giá trị điểm 1 tiết cho môn học {ten_mh}!"}), 400

            # Kiểm tra số lượng điểm thi cho môn học này
            if diem_thi:
                cursor.execute("""
                    SELECT COUNT(*) FROM bang_diem_chi_tiet 
                    WHERE ma_bang_diem = %s AND LoaiDiem = 'thi' AND ma_mon_hoc = %s
                """, (ma_bang_diem, ma_mon_hoc))
                existing_diem_thi = cursor.fetchone()['COUNT(*)']
                if existing_diem_thi >= 1:
                    return jsonify({'error': f"Học sinh đã có đủ 1 giá trị điểm thi cho môn học {ten_mh}!"}), 400

            # Thêm điểm vào bảng bang_diem_chi_tiet cho môn học này
            if diem_15_phut:
                cursor.execute("""
                    INSERT INTO bang_diem_chi_tiet (ma_bang_diem, LoaiDiem, SoDiem, ma_mon_hoc)
                    VALUES (%s, '15 phút', %s, %s)
                """, (ma_bang_diem, diem_15_phut, ma_mon_hoc))
            if diem_1_tiet:
                cursor.execute("""
                    INSERT INTO bang_diem_chi_tiet (ma_bang_diem, LoaiDiem, SoDiem, ma_mon_hoc)
                    VALUES (%s, '1 tiết', %s, %s)
                """, (ma_bang_diem, diem_1_tiet, ma_mon_hoc))
            if diem_thi:
                cursor.execute("""
                    INSERT INTO bang_diem_chi_tiet (ma_bang_diem, LoaiDiem, SoDiem, ma_mon_hoc)
                    VALUES (%s, 'thi', %s, %s)
                """, (ma_bang_diem, diem_thi, ma_mon_hoc))

            connection.commit()  # Commit để lưu điểm

        return jsonify({'message': 'Điểm đã được lưu thành công!'}), 200

    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
        return jsonify({'error': 'Đã có lỗi xảy ra khi lưu điểm!'}), 500

    finally:
        cursor.close()
        connection.close()




    
@app.route('/show_summary_table', methods=['POST'])
def show_summary_table():
    # Lấy dữ liệu từ request
    data = request.get_json()
    mon = data.get('mon')
    hoc_ky = data.get('hoc_ky')
    nam_hoc = data.get('nam_hoc')
    print("mon-hocky-namhoc: ", mon, hoc_ky, nam_hoc)
    # Kết nối đến cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    results = []
    try:
        cursor.callproc('CalculatePassingStudents', [mon, hoc_ky, nam_hoc])
        for result in cursor.stored_results():
            results.extend(result.fetchall())

        print('results summary_table: ', results)
        return jsonify(results), 200

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/class')
def classList():
    return render_template('class.html')

@app.route('/point')
def Point():
    return render_template('point.html')

@app.route('/statistics')
def Statistics():
    return render_template('statistics.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')
    
#####
if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=True)