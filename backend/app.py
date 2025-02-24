from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import time
from utils.driver import init_chromedriver
from utils.contact_finder import find_contact_page
from utils.form_filler import fill_contact_form
from utils.screenshot import capture_full_page_screenshot

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    """問い合わせフォームにデータを自動入力するAPI"""
    data = request.json
    urls = data.get("urls", [])
    form_data = data.get("form_data", {})

    if not urls:
        return jsonify({"status": "error", "message": "URLリストが空です"}), 400

    driver = init_chromedriver()  # ChromeDriver起動
    results = []

    for url in urls:
        try:
            # 問い合わせページの検索
            contact_page_result = find_contact_page(driver, url)

            # もし `find_contact_page()` がエラーを返した場合
            if contact_page_result["status"] == "error":
                results.append({
                    "status": "error",
                    "message": contact_page_result["message"],
                    "contact_page": contact_page_result.get("contact_page", "-"),  # 🔹 URLを格納
                    "screenshot": None
                })
                continue  # 次の URL に進む

            # 実際の問い合わせページURLを取得
            contact_url = contact_page_result["contact_page"]
            driver.get(contact_url)
            time.sleep(5)

            # フォームに入力
            form_success = fill_contact_form(driver, form_data, contact_url)
            if not form_success:
                results.append({
                    "status": "error",
                    "message": "送付失敗（フォーム入力に失敗しました）",
                    "contact_page": contact_url,
                    "screenshot": None
                })
                continue  # 次の URL に進む

            # スクリーンショット撮影
            screenshot_filename = f"{url.replace('https://', '').replace('/', '_')}.png"
            # screenshot_path = os.path.join("static/screenshots", screenshot_filename)
            # capture_full_page_screenshot(driver, screenshot_path)

            results.append({
                "status": "success",
                "message": "送付成功",
                "contact_page": contact_url,
                "screenshot": f"http://127.0.0.1:5000/static/screenshots/{screenshot_filename}"
            })

        except Exception as e:
            results.append({
                "status": "error",
                "message": f"送付失敗（その他エラー: {str(e)}）",
                "contact_page": "-",
                "screenshot": None
            })

    driver.quit()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
