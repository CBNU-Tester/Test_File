# main.py

import json
from .model import load_model
from .preprocess import preprocess_data
from transformers import AutoTokenizer
import torch
from .data_extractor import extract_data

def create_main(url):
    # 출력 파일 경로 설정
    output_filename = 'final_data.json'

    # 데이터 추출
    data = extract_data(url)

    # 모델 입력을 위한 데이터 전처리
    tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base')
    inputs = preprocess_data(data, tokenizer)

    # 모델 로드
    model_path = '/Users/idongmin/Desktop/final_Project/Test_File/testweb/testsel/modelCode/best_model.pth'  # 모델 파라미터가 저장된 경로로 변경해야 함
    num_type_labels = 3  # type 매핑 개수
    num_important_labels = 2  # important 매핑 개수
    model = load_model(model_path, 'xlm-roberta-base', num_type_labels, num_important_labels)
    # 타입 레이블 매핑
    type_label_map = {0: 'process_click_xpath', 1: 'process_click_xpath_otherurl', 2: 'process_send_xpath'}
    # 중요도 레이블 매핑
    important_label_map = {0: 0, 1: 1}
    print("모델불러오기 성공")
    # 모델 예측 및 결과 병합
    with torch.no_grad():
        for i, input_data in enumerate(inputs):
            input_ids = input_data['input_ids'].unsqueeze(0)
            attention_mask = input_data['attention_mask'].unsqueeze(0)

            type_logits, important_logits = model(input_ids, attention_mask)

            # 예측 결과
            type_pred = torch.argmax(type_logits, dim=1).item()
            important_pred = torch.argmax(important_logits, dim=1).item()

            # 레이블 매핑
            type_label = type_label_map.get(type_pred, 'unknown')
            important_label = important_label_map.get(important_pred, 0)

            # 결과 병합
            data[i]['type_'] = type_label
            data[i]['important'] = important_label

            # 'index' 제거
            data[i].pop('index', None)

    return data