from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.common.action_chains import ActionChains
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
            EC.presence_of_element_located((By.XPATH, target))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
        time.sleep(2)  # Optional delay
        # 자식 요소 클릭하기
        target_element.click()
        processed_data = "성공"
        
    except TimeoutException:
        processed_data = "시간초과"
        
    return processed_data

#2. 클릭했을때 다른 URL로 넘어가는 경우 
def process_click_xpath_otherurl(driver, url, target, input, expected_url):
    try:
        # 요소가 클릭 가능한 상태일 때까지 기다림
        target_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target))
        )
        time.sleep(2)  # Optional delay
        
        # JavaScript를 사용하여 클릭
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
        time.sleep(2)  # Optional delay
        driver.execute_script("arguments[0].click();", target_element)

        # 새로운 URL 확인
        WebDriverWait(driver, 10).until(EC.url_changes(url))  # URL 변경을 기다림
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
            EC.presence_of_element_located((By.XPATH, target))
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
            EC.presence_of_element_located((By.XPATH, target))
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
import time
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

def process_send_xpath(driver, url, target, input, result):
    try:
        # Xpath로 요소를 찾고 기다립니다.
        input_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target))
        )

        # 요소로 스크롤 이동 (커서가 해당 위치에 있도록 함)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", input_element)
        
        # 약간의 대기 시간을 줘서 스크롤 완료 후 안정화
        time.sleep(2)  # 대기 시간을 늘려 안정성 향상
        WebDriverWait(driver, 4).until(EC.visibility_of(input_element))
        
        # 기존 값 지우기
        input_element.clear()
        
        # send_keys()로 값을 입력해보고, 실패하면 JavaScript로 설정
        input_element.send_keys(input)
        
        # send_keys()로 값이 입력되었는지 확인
        if input_element.get_attribute("value") == input:
            processed_data = "성공"
        else:
            # JavaScript로 값 입력 시도
            driver.execute_script("arguments[0].value = arguments[1];", input_element, input)
            
            # JavaScript로 값이 입력되었는지 확인
            if input_element.get_attribute("value") == input:
                processed_data = "성공"
            else:
                processed_data = "실패"
                
    except TimeoutException:
        processed_data = "시간초과"
    except Exception as e:
        processed_data = f"오류 발생: {str(e)}"
    
    return processed_data

