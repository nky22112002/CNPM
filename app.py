from flask import Flask, json, render_template, jsonify, request, redirect, url_for, flash
from datetime import datetime
from db_connector import get_db_connection
import mysql.connector
import traceback
import json

app = Flask(__name__)
app.config['DEBUG'] = True  # Bật chế độ debug
classSize = 40


# def fetch_data_from_db():
#     try:
#         # Tạo kết nối
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)

#         # Thực hiện truy vấn
#         query = "SELECT * FROM hoc_sinh"
#         cursor.execute(query)

#         # Lấy dữ liệu từ cơ sở dữ liệu
#         results = cursor.fetchall()

#         # Ghi dữ liệu vào file hocsinh.json
#         with open('data/hocsinh.json', 'w', encoding='utf-8') as f:
#             json.dump(results, f, ensure_ascii=False, indent=4)

#         print("Dữ liệu đã được ghi vào hocsinh.json")

#     except mysql.connector.Error as err:
#         print(f"Lỗi: {err}")

#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()

# # Chạy hàm để lấy dữ liệu
# fetch_data_from_db()



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
    if tuoi < 15 or tuoi > 20:
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