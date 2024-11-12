from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from testsel.models import Ts, Tc, TcResult, TcList, AuthUser
from testsel.selenium_list import (
    process_click_xpath, process_click_xpath_otherurl, 
    process_click_xpath_div, process_click_xpath_iframe,
    process_send_xpath
)
from django.shortcuts import get_object_or_404
from django.utils import timezone

# 스케줄러 인스턴스 생성
scheduler = BackgroundScheduler()

def check_and_run_scheduled_tests():

    now = timezone.now()
    print("Now:", now)
    next_minute = now + timedelta(seconds=60)  # 현재 시간 기준으로 1분 후 계산
    print("Next minute:", next_minute)

    # ts_time이 현재 시간과 1분 후 사이에 있는 스케줄만 선택
    schedules = Ts.objects.filter(ts_time__gte=now, ts_time__lt=next_minute)
    print("Schedules:", schedules)

    if not schedules.exists():
        print("No schedules found within the next 60 seconds.")
        return  # 스케줄이 없으면 종료
    
    for schedule in schedules:
        print(f"Running scheduled test for schedule ID: {schedule.tc_pid} at {schedule.ts_time}")
        print("Running test case...")
        
        tc_pid = schedule.tc_pid.tc_pid
        user_id = schedule.tc_uid.id
        tc_instance = TcList.objects.filter(tc_pid=tc_pid).first()  # 첫 번째 인스턴스를 가져오기
        print("tc_instance:", tc_instance)

        if not tc_instance:
            print(f"No TcList instance found for tc_pid: {tc_pid}")
            continue  # 인스턴스가 없으면 다음 스케줄로 넘어가기

        test_cases = Tc.objects.filter(tc_pid=tc_pid)
        print("test_cases:", test_cases)

        if not test_cases.exists():
            print(f"No test cases found for tc_pid: {tc_pid}")
            continue  # 테스트 케이스가 없으면 다음 스케줄로 넘어가기

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")  # Headless 모드 추가
        chrome_options.add_argument("--no-sandbox")  # 옵션 추가 (일부 환경에서는 필요)
        chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용 비활성화 (리소스 절약)
        

        ##원격 서버 사용시의 셋팅
        driver = webdriver.Remote(
            command_executor='http://' + os.getenv("DB_HOST") + ":" +os.getenv("SEL_PORT") + '/wd/hub',
            options=chrome_options
        )
        
        #driver = webdriver.Chrome(options=chrome_options)

        main_page_status = "성공"
        all_success = True
        failure_reasons = []

        #첫 url 가져오기
        main_url = test_cases.first().tc_url
        driver.get(main_url)

        for tc in test_cases:
            try:
                process_type = tc.tc_type
                target = tc.tc_target
                input_data = tc.tc_input
                result = tc.tc_result
                iframe_xpath = ''  # 필요 시 추가

                # 각 process_type에 따라 처리
                if process_type == 'process_click_xpath':
                    processed_data = process_click_xpath(driver, main_url, target, input_data, result)
                elif process_type == 'process_click_xpath_otherurl':
                    processed_data = process_click_xpath_otherurl(driver, main_url, target, input_data, result)
                elif process_type == 'process_click_xpath_div':
                    processed_data = process_click_xpath_div(driver, main_url, target, input_data, result)
                elif process_type == 'process_click_xpath_iframe':
                    processed_data = process_click_xpath_iframe(driver, main_url, target, input_data, result, iframe_xpath)
                elif process_type == 'process_send_xpath':
                    processed_data = process_send_xpath(driver, main_url, target, input_data, result)
                else:
                    processed_data = f"Unsupported process type: {process_type}"
                    main_page_status = "실패"
                    failure_reason = processed_data

                if processed_data != "성공":
                    all_success = False
                    failure_reasons.append(f"Type: {process_type}, Target: {target}, Result: {processed_data}")
            except TimeoutException:
                main_page_status = "실패"
                failure_reason = "페이지 로딩 시간 초과"

            except Exception as e:
                main_page_status = "실패"
                failure_reason = str(e)

        driver.quit()

        # Determine final test result
        main_page_status = "성공" if all_success else "실패"
        failure_reason = "; ".join(failure_reasons) if not all_success else ""

        # 테스트 결과 저장
        try:
            TcResult.objects.create(
                test_pid=tc_instance,  # 필드와 실제 모델 참조 확인
                test_uid=get_object_or_404(AuthUser, pk=user_id),
                test_result=main_page_status,
                failure_reason=failure_reason
            )
        except Exception as e:
            print(f"Error saving test result: {e}")


scheduler.add_job(check_and_run_scheduled_tests, 'interval', seconds=60)

# 스케줄러에서 1분마다 check_and_run_scheduled_tests 실행
# 스케줄러 초기화 코드
def start_scheduler():
    scheduler.start()