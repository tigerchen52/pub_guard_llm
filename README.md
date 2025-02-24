# Pub-Guard-LLM


[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pub-guard-llm/)
[![arXiv](https://img.shields.io/badge/arXiv-2502.15429-b31b1b.svg)](https://arxiv.org/html/2502.15429v1)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=000)](https://huggingface.co/Lihuchen/pub-guard-llama-8b)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pub-Guard-LLM is a specifically designed LLM for detecting fraudulent papers in academic publications. Pub-Guard-LLM consistently surpasses the performance of various baselines and provides more reliable explanations.

🤗 [Pub-Guard-LLM-1B](https://huggingface.co/Lihuchen/pub-guard-llama-1b) 🤗 [Pub-Guard-LLM-8B](https://huggingface.co/Lihuchen/pub-guard-llama-8b)
📐 [Pubmed Retraction Benchmark](https://huggingface.co/datasets/Lihuchen/pubmed_retraction)

# Quick Start
Install Pub-Guard-LLM using pip:
```python
pip install pub-guard-llm
```

An example to show how to use our model to detect fraudulent articles.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pub_guard_llm import PubGuard



input_article = {
    'Title':"Challenges in diagnosis and management of diabetes in the young.",
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
```
Pub-Guard automatically retrieves external knowledge to verify the credibility of authors, affiliations, and the journal:
```
Authors: R. Unnikrishnan (author h-index: 38, Influential Researcher); V. Shah (author h-index: 33, Influential Researcher); V. Mohan (author h-index: 105, Leading Expert)
Institutions: Barbara Davis Center for Diabetes, University of Colorado Anschutz Campus, Aurora, CO USA (institution average citation: 28.0, Established Institution); Madras Diabetes Research Foundation & Dr Mohan's Diabetes Specialties Centre, Who Collaborating Centre for Non-Communicable Diseases Prevention and Control, 4, Conran Smith Road, Gopalapuram, Chennai, 600 086 India. (null)
Journal: Frontiers in Cell and Developmental Biology (journal JCR: Q4, Low Level Journal)
```

Following that, Pub-Gaurd outputs the prediction with explanations:
```
No

The article appears legitimate based on the reputation of the authors, who are influential researchers and leading experts in their field, as indicated by their high h-index scores.

The institutions they are affiliated with are also established and have a high average citation score.

However, the journal in which the article is published is ranked in the Q4 category, indicating a lower level of impact and prestige.

The title and abstract of the article do not raise any immediate red flags regarding controversial topics, made-up data, or plagiarism.

However, the absence of information for one of the institutions is a concern.
```

# Experimental Results
![image](https://github.com/user-attachments/assets/e0e94771-ac46-495f-992b-ef7fba373225)

# Citation

If you find our work useful, please give us a citation:

```
@misc{chen2025pubguardllm,
      title={Pub-Guard-LLM: Detecting Fraudulent Biomedical Articles with Reliable Explanations}, 
      author={Lihu Chen and Shuojie Fu and Gabriel Freedman and Cemre Zor and Guy Martin and James Kinross and Uddhav Vaghela and Ovidiu Serban and Francesca Toni},
      year={2025},
      eprint={2502.15429},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.15429}, 
}
```
