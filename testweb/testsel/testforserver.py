from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Chrome 옵션 설정
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # GUI 없이 실행

driver = None

try:
    driver = webdriver.Remote(
        command_executor='알아서 적어',
        options=options
    )
    print("Connected successfully to the Selenium Grid.")

    # 타겟 URL 열기
    target_url = 'https://www.naver.com'
    print(f"Navigating to {target_url}...")
    driver.get(target_url)
    page_source = driver.page_source
    print(f"Page source: {page_source}")
    print("Page loaded successfully.")

except Exception as e:
    print(f"Error during Selenium Grid connection or page load: {e}")
finally:
    # 드라이버 종료
    try:
        driver.quit()
        print("Driver closed successfully.")
    except Exception as e:
        print(f"Error during driver closure: {e}")
