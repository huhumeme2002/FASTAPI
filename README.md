# FastAPI License Key Server cho Render

Đây là một API server hoàn chỉnh được xây dựng bằng FastAPI để quản lý và xác thực key bản quyền, được tối ưu hóa để triển khai trên Render.

## Tính năng

- **Xác thực Key:** Endpoint `/api/validate-key` để extension của bạn gọi đến.
- **Tạo Key:** Endpoint `/api/generate-key` được bảo vệ bằng mật khẩu admin để bạn tạo key mới cho người dùng.
- **Tích hợp Database:** Sử dụng PostgreSQL để lưu trữ key an toàn và lâu dài.
- **Sẵn sàng triển khai:** Cung cấp tệp `render.yaml` để tự động hóa việc triển khai trên Render.

## Cấu trúc API

### 1. Tạo Key mới (Admin)

- **Endpoint:** `POST /api/generate-key`
- **Mô tả:** Tạo một key bản quyền mới. Endpoint này yêu cầu xác thực.
- **Header:**
  - `X-Admin-Secret`: `YOUR_ADMIN_SECRET` (Mật khẩu bí mật bạn tự đặt)
- **Body (JSON):**
  ```json
  {
    "days_valid": 30,
    "notes": "Key cho khách hàng a@example.com"
  }
  ```
- **Phản hồi thành công (200):**
  ```json
  {
    "key_string": "PRO-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX",
    "expires_at": "2023-12-25T12:00:00Z",
    "notes": "Key cho khách hàng a@example.com"
  }
  ```

### 2. Xác thực Key (Dùng cho Extension)

- **Endpoint:** `POST /api/validate-key`
- **Mô tả:** Xác thực một key bản quyền. Đây là endpoint mà extension của bạn sẽ gọi.
- **Body (JSON):**
  ```json
  {
    "licenseKey": "PRO-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX"
  }
  ```
- **Phản hồi (Key hợp lệ):**
  ```json
  {
    "isValid": true,
    "expiresAt": "2023-12-25T12:00:00Z"
  }
  ```
- **Phản hồi (Key không hợp lệ):**
  ```json
  {
    "isValid": false,
    "message": "Key bản quyền không hợp lệ hoặc đã hết hạn."
  }
  ```

## Chạy Local (Tùy chọn)

1.  **Cài đặt Python 3.9+** và tạo môi trường ảo:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: venv\Scripts\activate
    ```

2.  **Cài đặt các thư viện:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Cài đặt và chạy PostgreSQL:** Sử dụng Docker hoặc cài đặt trực tiếp. Tạo một database và lấy chuỗi kết nối (Connection String).

4.  **Tạo file `.env`** và cấu hình:
    ```
    # Ví dụ chuỗi kết nối PostgreSQL local
    DATABASE_URL="postgresql://user:password@localhost:5432/license_db"
    ADMIN_SECRET_KEY="day-la-mat-khau-bi-mat-cua-toi"
    ```

5.  **Chạy server:**
    ```bash
    uvicorn main:app --reload
    ```
    API sẽ chạy tại `http://127.0.0.1:8000`.

## Hướng dẫn triển khai trên Render

1.  **Tạo tài khoản GitHub:** Đưa toàn bộ các file này vào một repository mới trên GitHub của bạn.

2.  **Tạo tài khoản Render:** Truy cập [render.com](https://render.com) và đăng ký.

3.  **Tạo ứng dụng mới:**
    - Trên Dashboard của Render, click **"New +"** -> **"Blueprint"**.
    - Kết nối tài khoản GitHub của bạn và chọn repository bạn vừa tạo.
    - Render sẽ tự động đọc file `render.yaml` và hiện ra 2 dịch vụ cần tạo:
        - **`license-db` (Database):** Dịch vụ PostgreSQL.
        - **`license-api` (Web Service):** Dịch vụ FastAPI API.
    - Bạn cần điền giá trị cho biến môi trường `ADMIN_SECRET_KEY`. Hãy đặt một mật khẩu an toàn và ghi nhớ nó.

4.  **Triển khai:**
    - Click **"Apply"**.
    - Render sẽ bắt đầu xây dựng database và triển khai ứng dụng của bạn. Quá trình này mất vài phút.
    - Sau khi hoàn tất, Render sẽ cung cấp cho bạn một URL có dạng `https://your-service-name.onrender.com`. Đây chính là API endpoint của bạn.

5.  **Sử dụng:**
    - Cập nhật URL này vào trong file `extension.js` của bạn.
    - Dùng một công cụ như Postman hoặc Insomnia để gọi đến endpoint `/api/generate-key` (với header `X-Admin-Secret`) để tạo những key đầu tiên. 