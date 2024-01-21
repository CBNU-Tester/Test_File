from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from .selenium_list import process_click_xpath, process_click_xpath_otherurl, process_click_xpath_div
# Create your views here.

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TestSave

class BaseView(TemplateView):
    template_name = 'base.html'

from django.shortcuts import render
from django.views.generic import TemplateView

class ProcessView(TemplateView):
    template_name = 'process.html'

    def post(self, request, *args, **kwargs):

        processed_data_list = []
        data = json.loads(request.body.decode('utf-8'))
        action_type = data.get('action_type', '')
        
        if action_type == 'test':
            try:
                dynamic_inputs_list = data.get('dynamic_inputs', [])
                for data in dynamic_inputs_list:
                    process_type = data.get('type')

                    # Assuming functions are imported from selenium_list.py
                    if process_type == 'process_click_xpath':
                        print("1번실행")
                        processed_data = process_click_xpath(
                            data.get('url'),
                            data.get('target'),
                            data.get('input'),
                            data.get('result')
                        )
                    elif process_type == 'process_click_xpath_otherurl':
                        print("2번실행")
                        processed_data = process_click_xpath_otherurl(
                            data.get('url'),
                            data.get('target'),
                            data.get('input'),
                            data.get('result')
                        )
                    elif process_type == 'process_click_xpath_div':
                        print("3번실행")
                        processed_data = process_click_xpath_div(
                            data.get('url'),
                            data.get('target'),
                            data.get('input'),
                            data.get('result')
                        )
                    else:
                        processed_data = f"Unsupported process type: {process_type}"

                    processed_data_list.append({
                        'type': process_type,
                        'url': data.get('url'),
                        'result': data.get('result'),
                        'processed_data': processed_data,
                    })

                return JsonResponse({'processed_data_list': processed_data_list})

            except json.JSONDecodeError:
                # Handle JSON decoding error
                pass

            return JsonResponse({'processed_data_list': []})
        elif action_type == 'save':
            # Handle the 'save' action type
            save_data_list = []
            dynamic_inputs_list = data.get('dynamic_inputs', [])
            for data in dynamic_inputs_list:
                test_save_instance = TestSave(
                    type=data.get('type', ''),
                    url=data.get('url', ''),
                    target=data.get('target', ''),
                    input=data.get('input', ''),
                    result=data.get('result', ''),
                    test_num = '1', #임시값 추후 사용자를 완성하면 추가할 예정 
                    test_uid = '1', #임시값 추후 사용자를 완성하면 추가할 예정
                )
                test_save_instance.save()

                save_data_list.append({
                    'saved_data': 'Save successful for input: {}'.format(data),
                })

            return JsonResponse({'save_data_list': save_data_list})
        elif action_type == 'load':  # 
            loaded_data_list = TestSave.objects.all().values()
            return JsonResponse({'loaded_data_list': list(loaded_data_list)})    
        else:
            return JsonResponse({'error': 'Unsupported action type'})


