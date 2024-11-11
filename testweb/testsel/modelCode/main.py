# main.py

import os
import pandas as pd
import numpy as np
import torch
from transformers import XLMRobertaTokenizer, XLMRobertaModel
from .model import MultiTaskModel
from .data_extractor import extract_data


def create_main(url, search_term):
    urls = [url]
    data_rows = extract_data(urls, search_term)
    data = pd.DataFrame(data_rows)

    if data.empty:
        print("No data collected.")
        return []

    texts = data['HTML'].tolist()
    tokenizer_output_dir = r'C:\Users\Administrator\Documents\GitHub\Test_File\testweb\testsel\modelCode\result\pre_train_html_tokenizer'
    model_output_dir = r'C:\Users\Administrator\Documents\GitHub\Test_File\testweb\testsel\modelCode\result\pre_train_html'
    model_path = r'C:\Users\Administrator\Documents\GitHub\Test_File\testweb\testsel\modelCode\output\best_model_updated1.pth'

    tokenizer = XLMRobertaTokenizer.from_pretrained(tokenizer_output_dir)
    base_model = XLMRobertaModel.from_pretrained(model_output_dir)

    num_type_labels = 4
    num_important_labels = 2

    model = MultiTaskModel(base_model, num_type_labels, num_important_labels)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )

    with torch.no_grad():
        type_logits, important_logits = model(
            input_ids=inputs['input_ids'].to(device),
            attention_mask=inputs['attention_mask'].to(device)
        )

    type_probs = torch.softmax(type_logits, dim=1)
    important_probs = torch.softmax(important_logits, dim=1)

    type_preds = torch.argmax(type_probs, dim=1).cpu().numpy()
    important_preds = torch.argmax(important_probs, dim=1).cpu().numpy()

    type_label_map = {0: 'Unknown', 1: 'process_click_xpath', 2: 'process_click_xpath_otherurl', 3: 'process_send_xpath'}
    important_label_map = {0: 0, 1: 1}

    data['Type'] = [type_label_map.get(pred, 'Unknown') for pred in type_preds]
    data['Important'] = [important_label_map.get(pred, 'Unknown') for pred in important_preds]

    output_data = data[['Tag', 'HTML', 'XPath', 'ParentXPath', 'Input', 'Result', 'Important', 'Type']]
    output_data = output_data.where(pd.notnull(output_data), None)

    output_list = output_data.to_dict(orient='records')
    for item in output_list:
        if item['Tag'] not in ['a', 'button', 'input', 'form']:
            item['Type'] = 'Unknown'
            item['Important'] = 0
    filtered_output_list = [item for item in output_list if item['Important'] == 1]
    print("Number of items with Important == 1:", len(filtered_output_list))

    return filtered_output_list


