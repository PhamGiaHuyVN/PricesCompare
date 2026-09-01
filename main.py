import json
import os
import warnings
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()

api_key = os.getenv("API_KEY")
# 1. Khởi tạo client (đảm bảo đã gán GEMINI_API_KEY trong biến môi trường)
client = genai.Client(api_key=api_key)

with open("data_item.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. Định nghĩa cấu trúc đầu ra bằng Pydantic (Structured Output)
class ProductAnalysis(BaseModel):
    best_selling_product: str = Field(description="Tên sản phẩm bán chạy nhất")
    link_to_product: str = Field(description="Link đến sản phẩm")

# 4. Viết Prompt phân tích
prompt = f"""
Hãy phân tích dữ liệu sản phẩm dưới đây và đưa ra nhận xét:
- Sản phẩm nào có giá tốt nhất(rẻ nhất) và chất lượng tốt nhất(đánh giá, lượt bán, ...)
- Hãy đưa ra giải thích dựa vào tiêu chí nào mà sản phẩm này là lựa chọn tốt nhất

Dữ liệu JSON:
{data}
"""

# 5. Gọi API với Gemini 2.5 Flash
response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_schema=ProductAnalysis,
        temperature=0.2,
    ),
)

# 6. In kết quả phân tích dạng JSON định dạng sẵn
print(response.text)