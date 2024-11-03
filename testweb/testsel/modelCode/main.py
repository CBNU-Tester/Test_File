# main.py

import os
import pandas as pd
import torch
from transformers import AutoTokenizer

from .data_extractor import extract_data
from .preprocess_html import preprocess_html
from .model import load_model

def create_main(url, search_term):
    # URL 리스트 설정
    urls = []
    urls.append(url)  # 검색할 URL (여러 개 추가 가능)

    # 검색할 용어 (포함되는 id, class, role을 찾기 위해)
    #search_term = 'search'  # 원하는 검색어로 변경 가능

    # 데이터 추출
    data_rows = extract_data(urls, search_term)

    # 데이터프레임 생성
    data = pd.DataFrame(data_rows)

    # HTML 필드 전처리
    data['processed_html'] = data['HTML'].apply(preprocess_html)

    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')

    # 모델 로드
    model_path = '/Users/idongmin/Desktop/final_Project/Test_File/testweb/testsel/modelCode/best_model_data1.pth'
    num_type_labels = 4  # 실제 클래스 수로 설정해야 함
    num_important_labels = 2  # 실제 클래스 수로 설정해야 함
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_model(model_path, 'xlm-roberta-base', num_type_labels, num_important_labels, device=device)

    # 데이터에 대한 예측 수행
    inputs = tokenizer(
        data['processed_html'].tolist(),
        padding=True,
        truncation=True,
        return_tensors='pt'
    )

    with torch.no_grad():
        type_logits, important_logits = model(
            input_ids=inputs['input_ids'].to(device),
            attention_mask=inputs['attention_mask'].to(device)
        )

    # 소프트맥스를 적용하여 확률로 변환
    type_probs = torch.softmax(type_logits, dim=1)
    important_probs = torch.softmax(important_logits, dim=1)

    # 가장 높은 확률의 클래스 선택
    type_preds = torch.argmax(type_probs, dim=1).cpu().numpy()
    important_preds = torch.argmax(important_probs, dim=1).cpu().numpy()

    # 예측된 레이블을 실제 레이블로 변환 (인덱스에서 레이블로)
    type_label_map = {0:'None',1: 'process_click_xpath', 2: 'process_click_xpath_otherurl', 3: 'process_send_xpath'}
    important_label_map = {0: 0,1:1}

    data['Type'] = [type_label_map.get(pred, 'Unknown') for pred in type_preds]
    data['Important'] = [important_label_map.get(pred, 'Unknown') for pred in important_preds]

    # 필요한 컬럼만 선택
    output_data = data[['Tag', 'HTML', 'XPath', 'ParentXPath', 'Input', 'Result', 'Important', 'Type']]

    # 빈 값을 None으로 설정
    output_data = output_data.where(pd.notnull(output_data), None)

    # 데이터를 리스트의 딕셔너리로 변환
    output_list = output_data.to_dict(orient='records')

    # # 사용자에게 전달할 데이터 출력
    # for item in output_list:
    #     print(item)

    # Important 값이 1인 데이터만 출력하려면 아래와 같이 필터링합니다.
    filtered_output_list = [item for item in output_list if item['Important'] == 1]
    print(filtered_output_list.count)
    
    return filtered_output_list
