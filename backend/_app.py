from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import logging
from urllib.parse import urljoin
import os
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

def init_chromedriver():
    """ChromeDriverを初期化"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        options.add_experimental_option("detach", True)  # ブラウザを閉じない
        driver = webdriver.Chrome(options=options)
        logging.info("ChromeDriver initialized successfully!")
        return driver
    except Exception as e:
        logging.error(f"Error initializing ChromeDriver: {e}")
        raise

def find_contact_page(driver, base_url):
    """問い合わせページを検索する"""
    try:
        driver.get(base_url)
        time.sleep(5)  # ページの読み込みを待つ
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 1. トップページ内にフォームがあるか確認
        if driver.find_elements(By.TAG_NAME, "form"):
            return base_url

        # 2. 「お問い合わせ」や「contact」のリンクを探して遷移
        keywords = ["お問い合わせ", "お問合せ", "コンタクト", "contact", "inquiry", "support"]
        links = soup.find_all("a", href=True)

        for link in links:
            link_text = link.get_text(strip=True).lower()
            href = link["href"]
            if any(keyword in link_text for keyword in keywords) or any(keyword in href.lower() for keyword in keywords):
                contact_page = urljoin(base_url, href)
                logging.info(f"問い合わせページ候補: {contact_page}")

                driver.get(contact_page)
                time.sleep(3)

                if driver.find_elements(By.TAG_NAME, "form"):
                    return contact_page

    except Exception as e:
        logging.error(f"問い合わせページ検索中にエラー: {e}")

    return None

def fill_contact_form(driver, form_data):
    """問い合わせフォームにデータを入力する"""
    try:
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        textarea_fields = driver.find_elements(By.TAG_NAME, "textarea")
        labels = driver.find_elements(By.TAG_NAME, "label")

        for field in input_fields:
            name_attr = field.get_attribute("name")
            field_type = field.get_attribute("type")
            placeholder = field.get_attribute("placeholder")

            # `name` 属性がある場合
            if name_attr and field_type != "hidden" and name_attr in form_data:
                field.clear()
                field.send_keys(form_data[name_attr])

            # `placeholder` を活用
            elif placeholder:
                for key, value in form_data.items():
                    if key.lower() in placeholder.lower():
                        field.clear()
                        field.send_keys(value)

        for textarea in textarea_fields:
            name_attr = textarea.get_attribute("name")
            if name_attr and name_attr in form_data:
                textarea.clear()
                textarea.send_keys(form_data[name_attr])

        # `label` を活用して適切なフィールドを探す
        for label in labels:
            label_text = label.text.strip().lower()
            for key, value in form_data.items():
                if key.lower() in label_text:
                    input_id = label.get_attribute("for")
                    if input_id:
                        field = driver.find_element(By.ID, input_id)
                        field.clear()
                        field.send_keys(value)

        logging.info("フォーム入力完了")

    except Exception as e:
        logging.error(f"フォーム入力中にエラー: {e}")

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
            contact_page = find_contact_page(driver, url)
            if not contact_page:
                results.append({
                    "status": "error",
                    "message": "問い合わせページが見つかりませんでした",
                    "screenshot": None
                })
                continue

            driver.get(contact_page)
            time.sleep(2)
            # フォームへデータ入力
            fill_contact_form(driver, form_data)

            # スクリーンショットを全ページスクロールして撮影（1枚の画像）
            screenshot_filename = f"{url.replace('https://', '').replace('/', '_')}.png"
            screenshot_path = os.path.join("static/screenshots", screenshot_filename)

            capture_full_page_screenshot(driver, screenshot_path)

            results.append({
                "status": "success",
                "message": "フォーム入力成功",
                "contact_page": contact_page,
                "screenshot": f"http://127.0.0.1:5000/static/screenshots/{screenshot_filename}"
            })

        except Exception as e:
            results.append({
                "status": "error",
                "message": f"処理中にエラーが発生しました: {str(e)}",
                "screenshot": None
            })

    driver.quit()
    return jsonify(results)

def capture_full_page_screenshot(driver, save_path):
    """ページ全体をスクロールしながらスクリーンショットを撮影し、1枚の画像に結合"""
    
    # ページ全体の高さとビューポートの高さを取得
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")

    # スクロール位置を保存
    scroll_positions = list(range(0, total_height, viewport_height)) + [total_height]

    # 各スクロールごとのスクリーンショットを保存
    screenshot_parts = []
    
    for y in scroll_positions:
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(0.5)  # 読み込み待機 (WebDriverWaitを使う場合は適切な要素が表示されるまで待機)
        
        # スクリーンショットをバッファに保存
        screenshot = driver.get_screenshot_as_png()
        screenshot_image = Image.open(io.BytesIO(screenshot))
        screenshot_parts.append(screenshot_image)

    # 画像の合成
    full_screenshot = Image.new('RGB', (screenshot_parts[0].width, sum(img.height for img in screenshot_parts)))
    
    y_offset = 0
    for part in screenshot_parts:
        full_screenshot.paste(part, (0, y_offset))
        y_offset += part.height

    # 保存
    full_screenshot.save(save_path)
    print(f"スクリーンショット保存完了: {save_path}")





if __name__ == '__main__':
    app.run(debug=True)
