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
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    processed_data = driver.title
    return processed_data

def process_click(url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    processed_data = driver.title
    return processed_data

#1. 일반적인 클릭의 경우
def process_click_xpath(driver, url, target, input, result):
    try:
        target_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        target_element.click()
        processed_data = "성공"
    except TimeoutException:
        processed_data = "시간초과"
    return processed_data

#2. 클릭했을때 다른 URL로 넘어가는 경우 
def process_click_xpath_otherurl(driver, url, target, input, expected_url):
    try:
        target_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        target_element.click()
        new_url = driver.current_url
        if new_url == expected_url:
            processed_data = "성공"
        else:
            processed_data = f"URL 불일치: 기대한 URL은 {expected_url}이지만, 실제 URL은 {new_url}입니다."
    except TimeoutException:
        processed_data = "시간초과"
    return processed_data

#3. 클릭했을때 특정요소 생성 탐지
def process_click_xpath_div(driver, url, target, input, result_xpath):
    try:
        target_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        target_element.click()
        result_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, result_xpath))
        )
        processed_data = "성공"
    except TimeoutException:
        processed_data = "시간초과"
    return processed_data

#4. 클릭시 iframe 내부의 로직 탐지
def process_click_xpath_iframe(driver, url, target, input, result_xpath, iframe_xpath):
    try:
        target_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        target_element.click()
        iframe_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, iframe_xpath))
        )
        driver.switch_to.frame(iframe_element)
        result_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, result_xpath))
        )
        processed_data = "성공"
    except TimeoutException:
        processed_data = "시간초과"
    finally:
        driver.switch_to.default_content()
    return processed_data

##########################################################입력 이벤트###########################################################

# 1. xpath 탐지하여 값만 추가
def process_send_xpath(driver, url, target, input, result):
    try:
        input_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        input_element.send_keys(input)
        processed_data = "성공"
    except TimeoutException:
        processed_data = "시간초과"
    return processed_data

