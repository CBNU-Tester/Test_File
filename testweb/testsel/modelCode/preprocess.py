# preprocess.py

import json
from transformers import AutoTokenizer


def preprocess_data(data, tokenizer, max_length=256):
    inputs = []
    for item in data:
        # 'index'와 'xPath' 제거
        item_input = item.copy()
        item_input.pop('index', None)
        item_input.pop('xPath', None)

        # JSON 문자열로 변환
        input_text = json.dumps(item_input, ensure_ascii=False)

        # 토크나이징
        tokenized = tokenizer(
            input_text,
            padding='max_length',
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        )

        inputs.append({
            'input_ids': tokenized['input_ids'].squeeze(0),
            'attention_mask': tokenized['attention_mask'].squeeze(0),
            'xPath': item.get('xPath')  # xPath는 나중에 사용
        })
    return inputs
