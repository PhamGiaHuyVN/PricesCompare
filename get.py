from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

# 1. Định nghĩa cấu trúc cho 1 sản phẩm
class ProductInfo(BaseModel):
    product_name: str = Field(description="Tên sản phẩm")
    price_vnd: int = Field(description="Giá sản phẩm (VNĐ)")
    star: float = Field(description="Số sao đánh giá của sản phẩm")
    rate: int = Field(description="Số lượt đánh giá của sản phẩm")
    sold_quantity: int = Field(description="Số lượng đã bán")
    link_to_product: str = Field(description="Link shoppe của sản phẩm")

# 2. Định nghĩa danh sách sản phẩm với tham số cố định số lượng
count_requested = 5  # Số lượng sản phẩm bạn muốn nhận về

class ProductList(BaseModel):
    products: List[ProductInfo] = Field(
        min_items=count_requested, 
        max_items=count_requested,
        description=f"Danh sách chứa đúng {count_requested} sản phẩm."
    )

client = genai.Client(api_key=api_key)

# 3. Gọi API
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=f"Cho tôi danh sách {count_requested} sản phẩm RP7 phổ biến nhất.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ProductList,
    ),
)

with open ("dataItem.json", "w", encoding="utf-8") as f:
    json.dump(response.text, f, ensure_ascii=False, indent=4)