$('#studentForm').submit(function(event) {
    event.preventDefault();
    $.ajax({
        url: "/submit",
        method: "POST",
        data: $(this).serialize(),
        success: function(response) {
            alert('Dữ liệu đã được gửi thành công!');
        },
        error: function(error) {
            alert('Có lỗi xảy ra: ' + error.responseText);
        }
    });

    // Xử lý input ngày sinh
    document.querySelector('input[name="ngay_sinh"]').addEventListener('input', function(e) {
        let value = this.value.replace(/[^0-9/]/g, ''); // Xóa ký tự không hợp lệ

        // Kiểm tra nếu không phải thao tác xóa (người dùng nhập thêm)
        if (e.inputType !== 'deleteContentBackward') {
            if (value.length === 2 || value.length === 5) {
                // Chỉ thêm dấu '/' nếu không có tại vị trí đó
                if (value[value.length - 1] !== '/') {
                    value += '/';
                }
            }
        }

        // Cập nhật giá trị ô nhập
        this.value = value.slice(0, 10); // Giới hạn tối đa 10 ký tự
    });
    
});
$(document).ready(function() {
    // Xử lý sự kiện click vào nút "Thêm hàng"
    $('#addRowBtn').click(function() {
        // Lấy số thứ tự hiện tại từ hàng cuối cùng
        let lastRow = $('#studentClass tbody tr:last');
        let lastSTT = parseInt(lastRow.find('td:first').text()) || 0;

        // Tạo hàng mới với số thứ tự tăng dần
        let newRow = `
            <tr style="text-align: center;">
                <td style="width: 5%;">${lastSTT + 1}</td>
                <td style="width: 30%;"><input type="text" name="ho_ten_${lastSTT + 1}" style="border: none; outline: none; background-color: transparent; width: 100%;"></td>
                <td style="width: 15%;"><input type="text" name="gioi_tinh_${lastSTT + 1}" style="border: none; outline: none; background-color: transparent; width: 100%;"></td>
                <td style="width: 20%;"><input type="text" name="nam_sinh_${lastSTT + 1}" style="border: none; outline: none; background-color: transparent; width: 100%;"></td>
                <td style="width: 30%;"><input type="text" name="dia_chi_${lastSTT + 1}" style="border: none; outline: none; background-color: transparent; width: 100%;"></td>
            </tr>
        `;

        // Thêm hàng mới vào bảng
        $('#studentClass tbody').append(newRow);
        // Cập nhật sĩ số
        let currentSiSo = parseInt($('#siSo').text()) || 0;
        $('#siSo').text(currentSiSo + 1);
    });
});
