from flask import Flask, json, render_template, jsonify, request, redirect, url_for, flash
from datetime import datetime
from db_connector import get_db_connection
import mysql.connector

app = Flask(__name__)
app.config['DEBUG'] = True  # Bật chế độ debug

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'student_management'
}
def fetch_data_from_db():
    try:
        # Tạo kết nối
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Thực hiện truy vấn
        query = "SELECT * FROM hoc_sinh"
        cursor.execute(query)

        # Lấy dữ liệu từ cơ sở dữ liệu
        results = cursor.fetchall()

        # Ghi dữ liệu vào file hocsinh.json
        with open('data/hocsinh.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print("Dữ liệu đã được ghi vào hocsinh.json")

    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Chạy hàm để lấy dữ liệu
#fetch_data_from_db()



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
        ngay_sinh = datetime.strptime(ngay_sinh, '%d/%m/%Y')
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/class')
def classList():
    return render_template('class.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=True)
