from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# **テスト用データ**
form_data = {
    "name": "山田 太郎",
    "kana": "ヤマダ タロウ",
    "tel": "03-1234-5678",
    "mail": "example@example.com",
    "content": "お問い合わせメッセージです。"
}

# **Selenium WebDriver の設定**
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # ヘッドレスモード（GUIなし）
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ChromeDriverの起動
driver = webdriver.Chrome(options=options)
driver.get("https://apollo-shonan.jp/contact/")
time.sleep(3)  # ページ読み込み待機

# **フォーム入力**
def fill_form():
    try:
        logging.info("🔍 フォーム入力開始")

        # 各フィールドにデータを入力
        for field_name, input_value in form_data.items():
            field = driver.find_element(By.NAME, field_name)
            
            driver.execute_script("arguments[0].removeAttribute('readonly');", field)
            driver.execute_script("arguments[0].removeAttribute('disabled');", field)

            field.click()
            time.sleep(0.5)
            field.send_keys(Keys.CONTROL, "a")
            field.send_keys(Keys.BACKSPACE)
            field.send_keys(input_value)
            field.send_keys(Keys.TAB)

            # 入力後の値を取得
            final_value = field.get_attribute("value")
            logging.info(f"📌 '{field_name}' に入力: '{final_value}'")
        
        # **スクリーンショット保存**
        driver.save_screenshot("apollo_form_test.png")
        logging.info("📸 スクリーンショットを保存しました: apollo_form_test.png")

        # **送信ボタンをクリック**
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        logging.info(f"🚀 送信ボタンをクリック: {submit_button.get_attribute('value')}")
        submit_button.click()

        time.sleep(3)  # 送信後の処理待機

        logging.info("✅ フォーム入力完了")

    except Exception as e:
        logging.error(f"❌ フォーム入力エラー: {e}")

# **フォームを実行**
fill_form()

# **ブラウザを閉じる**
driver.quit()
