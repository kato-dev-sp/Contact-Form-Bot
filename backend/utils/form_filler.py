from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging
import time
import os
from .screenshot import capture_full_page_screenshot 

FORM_MAPPING = {
    "姓": ["姓", "名字", "苗字", "last_name", "family_name"],
    "名": ["名", "名前", "first_name", "given_name"],
    "氏名": ["氏名", "name"],  # ✅ 'name' に対応
    "姓カナ": ["姓カナ", "セイ", "last_name_kana"],
    "名カナ": ["名カナ", "メイ", "first_name_kana"],
    "フリガナ": ["フリガナ", "kana"],  # ✅ 'kana' に対応
    "郵便番号": ["郵便番号", "zip", "zipCode", "postal_code", "postal"],  # ✅ 'zipCode' 追加
    "住所": ["住所", "address", "addr", "location"],  # ✅ 'address' 追加
    "電話番号": ["電話番号", "phone", "tel"],  # ✅ 'tel' に対応
    "メールアドレス": ["メールアドレス", "email", "e-mail", "mail"],  # ✅ 'mail' に対応
    "自社HP URL": ["自社HP", "ホームページ", "website", "url", "companyUrl"],  # ✅ 'companyUrl' 追加
    "お問い合わせ内容": ["お問い合わせ", "問合せ", "問い合わせ内容", "message", "inquiry", "content"],  # ✅ 'content' に対応
}


def preprocess_form_data(form_data):
    """姓+名, 姓カナ+名カナ を結合して `氏名` と `フリガナ` を `name` と `kana` に変換"""
    combined_data = {}

    # `氏名` を `name` に統合
    if "lastName" in form_data and "firstName" in form_data:
        combined_data["name"] = f"{form_data['lastName']} {form_data['firstName']}".strip()

    # `フリガナ` を `kana` に統合
    if "lastNameKana" in form_data and "firstNameKana" in form_data:
        combined_data["kana"] = f"{form_data['lastNameKana']} {form_data['firstNameKana']}".strip()

    # 他のフィールドを `フォームの name` に変換
    mapping = {
        "phone": "tel",
        "email": "mail",
        "message": "content"
    }

    for key, value in form_data.items():
        if key in mapping:
            combined_data[mapping[key]] = value
        elif key not in ["lastName", "firstName", "lastNameKana", "firstNameKana"]:  # 既に `氏名` `フリガナ` は統合済み
            combined_data[key] = value

    logging.info(f"🛠 変換後の入力データ: {combined_data}")
    return combined_data

def fill_contact_form(driver, form_data, screenshot_path):
    """問い合わせフォームにデータを入力し、送信する"""
    try:
        success = False
        form_data = preprocess_form_data(form_data)  # ✅ 事前変換
        logging.info(f"📝 変換後の入力データ: {form_data}")

        input_fields = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")

        logging.info(f"🔍 検出された入力フィールド数: {len(input_fields)}, テキストエリア数: {len(textareas)}")

        for field_name, field_value in form_data.items():
            field_element = None
            logging.info(f"📝 field_name: {field_name}, field_value: {field_value}")

            # **フォーム要素を検索**
            field_candidates = driver.find_elements(By.NAME, field_name)
            if not field_candidates:
                field_candidates = driver.find_elements(By.CSS_SELECTOR, f"input[name='{field_name}'], textarea[name='{field_name}']")
            if not field_candidates:
                field_candidates = driver.find_elements(By.XPATH, f"//input[@name='{field_name}'] | //textarea[@name='{field_name}']")
            
            if field_candidates:
                field_element = field_candidates[0]  # 最初に見つかった要素を使用
                logging.info(f"✅ フィールド '{field_name}' が見つかりました: {field_element.get_attribute('outerHTML')}")
            else:
                logging.error(f"❌ フィールド '{field_name}' が見つかりませんでした！")
                continue

            try:
                # **入力前の `value` を取得**
                before_value = field_element.get_attribute("value")
                logging.info(f"🔎 フィールド '{field_name}' の入力前の値: '{before_value}'")

                # **既に期待値が設定されている場合はスキップ**
                if before_value == field_value:
                    logging.info(f"✅ '{field_name}' は既に正しく入力済み: '{before_value}'")
                    continue

                # **readonly, disabled 属性を解除**
                driver.execute_script("arguments[0].removeAttribute('readonly');", field_element)
                driver.execute_script("arguments[0].removeAttribute('disabled');", field_element)

                # **JavaScript で `value` をセット**
                driver.execute_script("""
                    arguments[0].value = arguments[1]; 
                    arguments[0].dispatchEvent(new Event('input'));
                    arguments[0].dispatchEvent(new Event('change'));
                """, field_element, field_value)
                time.sleep(0.5)

                # **入力後の `value` を取得**
                final_value = field_element.get_attribute("value")
                logging.info(f"📌 フィールド '{field_name}' に入力: '{final_value}' (期待値: '{field_value}')")

                if final_value == field_value:
                    logging.info(f"✅ '{field_name}' に '{field_value}' を入力しました。")
                    success = True
                else:
                    logging.warning(f"⚠ '{field_name}' の入力に失敗！現在の値: '{final_value}'")

            except Exception as e:
                logging.error(f"❌ フィールド '{field_name}' の入力エラー: {e}")

        # # **スクリーンショット保存**
        # screenshot_path = "static/screenshots/form_filled.png"
        # capture_full_page_screenshot(driver,)
        # driver.save_screenshot(screenshot_path)
        # logging.info(f"📸 スクリーンショットを保存しました: {screenshot_path}")

        # スクリーンショット撮影
            capture_full_page_screenshot(driver, screenshot_path)
            logging.info(f"📸 スクリーンショットを保存しました: {screenshot_path}")

        # **送信ボタンを探してクリック**
        try:
            submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            logging.info(f"🚀 送信ボタンをクリックします: {submit_button.get_attribute('value')}")
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(3)
            success = True
        except:
            logging.error("❌ 送信ボタンが見つかりませんでした！")

        return success

    except Exception as e:
        logging.error(f"❌ フォーム入力中にエラー: {e}")
        return False


def match_form_field(name_attr, placeholder_attr):
    """フォームの name 属性や placeholder を基に適切な入力フィールドを特定"""
    if name_attr:
        for key, patterns in FORM_MAPPING.items():
            if any(pattern in name_attr.lower() for pattern in patterns):
                logging.info(f"✅ '{name_attr}' は '{key}' にマッピング")
                return key
    if placeholder_attr:
        for key, patterns in FORM_MAPPING.items():
            if any(pattern in placeholder_attr.lower() for pattern in patterns):
                logging.info(f"✅ '{placeholder_attr}' は '{key}' にマッピング")
                return key
    return None
