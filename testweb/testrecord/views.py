from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse

# Create your views here.

import json
from django.views.decorators.csrf import csrf_exempt

class RecordView(TemplateView):
    template_name = 'record.html'