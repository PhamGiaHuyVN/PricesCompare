import json
import os
import time
import warnings
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from pydantic import BaseModel, Field
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()

api_key = os.getenv("API_KEY")


# định nghĩa các variant
class ProductVariant(BaseModel):
    variant_name: str = Field(description="Tên loại/biến thể (ví dụ: Chai 100g, Chai 300g, Combo 2 chai...)")
    price_vnd: int | None = Field(default=None, description="Giá tương ứng VNĐ")
    stock: int | None = Field(default=None, description="Số lượng tồn kho")


#cấu trúc - thông tin của 1 sản phẩm
class ProductInfo(BaseModel):
    product_name: str = Field(description="Tên đầy đủ của sản phẩm")
    brand: str = Field(description="Thương hiệu sản phẩm")
    price_vnd: int = Field(description="Tổng giá niêm yết của sản phẩm/combo")

    # --- CÁC TRƯỜNG PHÂN LOẠI COMBO & TÍNH ĐƠN GIÁ ---
    is_combo: bool = Field(
        description="True nếu tên hoặc mô tả thể hiện đây là combo/lô/bộ gồm từ 2 sản phẩm trở lên, ngược lại là False."
    )
    items_in_combo: int = Field(
        default=1,
        description="Tổng số lượng sản phẩm đơn lẻ có trong combo này (ví dụ: 'Combo 3 chai' -> 3, sản phẩm đơn -> 1)."
    )
    price_per_unit_vnd: int = Field(
        description="Đơn giá tính cho 1 sản phẩm đơn lẻ = (Tổng giá / Số lượng trong combo)."
    )
    # --------------------------------------------------

    star: float = Field(description="Số sao đánh giá")
    rate: int = Field(description="Số lượt đánh giá")
    sold_quantity: int = Field(description="Số lượng đã bán")
    link_to_product: str = Field(description="Link Shopee sản phẩm")

    all_colors: list[str] = Field(default=[], description="Danh sách màu sắc")
    all_sizes_or_weights: list[str] = Field(default=[], description="Danh sách dung tích/kích thước")
    variants: list[ProductVariant] = Field(default=[], description="Danh sách các biến thể chi tiết")


# danh sách sản phẩm
class ProductList(BaseModel):
    products: list[ProductInfo] = Field(
        description="Danh sách TOÀN BỘ sản phẩm và biến thể tìm thấy."
    )

client = genai.Client(api_key=api_key)

user_product_name = input("Nhập tên sản phẩm hoặc từ khóa bạn muốn tìm kiếm: ").strip()
get_quantity = 10

if not user_product_name:
    print("Bạn chưa nhập tên sản phẩm!")
    exit()


prompt_text = (
    f"Hãy thu thập danh sách của {get_quantity} sản phẩm liên quan đến từ khóa: '{user_product_name}'.\n"
    f"QUY TẮC PHÂN LOẠI COMBO VÀ TÍNH GIÁ:\n"
    f"1. Kiểm tra tiêu đề và mô tả: Nếu chứa các từ khóa như 'Combo', 'Bộ', 'Lô', 'Set', 'x2', 'x3', '2 chai', '3 cái'..., "
    f"hãy đánh dấu 'is_combo = True' và xác định chính xác số lượng 'items_in_combo'.\n"
    f"2. Nếu là sản phẩm lẻ, set 'is_combo = False' và 'items_in_combo = 1'.\n"
    f"3. Tự động tính toán 'price_per_unit_vnd' = (price_vnd / items_in_combo) để quy đổi giá về 1 sản phẩm duy nhất."
)
print(f"\nĐang tìm kiếm và trích xuất dữ liệu cho sản phẩm: '{user_product_name}'...")

count = 1
# hàm gọi API có cơ chế retry và đổi model dự phòng khi lỗi 503
def generate_content_with_retry(prompt, models_to_try=["gemini-3.6-flash", "gemini-2.5-flash"]):
    for model_name in models_to_try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Đang gửi yêu cầu tới mô hình '{model_name}' (Lần thử {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ProductList,
                        temperature=0.1,
                        max_output_tokens=8192
                    ),
                )

                print(f"Lấy sản phẩm {count} thành công")
                return response
            except ServerError as e:
                print(f"Máy chủ quá tải (Lỗi 503). Đợi 5 giây trước khi thử lại...")
                time.sleep(5)
            except Exception as e:
                print(f"Lỗi khác: {e}")
                break
    raise Exception("Tất cả các mô hình và lần thử đều thất bại do máy chủ quá tải.")


# Gọi API và lưu file
try:
    response = generate_content_with_retry(prompt_text)
    data = json.loads(response.text)

    with open("data_item.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(
        f"\nTrích xuất thành công {len(data.get('products', []))} sản phẩm liên quan đến '{user_product_name}' vào file dataItem.json!")

except Exception as e:
    print(f"\nKhông thể trích xuất dữ liệu: {e}")