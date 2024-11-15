let selectedStudents = [];

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

    
    
});
document.addEventListener('DOMContentLoaded', function() {
    // Lắng nghe sự kiện "input" của thẻ input
    const inputElement = document.querySelector('input[name="ngay_sinh"]');

    inputElement.addEventListener('input', function(e) {
        let value = this.value.replace(/[^0-9-]/g, ''); // Chỉ giữ lại số, bỏ dấu '-'

        // Kiểm tra nếu người dùng không xóa ký tự (tránh thêm dấu khi xóa)
        if (e.inputType !== 'deleteContentBackward') {
            // Chỉ thêm dấu '-' sau 2 ký tự và 5 ký tự
            if (value.length === 4 || value.length === 7) {
                // Thêm dấu '-' nếu chưa có tại vị trí đó
                if (value[value.length - 1] !== '-') {
                    value += '-';
                }
            }
        }

        // Giới hạn độ dài chuỗi là 10 ký tự (dd-mm-yyyy)
        this.value = value.slice(0, 10);
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
                        let li = $(`<li class="suggestion-item">${item[1]} | ${item[2]} | ${item[3]} | ${item[4]}</li>`);  // item[0] là FullName nếu dữ liệu trả về là mảng con
                        li.click(function() {
                            selectStudent(rowId, item);  // Hàm chọn sinh viên
                        });
                        searchResults.append(li);
                    });
                    console.log("selectedStudent: ", selectedStudents);
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
    const studentId = item[0];  // Mã sinh viên
    const existingStudentId = selectedStudents[rowId - 1]; // Lấy giá trị sinh viên hiện tại của rowId

    // Nếu có giá trị sinh viên cũ, xóa nó khỏi mảng trước khi thêm giá trị mới
    if (existingStudentId) {
        const index = selectedStudents.indexOf(existingStudentId);
        if (index !== -1) {
            selectedStudents.splice(index, 1);  // Xóa giá trị sinh viên cũ
        }
    }

    // Thêm mã sinh viên mới vào mảng cho rowId
    selectedStudents[rowId - 1] = studentId;
    $(`#nameInput_${rowId}`).val(item[1]); // Cập nhật tên vào ô input
    $(`#genderLabel_${rowId}`).text(item[2]); // Cập nhật giới tính
    $(`#birthYearLabel_${rowId}`).text(item[3]); // Cập nhật năm sinh
    $(`#addressLabel_${rowId}`).text(item[4]); // Cập nhật địa chỉ

    // Ẩn nav sau khi chọn
    $('#searchNav').hide();
}

// Hàm gửi mảng selectedStudents tới server khi nhấn nút "Thêm vào lớp"
function sendSelectedStudentsToServer() {
    const lop = $('input[name="lop"]').val();  // Lấy tên lớp từ ô input
    console.log("Lớp:", lop);
    console.log("selectedStudent:", selectedStudents);

    if (lop && selectedStudents.length > 0) {
        $.ajax({
            url: '/add_class_list',  // Đường dẫn tới route Flask xử lý
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                TenLop: lop,
                MaHS: selectedStudents  // Gửi mảng mã học sinh
            }),
            success: function(response) {
                response.forEach(item => {
                    alert('Học sinh với STT ' + item.MaHS + ': ' + item.message);  // Hiển thị thông báo từ server
                    console.log("Response from server:", item.MaHS + ': ' + item.message);

                });            },
            error: function(error) {
                console.error("Error sending data:", error);
                alert('Có lỗi khi gửi dữ liệu!');
            }
        });
    } else {
        alert("Vui lòng nhập lớp và chọn học sinh!");
    }
}

// Hàm được gọi khi người dùng nhấn nút "Thêm vào lớp"
$('#addClassBtn').on('click', function() {
    sendSelectedStudentsToServer();  // Gửi mảng selectedStudents tới server
});

// Hàm lấy danh sách học sinh từ lớp, môn, học kỳ, năm học
$(document).ready(function() {
    $('#fetchDataBtn').click(function() {
        // Lấy giá trị từ các ô input
        let lop = $('input[name="ten-lop"]').val();
        let mon = $('input[name="ten-mh"]').val();
        let hocKy = $('input[name="hoc-ky"]').val();
        let namHoc = $('input[name="nam-hoc"]').val();

        // Gửi yêu cầu AJAX đến Flask để gọi Stored Procedure
        $.ajax({
            url: '/get-students',
            type: 'GET',
            data: { ten_lop: lop, ten_mh: mon, hoc_ky: hocKy, nam_hoc: namHoc },
            success: function(data) {
                // Xóa các hàng cũ trong bảng (nếu có)
                $('#studentTableBody').find("tr:gt(0)").remove();

                

                // Kiểm tra và hiển thị dữ liệu từ Stored Procedure
                if (data && data.length > 0) {
                    data.forEach((row, index) => {
                        $('#studentTableBody').append(`
                             <tr style="text-align: center;">
                                <td style="width: 5%;">${index + 1}</td>
                                <td style="width: 30%;">${row.ten_hoc_sinh}</td>
                                <td style="width: 15%;">
                                    <input type="text" class="diem-15phut" data-id="${row.ma_hoc_sinh}" value="${row.diem_15_phut || ''}" placeholder="" />
                                </td>
                                <td style="width: 20%;">
                                    <input type="text" class="diem-1tiet" data-id="${row.ma_hoc_sinh}" value="${row.diem_1_tiet || ''}" placeholder="" />
                                </td>
                                <td style="width: 30%;">
                                    <input type="text" class="diem-thi" data-id="${row.ma_hoc_sinh}" value="${row.diem_thi || ''}" placeholder="" />
                                </td>
                            </tr>
                        `);
                    });
                } else {
                    $('#studentTableBody').append('<tr><td colspan="5" style="text-align: center;">Không có dữ liệu</td></tr>');
                }
            },
            error: function(err) {
                console.log("Error:", err);
                alert("Không thể lấy dữ liệu. Vui lòng kiểm tra lại!");
            }
        });
    });
}); 



