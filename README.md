测试医疗领域大模型健康咨询类数字医生应用的问答准确性
爬取某著名医疗手册清洗后作为测试数据集，通过BERT-base对推理结果提取医学关键词，然后对推理结果进行关键词匹配和语义相似度两方面评估，输出关键词命中率（percision），语义相似度（bert_score）
