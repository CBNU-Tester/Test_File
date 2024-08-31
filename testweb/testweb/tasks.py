from background_task import background
from testsel.models import Ts, Tc, TcResult
from testsel.selenium_list import (
    process_click_xpath, process_click_xpath_otherurl, 
    process_click_xpath_div, process_click_xpath_iframe,
    process_send_xpath
)
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def get_next_run_times(schedule):
    now = make_aware(datetime.now())
    next_run_times = []

    start_time = schedule.ts_start

    if schedule.ts_repeat_interver == "daily":
        interval_count = int(schedule.ts_repeat_interval_value)
        interval_hours = 24 / interval_count

        while start_time < schedule.ts_end:
            for i in range(interval_count):
                run_time = start_time + timedelta(hours=interval_hours * i)
                if run_time >= now and run_time < schedule.ts_end:
                    next_run_times.append(run_time)
            start_time += timedelta(days=1)  # 다음 날로 이동

    elif schedule.ts_repeat_interver == "weekly":
        interval_count = int(schedule.ts_repeat_interval_value)
        while start_time < schedule.ts_end:
            for i in range(interval_count):
                run_time = start_time + timedelta(days=i*7)
                if run_time >= now and run_time < schedule.ts_end:
                    next_run_times.append(run_time)
            start_time += timedelta(weeks=1)  # 다음 주로 이동

    elif schedule.ts_repeat_interver == "monthly":
        interval_count = int(schedule.ts_repeat_interval_value)
        while start_time < schedule.ts_end:
            for i in range(interval_count):
                run_time = start_time + timedelta(days=i*30)  # 대략적인 한 달을 30일로 계산
                if run_time >= now and run_time < schedule.ts_end:
                    next_run_times.append(run_time)
            start_time += relativedelta(months=1)  # 다음 달로 이동

    return next_run_times


@background(schedule=60)  # 60초마다 실행
def check_and_run_scheduled_tests():
    now = make_aware(datetime.now())
    schedules = Ts.objects.filter(ts_start__lte=now, ts_end__gte=now)

    for schedule in schedules:
        next_run_times = get_next_run_times(schedule)

        for run_time in next_run_times:
            if abs((now - run_time).total_seconds()) <= 60:
                # 스케줄 실행
                run_test_case(schedule)
                break  # 이미 실행했으므로 다음 스케줄로 이동

def run_test_case(schedule):
    test_cases = Tc.objects.filter(tc_pid=schedule.tc_pid)

    for tc in test_cases:
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=chrome_options)

            main_url = tc.tc_url
            driver.get(main_url)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            main_page_status = "성공"
            failure_reason = ""  # 실패 사유가 없으므로 빈 문자열

            process_type = tc.tc_type
            target = tc.tc_target
            input_data = tc.tc_input
            result = tc.tc_result
            iframe_xpath = ''  # 필요 시 추가

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
                failure_reason = processed_data  # 실패 이유를 지원되지 않는 타입으로 설정

        except TimeoutException:
            main_page_status = "실패"
            failure_reason = "페이지 로딩 시간 초과"

        except Exception as e:
            main_page_status = "실패"
            failure_reason = str(e)  # 실패 사유로 예외 메시지를 저장

        finally:
            # 결과를 TcResult 모델에 저장
            TcResult.objects.create(
                test_pid=schedule.tc_pid,  # TcList의 tc_pid를 사용
                test_result=main_page_status,
                failure_reason=failure_reason
            )

            driver.quit()
    # 여기에 processed_data_list를 저장하거나 로그를 기록할 수 있음
