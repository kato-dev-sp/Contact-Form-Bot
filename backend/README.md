### **API設計**

#### **1. 問い合わせページ検出API**
- **エンドポイント:** `/detect-contact-page`
- **HTTPメソッド:** POST
- **インプット:**
    ```json
    {
        "url": "https://example.com"
    }
    ```
- **レスポンス:**
    ```json
    {
        "contact_page": "https://example.com/contact",
        "status": "found"
    }
    ```

#### **2. フォーム入力API**
- **エンドポイント:** `/submit-form`
- **HTTPメソッド:** POST
- **インプット:**
    ```json
    {
        "contact_page": "https://example.com/contact",
        "form_data": {
            "name": "山田 太郎",
            "email": "yamada@example.com",
            "message": "お問い合わせ内容です。"
        }
    }
    ```
- **レスポンス:**
    ```json
    {
        "status": "success",
        "screenshot": "https://storage.example.com/screenshots/contact_page_001.png"
    }
    ```

#### **3. 処理結果取得API**
- **エンドポイント:** `/get-results`
- **HTTPメソッド:** GET
- **レスポンス:**
    ```json
    {
        "total_success": 10,
        "total_failure": 2,
        "results": [
            {
                "url": "https://example1.com",
                "contact_page": "https://example1.com/contact",
                "status": "success",
                "screenshot": "https://storage.example.com/screenshots/example1.png"
            },
            {
                "url": "https://example2.com",
                "contact_page": null,
                "status": "failure",
                "error": "フォームが見つかりませんでした"
            }
        ]
    }
    ```

---