from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# 브라우저 꺼짐 방지 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Chrome 웹 드라이버 초기화
driver = webdriver.Chrome(options=chrome_options)

# 네이버 홈페이지로 이동
url = 'http://113.198.137.123:8080/UI/analysis/381280/'
driver.get(url)

# 검색 입력 필드가 나타날 때까지 대기
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'ResultInputNum'))
)

# 검색어 입력 및 엔터키 전송
element.send_keys('5')
element.send_keys(Keys.RETURN)

# 시간초를 설정하는 곳
time.sleep(10)

# 초기 URL 가져오기
initial_url = driver.current_url

# 'next-summary-button' 클래스를 가진 요소를 반복해서 찾아 클릭
while True:
    try:
        # 'next-summary-button' 클래스를 가진 요소가 클릭 가능할 때까지 대기
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'next-summary-button'))
        )
        # 'next-summary-button' 클래스를 가진 요소를 클릭
        next_button.click()

        # URL이 변화했는지 확인
        if driver.current_url != initial_url:
            initial_url = driver.current_url
        else:
            # URL이 변하지 않으면 메시지를 출력하고 반복문을 종료
            print("페이지의 끝에 도달했습니다. 더 이상 'next-summary-button'이 없습니다.")
            break

        # 컨텐츠가 없다면
        if not driver.find_element(By.ID, 'next-summary-content').text.strip():
            print("No content in 'next-summary-content'. Exiting the loop.")
            break

    except TimeoutException:
        # 'next-summary-button'이 지정된 시간 내에 찾아지지 않을 때 TimeoutException이 발생
        print("페이지의 끝에 도달했습니다. 더 이상 'next-summary-button'이 없습니다.")
        break
