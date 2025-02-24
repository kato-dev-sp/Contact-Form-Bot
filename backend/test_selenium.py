from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_browser():
    options = Options()
    options.add_argument("--headless")  # これをコメントアウト
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)  # ブラウザを開いたままにする

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        input("ブラウザが開いているか確認してください（Enterで終了）")
        driver.quit()
    except Exception as e:
        print("エラー発生:", e)

test_browser()
