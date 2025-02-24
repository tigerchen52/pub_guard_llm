import traceback
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .utils import format_prompt, extract_answer, Metadata

# Configure logging to print INFO messages to the console
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)

class PubGuard():
    def __init__(self, model, tokenizer):
        self.metadata = Metadata()
        self.tokenizer = tokenizer
        self.model = model
    
    def predict(self, input_article, max_new_token=256, temperature=0.1, **kwargs):
        required_keys = {'Title', 'Abstract', 'Authors', 'Institutions', 'Journal'}

        # Ensure all required keys are present
        assert required_keys.issubset(input_article.keys()), f"Missing keys: {required_keys - input_article.keys()}"
        
        try:
            input_article = self.metadata.get_external_knowledge(input_article)
            prompt = format_prompt(input_article, examples=[], k_shot=0)
            logger.info(f"Generated Prompt: {prompt}")
            messages = [
            {"from": "human", "value": prompt},
            ]
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
            ).to(self.model.device)

            outputs = self.model.generate(input_ids=inputs, max_new_tokens=max_new_token, use_cache=True,
                                temperature=temperature, **kwargs)
            generated_text = self.tokenizer.batch_decode(outputs)
            answer = extract_answer(generated_text[0])
            
            return answer
        
        except ValueError as ve:
            traceback.print_exc() 
            logger.error(f"ValueError: {ve}")
            return "Error: Invalid input provided."

        except RuntimeError as re:
            traceback.print_exc() 
            logger.error(f"RuntimeError: {re}")
            return "Error: Model failed to generate a response."

        except Exception as e:
            traceback.print_exc() 
            logger.error(f"Unexpected Error: {e}")
            return "Error: An unexpected issue occurred during prediction."



if __name__ == '__main__':
    input_article = {
        'Title':"The prevalence of diabetes in children and adolescents is increasing worldwide",
        'Abstract':"The prevalence of diabetes in children and adolescents is increasing worldwide, with profound implications on the long-term health of individuals, societies, and nations. The diagnosis and management of diabetes in youth presents several unique challenges. Although type 1 diabetes is more common among children and adolescents, the incidence of type 2 diabetes in youth is also on the rise, particularly among certain ethnic groups. In addition, less common types of diabetes such as monogenic diabetes syndromes and diabetes secondary to pancreatopathy (in some parts of the world) need to be accurately identified to initiate the most appropriate treatment. A detailed patient history and physical examination usually provides clues to the diagnosis. However, specific laboratory and imaging tests are needed to confirm the diagnosis. The management of diabetes in children and adolescents is challenging in some cases due to age-specific issues and the more aggressive nature of the disease. Nonetheless, a patient-centered approach focusing on comprehensive risk factor reduction with the involvement of all concerned stakeholders (the patient, parents, peers and teachers) could help in ensuring the best possible level of diabetes control and prevention or delay of long-term complications. ",
        'Authors':["Ranjit Unnikrishnan", "Viral N Shah", "Viswanathan Mohan"],
        'Institutions':["Barbara Davis Center for Diabetes, University of Colorado Anschutz Campus, Aurora, CO USA", "Madras Diabetes Research Foundation & Dr Mohan's Diabetes Specialties Centre, Who Collaborating Centre for Non-Communicable Diseases Prevention and Control, 4, Conran Smith Road, Gopalapuram, Chennai, 600 086 India."],
        'Journal':'Frontiers in Cell and Developmental Biology',
    }
    # metadata = Metadata()
    # article = metadata.get_external_knowledge(input_article)
    #Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("Lihuchen/pub-guard-llama-8b")
    # Load the model
    model = AutoModelForCausalLM.from_pretrained("Lihuchen/pub-guard-llama-8b", torch_dtype=torch.bfloat16)
    model.to('cuda')
    
    pub_guard = PubGuard(model=model, tokenizer=tokenizer)
    answer = pub_guard.predict(input_article)
    #answer = predict_retraction(article)
    print(answer)