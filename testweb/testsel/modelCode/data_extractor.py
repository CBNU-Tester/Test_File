# data_extractor.py

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import os

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
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    data_rows = []
    for url in urls:
        try:
            driver.get(url)
            time.sleep(2)

            xpath_expression = f"//*[contains(@id, '{search_term}') or contains(@class, '{search_term}') or contains(@role, '{search_term}')]"
            elements = driver.find_elements(By.XPATH, xpath_expression)

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

            processed_xpaths = set()

            for element in unique_elements:
                elements_queue = [(element, None)]
                while elements_queue:
                    try:
                        current_element, parent_xpath = elements_queue.pop(0)
                        current_xpath = get_xpath(current_element)
                        if not current_xpath or current_xpath in processed_xpaths:
                            continue
                        processed_xpaths.add(current_xpath)

                        outer_html = current_element.get_attribute('outerHTML')
                        match = re.match(r'<[^>]+?>', outer_html) if outer_html else None
                        element_only_html = match.group() if match else f'<{current_element.tag_name}>'

                        tag_name = current_element.tag_name
                        input_field = result_field = important_field = type_field = None

                        if tag_name == 'input':
                            name_attr = current_element.get_attribute('name')
                            id_attr = current_element.get_attribute('id')
                            if name_attr and search_term in name_attr.lower() or id_attr and search_term in id_attr.lower():
                                input_field = 'input_text'

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

                        for key in row:
                            if not row[key]:
                                row[key] = None

                        data_rows.append(row)

                        child_elements = current_element.find_elements(By.XPATH, './*')
                        for child in child_elements:
                            elements_queue.append((child, current_xpath))
                    except (StaleElementReferenceException, Exception) as e:
                        print(f"Error processing element: {e}")
                        continue
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            continue

    driver.quit()
    return data_rows
