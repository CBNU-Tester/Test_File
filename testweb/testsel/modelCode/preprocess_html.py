# preprocess.py

import re

def preprocess_html(html_text):
    # 특수문자 제거
    text = re.sub('[^0-9a-zA-Zㄱ-ㅎ가-힣 ]', ' ', html_text)
    # 공백 여러 개를 하나로
    text = re.sub('\s+', ' ', text).strip()
    return text
