from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, HttpResponseBadRequest
import json
from .models import TestSave, TestSchedule, TestResult
from .forms import TestScheduleForm
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

class BaseView(TemplateView):
    template_name = 'base.html'

class ProcessView(TemplateView):
    template_name = 'process.html'

    def get(self, request, *args, **kwargs):
        test_name = request.GET.get('test_name')

        if test_name:
            selected_test_names = [test_name]
            filtered_tests = TestSave.objects.filter(test_name__in=selected_test_names).values()
            return render(request, self.template_name, {'data': list(filtered_tests), 'test_name': test_name})
        
        return render(request, self.template_name, {'data': [], 'test_name': None})

    def post(self, request, *args, **kwargs):
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
            dynamic_inputs_list = data.get('dynamic_inputs', [])
            for item in dynamic_inputs_list:
                test_save_instance = TestSave(
                    test_name=test_name,
                    type=item.get('type', ''),
                    url=main_url,
                    target=item.get('target', ''),
                    input=item.get('input', ''),
                    result=item.get('result', ''),
                    test_num='1',  # 임시값
                    test_uid='1',  # 임시값
                    iframe_xpath=item.get('iframe_xpath', '')  # 추가
                )
                test_save_instance.save()

                save_data_list.append({
                    'saved_data': f"Save successful for input: {item}",
                })

            return JsonResponse({'save_data_list': save_data_list})

        elif action_type == 'load':
            test_names = TestSave.objects.values_list('test_name', flat=True).distinct()
            return JsonResponse({'test_names': list(test_names)})

        elif action_type == 'db_load':
            selected_test_names = data.get('selectedTests', [])
            
            filtered_tests = TestSave.objects.filter(test_name__in=selected_test_names).values()
            return JsonResponse({'data': list(filtered_tests)})

        else:
            return JsonResponse({'error': 'Unsupported action type'}, status=400)

class ProcessListView(TemplateView):
    template_name = 'processList.html'

    def get(self, request, *args, **kwargs):
        test_names = TestSave.objects.values_list('test_name', flat=True).distinct()
        return self.render_to_response({'test_names': test_names})

class RecordView(TemplateView):
    template_name='test.html'
    
class TestScheduleCreateView(View):
    def get(self, request, *args, **kwargs):
        form = TestScheduleForm()
        return render(request, 'schedule/schedule_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = TestScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.save()
            form.save_m2m()  # Many-to-many 관계 저장
            
            # 스케줄 시간에 따라 작업 예약
            if schedule.scheduled_time:
                from django_q.models import Schedule
                Schedule.objects.create(
                    func='my_app.tasks.schedule_test',
                    args=str(schedule.id),
                    schedule_type=Schedule.ONCE,
                    next_run=schedule.scheduled_time,
                )
            
            return redirect('schedule_list')
        return render(request, 'schedule/schedule_form.html', {'form': form})

class TestScheduleListView(ListView):
    model = TestSchedule
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'schedules'

class TestScheduleDetailView(DetailView):
    model = TestSchedule
    template_name = 'schedule/schedule_detail.html'
    context_object_name = 'schedule'

class TestResultListView(View):
    def get(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(TestSchedule, pk=schedule_id)
        results = schedule.results.all()
        return render(request, 'schedule/result_list.html', {'schedule': schedule, 'results': results})
