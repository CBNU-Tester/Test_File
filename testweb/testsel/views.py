from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # User 모델 가져오기
import json
from .models import TcList, Ts, Tc,AuthUser
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
                
                dynamic_inputs_list = data.get('dynamic_inputs', [])
                for item in dynamic_inputs_list:
                    process_type = item.get('type')
                    target = item.get('target')
                    input_data = item.get('input')
                    result = item.get('result')
                    iframe_xpath = item.get('iframe_xpath', '')  # 추가

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

                    processed_data_list.append({
                        'type': process_type,
                        'target': target,
                        'input': input_data,
                        'result': result,
                        'processed_data': processed_data,
                    })

                driver.quit()
                return JsonResponse({'processed_data_list': processed_data_list})

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)

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
            print("TcList 저장 완료") 
            print(test_list_instance)

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

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tc_pid = request.POST.get('tc_pid')
            try:
                # 해당 테스트 케이스 삭제
                test_case = TcList.objects.get(tc_pid=tc_pid, tc_uid=user_id)
                test_case.delete()
                return JsonResponse({'success': True})
            except TcList.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Test case not found.'})
        return JsonResponse({'success': False, 'message': 'Invalid request.'})
    
class RecordView(LoginRequiredMixin, TemplateView):
    template_name='base.html'
