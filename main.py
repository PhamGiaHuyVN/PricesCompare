import json
import pandas as pd

# 1. Đọc file JSON thô (lúc này data_str đang là 1 chuỗi string bị bọc nháy kép)
with open('dataItem.json', 'r', encoding='utf-8') as f:
    data_str = json.load(f)

# 2. Giải mã chuỗi string đó một lần nữa để chuyển thành Dictionary thật
actual_data = json.loads(data_str)

# 3. Làm phẳng dữ liệu từ key 'products'
df = pd.json_normalize(actual_data, record_path=['products'])

# 4. Xuất ra file CSV
df.to_csv('dataItem.csv', index=False, encoding='utf-8')

print("Đã chuyển đổi thành công! Hãy kiểm tra file dataItem.csv")
