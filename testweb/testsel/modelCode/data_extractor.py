# data_extractor.py

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


def get_xpath(element):
    script = """
    function getElementXPath(elt) {
        var path = '';
        for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
            idx = getElementIdx(elt);
            xname = elt.tagName.toLowerCase();
            if (idx > 1) xname += '[' + idx + ']';
            path = '/' + xname + path;
        }
        return path;
    }
    function getElementIdx(elt) {
        var count = 1;
        for (var sib = elt.previousSibling; sib; sib = sib.previousSibling) {
            if(sib.nodeType == 1 && sib.tagName == elt.tagName) count++;
        }
        return count;
    }
    return getElementXPath(arguments[0]);
    """
    try:
        return element._parent.execute_script(script, element)
    except StaleElementReferenceException:
        return None


def extract_data(urls, search_term):
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 화면 표시 없이 실행
    driver = webdriver.Chrome(options=chrome_options)

    # 이미 처리된 요소의 XPath를 추적하기 위한 세트
    processed_xpaths = set()
    data_rows = []

    for url in urls:
        try:
            driver.get(url)
            time.sleep(2)  # 페이지 로딩 대기

            # 검색할 id, class, role 속성에 search_term이 포함된 요소를 XPath로 찾기
            xpath_expression = f"//*[contains(@id, '{search_term}') or contains(@class, '{search_term}') or contains(@role, '{search_term}')]"
            elements = driver.find_elements(By.XPATH, xpath_expression)

            # 중복된 요소를 제거하기 위해 XPath를 사용
            unique_elements = []
            unique_xpaths = set()
            for elem in elements:
                try:
                    xpath = get_xpath(elem)
                    if xpath and xpath not in unique_xpaths:
                        unique_elements.append(elem)
                        unique_xpaths.add(xpath)
                except StaleElementReferenceException:
                    continue

            # 각 요소와 모든 하위 요소를 가져옴
            for element in unique_elements:
                elements_queue = [(element, None)]  # (element, parent_xpath)
                while elements_queue:
                    try:
                        current_element, parent_xpath = elements_queue.pop(0)
                        current_xpath = get_xpath(current_element)
                        if not current_xpath or current_xpath in processed_xpaths:
                            continue
                        processed_xpaths.add(current_xpath)

                        # 현재 요소의 태그만 가져오기
                        outer_html = current_element.get_attribute('outerHTML')
                        # 정규식을 사용하여 시작 태그만 추출
                        match = re.match(r'<[^>]+?>', outer_html)
                        if match:
                            element_only_html = match.group()
                        else:
                            element_only_html = f'<{current_element.tag_name}>'

                        # 현재 요소 처리
                        tag_name = current_element.tag_name
                        input_field = None
                        result_field = None
                        important_field = None
                        type_field = None

                        # input 태그 데이터 처리
                        if tag_name == 'input':
                            name_attr = current_element.get_attribute('name')
                            id_attr = current_element.get_attribute('id')
                            if name_attr and search_term in name_attr.lower():
                                input_field = 'input_text'
                            elif id_attr and search_term in id_attr.lower():
                                input_field = 'input_text'

                        # a 태그나 버튼의 Result 처리
                        if tag_name == 'a':
                            href = current_element.get_attribute('href')
                            if href:
                                result_field = href
                        elif tag_name == 'button':
                            onclick = current_element.get_attribute('onclick')
                            if onclick:
                                result_field = onclick
                        else:
                            onclick = current_element.get_attribute('onclick')
                            if onclick:
                                result_field = onclick

                        row = {
                            'Tag': tag_name,
                            'HTML': element_only_html,
                            'XPath': current_xpath,
                            'ParentXPath': parent_xpath if parent_xpath else '',
                            'Input': input_field,
                            'Result': result_field,
                            'Important': important_field,
                            'Type': type_field
                        }

                        # 빈 필드를 None으로 설정
                        for key in row:
                            if not row[key]:
                                row[key] = None

                        data_rows.append(row)

                        # 자식 요소들을 큐에 추가
                        child_elements = current_element.find_elements(By.XPATH, './*')
                        for child in child_elements:
                            elements_queue.append((child, current_xpath))

                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        print(f"Error processing element: {e}")
                        continue
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            continue

    # 드라이버 종료
    driver.quit()

    return data_rows
