from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from .selenium_list import process_click_xpath, process_click_xpath_otherurl, process_click_xpath_div
# Create your views here.

import json
from django.views.decorators.csrf import csrf_exempt

class BaseView(TemplateView):
    template_name = 'base.html'

class ProcessView(TemplateView):
    template_name = 'process.html'

    def post(self, request, *args, **kwargs):

        processed_data_list = []
        
        try:
            data = json.loads(request.body.decode('utf-8'))
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
    
class RecordView(TemplateView):
    template_name='test.html'
    
    