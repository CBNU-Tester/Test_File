from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from .models import Tc
import logging

logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
class RecordView(TemplateView):
    template_name = 'record.html'

    def post(self, request, *args, **kwargs):
        # 원시 요청 본문을 디코딩하여 로그로 남김
        raw_body = request.body.decode('utf-8')
        logger.warning("Raw request body: %s", raw_body)

        # JSON 데이터 로드
        data = json.loads(raw_body)
        xpath_value = data.get('xpath', 'Default Value')
        # 추출한 값으로 컨텍스트 준비
        context = self.get_context_data(**kwargs)
        context['xpath_value'] = xpath_value
        # logger.warning(xpath_value)

        return self.render_to_response(context)
        # return render(request,self.template_name,context)

        #return redirect(self.template_name,context)
        #return JsonResponse({'xpath_value' : xpath_value})
    

class SaveDBView(TemplateView):
    template_name = 'record.html'
    def post(self,request,*args,**kargs):
        raw_body = request.body.decode('utf-8')
        data = json.loads(raw_body)
        xpath_values = data.get('xpath', 'Default Value')
        #  ex) xpath_values : {'id': '1', 'role': 'Click', 'xpath': 'BODY/DIV[2]/DIV[2]', 'input': 'None', 'output': 'None'},
        for data in xpath_values:
            print(data)
            # tc_instance = Tc(
            #     tc_num=data.id,
            #     tc_pid
            #     tc_type
            #     tc_url
            #     tc_target
            #     tc_input
            #     tc_result
            # )
            # tc_instance.save()