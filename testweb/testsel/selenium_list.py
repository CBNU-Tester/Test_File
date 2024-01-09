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

def process_url(url):
    # Selenium 코드 작성 (예시)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 헤드리스 모드로 실행 (화면 표시 X)

    driver = webdriver.Chrome(options=chrome_options)

    # URL을 Selenium으로 열고 처리
    driver.get(url)

    # 결과 가져오기 (예시)
    processed_data = driver.title

    return processed_data

def process_click(url):
    chrome_options = Options()

    driver = webdriver.Chrome(options=chrome_options)
    
    processed_data = driver.title
    return processed_data

#1. 일반적인 클릭의 경우
def process_click_xpath(url, target, input, result):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    print("test")
    try:
        target_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )

        target_element.click()
        processed_data = "성공"

    except TimeoutException:
        processed_data = "시간초과"

    finally:
        driver.quit()

    return processed_data

#2. 클릭했을때 다른 URL로 넘어가는 경우 
def process_click_xpath_otherurl(url, target, input, expected_url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        
        target_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )

        initial_url = driver.current_url
        target_element.click()
        new_url = driver.current_url

        if new_url == expected_url:
            processed_data = "성공"
        else:
            processed_data = f"URL 불일치: 기대한 URL은 {expected_url}이지만, 실제 URL은 {new_url}입니다."

    except TimeoutException:
        processed_data = "시간초과"

    finally:
        driver.quit()

    return processed_data


#3. 클릭했을때 해당 특정요소 탐지
def process_click_xpath_div(url, target, input, result_xpath):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        #클릭 가능한지 확인
        target_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )

        #클릭
        target_element.click()

        #새롭게나타난 요소 탐지
        result_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, result_xpath))
        )
        processed_data = "성공"

    except TimeoutException:
        processed_data = "시간초과"

    finally:
        driver.quit()

    return processed_data
 

##########################################################입력 이벤트###########################################################

def process_send_xpath(url, target, input, result):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        input_element = driver.find_element(By.XPATH, target)
        input_element.send_keys(input)  

        target_element = driver.find_element(By.XPATH, target)
        target_element.click()

    except TimeoutException:
        processed_data = "Timeout: Unable to perform the action."

    finally:
        driver.quit()

    return processed_data

