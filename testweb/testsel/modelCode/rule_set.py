from durable.lang import *
# xpath_extractor 모듈 import
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from process import initialize_file
import json
import csv
import os

import csv
import json
import os

# 처리된 데이터를 저장하는 함수
def save_processed_data(data):
    # 여기에 데이터를 JSON 파일, 데이터베이스, 또는 다른 형태로 저장하는 로직 구현
    # 예: JSON 파일에 저장
    # 데이터 객체에서 'tag' 값을 기반으로 파일명 결정
    tag_name = data.get('tag', 'processed')  # 'tag' 키가 없는 경우 'unknown'을 기본값으로 사용
    filename = f'{tag_name}_data.json'  # 파일명 형식을 '{태그명}_data.json'으로 설정

    with open(filename, 'a', encoding='utf8') as file:
        import json
        file.write(json.dumps(data) + '\n')


with ruleset('web_test'):

    # rule
    # Button 태그 테스트
    @when_all((m.tag == 'button') & (m.xPath != None))
    def button_test(c):

        if c.m.name:
            print(f"해당 {c.m.tag}의 역할은 '{c.m.name}' 입니다.")
        elif c.m.text:
            print(f"해당 {c.m.tag}의 역할은 '{c.m.text}' 입니다.")
        elif c.m.role:
            print(f"해당 {c.m.tag}의 역할은 '{c.m.role}' 입니다.")
        elif c.m.id:
            print(f"해당 {c.m.tag}의 역할은 '{c.m.id}' 입니다.")
        else:
            # 모든 조건이 충족되지 않으면 출력하지 않고 종료
            return

        # print(f'해당 버튼이 속한 form의 ID는 "{c.m.btn_form}" 입니다.' if c.m.btn_form else '해당 버튼이 속한 form 정보가 없습니다.')
        button_data = {
            'tag': c.m.tag,
            #'index': c.m.index,
            'role': c.m.name if c.m.name else (c.m.text if c.m.text else (c.m.role if c.m.role else c.m.id)),
            'xPath': c.m.xPath,
            'disabled': True if c.m.disabled == 'disabled' else False,
            'value': c.m.value if c.m.value else None,
            'btn_form': c.m.btn_form if c.m.btn_form else None,
            'url':c.m.url if c.m.url else None
        }
        save_processed_data(button_data)


    # Form 태그 테스트
    @when_all((m.tag == 'form') & (m.xPath != None))
    def form_test(c):
        purpose = ''
        if c.m.role:
            purpose = c.m.role
        elif c.m.action:
            purpose = c.m.action
        elif c.m.name:
            purpose = c.m.name
        elif c.m.text:
            purpose = c.m.text
        elif c.m.id:
            purpose = c.m.id
        else:
            # 모든 속성이 없는 경우, 출력하지 않고 함수를 종료
            return
        form_data = {
            'tag': c.m.tag,
            'index': c.m.index,
            'purpose': purpose,
            'xPath': c.m.xPath,
            'target': c.m.target,
            'inputs': c.m.inputs,
            'selects': c.m.selects,
            'textareas': c.m.textareas
        }
        save_processed_data(form_data)

        # select 요소들에 대한 정보 출력
        if c.m.selects:
            print('해당 폼에는 다음 select 요소들이 있습니다:')
            for select_html in c.m.selects:
                soup = BeautifulSoup(select_html, 'html.parser')
                select = soup.select_one('select')
                # select_name = select.get('name', '이름 없음')
                # select_id = select.get('id', 'ID 없음')
                select_name = select.get('name', '이름 없음')
                select_id = select.get('id', 'ID 없음')
                select_class = select.get('class')
                if select_id != 'ID 없음':
                    # id 속성이 있는 경우
                    select_xpath = f"//select[@id='{select_id}']"
                select_size = select.get('size', '기본 크기')
                select_multiple = 'yes' if select.has_attr('multiple') else 'no'
                select_disabled = 'yes' if select.has_attr('disabled') else 'no'
                select_autofocus = 'yes' if select.has_attr('autofocus') else 'no'
                select_required = 'yes' if select.has_attr('required') else 'no'
                select_form = select.get('form', '연결된 폼 없음')

                print(f"Select 이름: {select_name}")
                print(f"Select ID: {select_id}")
                print(f'Select의 xPath: {select_xpath}')
                print(f"Select 크기: {select_size}")
                print(f"다중 선택 가능: {select_multiple}")
                print(f"사용 불가: {select_disabled}")
                print(f"자동 포커스: {select_autofocus}")
                print(f"필수 선택: {select_required}")
                print(f"연결된 폼: {select_form}")

        if c.m.textareas:
            print('해당 폼에는 다음 textarea 요소들이 있습니다:')
            for textarea_html in c.m.textareas:
                soup = BeautifulSoup(textarea_html, 'html.parser')
                textarea = soup.find('textarea')

                textarea_name = textarea.get('name', '이름 없음')
                textarea_id = textarea.get('id', 'ID 없음')
                if textarea_id != 'ID 없음':
                    # id 속성이 있는 경우
                    textarea_xpath = f"//textarea[@id='{textarea_id}']"
                else:
                    textarea_xpath = "id 값이 없어 추적 불가"
                textarea_rows = textarea.get('rows', '행 수 없음')
                textarea_cols = textarea.get('cols', '열 수 없음')
                textarea_disabled = 'yes' if textarea.has_attr('disabled') else 'no'
                textarea_readonly = 'yes' if textarea.has_attr('readonly') else 'no'
                textarea_placeholder = textarea.get('placeholder', '플레이스홀더 없음')
                textarea_maxlength = textarea.get('maxlength', '제한 없음')
                textarea_autofocus = 'yes' if textarea.has_attr('autofocus') else 'no'
                textarea_wrap = textarea.get('wrap', 'wrap 속성 없음')

                print(f"Textarea 이름: {textarea_name}")
                print(f"Textarea ID: {textarea_id}")
                print(f'Textarea의 xPath: {textarea_xpath}')
                print(f"Textarea 행 수: {textarea_rows}")
                print(f"Textarea 열 수: {textarea_cols}")
                print(f"사용 불가: {textarea_disabled}")
                print(f"읽기 전용: {textarea_readonly}")
                print(f"플레이스홀더: {textarea_placeholder}")
                print(f"최대 길이: {textarea_maxlength}")
                print(f"자동 포커스: {textarea_autofocus}")
                print(f"Wrap: {textarea_wrap}")



    @when_all((m.tag == 'a') & (m.xPath != None))
    def link_test(c):

        # aria-label, title, text, id 속성에 따른 조건부 출력
        # target 속성 확인
        target_info = {
            "_blank": "새 창이나 탭에서 열립니다.",
            "_self": "같은 프레임이나 창에서 열립니다.",
            "_parent": "부모 프레임에서 열립니다.",
            "_top": "전체 창에서 열립니다."
        }
        # print(f'링크 대상(target): "{c.m.target}" ({target_info.get(c.m.target, "알 수 없음")})')

        # rel 속성 추가 정보
        rel_info = {
            "alternate": "대체 버전 링크",
            "author": "저자 링크",
            "bookmark": "북마크",
            "external": "외부 링크",
            "help": "도움말 링크",
            "license": "라이선스 링크",
            "next": "다음 문서",
            "nofollow": "링크 따라가지 않음",
            # "noreferrer": "referrer 정보 전송하지 않음",
            # "noopener": "새 창에서 열리지만 opener 속성 없음",
            "prev": "이전 문서",
            "search": "검색 링크",
            "tag": "태그 링크"
        }

        role = c.m.aria_label if c.m.aria_label else (
            c.m.title if c.m.title else (c.m.text if c.m.text else (c.m.id if c.m.id else "0")))
        result = "알 수 없음"  # 초기값 설정

        # target_info와 rel_info 결합하여 result 계산
        target_info = "_self" if not c.m.target else c.m.target
        rel_info = "기본 동작" if not c.m.rel else c.m.rel
        result = f"target: {target_info}, rel: {rel_info}"

        download = "0" if not c.m.download else c.m.download

        link_data = {
            'tag': 'a',
            'index': c.m.index, # 인덱스는 enumerate를 통해 처리되어야 하나, 여기서는 직접적인 처리 방법을 제공하지 않음
            'href': c.m.href,
            'text': c.m.text,
            'role': role,
            'result': result,
            'download': download,
            'xPath': c.m.xPath,
            'url':c.m.url
        }

        # 파일명은 'a_test.json'
        save_processed_data(link_data)


    @when_all((m.tag == 'div') & (m.xPath != None))
    def element_info(c):
        # 속성에 따른 메시지 설정

        role = c.m.role if c.m.role else (
            c.m.name if c.m.name else (c.m.id if c.m.id else "unspecified"))

        # role이 "unspecified"일 경우 저장하지 않음
        if role == "unspecified":
            return
        # 텍스트가 비어 있는 경우 제외
        if not c.m.text.strip():
            return
            # 텍스트 내용을 가져오고 공백 제거
        text_content = c.m.text.strip()

        # 텍스트가 비어 있는 경우 제외
        if not text_content:
            return

        result = f"contenteditable: {'yes' if c.m.contenteditable == 'true' else 'no'}, draggable: {'yes' if c.m.draggable == 'true' else 'no'}, hidden: {'yes' if c.m.hidden == 'true' else 'no'}"

        div_data = {
            'tag': c.m.tag,
            'index': c.m.index,
            'role': role,
            'text': c.m.text,
            'result': result,
            'tabindex': c.m.tabindex if c.m.tabindex else "None",
            'xPath': c.m.xPath,
            'title': c.m.title if c.m.title else "None",
            'url':c.m.url if c.m.title else "None"
        }
        save_processed_data(div_data)


    def print_additional_info(c):
        # 추가 속성에 대한 정보 출력
        print(f"xPath는 {c.m.xPath}입니다.") if c.m.xPath else print("xPath 정보가 없습니다.")
        print(f"contenteditable: {'편집 가능' if c.m.contenteditable else '편집 불가능'}")
        print(f"draggable: {'드래그 가능' if c.m.draggable else '드래그 불가능'}")
        print(f"tabindex: {c.m.tabindex}") if c.m.tabindex else print("tabindex 정보가 없습니다.")
        print(f"hidden: {'보이지 않음' if c.m.hidden else '보임'}")
        print(f"title: {c.m.title}") if c.m.title else print("title 정보가 없습니다.")

    # input 요소에 대한 규칙
    @when_all(m.tag == 'input')
    def input_rule(c):
        # type 속성에 따른 출력
        input_type = c.m.type
        if input_type == 'text':
            c.m.role = '텍스트 입력 필드'
        elif input_type == 'password':
            c.m.role = '비밀번호 입력 필드'
        elif input_type == 'submit':
            c.m.role = '폼 제출 버튼'
        elif input_type == 'reset':
            c.m.role = '폼 리셋 버튼'
        elif input_type == 'radio':
            c.m.role = '라디오 버튼'
        elif input_type == 'checkbox':
            c.m.role = '체크박스'
        elif input_type == 'button':
            c.m.role = '일반 버튼'
        elif input_type == 'file':
            c.m.role = '파일 업로드 필드'
        elif input_type == 'hidden':
            c.m.role = '숨겨진 입력 필드'
        elif input_type == 'image':
            c.m.role = '이미지 제출 버튼'
        elif input_type == 'email':
            c.m.role = '이메일 주소 입력 필드'
        elif input_type == 'url':
            c.m.role = 'URL 입력 필드'
        elif input_type == 'number':
            c.m.role = '숫자 입력 필드'
        elif input_type == 'range':
            c.m.role = '범위 선택 슬라이더'
        elif input_type == 'date':
            c.m.role = '날짜 선택 필드'
        elif input_type == 'month':
            c.m.role = '월 선택 필드'
        elif input_type == 'week':
            c.m.role = '주 선택 필드'
        elif input_type == 'time':
            c.m.role = '시간 선택 필드'
        elif input_type == 'datetime-local':
            c.m.role = '날짜 및 시간 선택 필드'
        elif input_type == 'color':
            c.m.role = '색상 선택 필드'
        elif input_type == 'search':
            c.m.role = '검색 필드'
        elif input_type == 'tel':
            c.m.role = '전화번호 입력 필드'
        else:
            c.m.role = f'{input_type}'

        if hasattr(c.m, 'role') and c.m.role not in [None, "None"]:
            purpose = c.m.role
        elif hasattr(c.m, 'name') and c.m.name not in [None, "None"]:
            purpose = c.m.name
        elif hasattr(c.m, 'id') and c.m.id not in [None, "None"]:
            purpose = c.m.id
        else:
            return  # role, name, id 모두 없을 경우 함수 종료
        save_processed_data({
            'tag': c.m.tag,
            'index': c.m.index,
            'role': c.m.role,
            'purpose': purpose,
            'xPath': c.m.xPath,
            'placeholder': c.m.placeholder,
            'disabled': c.m.disabled,
            'required': c.m.required
        })

