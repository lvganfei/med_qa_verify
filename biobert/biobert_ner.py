from transformers import AutoTokenizer, AutoModelForTokenClassification
import os
import json
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:52581'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:52581'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

tokenizer = AutoTokenizer.from_pretrained("Adapting/bert-base-chinese-finetuned-NER-biomedical")
model = AutoModelForTokenClassification.from_pretrained("Adapting/bert-base-chinese-finetuned-NER-biomedical",revision='7f63e3d18b1dc3cc23041a89e77be21860704d2e').to("cuda")


from transformers import pipeline
bio_ner_task = pipeline('ner',model=model,tokenizer = tokenizer)

tag_list = [
 'B_手术',
 'I_疾病和诊断',
 'B_症状',
 'I_解剖部位',
 'I_药物',
 'B_影像检查',
 'B_药物',
 'B_疾病和诊断',
 'I_影像检查',
 'I_手术',
 'B_解剖部位',
 'O',
 'B_实验室检验',
 'I_症状',
 'I_实验室检验'
 ]
 
tag2id = lambda tag: tag_list.index(tag)
id2tag = lambda id: tag_list[id]

def text_split(raw_text, max_length=500, overlap=50):
    """
    分块处理长文本（滑动窗口策略）
    """
    print(f"原始文本长度: {len(raw_text)}")
    if len(raw_text) == 0:
        return ["文本长度为0，填充字符"]
    chunks = []
    start = 0
    while start < len(raw_text):
        print(f"原始文本长度: {len(raw_text)}")
        end = min(start + max_length, len(raw_text)-1)
        print(f"end: {end}")
        chunk_text = raw_text[start:end]
        print(chunk_text)
        chunks.append(chunk_text)
        if end >= len(raw_text) - 1:
            break
        start = end - overlap  # 重叠避免截断实体
        print(f"start: {start}")
    return chunks


def readable_result(results):
    print("------------------------------result------------------------------")
    print(results)
    results_in_word = []
    for result in results:
        
        j = 0
        while j < len(result) and j <= 500:   
            i = result[j]
            entity = id2tag(int(i['entity'][i['entity'].index('_')+1:]))
            token = i['word']
            if entity.startswith('B'):
                entity_name = entity[entity.index('_')+1:]

                word = token
                j = j+1
                while j<len(result):
                    next = result[j]
                    next_ent = id2tag(int(next['entity'][next['entity'].index('_')+1:]))
                    next_token = next['word']

                    if next_ent.startswith('I') and next_ent[next_ent.index('_')+1:] == entity_name:
                        word += next_token
                        j += 1

                        if j >= len(result):
                            results_in_word.append((entity_name,word))
                    else:
                        results_in_word.append((entity_name,word))
                        break

            else:
                j += 1
    # print(results_in_word)
    return results_in_word

def symptom_ner(json_path):
    with open(json_path, 'r', encoding="utf-8") as f:
        symptoms_list = json.load(f)
        f.close()
    
    for symptom in symptoms_list:
        symptoms_description = symptom["symptoms_description"]
        print(readable_result(bio_ner_task(text_split(symptoms_description, 500, 50))))
        symptoms_causes = max(symptom["symptoms_causes"]["detail_causes"], symptom["symptoms_causes"]["allinone"])
        print(readable_result(bio_ner_task(text_split(symptoms_causes, 500, 50))))
        symptoms_evaluation = max(symptom["symptoms_evaluation"]["evaluation_detail"],symptom["symptoms_evaluation"]["allinone"])
        print(readable_result(bio_ner_task(text_split(symptoms_evaluation, 500, 50))))
        symptoms_treatment = max(symptom["symptoms_treatment"]["detail_treatment"],symptom["symptoms_treatment"]["detail_treatment"])
        print(readable_result(bio_ner_task(text_split(symptoms_treatment, 500, 50))))
        symptoms_keywords = symptom["symptoms_key_point"]
        print(symptoms_keywords)


test_symptom = "治疗描述： 黄疸的治疗 病因的治疗 可使用消胆胺消除瘙痒症状 对于胆管阻塞，可通过一些手术打通胆管,如内镜逆行胰胆管造影 [ ERCP ] 基础疾病及其导致的任何问题均需要治疗。如果黄疸是由 急性病毒性肝炎 引起，黄疸不经治疗也可能会随肝炎症状的好转而逐渐消失。然而，即使黄疸消失，肝炎却可能会转为慢性肝炎。成人黄疸本身并不需要治疗（与新生儿黄疸不同——参见 高胆红素血症 ）。 通常情况下，随肝脏的病情好转，瘙痒会逐渐消失。当瘙痒比较严重时，口服考来烯胺（消胆胺）可有所帮助。但当胆管被完全阻塞时，考来烯胺是无效的。 如果病因是由于胆管阻塞，可通过一些操作手段打通胆管。这种操作通常可以在ERCP检查过程中使用经 内镜下 的器械完成。"
test_symptom2= "肝炎  通常是由病毒引起的肝脏炎症，但可由自身免疫性疾病或使用某些药物引起。肝炎可损害肝脏，使得输送胆红素进入胆管的能力减弱。肝炎通常由病毒引起，可能是急性的（短暂的）或慢性的（持续至少 6 个月）。急性病毒性肝炎是黄疸的常见病因，尤其是发生在年轻人和其他健康人群的黄疸。当肝炎是由某种自身免疫性疾病或某些药物引起时，是不会造成人与人之间传染的。\n酒精相关性肝病 酒精相关性肝病 长期大量饮酒会损害肝脏。造成肝损伤的饮酒量及所需时间存在个体差异，但通常情况下，一般过度饮酒至少8至10年可引起肝损伤。\n胆管梗阻 胆管梗阻 当胆管阻塞时，胆红素将在血液中积聚。大多数堵塞是由胆结石引起的，但有些是由肿瘤（例如胰腺或胆管的肿瘤）或罕见的肝脏疾病（如 原发性胆汁性胆管炎 原发性胆汁性胆管炎 原发性胆汁性胆管炎 或 原发性硬化性胆管炎 原发性硬化性胆管炎 原发性硬化性胆管炎 ）引起。\n黄疸的其他原因 黄疸的其他原因 一些药物、毒素和草药产品也会对肝脏造成损害（参见表 黄疸的一些病因及特征 黄疸的一些病因及特征 黄疸的一些病因及特征 ）。 黄疸不常见的病因包括干扰人体胆红素代谢的遗传性疾病，例如Gilbert综合症和其他少见的疾病，如慢性特发性黄疸（Dubin-Johnson 综合征）。Gilbert 综合症患者的胆红素水平会稍有升高，但通常不足以引起黄疸。这种疾病通常与遗传有关，常常在年轻人做常规筛查时发现，它没有其他症状也不会引起不良后果。 引起红细胞过度分解的疾病（溶血）通常会引起黄疸（参见 自身免疫性溶血性贫血 自身免疫性溶血性贫血 自身免疫性溶血性贫血 和 新生儿溶血病 新生儿溶血病 新生儿溶血病 ）"

symptom_ner("./data/symptoms.json")

# print(len(test_symptom2))
# print(readable_result(bio_ner_task([test_symptom,test_symptom2])))
