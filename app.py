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


#Thêm học sinh mới
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

# Hàm tính NamHoc
def get_namhoc():
    current_year = datetime.now().year
    return f"{current_year}-{current_year + 1}"

@app.route('/get_class', methods=['POST'])
def get_class():
    # Lấy NamHoc tự động
    nam_hoc = get_namhoc()
    
    # Lấy dữ liệu từ frontend
    ten_lop = request.json.get('lop', None)
    
    if not ten_lop:
        return jsonify({'error': 'Tên lớp không hợp lệ'}), 400
    
    
    # Kết nối đến cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()    
    # Thực thi câu lệnh SQL
    query = """
        SELECT hs.FullName, hs.GioiTinh, YEAR(hs.NgaySinh) AS NamSinh, hs.DiaChi
        FROM tham_gia_lop tgl
        JOIN ds_lop dl ON tgl.ma_lop = dl.MaLop
        JOIN hoc_sinh hs ON tgl.ma_hoc_sinh = hs.MaHS
        WHERE NamHoc = %s AND dl.TenLop = %s
    """
    cursor.execute(query, (nam_hoc, ten_lop))
    results = cursor.fetchall()
    
    # Đóng kết nối
    cursor.close()
    connection.close()
    # Chuyển kết quả thành JSON
    data = [
        {'FullName': row[0], 'GioiTinh': row[1], 'NamSinh': row[2], 'DiaChi': row[3]}
        for row in results
    ]

    print("results: ", results  )
    # Chuẩn bị dữ liệu trả về
    return jsonify({
        'lop': ten_lop,
        'si_so': len(results),
        'data': results
    })

    ### Point index xuất danh sách học sinh
