import os
os.environ['TRANSFORMERS_CACHE'] = "/home/ubuntu/my_data/hf_model"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from source import PubGuard



input_article = {
    'Title':"The prevalence of diabetes in children and adolescents is increasing worldwide",
    'Abstract':"The prevalence of diabetes in children and adolescents is increasing worldwide, with profound implications on the long-term health of individuals, societies, and nations. The diagnosis and management of diabetes in youth presents several unique challenges. Although type 1 diabetes is more common among children and adolescents, the incidence of type 2 diabetes in youth is also on the rise, particularly among certain ethnic groups. In addition, less common types of diabetes such as monogenic diabetes syndromes and diabetes secondary to pancreatopathy (in some parts of the world) need to be accurately identified to initiate the most appropriate treatment. A detailed patient history and physical examination usually provides clues to the diagnosis. However, specific laboratory and imaging tests are needed to confirm the diagnosis. The management of diabetes in children and adolescents is challenging in some cases due to age-specific issues and the more aggressive nature of the disease. Nonetheless, a patient-centered approach focusing on comprehensive risk factor reduction with the involvement of all concerned stakeholders (the patient, parents, peers and teachers) could help in ensuring the best possible level of diabetes control and prevention or delay of long-term complications. ",
    'Authors':["Ranjit Unnikrishnan", "Viral N Shah", "Viswanathan Mohan"],
    'Institutions':["Barbara Davis Center for Diabetes, University of Colorado Anschutz Campus, Aurora, CO USA", "Madras Diabetes Research Foundation & Dr Mohan's Diabetes Specialties Centre, Who Collaborating Centre for Non-Communicable Diseases Prevention and Control, 4, Conran Smith Road, Gopalapuram, Chennai, 600 086 India."],
    'Journal':'Frontiers in Cell and Developmental Biology',
    }

tokenizer = AutoTokenizer.from_pretrained("Lihuchen/pub-guard-llama-8b")
model = AutoModelForCausalLM.from_pretrained("Lihuchen/pub-guard-llama-8b", torch_dtype=torch.bfloat16)
model.to('cuda')

pub_guard = PubGuard(model=model, tokenizer=tokenizer)
answer = pub_guard.predict(input_article)
print(answer)