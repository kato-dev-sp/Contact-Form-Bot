from selenium import webdriver
import logging

def init_chromedriver():
    """ChromeDriverを初期化"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # ヘッドレスモード（GUIなし）
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # ChromeDriverの起動
        driver = webdriver.Chrome(options=options)
        logging.info("ChromeDriver initialized successfully!")
        return driver
    except Exception as e:
        logging.error(f"Error initializing ChromeDriver: {e}")
        raise
