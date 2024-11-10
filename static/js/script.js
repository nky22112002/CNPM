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
                <td style="width: 30%;">
                    <input type="text" id="nameInput_${lastSTT + 1}" name="ho_ten_${lastSTT + 1}" 
                           onkeyup="fetchSuggestions(${lastSTT + 1})" 
                           style="border: none; outline: none; background-color: transparent; width: 100%; text-align: center;">
                    <div id="suggestions_${lastSTT + 1}" class="suggestions-box"></div>
                </td>
                <td style="width: 15%;"><label id="genderLabel_${lastSTT + 1}">-</label></td>
                <td style="width: 20%;"><label id="birthYearLabel_${lastSTT + 1}">-</label></td>
                <td style="width: 30%;"><label id="addressLabel_${lastSTT + 1}">-</label></td>
            </tr>
        `;

        // Thêm hàng mới vào bảng
        $('#studentClass tbody').append(newRow);
        
        // Cập nhật sĩ số
        let currentSiSo = parseInt($('#siSo').text()) || 0;
        $('#siSo').text(currentSiSo + 1);
    });
});


// Hàm fetchSuggestions() sửa đổi để thêm kết quả vào nav
function fetchSuggestions(rowId) {
    const query = $(`#nameInput_${rowId}`).val();  // Lấy giá trị từ ô input
    console.log("Query:", query);  // Kiểm tra giá trị query

    if (query && query.length > 0) {
        $.ajax({
            url: '/search_student',  // Kiểm tra đường dẫn API
            method: 'GET',
            data: { query: query },
            success: function(data) {
                console.log("Received suggestions:", data);  // Kiểm tra kết quả từ API

                let searchResults = $('#searchResults');
                searchResults.empty();  // Xóa các kết quả cũ

                if (data.length > 0) {
                    // Hiển thị kết quả trong nav
                    data.forEach(item => {
                        let li = $(`<li class="suggestion-item">${item[0]} | ${item[1]} | ${item[2]} | ${item[3]}</li>`);  // item[0] là FullName nếu dữ liệu trả về là mảng con
                        li.click(function() {
                            selectStudent(rowId, item);  // Hàm chọn sinh viên
                        });
                        searchResults.append(li);
                    });

                    // Cập nhật vị trí của #searchNav theo thẻ input
                    let inputPosition = $(`#nameInput_${rowId}`).offset();  // Lấy vị trí của thẻ input
                    let inputHeight = $(`#nameInput_${rowId}`).outerHeight();  // Lấy chiều cao của thẻ input
                    let inputWidth = $(`#nameInput_${rowId}`).outerWidth();  // Lấy chiều rộng của thẻ input

                    // Cập nhật vị trí cho #searchNav
                    $('#searchNav').css({
                        top: inputPosition.top + inputHeight,  // Vị trí dọc (xuống dưới thẻ input)
                        left: inputPosition.left,  // Vị trí ngang (cùng vị trí với thẻ input)
                        width: inputWidth  // Chiều rộng của nav bằng chiều rộng của input
                    });

                    // Hiển thị nav khi có kết quả
                    $('#searchNav').show();  // Hiển thị nav chứa kết quả tìm kiếm
                } else {
                    searchResults.append('<div>No suggestions found.</div>');
                    $('#searchNav').show();  // Hiển thị thông báo
                }
            },
            error: function(error) {
                console.error("Error fetching suggestions:", error);
            }
        });
    } else {
        $('#searchNav').hide();  // Ẩn nav nếu không có query
    }
}


// Hàm để chọn sinh viên và cập nhật các thẻ label
function selectStudent(rowId, item) {
    // item[0] là FullName, item[1] là Giới tính, item[2] là Năm sinh, item[3] là Địa chỉ
    $(`#nameInput_${rowId}`).val(item[0]); // Cập nhật tên vào ô input
    $(`#genderLabel_${rowId}`).text(item[1]); // Cập nhật giới tính
    $(`#birthYearLabel_${rowId}`).text(item[2]); // Cập nhật năm sinh
    $(`#addressLabel_${rowId}`).text(item[3]); // Cập nhật địa chỉ

    // Ẩn nav sau khi chọn
    $('#searchNav').hide();
}





