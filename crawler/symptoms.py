import requests
from bs4 import BeautifulSoup
import lxml  
import re
import json

'''
构建数据结构
topic = [
{"name": "症状名称", "url": "症状链接"},
]

'''

class Symptoms:
    def __init__(self, url):
        self.url = url
        self.topic = []
        self.raw_symptoms = []
        self.locator_start_flag_after_title = 'div[data-testid="topic-resource"]'
        self.locator_symptoms_title = 'h1.TopicHead_topicHeaderTittle__miyQz span'
        self.locator_symptoms_description = 'div.TopicMainContent_content__MEmoN span[data-testid *= "topicText"]'
        self.locator_stop_flag_before_causes = 'a.TopicFHead_topicFHeadSectionWithScroll__XoxGU[aria-hidden=true]'
        #下面的每个大项都会包含几个section，每个section有个ul，ul下面有li，li下面有p
        self.locator_root_cause = 'section[id*="病因"]>div>section'
        self.locator_root_cause_span = 'section[id*="病因"] span[data-testid="topicText"]'
        self.locator_evaluation = 'section[id*="评估"]>div>section'
        self.locator_evaluation_span = 'section[id*="评估"] span[data-testid="topicText"]'
        self.locator_treatment = 'section[id*="治疗"]>div>section'
        self.locator_treatment_span = 'section[id*="治疗"] span[data-testid="topicText"]'
        self.locator_key_points = 'section[id*="关键点"]'
        self.locator_key_points_span = 'section[id*="关键点"] span[data-testid="topicText"]'
        self.locator_harsh_symptoms = 'h2[data-originaltitle="严重症状"]'

        
    
    def get_topic(self, topic_path):
        response = requests.get(self.url+'/home/symptoms')
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            lists = soup.select('main li a')
            for item in lists:
            
                self.topic.append({item.get_text(): item['href']})
        #将数据写入json文件
        with open(topic_path, 'w', encoding='utf-8') as f:
            json.dump(topic_path, f, ensure_ascii=False)
            f.close()
        print("数据写入json文件成功！")

    def get_detail_symptom(self, topic_path, symptoms_file_path):
        raw_symptoms = []

        '''
            {
            "name": "症状名称",
            "url": "症状链接"，
            "symptoms_description": "",
            "symptoms_causes": {
                "allinone": "病因描述",
                "detail_causes": [],
            },
            "symptoms_evaluation": {
                "allinone": "评估描述",
                "evaluation_detail": {
                    "warning_symptom": "",
                    "when_see_doctor": "",
                    "what_doctor_do": "",
                    "what_to_exam": ""
                },
            },
            "symptoms_treatment": {
                "allinone": "治疗描述",
                "detail_treatment": [],
            },
            "symptoms_key_point": [],
        }
        '''
        with open(topic_path, 'r', encoding='utf-8') as f:
            topics = json.load(f)
            f.close()
        
        # topics = [{"眼睛凸出（突眼或眼球突出）": "/home/eye-disorders/symptoms-of-eye-disorders/bulging-eyes"}]
        for item in topics:
            for key, value in item.items():
                print(f"now processing {key}, {value}")
                item_symptoms = {
                    "name": key,
                    "url": value,
                    "symptoms_description": "",
                    "symptoms_causes": {
                        "allinone": "病因描述：",
                        "detail_causes": "",
                    },
                    "symptoms_evaluation": {
                        "allinone": "评估描述：",
                        "evaluation_detail": "",
                    },
                    "symptoms_treatment": {
                        "allinone": "治疗描述：",
                        "detail_treatment": "",
                    },
                    "symptoms_key_point": [],
                }
                
                
                response = requests.get(self.url + value)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    symptoms_description = soup.select(self.locator_symptoms_description)
                    symptoms_description_flag = soup.select_one(self.locator_stop_flag_before_causes)
                    # symptoms_description_span =symptoms_description.find_all_previous('span')
                    symptoms_causes = soup.select(self.locator_root_cause)
                    symptoms_causes_span = soup.select(self.locator_root_cause_span)
                    symptoms_evaluation = soup.select(self.locator_evaluation)
                    symptoms_evaluation_span = soup.select(self.locator_evaluation_span)
                    symptoms_treatment = soup.select(self.locator_treatment)
                    symptoms_treatment_span = soup.select(self.locator_treatment_span)
                    symptoms_key_points = soup.select(self.locator_key_points_span)
                    
                    symptoms_description = []
                    try:
                        if symptoms_description_flag:    
                            print('倒查1，输出的元素顺序是反的')
                            symptoms_description = symptoms_description_flag.find_all_previous('span', attrs={"data-testid": "topicText"})
                            print(symptoms_description)
                            print(len(symptoms_description))
                            print(type(symptoms_description))
                            
                        else:
                            print('倒查2，输出的元素顺序是反的')
                            symptoms_description = soup.select_one("a[aria-hidden][tabindex]").find_all_previous('span', attrs={"data-testid": "topicText"})
                            print(symptoms_description)
                            print(len(symptoms_description))
                            print(type(symptoms_description))
                        
                    except Exception as e:
                        print(e)
                        print("特殊页面，只有症状描述没有其他的, 处理完描述跳到下一个")
                        symptoms_description = soup.select(self.locator_symptoms_description)
                        
                        for description_span in symptoms_description:
                            # print(description_span.get_text())
                            item_symptoms["symptoms_description"] += " " + description_span.get_text()
                        raw_symptoms.append(item_symptoms)
                        continue
                    finally:
                        print(len(symptoms_description))
                        print(type(symptoms_description))
                        for description_span in symptoms_description:
                            # print(description_span.get_text())
                            item_symptoms["symptoms_description"] =  description_span.get_text() +" "+ item_symptoms["symptoms_description"]
                    #先处理symptoms_description 
                    
                    
                    
                    
                    #处理symptoms_causes
                    #下面的每个大项都会包含几个section，每个section有个ul，ul下面有li，li下面有p
                    if len(symptoms_causes) > 0:
                        symptoms_causes_content = ""
                        for cause in symptoms_causes:
                            
                            spans = cause.find_all('span')
                            

                            symptoms_causes_content += " ".join([s.get_text() for s in spans]) + "\n"

                        item_symptoms["symptoms_causes"]["detail_causes"] = symptoms_causes_content
                    else:
                        for span in symptoms_causes_span:
                            
                            item_symptoms["symptoms_causes"]["allinone"] += " " + span.get_text()
                    
                    #处理评估信息
                    if len(symptoms_evaluation) > 0:
                        symptoms_evaluation_content = ""
                        for evaluation in symptoms_evaluation:
                            spans = evaluation.find_all('span')
                            
                            
                            symptoms_evaluation_content += " ".join([s.get_text() for s in spans]) + "\n"

                        item_symptoms["symptoms_evaluation"]["evaluation_detail"] = symptoms_evaluation_content
                    else:
                        for span in symptoms_evaluation_span:
                            
                            item_symptoms["symptoms_evaluation"]["allinone"] += " " + span.get_text() 

                    #处理治疗信息   
                    if len(symptoms_treatment) > 0:
                        symptoms_treatment_content = ""
                        for treatment in symptoms_treatment:
                            spans = treatment.find_all('span')

                            symptoms_treatment_content += " ".join([s.get_text() for s in spans]) + "\n"

                        item_symptoms["symptoms_treatment"]["detail_treatment"] = symptoms_treatment_content
                    else:
                        for span in symptoms_treatment_span:
                            
                            item_symptoms["symptoms_treatment"]["allinone"] += " " + span.get_text()
                    
                    #处理关键点信息
                    if len(symptoms_key_points) > 0:
                        for key_point in symptoms_key_points:
                            item_symptoms["symptoms_key_point"].append(key_point.get_text())
                    else:
                        item_symptoms["symptoms_key_point"] = []
                    
                    print(item_symptoms)
                    raw_symptoms.append(item_symptoms)
                    # self.raw_symptoms.append({
                    #     "name": key,
                    #     "url": value,
                    #     "symptoms_description": symptoms_description,
                    #     "symptoms_causes": symptoms_causes,
                    #     "symptoms_diagnosis": symptoms_diagnosis,
                    #     "symptoms_treatment": symptoms_treatment,
                    #     "symptoms_examination": symptoms_examination
                    # })
                else:
                    print(response.url)
                    print(response.status_code)
        
        #将数据写入json文件
        with open(symptoms_file_path, 'w', encoding='utf-8') as f:
            json.dump(raw_symptoms, f, ensure_ascii=False)
            f.close()
        return True
    
if __name__ == "__main__":
    url = "https://www.msdmanuals.cn"
    symptoms = Symptoms(url)
    # topic = symptoms.get_topic()
    path = "./data/raw_topics.json"
    result = symptoms.get_detail_symptom(path, './data/symptoms.json')
    print(result)
    
    