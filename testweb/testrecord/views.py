from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from .models import Tc,TcList,AuthUser
import logging
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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

@csrf_exempt
@login_required
def save_record(request):
    if request.method == 'POST':
        print("record save function start")

        try:
            user_id = request.user.id  # 로그인된 사용자 가져오기
            raw_body = request.body.decode('utf-8')
            data = json.loads(raw_body)
            # 주요 데이터 가져오기
            # main_url = data.get('main_url', '')
            # test_name = data.get('test_name', '')
            # test_description = data.get('test_description', '')
            print("data : ",data)
            
            print(user_id)
            user_instance = get_object_or_404(AuthUser, pk=user_id)
            main_url="test URL"
            test_name="record function test2"
            test_description="record function test description2"

            # TcList에 저장
            test_list_instance = TcList(
                tc_uid=user_instance,  # ForeignKey 필드에 로그인된 사용자 객체 저장
                tc_name=test_name,
                tc_describe=test_description
            )
            test_list_instance.save()  # 데이터 저장 후 자동으로 생성된 `tc_pid` 값을 가져옴

            tc_pid = test_list_instance  # 저장된 TcList 인스턴스를 참조
            print("TcList 저장 성공: ", test_list_instance)
            save_data_list = []  # 저장 결과를 담을 리스트

            for item in data:
                role=replace_role(item.get('role', ''))
                try:
                    # Tc 모델에 각 xpath 값을 저장
                    test_save_instance = Tc(
                        tc_type=role,
                        tc_url=main_url,
                        tc_target=item.get('xpath', ''),  # `xpath` 필드 값 사용
                        tc_input=item.get('input', ''),
                        tc_result=item.get('output', ''),  # `output` 필드 값 사용
                        tc_pid=tc_pid  # TcList의 외래 키로 참조
                    )

                    # 데이터베이스에 저장
                    test_save_instance.save()
                    print("Tc 저장 성공: ", test_save_instance)

                    save_data_list.append({
                        'saved_data': f"Save successful for input: {item}",
                    })

                except Exception as e:
                    print(f"Error saving Tc instance: {e}")
                    save_data_list.append({
                        'error': f"Error saving for input: {item}, Error: {str(e)}",
                    })

            return JsonResponse({'save_data_list': save_data_list})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def replace_role(role):
    if role=="URL Change":
        return "process_click_xpath_otherurl"
    elif role=="Click":
        return "process_click_xpath"
    elif role=="Input":
        return "process_send_xpath"
    
    # "process_send_xpath" -> input
    # "process_click_xpath_otherurl" -> URL change
    # "process_click_xpath" -> "click"