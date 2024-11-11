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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#1. 클릭 후 결과 확인
def process_click_xpath(driver, url, target, input, result):
    try:
        # 요소가 로드될 때까지 기다림
        target_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target))
        )
        
        # 요소가 클릭 가능한지 확인
        if WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, target))):
            # 클릭 가능한 상태라면 일반적인 클릭
            target_element.click()
            processed_data = "성공"
        else:
            # 클릭할 수 없다면 존재 여부를 확인하고 강제로 클릭
            if target_element.is_displayed():  # 요소가 화면에 표시되었는지 확인
                # 요소가 보이면 JavaScript를 사용하여 클릭을 강제로 시도
                driver.execute_script("arguments[0].click();", target_element)
                processed_data = "성공 (JavaScript로 강제 클릭)"
            else:
                processed_data = "요소가 보이지 않음"
                
        # 클릭 후 URL 변경 등을 확인하는 부분을 추가할 수 있음
        time.sleep(2)  # Optional delay
        
    except TimeoutException:
        processed_data = "시간초과"
    except Exception as e:
        processed_data = f"클릭 실패: {str(e)}"
        
    return processed_data


#2. 클릭 후 다른 URL로 이동하는 경우
def process_click_xpath_otherurl(driver, url, target, input, expected_url):
    try:
        # 요소가 로드될 때까지 기다림
        target_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target))
        )
        
        # 요소가 클릭 가능한지 확인
        if WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, target))):
            # 일반적인 클릭 시도
            target_element.click()
            print("일반 클릭 시도")
        else:
            # 요소가 화면에 보이는지 확인 후 강제 클릭 시도
            if target_element.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
                time.sleep(1)  # Optional delay
                driver.execute_script("arguments[0].click();", target_element)
                print("JavaScript 클릭 시도")
            else:
                processed_data = "요소가 보이지 않음"
                return processed_data

        # URL 변경 확인 - 최종 URL에 도달할 때까지 확인
        timeout = 10  # 최대 대기 시간 (초)
        poll_frequency = 0.5  # 확인 주기 (초)
        start_time = time.time()
        
        # 최종 URL이 expected_url에 도달할 때까지 확인
        while time.time() - start_time < timeout:
            new_url = driver.current_url
            print(f"현재 URL 확인: {new_url}")
            if new_url == expected_url:
                print(f"최종 URL 도달: {new_url}")
                processed_data = "성공"
                break
            time.sleep(poll_frequency)
        else:
            processed_data = f"URL 불일치: 기대한 URL은 {expected_url}이지만, 실제 URL은 {driver.current_url}입니다."

    except TimeoutException:
        processed_data = "시간초과"
    except Exception as e:
        processed_data = f"예외 발생: {e}"

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

#5. 새 창이 열렸는지 확인하는 함수
def process_click_check_new_window(driver, target_xpath):
    original_windows = driver.window_handles  # 현재 열린 모든 창 핸들 저장
    processed_data = "새 창 없음"  # 기본 결과는 새 창 없음으로 설정

    try:
        # 타겟 요소를 기다렸다가 클릭
        target_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, target_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
        time.sleep(2)  # Optional delay
        target_element.click()
        
        # 새 창이 열렸는지 확인
        WebDriverWait(driver, 10).until(EC.new_window_is_opened(original_windows))
        processed_data = "새 창 열림"  # 새 창이 열리면 결과 업데이트

    except TimeoutException:
        processed_data = "시간초과 - 새 창 없음"

    return processed_data

def process_click_and_check_html_change(driver, click_xpath, result_html_snippet, timeout=20):
    """
    클릭 후, 바뀐 HTML을 확인하여 주어진 HTML 스니펫이 존재하는지 확인하는 함수
    """
    try:
        # 1. 클릭할 요소를 찾고 클릭
        element_to_click = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, click_xpath))
        )
        element_to_click.click()
        time.sleep(2)  # 클릭 후 잠시 대기 (필요에 따라 조정)

        # 2. 페이지가 로드되고 나서 전체 HTML을 가져옴
        current_html = driver.page_source  # 현재 HTML을 가져옵니다.

        # 3. HTML에서 변경된 부분 확인
        if result_html_snippet in current_html:
            return "변경된 HTML이 존재합니다."
        else:
            return "변경된 HTML이 존재하지 않습니다."

    except Exception as e:
        print(f"에러 발생: {e}")
        return "에러 발생"


# 클릭 하고 나서 특정 요소가 화면에 나타날 때까지 대기하는 함수
def process_click_and_check_visibility(driver, target_xpath, result_xpath, timeout=20):
    try:
        # target 요소가 로드될 때까지 대기
        target_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, target_xpath))
        )
        
        # 요소를 화면 중앙으로 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", target_element)
        time.sleep(2)  # Optional delay
        
        # target 요소 클릭
        target_element.click()
        
        # result 요소가 화면에 표시될 때까지 대기
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, result_xpath))
        )
        
        processed_data = "성공"
        
    except TimeoutException:
        processed_data = "시간초과"
        
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

