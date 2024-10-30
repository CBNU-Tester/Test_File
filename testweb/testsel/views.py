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
from django.utils.dateparse import parse_datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.views.generic import TemplateView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import TcResult, Ts
from django.db.models import Count
from django.db.models.functions import TruncDate
from .modelCode.main import create_main
from dotenv import load_dotenv
import os

class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

class ProcessView(LoginRequiredMixin, TemplateView):
    template_name = 'process.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        tc_pid = request.GET.get('tc_pid')  # 'test_name' 대신 'tc_pid'로 변경

        if tc_pid:
            filtered_tests = Tc.objects.filter(tc_pid=tc_pid).values()
            return render(request, self.template_name, {'data': list(filtered_tests), 'tc_pid': tc_pid,
                                                        'test_name' : TcList.objects.filter(tc_pid=tc_pid).values_list('tc_name')[0][0],
                                                        'test_description' : TcList.objects.filter(tc_pid=tc_pid).values_list('tc_describe')[0][0]})
                                                                        
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
                chrome_options.add_argument("--headless")  # Headless 모드 추가
                chrome_options.add_argument("--no-sandbox")  # 옵션 추가 (일부 환경에서는 필요)
                chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용 비활성화 (리소스 절약)
                
                driver = webdriver.Remote(
                    command_executor='http://' + os.getenv("DB_HOST") + ":" +os.getenv("SEL_PORT") + '/wd/hub',
                    options=chrome_options
                )
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
            tc_pid = data.get('tc_pid', '')
            user_instance = get_object_or_404(AuthUser, pk=user_id)


            if tc_pid != '':
                test_case = get_object_or_404(TcList, tc_pid=tc_pid, tc_uid=user_instance)
                test_case.tc_name = test_name
                test_case.tc_describe = test_desciption
                test_case.save()
                
                #이전 tc_pid에 연결된 Tc들 삭제
                Tc.objects.filter(tc_pid=tc_pid).delete()

                for item in dynamic_inputs_list:
                    try:
                        # Tc에 저장
                        test_save_instance = Tc(
                            tc_type=item.get('type', ''),
                            tc_url=main_url,
                            tc_target=item.get('target', ''),
                            tc_input=item.get('input', ''),
                            tc_result=item.get('result', ''),
                            tc_pid=test_case  # 저장된 TcList의 인스턴스 사용
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

            else:
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

        elif action_type == 'ai':
            url = data.get('url', '')
            data =create_main(url)

            tc_objects = []

            for item in data:
                tc_data = {
                    'tc_type': item.get('type_', None),
                    'tc_url': item.get('url', None),
                    'tc_target': item.get('xPath', None),
                    'tc_input': None,
                    'tc_result': item.get('href', None),
                }
                tc_objects.append(tc_data)

            return JsonResponse({'data': list(tc_objects)})

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
                ts_time = data.get('schedule_time')

                # ts_time을 DateTime 형식으로 변환
                ts_time = datetime.strptime(ts_time, '%Y-%m-%dT%H:%M')

                # 유저 인스턴스 가져오기
                user_instance = get_object_or_404(AuthUser, pk=user_id)

                # 스케줄 생성
                schedule = Ts.objects.create(
                    tc_uid=user_instance,  # AuthUser 인스턴스를 할당
                    ts_time=ts_time
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

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # Fetch schedules associated with the user
        schedules = Ts.objects.filter(tc_uid=user_id).order_by('-ts_time').values_list()

        schedule_data = []

        for schedule in schedules:
            test_name = TcList.objects.filter(tc_pid=schedule[1]).values_list('tc_name')
            schedule_info = {
                'ts_num': schedule[0],
                'tc_pid': schedule[1],
                'ts_time': schedule[3],
                'test_name': test_name[0][0]
            }
            schedule_data.append(schedule_info)
        
        return self.render_to_response({'schedules': schedule_data, 'test_data' : TcList.objects.filter(tc_uid=user_id).values_list('tc_pid','tc_name')})

    def post(self, request):
        user_id = request.user.id
        action = request.POST.get('action', '')

        if action == 'delete':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                ts_num = request.POST.get('ts_num')
                try:
                    # Delete the specified schedule
                    schedule = Ts.objects.get(ts_num=ts_num, tc_uid=user_id)
                    schedule.delete()
                    return JsonResponse({'success': True})
                except Ts.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Schedule not found.'})
        
        elif action == 'update':
            ts_num = request.POST.get('ts_num')
            ts_time = request.POST.get('schedule_time')
            tc_pid = request.POST.get('tc_pid')
            tc_pid = get_object_or_404(TcList, tc_pid=tc_pid, tc_uid=user_id)

            try:
                # Update the specified schedule with the new time and test case ID
                schedule = Ts.objects.get(ts_num=ts_num, tc_uid=user_id)
                schedule.ts_time = ts_time
                schedule.tc_pid = tc_pid
                schedule.save()
                return JsonResponse({'success': True})
            except Ts.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Schedule not found.'})
        
        elif action == 'get_tests':
            # Fetch available test cases for the select bar
            tests = TcList.objects.filter(tc_uid=user_id).values('tc_pid', 'tc_name')
            tests_list = list(tests)
            return JsonResponse({'success': True, 'tests': tests_list})

        return JsonResponse({'success': False, 'message': 'Invalid request.'})
    
class ResultListView(LoginRequiredMixin, TemplateView):
    template_name = 'resultList.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # 사용자와 연결된 테스트 케이스 목록 가져오기
        tests = TcResult.objects.filter(test_uid=user_id).order_by('-test_time').values_list()
        
        #맨 마지막에 TC_LIST에서 가져온테스트 이름 추가하기
        
        test_data = []

        for test in tests:
            test_name = TcList.objects.filter(tc_pid=test[1]).values_list('tc_name')
            test_info = {
                'result_id': test[0],
                'test_pid': test[1],
                'test_uid': test[5],
                'failure_reason': test[3],
                'test_time': test[4],
                'test_result' : test[2],
                'test_name' : test_name[0][0]
            }
            test_data.append(test_info)
        # 테스트 케이스 목록을 템플릿으로 전달
        return self.render_to_response({'tests': test_data})
    
    def post(self, request):
        user_id = request.user.id
        action = request.POST.get('action', '')

        if action == 'delete':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                result_id = request.POST.get('result_id')
                try:
                    # 해당 테스트 결과 삭제
                    test_case = TcResult.objects.get(result_id=result_id, test_uid=user_id)
                    test_case.delete()
                    return JsonResponse({'success': True})
                except TcResult.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Test case not found.'})
        elif action == 'description':
            des = TcResult.objects.filter(result_id=request.POST.get('result_id'))
            print(des)
            return JsonResponse({'success' : True, 'description': des[0].failure_reason})
        
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id

        # 이번 달의 시작일과 종료일 설정
        now = timezone.now()
        start_of_month = now.replace(day=1)
        end_of_month = (start_of_month + pd.DateOffset(months=1)).replace(day=1) - pd.DateOffset(days=1)

        # 전체 테스트 결과 데이터 가져오기 (현재 사용자 기준)
        total_tests = TcResult.objects.filter(test_uid=user_id).count()
        failed_tests = TcResult.objects.filter(test_uid=user_id, test_result='실패').count()
        success_tests = total_tests - failed_tests
        failure_percentage = (failed_tests / total_tests * 100) if total_tests > 0 else 0

        # 이번 주에 실행된 테스트 수 (현재 사용자 기준)
        start_of_week = now - timezone.timedelta(days=now.weekday())
        tests_this_week = TcResult.objects.filter(test_uid=user_id, test_time__gte=start_of_week).count()

        # 최근 실행된 테스트 항목 3개 (현재 사용자 기준)
        recent_tests = TcResult.objects.filter(test_uid=user_id).order_by('-test_time')[:3]

        # 현재 시간을 기준으로 가장 빨리 실행될 스케줄 3개 (현재 사용자 기준)
        upcoming_schedules = Ts.objects.filter(tc_uid=user_id, ts_time__gte=now).order_by('ts_time')[:3]

        # 이번 달 날짜별 테스트 횟수 조회
        daily_test_data = (TcResult.objects.filter(test_uid=user_id, test_time__gte=start_of_month)
                           .annotate(day=TruncDate('test_time'))
                           .values('day')
                           .annotate(test_count=Count('result_id'))
                           .order_by('day'))

        # 이번 달 1일부터 말일까지 날짜 생성
        full_dates = pd.date_range(start=start_of_month, end=end_of_month)
        date_map = {data['day']: data['test_count'] for data in daily_test_data}

        # x축: 이번 달의 모든 날짜, y축: 테스트 횟수
        dates = [day.date() for day in full_dates]
        counts = [date_map.get(day.date(), 0) for day in full_dates]

        # Line + Bar chart for this month's test records with x-axis as all days of the month
        fig = go.Figure()

        # Line graph
        fig.add_trace(go.Scatter(x=dates, y=counts, mode='lines', name='테스트 횟수 (라인)', line=dict(color='royalblue')))

        # Bar graph
        fig.add_trace(go.Bar(x=dates, y=counts, name='테스트 횟수 (막대)', marker_color='lightblue'))

        # Layout 업데이트 (x축 제목, y축 제목, 제목 위치)
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="횟수",
            title="이번 달 테스트 기록",
            title_x=0.5,
            bargap=0.2,  # 막대 간격
            template='plotly_white'
        )

        line_chart = fig.to_html(full_html=False)

        # Pie chart for test results
        labels = ['성공', '실패']
        values = [success_tests, failed_tests]
        pie_fig = px.pie(names=labels, values=values, title="테스트 결과 성공/실패 비율")
        pie_fig.update_layout(title_x=0.5)  # 제목을 가운데 정렬
        pie_chart = pie_fig.to_html(full_html=False)

        context.update({
            'failure_percentage': failure_percentage,
            'tests_this_week': tests_this_week,
            'recent_tests': recent_tests,
            'upcoming_schedules': upcoming_schedules,
            'line_chart': line_chart,  # 이번 달 테스트 기록 (Line + Bar)
            'pie_chart': pie_chart,    # 성공/실패 비율 파이 차트
        })
        return context

class RecordView(LoginRequiredMixin, TemplateView):
    template_name='base.html'