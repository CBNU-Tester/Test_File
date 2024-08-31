from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # User 모델 가져오기
import json
from .models import TcList, Ts, Tc,AuthUser,TcResult
from .selenium_list import (
    process_click_xpath, process_click_xpath_otherurl, 
    process_click_xpath_div, process_click_xpath_iframe,
    process_send_xpath
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime

class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

class ProcessView(LoginRequiredMixin, TemplateView):
    template_name = 'process.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        tc_pid = request.GET.get('tc_pid')  # 'test_name' 대신 'tc_pid'로 변경

        if tc_pid:
            filtered_tests = Tc.objects.filter(tc_pid=tc_pid).values()
            return render(request, self.template_name, {'data': list(filtered_tests), 'tc_pid': tc_pid})
        
        return render(request, self.template_name, {'data': [], 'tc_pid': None})

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        processed_data_list = []
        data = json.loads(request.body.decode('utf-8'))
        action_type = data.get('action_type', '')

        if action_type == 'test':
            try:
                data = json.loads(request.body)

                # Get tc_pid from query parameters
                tc_pid = data.get('tc_pid')

                if not tc_pid:
                    return JsonResponse({'error': 'Missing tc_pid parameter'}, status=400)
                
                # Fetch test case
                tc_instance = get_object_or_404(TcList, tc_pid=tc_pid)

                chrome_options = Options()
                chrome_options.add_experimental_option("detach", True)
                driver = webdriver.Chrome(options=chrome_options)

                main_url = data.get('main_url', '')
                driver.get(main_url)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    main_page_status = "성공"
                except TimeoutException:
                    main_page_status = "시간초과"

                # Initialize success flag and failure reasons
                all_success = True
                failure_reasons = []

                dynamic_inputs_list = data.get('dynamic_inputs', [])
                processed_data_list = []

                for item in dynamic_inputs_list:
                    process_type = item.get('type')
                    target = item.get('target')
                    input_data = item.get('input')
                    result = item.get('result')
                    iframe_xpath = item.get('iframe_xpath', '')

                    try:
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

                        # Append processed data to list
                        processed_data_list.append({
                            'type': process_type,
                            'target': target,
                            'input': input_data,
                            'result': result,
                            'processed_data': processed_data,
                        })

                        # Check if processed data indicates a failure
                        if processed_data != "성공":
                            all_success = False
                            failure_reasons.append(f"Type: {process_type}, Target: {target}, Result: {processed_data}")

                    except Exception as e:
                        print(f"Error processing item {item}: {e}")
                        all_success = False
                        failure_reasons.append(f"Error processing item {item}: {e}")

                driver.quit()

                # Determine final test result
                test_final_result = "성공" if all_success else "실패"
                failure_reason = "; ".join(failure_reasons) if not all_success else ""

                # Save results
                TcResult.objects.create(
                    test_pid=tc_instance,
                    test_uid = get_object_or_404(AuthUser, pk=user_id),
                    test_result=test_final_result,
                    failure_reason=failure_reason
                )

                return JsonResponse({'processed_data_list': processed_data_list})

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        elif action_type == 'save':
            save_data_list = []
            main_url = data.get('main_url', '')
            test_name = data.get('test_name', '')
            test_desciption = data.get('test_description', '')
            dynamic_inputs_list = data.get('dynamic_inputs', [])

            # AuthUser 모델에서 사용자 객체를 가져옴
            user_instance = get_object_or_404(AuthUser, pk=user_id)

            # TcList에 저장
            test_list_instance = TcList(
                tc_uid=user_instance,  # ForeignKey이므로 AuthUser 객체로 설정
                tc_name=test_name,
                tc_describe = test_desciption
            )
            test_list_instance.save()  # 데이터 저장 후 tc_pid 생성

            # 저장된 TcList 객체의 tc_pid 가져오기
            tc_pid = test_list_instance  # tc_pid는 TcList 인스턴스를 참조해야 함

            for item in dynamic_inputs_list:
                try:
                    # Tc에 저장
                    test_save_instance = Tc(
                        tc_type=item.get('type', ''),
                        tc_url=main_url,
                        tc_target=item.get('target', ''),
                        tc_input=item.get('input', ''),
                        tc_result=item.get('result', ''),
                        tc_pid=tc_pid  # 저장된 TcList의 인스턴스 사용
                    )

                    # 데이터 저장
                    test_save_instance.save()
                    print("Tc 저장 성공: ", test_save_instance)  # 성공 메시지 출력

                    save_data_list.append({
                        'saved_data': f"Save successful for input: {item}",
                    })
                
                except Exception as e:
                    print(f"Error saving Tc instance: {e}")  # 오류 메시지 출력
                    save_data_list.append({
                        'error': f"Error saving for input: {item}, Error: {str(e)}",
                    })

            return JsonResponse({'save_data_list': save_data_list})

        elif action_type == 'load': #테스트 케이스 생성에서 테스트 케이스 각 이름들 간단하게 불러오는 기능
            testInfo = TcList.objects.filter(tc_uid=user_id).values_list('tc_pid','tc_name').distinct()
            return JsonResponse({'testInfo': list(testInfo)})

        elif action_type == 'db_load': #load에서 버튼을 누르면 그 정보로 테스트 케이스 불러오기
            selectedTestPID = data.get('selectedTest')
            filtered_tests = Tc.objects.filter(tc_pid=selectedTestPID).values()
            return JsonResponse({'data': list(filtered_tests)})

        else:
            return JsonResponse({'error': 'Unsupported action type'}, status=400)

class ProcessListView(LoginRequiredMixin, TemplateView):
    template_name = 'processList.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # 사용자와 연결된 테스트 케이스 목록 가져오기
        tests = TcList.objects.filter(tc_uid=user_id).values_list('tc_pid', 'tc_name').distinct()
        # 테스트 케이스 목록을 템플릿으로 전달
        return self.render_to_response({'tests': tests})

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        # AJAX 요청 확인
        user_id = get_object_or_404(AuthUser, pk=request.user.id)
        action = request.POST.get('action', '')

        if action == 'delete':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                tc_pid = request.POST.get('tc_pid')
                try:
                    # 해당 테스트 케이스 삭제
                    test_case = TcList.objects.get(tc_pid=tc_pid, tc_uid=user_id)
                    test_case.delete()
                    return JsonResponse({'success': True})
                except TcList.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Test case not found.'})
        elif action == 'description':
            des = TcList.objects.filter(tc_pid=request.POST.get('tc_pid'))
            return JsonResponse({'success' : True, 'description': des[0].tc_describe})
        
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        user_id = request.user.id

        if request.POST.get('action') == 'get_tests':
            # 현재 사용자가 소유한 테스트 케이스 목록 가져오기
            tests = TcList.objects.filter(tc_uid=user_id).values('tc_pid', 'tc_name').distinct()
            return JsonResponse({'tests': list(tests)})

        elif request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                dynamic_inputs = data.get('dynamic_inputs')
                tc_pid = data.get('tc_pid')
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                repeat_interval = data.get('repeat_interval')
                repeat_interval_value = data.get('repeat_interval_value')

                # 시작일과 종료일을 DateTime 형식으로 변환
                start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
                end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

                # 유저 인스턴스 가져오기
                user_instance = get_object_or_404(AuthUser, pk=user_id)

                # 스케줄 생성
                schedule = Ts.objects.create(
                    tc_uid=user_instance,  # AuthUser 인스턴스를 할당
                    ts_start=start_date,
                    ts_end=end_date,
                    ts_repeat_interver=repeat_interval,
                    ts_repeat_interval_value=repeat_interval_value
                )

                # TcList에서 연결된 테스트 케이스 찾기
                test_case = get_object_or_404(TcList, tc_pid=tc_pid, tc_uid=user_instance)
                
                # 스케줄의 테스트 케이스 ID 저장
                schedule.tc_pid = test_case
                schedule.save()

                return JsonResponse({'message': '스케줄 저장 성공'}, status=200)

            except Exception as e:
                print(e)
                return JsonResponse({'error': '스케줄 저장 중 오류가 발생했습니다.'}, status=400)

        return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

class ScheduleListView(LoginRequiredMixin, TemplateView):
    template_name = 'scheduleList.html'

class ResultListView(LoginRequiredMixin, TemplateView):
    template_name = 'resultList.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # 사용자와 연결된 테스트 케이스 목록 가져오기
        tests = TcResult.objects.filter(tc_uid=user_id).values_list('tc_pid', 'tc_name').distinct()
        # 테스트 케이스 목록을 템플릿으로 전달
        return self.render_to_response({'tests': tests})

class RecordView(LoginRequiredMixin, TemplateView):
    template_name='base.html'
