from sentence_transformers import SentenceTransformer, util

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:52581'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:52581'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


model = SentenceTransformer('dmis-lab/biobert-v1.1')
symptoms = ["眼白和皮肤通常看起来发黄", "尿液黄全身瘙痒"]
embeddings = model.encode(symptoms, convert_to_tensor=True, fp16=True)
similarity = util.cos_sim(embeddings[0], embeddings[1])
print(f"症状相似度：{similarity.item():.2f}")