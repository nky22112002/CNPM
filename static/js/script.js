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
    $('#saveScoresBtn').click(function () {
        let students = [];
        $('#studentTableBody tr').each(function () {
            const maHocSinh = $(this).find('input.diem-15phut').data('id');
            const diem15Phut = $(this).find('input.diem-15phut').val();
            const diem1Tiet = $(this).find('input.diem-1tiet').val();
            const diemThi = $(this).find('input.diem-thi').val();
    
            if (maHocSinh) {
                students.push({
                    ma_hoc_sinh: maHocSinh,
                    ten_mh: $('input[name="ten-mh"]').val(),
                    hoc_ky: $('input[name="hoc-ky"]').val(),
                    diem_15_phut: diem15Phut,
                    diem_1_tiet: diem1Tiet,
                    diem_thi: diemThi
                });
            }
        });
    
        $.ajax({
            url: '/save-student-grades',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ students }),
            success: function (response) {
                // Hiển thị thông báo khi lưu điểm thành công
                alert(response.message || 'Điểm đã được lưu thành công!');
            },
            error: function (xhr, status, error) {
                // Lấy dữ liệu lỗi từ server (nếu có)
                let errorMessage = "Đã xảy ra lỗi trong quá trình lưu điểm!";
                
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;  // Lấy thông báo lỗi từ server
                }
    
                console.error("Error:", errorMessage);
                alert(errorMessage);  // Hiển thị thông báo lỗi cụ thể
            }
        });
    });
    
}); 


$(document).ready(function () {
    $("#reportForm").on("submit", function (e) {
        e.preventDefault(); // Ngăn chặn hành động submit mặc định của form

        // Lấy giá trị từ các input
        const mon = $("#mon").val();
        const hocKy = $("#hocKy").val();
        const namHoc = $("#namHoc").val();

        // Gửi dữ liệu qua AJAX đến Flask
        $.ajax({
            url: "/show_summary_table", // URL của Flask endpoint
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                mon: mon,
                hoc_ky: hocKy,
                nam_hoc: namHoc
            }),
            success: function (response) {
                
                // Xử lý dữ liệu trả về để hiển thị vào bảng
                const tbody = $("table tbody");
                tbody.find("tr:not(:first)").remove(); // Xóa các hàng cũ, giữ lại hàng tiêu đề

                response.forEach((item, index) => {
                    const [lop, siSo, soLuongDat] = item;
                    const tyLe = ((soLuongDat / siSo) * 100).toFixed(2); // Tính tỷ lệ (%)

                    const newRow = `
                        <tr style="text-align: center;">
                            <td>${index + 1}</td>
                            <td>${lop}</td>
                            <td>${siSo}</td>
                            <td>${soLuongDat}</td>
                            <td>${tyLe}%</td>
                        </tr>
                    `;

                    tbody.append(newRow); // Thêm hàng mới vào tbody
                });
                $("#showChart").show();

            },
            error: function (xhr, status, error) {
                console.error("Error:", error);
            }
        });
    });
});
    
$(document).ready(function() {
    let chartInstance = null; // Biến lưu trữ biểu đồ để cập nhật lại khi có dữ liệu mới

    // Hàm vẽ biểu đồ
    function drawChart(labels, data) {
        const ctx = document.getElementById('summaryChart').getContext('2d');

        // Xóa biểu đồ cũ nếu có
        if (chartInstance) {
            chartInstance.destroy();
        }

        // Tạo biểu đồ mới
        chartInstance = new Chart(ctx, {
            type: 'bar', // Loại biểu đồ (cột)
            data: {
                labels: labels, // Tên các lớp
                datasets: [{
                    label: 'Tỷ lệ đạt (%)',
                    data: data, // Dữ liệu tỷ lệ
                    backgroundColor: 'rgba(75, 192, 192, 0.6)', // Màu nền
                    borderColor: 'rgba(75, 192, 192, 1)', // Màu viền
                    borderWidth: 1, // Độ dày viền
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.raw + '%'; // Hiển thị đơn vị %
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Tỷ lệ (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Lớp học'
                        }
                    }
                }
            }
        });
    }

    // Xử lý khi nhấn nút "Biểu đồ"
    $("#showChart").on("click", function() {
        let labels = [];
        let data = [];

        // Duyệt qua tất cả các hàng trong bảng và lấy dữ liệu lớp và tỷ lệ đạt
        $("tbody tr").each(function(index) {
            // Bỏ qua hàng đầu tiên (tiêu đề)
            if (index === 0) return;
        
            const className = $(this).find("td:nth-child(2)").text(); // Lấy tên lớp (cột 2)
            const siSo = $(this).find("td:nth-child(3)").text(); // Lấy sĩ số (cột 3)
            const soLuongDat = $(this).find("td:nth-child(4)").text(); // Lấy số lượng đạt (cột 4)
        
            if (className && siSo && soLuongDat) {
                // Tính tỷ lệ đạt
                const rate = ((parseInt(soLuongDat) / parseInt(siSo)) * 100).toFixed(2);
        
                // Thêm dữ liệu vào mảng labels và data
                labels.push(className); // Lớp học
                data.push(rate); // Tỷ lệ đạt
            }
        });
        

        // Vẽ biểu đồ
        drawChart(labels, data);
    });
});

$(document).ready(function () {
    // Định nghĩa thông báo thành công
    const successMessage = "Cập nhật thành công!";

    // Gửi dữ liệu cập nhật về server
    function updateSettings(data) {
        $.ajax({
            url: '/update_setting', // Đảm bảo đường dẫn đúng với route Flask
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                if (response.status === "success") {
                    alert(successMessage); // Thông báo thành công
                } else {
                    alert("Cập nhật thất bại: " + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert("Có lỗi xảy ra: " + error);
            }
        });
    }

    // Nút thay đổi độ tuổi
    $("#updateAge").on("click", function () {
        const minAge = $("#minAge").val();
        const maxAge = $("#maxAge").val();

        // Kiểm tra nếu minAge và maxAge là số hợp lệ
        if (!minAge || !maxAge || isNaN(minAge) || isNaN(maxAge)) {
            alert("Vui lòng nhập độ tuổi hợp lệ!");
            return;
        }

        // Cập nhật dữ liệu minAge và maxAge cùng một lần
        updateSettings({
            name: "ageSettings", 
            minAge: parseInt(minAge), 
            maxAge: parseInt(maxAge)
        });
    });

    // Nút thay đổi sĩ số lớp
    $("#updateClassSize").on("click", function () {
        const classSize = $("#classSize").val();

        // Kiểm tra nếu classSize là số hợp lệ
        if (!classSize || isNaN(classSize)) {
            alert("Vui lòng nhập sĩ số lớp hợp lệ!");
            return;
        }

        // Cập nhật dữ liệu
        updateSettings({ name: "classSize", value: parseInt(classSize) });
    });
});





