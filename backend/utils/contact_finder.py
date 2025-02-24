from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time
import logging
import requests

# スクレイピング禁止ワード
SCRAPING_DISALLOW = ["User-agent: * Disallow: /"]

# 営業利用禁止ワード
SALES_DISALLOW_WORDS = ["営業", "セールス", "お断り", "遠慮", "商用目的", "勧誘", "私はロボットではありません"]

def check_scraping_allowed(base_url):
    """サイトの `robots.txt` をチェックし、スクレイピングが許可されているか確認"""
    try:
        robots_url = urljoin(base_url, "/robots.txt")
        response = requests.get(robots_url, timeout=5)

        if response.status_code == 200:
            robots_content = response.text.lower()
            for rule in SCRAPING_DISALLOW:
                if rule.lower() in robots_content:
                    logging.info(f"スクレイピングNG: {base_url}")
                    return False
        return True
    except Exception as e:
        logging.warning(f"robots.txt チェック失敗 ({base_url}): {e}")
        return True  # `robots.txt` が取得できなかった場合はスクレイピング可能と判断

def contains_sales_restrictions(driver):
    """問い合わせページに営業利用禁止ワードが含まれているか確認"""
    page_text = driver.page_source.lower()
    return any(word in page_text for word in SALES_DISALLOW_WORDS)

def find_contact_page(driver, base_url):
    """問い合わせページを検索する"""
    logging.info(f"問い合わせページ検索開始: {base_url}")

    if not check_scraping_allowed(base_url):
        logging.info(f"スクレイピングNG: {base_url}")
        return {"status": "error", "message": "スクレイピングNG"}

    try:
        driver.get(base_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 1. トップページ内にフォームがあるか確認
        if is_valid_contact_page(driver):
            logging.info(f"問い合わせフォームをトップページで発見: {base_url}")
            return {"status": "success", "contact_page": base_url}

        # 2. 「お問い合わせ」や「contact」のリンクを探して遷移
        keywords = ["お問い合わせ", "お問合せ", "コンタクト", "contact", "inquiry", "support"]
        links = soup.find_all("a", href=True)

        for link in links:
            link_text = link.get_text(strip=True).lower()
            href = link["href"]

            if any(keyword in link_text for keyword in keywords) or any(keyword in href.lower() for keyword in keywords):
                contact_page = urljoin(base_url.rstrip("/"), href.lstrip("/"))
                logging.info(f"問い合わせページ候補: {contact_page}")

                driver.get(contact_page)
                time.sleep(3)

                if is_valid_contact_page(driver):
                    # 送付不可ワードが含まれているかチェック
                    if contains_sales_restrictions(driver):
                        logging.info(f"送付不可ワード検出: {contact_page}")
                        return {"status": "error", "message": "送付不可（営業利用禁止）"}

                    logging.info(f"問い合わせページ確定: {contact_page}")
                    return {"status": "success", "contact_page": contact_page}

    except Exception as e:
        logging.error(f"問い合わせページ検索中にエラー: {e}")

    logging.info(f"問い合わせページが見つかりませんでした: {base_url}")
    return {"status": "error", "message": "問い合わせページが見つかりませんでした"}

def is_valid_contact_page(driver):
    """問い合わせページとして適切かを判定"""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_desc = soup.find("meta", {"name": "description"})
        meta_content = meta_desc["content"].lower() if meta_desc else ""

        # 問い合わせページとして考えられるキーワード（参考程度）
        valid_keywords = ["お問い合わせ", "お問合せ", "コンタクト", "contact", "inquiry", "support", "customer service"]

        # ページ内のフォームを取得
        forms = driver.find_elements(By.TAG_NAME, "form")
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")

        # 🔹 【修正ポイント】フォームが存在することを最優先条件にする
        has_form = len(forms) > 0

        # 🔹 【修正ポイント】問い合わせフォームらしい入力フィールドがあるかを重視
        has_email_field = any("email" in field.get_attribute("name").lower() for field in input_fields)
        has_textarea = len(textareas) > 0

        # 🔹 【修正ポイント】URLにも着目する
        contact_url_keywords = ["contact", "inquiry", "support", "customer"]
        has_contact_url = any(keyword in driver.current_url.lower() for keyword in contact_url_keywords)

        # 🔹 【修正ポイント】タイトルやメタ情報の影響を弱める（補助的）
        has_relevant_title = any(keyword in driver.title.lower() for keyword in valid_keywords)
        has_relevant_meta = any(keyword in meta_content for keyword in valid_keywords)

        # 🔹 【新しい判定基準】フォームがあり、かつメール欄 or テキストエリアがある場合は問い合わせページとする
        if has_form and (has_email_field or has_textarea):
            return True
        
        # 🔹 フォームがない場合でも、URLやタイトル、メタ情報で補助的に問い合わせページか判断
        if has_form and (has_contact_url or has_relevant_title or has_relevant_meta):
            return True

        return False  # どの条件も満たさない場合は問い合わせページではない

    except Exception as e:
        logging.error(f"問い合わせページ判定エラー: {e}")
        return False


def find_contact_page(driver, base_url):
    """問い合わせページを検索する"""
    logging.info(f"問い合わせページ検索開始: {base_url}")

    if not check_scraping_allowed(base_url):
        logging.info(f"スクレイピングNG: {base_url}")
        return {"status": "error", "message": "スクレイピングNG", "contact_page": None}

    try:
        driver.get(base_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 1. トップページ内にフォームがあるか確認
        if is_valid_contact_page(driver):
            logging.info(f"問い合わせフォームをトップページで発見: {base_url}")

            # 🔹 問い合わせページに営業利用禁止ワードが含まれるか確認
            if contains_sales_restrictions(driver):
                logging.info(f"送付不可ワード検出: {base_url}")
                return {"status": "error", "message": "送付不可（営業利用禁止）", "contact_page": base_url}

            return {"status": "success", "contact_page": base_url}

        # 2. 「お問い合わせ」や「contact」のリンクを探して遷移
        keywords = ["お問い合わせ", "お問合せ", "コンタクト", "contact", "inquiry", "support"]
        links = soup.find_all("a", href=True)

        for link in links:
            link_text = link.get_text(strip=True).lower()
            href = link["href"]

            if any(keyword in link_text for keyword in keywords) or any(keyword in href.lower() for keyword in keywords):
                contact_page = urljoin(base_url.rstrip("/"), href.lstrip("/"))
                logging.info(f"問い合わせページ候補: {contact_page}")

                driver.get(contact_page)
                time.sleep(3)

                if is_valid_contact_page(driver):
                    # 🔹 問い合わせページに営業利用禁止ワードが含まれるか確認
                    if contains_sales_restrictions(driver):
                        logging.info(f"送付不可ワード検出: {contact_page}")
                        return {"status": "error", "message": "送付不可（営業利用禁止）", "contact_page": contact_page}

                    logging.info(f"問い合わせページ確定: {contact_page}")
                    return {"status": "success", "contact_page": contact_page}

    except Exception as e:
        logging.error(f"問い合わせページ検索中にエラー: {e}")

    logging.info(f"問い合わせページが見つかりませんでした: {base_url}")
    return {"status": "error", "message": "問い合わせページが見つかりませんでした", "contact_page": None}
