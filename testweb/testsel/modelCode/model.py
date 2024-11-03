# model.py

import torch
import torch.nn as nn
from transformers import AutoModel


class MultiTaskModel(nn.Module):
    def __init__(self, model_name, num_type_labels, num_important_labels, dropout_ratio=0.1):
        super(MultiTaskModel, self).__init__()
        self.roberta = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout_ratio)

        # type 분류를 위한 출력 레이어
        self.type_classifier = nn.Linear(self.roberta.config.hidden_size, num_type_labels)

        # important 분류를 위한 출력 레이어
        self.important_classifier = nn.Linear(self.roberta.config.hidden_size, num_important_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)

        # [CLS] 토큰의 출력
        cls_output = outputs.last_hidden_state[:, 0, :]
        cls_output = self.dropout(cls_output)

        # 분류 결과
        type_logits = self.type_classifier(cls_output)
        important_logits = self.important_classifier(cls_output)

        return type_logits, important_logits


def load_model(model_path, model_name, num_type_labels, num_important_labels, device='cpu'):
    """
    저장된 모델을 로드하는 함수입니다.
    """
    model = MultiTaskModel(
        model_name=model_name,
        num_type_labels=num_type_labels,
        num_important_labels=num_important_labels
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()  # 평가 모드로 전환
    return model
