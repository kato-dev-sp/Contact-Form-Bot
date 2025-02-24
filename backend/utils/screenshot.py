from PIL import Image
import io
import time

def capture_full_page_screenshot(driver, save_path):
    """ページ全体をスクロールしながらスクリーンショットを撮影し、1枚の画像に結合"""
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")

    screenshot_parts = []
    for y in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(0.5)
        screenshot = driver.get_screenshot_as_png()
        screenshot_image = Image.open(io.BytesIO(screenshot))
        screenshot_parts.append(screenshot_image)

    full_screenshot = Image.new('RGB', (screenshot_parts[0].width, sum(img.height for img in screenshot_parts)))
    y_offset = 0
    for part in screenshot_parts:
        full_screenshot.paste(part, (0, y_offset))
        y_offset += part.height

    full_screenshot.save(save_path)
