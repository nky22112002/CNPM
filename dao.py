import json

def read_data_from_json():
    try:
        with open('data/hocsinh.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File hocsinh.json không tồn tại.")
        return []
    except json.JSONDecodeError:
        print("Lỗi trong việc phân tích cú pháp file JSON.")
        return []

# Ví dụ sử dụng
if __name__ == '__main__':
    data = read_data_from_json()
    for student in data:
        print(student)
