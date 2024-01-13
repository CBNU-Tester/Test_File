from django.shortcuts import render
from django.views.generic import TemplateView
from .recorder.record import selenium_start
import json
# Create your views here.

class RecordView(TemplateView):
    template_name = 'record.html'

def record_start(request):
    print("record start")
    selenium_start()

# api for user click component
# trigger : /recorder/component
# return : component xpath
def create_test_case(request):
     data = json.loads(request.body.decode('utf-8'))
     print(data)

