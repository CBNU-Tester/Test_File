from django.shortcuts import render
from django.views.generic import TemplateView
from .recorder.record import selenium_start
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

class RecordView(TemplateView):
    template_name = 'record.html'

def record_start(request):
    print("record start")
    selenium_start()

# api for user click component
# trigger : /recordes/component
# return : component xpath
@csrf_exempt
def create_test_case(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        # Your view logic here
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    
