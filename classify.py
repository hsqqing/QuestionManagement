from transformers import BertTokenizer, BertForSequenceClassification
import torch
import logging

# 加载BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained('QuestionManagement')
model = BertForSequenceClassification.from_pretrained('QuestionManagement', num_labels=3)

def classify_question(content):
    """
    使用BERT模型进行题目分类
    :param content: 题目内容
    :return: 分类结果（科目、难度、题型、知识点等）
    """
    try:
        inputs = tokenizer(content, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        classification = torch.argmax(outputs.logits, dim=1).item()

        # 模拟返回的分类结果
        if classification == 0:
            return {
                'subject': 'geography',  # 假设分类为地理学科
                'difficulty': 'medium',  # 假设难度为中等
                'type': 'single_choice',  # 假设题型为单选题
                'knowledge_point': 'European capitals'  # 假设知识点为欧洲首都
            }
        elif classification == 1:
            return {
                'subject': 'history',
                'difficulty': 'hard',
                'type': 'multiple_choice',
                'knowledge_point': 'World War II'
            }
        else:
            return {
                'subject': 'science',
                'difficulty': 'easy',
                'type': 'true_false',
                'knowledge_point': 'Basic Physics'
            }

    except Exception as e:
        logging.error(f"Error during classification: {e}")
        return {
            'subject': 'unknown',
            'difficulty': 'unknown',
            'type': 'unknown',
            'knowledge_point': 'unknown'
        }