@app.route('/get-students', methods=['GET'])
def get_students():
    ten_lop = request.args.get('ten_lop')
    ten_mh = request.args.get('ten_mh')
    hoc_ky = request.args.get('hoc_ky')
    nam_hoc = request.args.get('nam_hoc')

    if not (ten_lop and ten_mh and hoc_ky and nam_hoc):
        return jsonify({'error': 'Thiếu tham số!'}), 400
    # Kiểm tra học kỳ hợp lệ (chỉ có thể là 1 hoặc 2)
    if hoc_ky not in ['1', '2']:
        return jsonify({'error': 'Học kỳ không hợp lệ! Chỉ có thể là học kỳ 1 hoặc 2.'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Lấy danh sách lớp dựa trên TenLop
        cursor.execute("SELECT MaLop FROM ds_lop WHERE TenLop = %s", (ten_lop,))
        ma_lop = cursor.fetchone()
        if not ma_lop:
            return jsonify({'error': 'Không tìm thấy lớp!'}), 404

        ma_lop = ma_lop['MaLop']

        # Lấy danh sách học sinh tham gia lớp
        cursor.execute("""
            SELECT hs.MaHS, hs.FullName, hs.NgaySinh, hs.SDT, hs.GioiTinh, hs.DiaChi, hs.Email
            FROM hoc_sinh hs
            JOIN tham_gia_lop tgl ON hs.MaHS = tgl.ma_hoc_sinh
            WHERE tgl.ma_lop = %s AND tgl.NamHoc = %s
        """, (ma_lop, nam_hoc))
        students = cursor.fetchall()

        if not students:
            return jsonify({'message': 'Không tìm thấy học sinh trong lớp!'}), 404

        updated_students = []

        for student in students:
            ma_hs = student['MaHS']

            # Kiểm tra học sinh đã có học kỳ trong bảng bang_diem chưa
            cursor.execute("""
                SELECT COUNT(*) AS count 
                FROM bang_diem 
                WHERE ma_hoc_sinh = %s AND HocKy = %s
            """, (ma_hs, hoc_ky))
            count = cursor.fetchone()['count']

            # Nếu chưa có, thêm học kỳ mới vào bảng bang_diem
            if count == 0:
                cursor.execute("""
                    INSERT INTO bang_diem (ma_hoc_sinh, HocKy)
                    VALUES (%s, %s)
                """, (ma_hs, hoc_ky))
                connection.commit()

            # Lấy điểm chi tiết cho học sinh này
            cursor.execute("""
                SELECT bdc.LoaiDiem, bdc.SoDiem, mh.TenMH 
                FROM bang_diem_chi_tiet bdc
                JOIN bang_diem bd ON bdc.ma_bang_diem = bd.MaBD
                JOIN mon_hoc mh ON bdc.ma_mon_hoc = mh.MaMH
                WHERE bd.ma_hoc_sinh = %s AND bd.HocKy = %s AND bdc.ma_mon_hoc = (
                    SELECT MaMH FROM mon_hoc WHERE TenMH = %s
                )
            """, (ma_hs, hoc_ky, ten_mh))
            diem_chi_tiet = cursor.fetchall()

            # Chuẩn bị dữ liệu học sinh
            student_data = {
                "ma_hoc_sinh": ma_hs,
                "ten_hoc_sinh": student['FullName'],
                "ngay_sinh": student['NgaySinh'],
                "sdt": student['SDT'],
                "gioi_tinh": student['GioiTinh'],
                "dia_chi": student['DiaChi'],
                "email": student['Email'],
                "diem_chi_tiet": diem_chi_tiet or []
            }
            updated_students.append(student_data)

        return jsonify(updated_students)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Lỗi cơ sở dữ liệu!"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
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

            # Lấy tên học sinh từ mã học sinh
            cursor.execute("""
                SELECT FullName FROM hoc_sinh WHERE MaHS = %s
            """, (ma_hoc_sinh,))
            student_name = cursor.fetchone()
            
            if student_name:
                student_name = student_name['FullName']
            else:
                student_name = "Học sinh không tồn tại"
            
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
                    return jsonify({'error': f"Học sinh {student_name} đã có đủ 5 giá trị điểm 15 phút cho môn học {ten_mh}!"}), 400

            # Kiểm tra số lượng điểm 1 tiết cho môn học này
            if diem_1_tiet:
                cursor.execute("""
                    SELECT COUNT(*) FROM bang_diem_chi_tiet 
                    WHERE ma_bang_diem = %s AND LoaiDiem = '1 tiết' AND ma_mon_hoc = %s
                """, (ma_bang_diem, ma_mon_hoc))
                existing_diem_1_tiet = cursor.fetchone()['COUNT(*)']
                if existing_diem_1_tiet >= 3:
                    return jsonify({'error': f"Học sinh {student_name} đã có đủ 3 giá trị điểm 1 tiết cho môn học {ten_mh}!"}), 400

            # Kiểm tra số lượng điểm thi cho môn học này
            if diem_thi:
                cursor.execute("""
                    SELECT COUNT(*) FROM bang_diem_chi_tiet 
                    WHERE ma_bang_diem = %s AND LoaiDiem = 'thi' AND ma_mon_hoc = %s
                """, (ma_bang_diem, ma_mon_hoc))
                existing_diem_thi = cursor.fetchone()['COUNT(*)']
                if existing_diem_thi >= 1:
                    return jsonify({'error': f"Học sinh {student_name} đã có đủ 1 giá trị điểm thi cho môn học {ten_mh}!"}), 400

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
@app.route('/get-avg-scores', methods=['GET'])
def get_avg_scores():
    ten_lop = request.args.get('ten_lop')
    ten_mh = request.args.get('ten_mh')
    nam_hoc = request.args.get('nam_hoc')

    if not (ten_lop and ten_mh and nam_hoc):
        return jsonify({'error': 'Thiếu tham số!'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Lấy mã lớp từ tên lớp
        cursor.execute("SELECT MaLop FROM ds_lop WHERE TenLop = %s", (ten_lop,))
        ma_lop = cursor.fetchone()
        if not ma_lop:
            return jsonify({'error': 'Không tìm thấy lớp!'}), 404

        ma_lop = ma_lop['MaLop']

        # Lấy danh sách học sinh trong lớp đó
        cursor.execute("""
            SELECT hs.MaHS, hs.FullName
            FROM hoc_sinh hs
            JOIN tham_gia_lop tgl ON hs.MaHS = tgl.ma_hoc_sinh
            WHERE tgl.ma_lop = %s AND tgl.NamHoc = %s
        """, (ma_lop, nam_hoc))
        students = cursor.fetchall()

        if not students:
            return jsonify({'message': 'Không tìm thấy học sinh trong lớp!'}), 404

        avg_scores = []

        for student in students:
            ma_hs = student['MaHS']
            full_name = student['FullName']

            # Lấy điểm của học sinh cho môn học đó ở cả 2 học kỳ
            cursor.execute("""
                SELECT 
                    AVG(CASE WHEN HocKy = 1 THEN (bdc.SoDiem) ELSE NULL END) AS avg_hk1,
                    AVG(CASE WHEN HocKy = 2 THEN (bdc.SoDiem) ELSE NULL END) AS avg_hk2
                FROM bang_diem_chi_tiet bdc
                JOIN bang_diem bd ON bdc.ma_bang_diem = bd.MaBD
                JOIN mon_hoc mh ON bdc.ma_mon_hoc = mh.MaMH
                WHERE bd.ma_hoc_sinh = %s AND mh.TenMH = %s
            """, (ma_hs, ten_mh))

            avg_result = cursor.fetchone()

            # Tính toán điểm trung bình cho học kỳ 1 và học kỳ 2
            avg_hk1 = avg_result['avg_hk1'] if avg_result['avg_hk1'] is not None else 0
            avg_hk2 = avg_result['avg_hk2'] if avg_result['avg_hk2'] is not None else 0

            avg_scores.append({
                'ma_hoc_sinh': ma_hs,
                'ten_hoc_sinh': full_name,
                'diem_hk1': round(avg_hk1, 2),  # Làm tròn đến 2 chữ số thập phân
                'diem_hk2': round(avg_hk2, 2)   # Làm tròn đến 2 chữ số thập phân
            })

        return jsonify(avg_scores)

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Lỗi cơ sở dữ liệu!"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
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
## Thêm môn học mới
@app.route('/subjects', methods=['POST'])
def add_subject():
    print("POST request received at /subjects")  # Debug log

    # Lấy dữ liệu từ request
    data = request.get_json()
    ma_mon_hoc = data.get('MaMH')
    ten_mon_hoc = data.get('TenMH')

    # Kiểm tra dữ liệu đầu vào
    if not ma_mon_hoc or not ten_mon_hoc:
        return "Vui lòng cung cấp đầy đủ thông tin!", 400

    # Kết nối tới cơ sở dữ liệu
    conn = get_db_connection()
    cursor = conn.cursor()

    # Câu lệnh INSERT
    query = "INSERT INTO mon_hoc (MaMH, TenMH) VALUES (%s, %s)"
    values = (ma_mon_hoc, ten_mon_hoc)

    try:
        cursor.execute(query, values)
        conn.commit()
        return "Thêm môn học thành công!", 200
    except Exception as e:
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        conn.close()
#### XÓa môn học
@app.route('/subjects/<int:maMH>', methods=['DELETE'])
def delete_subject(maMH):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kiểm tra xem môn học có trong bảng bang_diem_chi_tiet không
    check_query = "SELECT COUNT(*) FROM bang_diem_chi_tiet WHERE ma_mon_hoc = %s"
    cursor.execute(check_query, (maMH,))
    result = cursor.fetchone()

    # Nếu môn học đã có điểm, không cho phép xóa
    if result[0] > 0:
        # Lấy tên môn học từ bảng mon_hoc
        name_query = "SELECT TenMH FROM mon_hoc WHERE MaMH = %s"
        cursor.execute(name_query, (maMH,))
        subject_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({"message": f"Không thể xóa môn học '{subject_name}' vì đã có điểm!"}), 400  # Trả về thông báo cụ thể về môn học

    # Nếu môn học không có điểm, tiến hành xóa
    delete_query = "DELETE FROM mon_hoc WHERE MaMH = %s"
    cursor.execute(delete_query, (maMH,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Môn học đã được xóa thành công!"}), 200

##### Cập nhập môn học
@app.route('/subjects', methods=['PUT'])
def update_subject():
    print("PUT request received at /subjects")  # Debug log

    # Lấy dữ liệu từ request
    data = request.get_json()
    ma_mon_hoc = data.get('MaMH')
    ten_mon_hoc = data.get('TenMH')

    # Kiểm tra dữ liệu đầu vào
    if not ma_mon_hoc or not ten_mon_hoc:
        return "Vui lòng cung cấp đầy đủ thông tin!", 400

    # Kết nối tới cơ sở dữ liệu
    conn = get_db_connection()
    cursor = conn.cursor()

    # Câu lệnh UPDATE
    query = "UPDATE mon_hoc SET TenMH = %s WHERE MaMH = %s"
    values = (ten_mon_hoc, ma_mon_hoc)

    try:
        cursor.execute(query, values)
        if cursor.rowcount == 0:
            return "Môn học không tồn tại!", 404
        conn.commit()
        return "Cập nhật môn học thành công!", 200
    except Exception as e:
        conn.rollback()
        return str(e), 500
    finally:
        cursor.close()
        conn.close()
######## Tìm kiếm môn học
@app.route('/subjects/search', methods=['GET'])
def search_subject():
    keyword = request.args.get('keyword', '')
    
    if not keyword:
    
        return jsonify([]), 400  # Trả về mảng rỗng nếu không có từ khóa tìm kiếm

    # Kết nối cơ sở dữ liệu và thực hiện truy vấn
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT MaMH, TenMH FROM mon_hoc WHERE TenMH LIKE %s"
    cursor.execute(query, ('%' + keyword + '%',))  # Sử dụng LIKE để tìm kiếm tên môn học

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Trả về kết quả tìm kiếm dưới dạng JSON
    return jsonify([{"MaMH": row[0], "TenMH": row[1]} for row in results])






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