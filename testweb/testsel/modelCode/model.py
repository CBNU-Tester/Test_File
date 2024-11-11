# model.py

import torch
import torch.nn as nn

# MultiTaskModel 클래스 정의
class MultiTaskModel(nn.Module):
    def __init__(self, base_model, num_type_labels, num_important_labels, dropout_ratio=0.1):
        super(MultiTaskModel, self).__init__()
        self.base_model = base_model
        self.dropout = nn.Dropout(dropout_ratio)

        hidden_size = base_model.config.hidden_size
        self.type_classifier = nn.Linear(hidden_size, num_type_labels)
        self.important_classifier = nn.Linear(hidden_size, num_important_labels)

    def forward(self, input_ids, attention_mask, output_attentions=False):
        outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask,
                                  output_attentions=output_attentions)
        cls_output = outputs.last_hidden_state[:, 0, :]
        cls_output = self.dropout(cls_output)

        type_logits = self.type_classifier(cls_output)
        important_logits = self.important_classifier(cls_output)

        if output_attentions:
            return type_logits, important_logits, outputs.attentions
        else:
            return type_logits, important_logits