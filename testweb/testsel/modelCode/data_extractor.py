# data_extractor.py

import json
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".config/.env", verbose=True)

def extract_data(url):
    # Selenium WebDriver 설정
    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # GUI 없이 실행

    driver = webdriver.Remote(
        command_executor='http://' + os.getenv("DB_HOST") + ":" +os.getenv("SEL_PORT") + '/wd/hub',
        options=options
    )
    driver.get(url)

    # XPath 추출을 위한 자바스크립트 함수
    script = """
        var getElementXPath = function(element) {
            if (!element || !element.tagName) return '';
            if (element.id !== '') {
                return "//" + element.tagName.toLowerCase() + "[@id='" + element.id + "']";
            }
            if (element.className !== '') {
                var classes = element.className.trim().split(/\\s+/).join('.');
                return "//" + element.tagName.toLowerCase() + "[contains(@class, '" + classes + "')]";
            }
            var attributes = element.attributes;
            var attributeXPath = '';
            for (var i = 0; i < attributes.length; i++) {
                var attr = attributes[i];
                if (attr.name !== 'id' && attr.name !== 'class') {
                    attributeXPath += "[@"+ attr.name + "='" + attr.value + "']";
                }
            }
            if (attributeXPath !== '') {
                return "//" + element.tagName.toLowerCase() + attributeXPath;
            }
            var ix= 0, siblings= element.parentNode.childNodes;
            for (var i= 0; i< siblings.length; i++) {
                var sibling= siblings[i];
                if (sibling === element) {
                    return getElementXPath(element.parentNode)+ '/' + element.tagName.toLowerCase() + '[' + (ix+1) + ']';
                }
                if (sibling.nodeType=== 1 && sibling.tagName=== element.tagName) {
                    ix++;
                }
            }
        };
        return getElementXPath(arguments[0]);
    """

    # 데이터를 저장할 리스트 초기화
    all_data = []

    # 처리할 태그 목록
    tags_to_process = ['a', 'button', 'div', 'input', 'select', 'textarea']

    for tag_name in tags_to_process:
        elements = driver.find_elements(By.TAG_NAME, tag_name)
        for index, element in enumerate(elements, start=1):
            try:
                element_html = element.get_attribute('outerHTML')
                soup = BeautifulSoup(element_html, 'html.parser')
                element_tag = soup.find(tag_name)

                # 공통 속성 추출
                element_id = element_tag.get('id')
                element_class = element_tag.get('class')
                class_value = element_class[0] if element_class else None
                element_text = element_tag.text.strip()

                # XPath 생성
                if element_id:
                    xpath = f"//{tag_name}[@id='{element_id}']"
                else:
                    try:
                        xpath = driver.execute_script(script, element)
                    except StaleElementReferenceException:
                        continue  # 오류 발생 시 다음 요소로 넘어감

                # 태그별로 추가 속성 추출
                data = {
                    'tag': tag_name,
                    'index': index,
                    'id': element_id,
                    'class_': class_value,
                    'text': element_text,
                    'xPath': xpath,
                    'url': url
                }

                if tag_name == 'a':
                    data.update({
                        'href': element_tag.get('href'),
                        'target': element_tag.get('target', '_self'),
                        'rel': element_tag.get('rel'),
                        'title': element_tag.get('title'),
                        'aria-label': element_tag.get('aria-label'),
                        'download': element_tag.get('download'),
                    })

                elif tag_name == 'button':
                    data.update({
                        'type': element_tag.get('type'),
                        'disabled': element_tag.get('disabled'),
                        'value': element_tag.get('value'),
                        'name': element_tag.get('name'),
                    })

                elif tag_name == 'div':
                    data.update({
                        'role': element_tag.get('role'),
                        'contenteditable': element_tag.get('contenteditable'),
                        'draggable': element_tag.get('draggable'),
                        'tabindex': element_tag.get('tabindex'),
                        'hidden': element_tag.get('hidden'),
                        'title': element_tag.get('title'),
                        'name': element_tag.get('name'),
                    })

                elif tag_name == 'input':
                    data.update({
                        'type': element_tag.get('type'),
                        'name': element_tag.get('name'),
                        'value': element_tag.get('value'),
                        'placeholder': element_tag.get('placeholder'),
                        'disabled': element_tag.get('disabled'),
                        'required': element_tag.get('required'),
                        'readonly': element_tag.get('readonly'),
                        'autocomplete': element_tag.get('autocomplete'),
                        'maxlength': element_tag.get('maxlength'),
                        'min': element_tag.get('min'),
                        'max': element_tag.get('max'),
                        'step': element_tag.get('step'),
                    })

                elif tag_name == 'select':
                    data.update({
                        'name': element_tag.get('name'),
                        'size': element_tag.get('size'),
                        'multiple': element_tag.get('multiple'),
                        'disabled': element_tag.get('disabled'),
                        'autofocus': element_tag.get('autofocus'),
                        'required': element_tag.get('required'),
                        'form': element_tag.get('form'),
                    })

                elif tag_name == 'textarea':
                    data.update({
                        'name': element_tag.get('name'),
                        'rows': element_tag.get('rows'),
                        'cols': element_tag.get('cols'),
                        'disabled': element_tag.get('disabled'),
                        'readonly': element_tag.get('readonly'),
                        'placeholder': element_tag.get('placeholder'),
                        'maxlength': element_tag.get('maxlength'),
                        'autofocus': element_tag.get('autofocus'),
                        'wrap': element_tag.get('wrap'),
                        'form': element_tag.get('form'),
                    })

                # 데이터 리스트에 추가
                all_data.append(data)

            except StaleElementReferenceException:
                continue  # 오류 발생 시 다음 요소로 넘어감
            except Exception as e:
                continue  # 다른 예외 발생 시에도 넘어감

    # 브라우저 닫기
    driver.quit()

    return all_data