# select 요소에 대한 규칙
    @when_all(m.tag == 'select')
    def select_test(c):
        # select 요소에 대한 처리 로직
        print(f"Select 태그: {c.m.xPath}")
        # select 요소의 role 설정 (이 예제에서는 select 요소에 대한 구체적인 role 분류가 없으므로, 일반적인 역할을 문자열로 할당)
        # c.m.role = '선택 입력 필드'

        # 목적(purpose) 설정: name, id를 기반으로 결정
        if hasattr(c.m, 'name') and c.m.name not in [None, "None"]:
            purpose = c.m.name
        elif hasattr(c.m, 'id') and c.m.id not in [None, "None"]:
            purpose = c.m.id
        else:
            purpose = "None"  # name, id 모두 없거나 유효하지 않을 경우

        # 데이터 저장
        save_processed_data({
            'index':c.m.index,
            'tag': c.m.tag,
            'purpose': purpose,
            'xPath': c.m.xPath,
            'multiple': c.m.multiple,
            'autofocus': c.m.autofocus,
            'disabled': c.m.select_disabled,
            'required': c.m.select_required,
            'form': c.m.form_
        })

# textarea 요소에 대한 규칙
    @when_all((m.tag == 'textarea') & (m.xPath != None))
    def textarea_test(c):
        # textarea 요소에 대한 처리 로직
        data = {
            'tag': c.m.tag,
            'xPath': c.m.xPath,
            'name': c.m.name,
            'id': c.m.id,
            'rows': c.m.rows,
            'cols': c.m.cols,
            'disabled': c.m.disabled,
            'readonly': c.m.readonly,
            'placeholder': c.m.placeholder,
            'maxlength': c.m.maxlength,
            'autofocus': c.m.autofocus,
            'wrap': c.m.wrap
        }
        # 목적(purpose) 설정: name, id를 기반으로 결정
        if data['name']:
            purpose = data['name']
        elif data['id']:
            purpose = data['id']
        else:
            purpose = "None"
        # purpose 추가
        data['purpose'] = purpose

        # 데이터 저장 (예시 함수, 실제 구현에 맞게 변경 필요)
        save_processed_data(data)
        print(f"Textarea 태그: {c.m.xPath}")
    # 추가적인 정보 출력 등
# 테스트 케이스 예시

#assert_fact('web_test', {'tag': 'button', 'text': '클릭하세요', 'xPath':'//tag[@input]', 'aria_label':'comic'})
#assert_fact('web_test', {'tag': 'form', 'action': '/submit', 'xPath':'//tag[@input]','aria_label':'comic'})
#assert_fact('web_test', {'tag': 'a', 'href': 'https://example.com', 'xPath':'//tag[@input]','aria_label':'comic'})