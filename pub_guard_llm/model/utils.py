import json
from typing import Dict, Optional, List
import traceback
import re
import requests
from pathlib import Path
# Get the directory of the current script
current_dir = Path(__file__).parent

class Metadata:
    def __init__(self):
        self.cache_journal_info = load_cache_journal(f"{current_dir}/data/journal_cache.jsonl")
        self.cache_institution_info = load_cache_affiliation(f"{current_dir}/data/affiliation_cache.jsonl")
        
    
    def get_external_knowledge(self, input_article: dict) -> dict:
        try:
            title = input_article['Title']
            authors, affiliations, journal = input_article['Authors'], input_article['Institutions'], input_article['Journal']
            external_author_info = get_author_info_by_title(title)
            if len(external_author_info) != 0:
                external_author_info = '; '.join([f"{obj['name']} ({categorize_h_index(int(obj['h-index']))})" for obj in external_author_info]) 
            else:
                external_author_info = '; '.join([author+" (null)" for author in authors])
            
            external_aff_info = list()
            for aff in affiliations:
                
                aff_name = get_ins_name(aff).casefold()
                external_info = self.cache_institution_info.get(aff_name, None)
                if external_info:
                    external_aff_info.append(f"{aff} ({categorize_avg_citation(external_info)})")
                else:external_aff_info.append(f"{aff} (null)")
            external_aff_info = "; ".join(external_aff_info)
            
            external_journal_info = self.cache_journal_info.get(journal.casefold(), None)
            if external_journal_info:
                external_journal_info = f"{journal} ({categorize_jcr_partition(journal)})"
            else:
                external_journal_info = f"{journal} (null)"
        except Exception:
            traceback.print_exc()
        
        input_article.update({
            'Authors':external_author_info,
            'Institutions':external_aff_info,
            'Journal':external_journal_info
        })
        return input_article

def load_cache_journal(file_name: str) -> Dict[str, float]:
    """
    Load journal impact factors from a JSON Lines file.

    Args:
        file_name (str): The path to the JSON Lines file.

    Returns:
        Dict[str, float]: A dictionary mapping journal names to their JCR values.
    """
    journal_jcr = {}
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    obj = json.loads(line)[0]
                    if 'journal' not in obj:continue
                    journal_name = obj['journal'].casefold()
                    jcr = obj['jcr']
                    journal_jcr[journal_name] = jcr
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"Error processing line: {line.strip()} - {e}")
                    traceback.print_exc() 
    except FileNotFoundError:
        print(f"File not found: {file_name}, current path: {current_dir}")
    except IOError as e:
        print(f"Error reading file: {file_name} - {e}")
    
    return journal_jcr


def load_cache_affiliation(file_name: str) -> Dict[str, float]:
    """
    Load citations of an institution from a JSON Lines file.

    Args:
        file_name (str): The path to the JSON Lines file.

    Returns:
        Dict[str, float]: A dictionary mapping institution names to their average citation.
    """
    institution_avg_citation = {}
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    obj = json.loads(line)
                    if 'name' not in obj:continue
                    institution_name = obj['name'].casefold()
                    works_count, cited_by_count = obj['works_count'], obj['cited_by_count']
                    avg_citation = cited_by_count / works_count if works_count!=0 else 0
                    institution_avg_citation[institution_name] = avg_citation
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"Error processing line: {line.strip()} - {str(e)}")
                    traceback.print_exc() 
    except FileNotFoundError:
        print(f"File not found: {file_name}, current path: {current_dir}")
    except IOError as e:
        print(f"Error reading file: {file_name} - {e}")
    
    return institution_avg_citation


def get_author_info_by_title(title: str) -> List[Dict]:
    """
    Fetches author details for a given paper title by retrieving their author IDs first.
    
    Args:
        title (str): The title of the paper.
    
    Returns:
        List[Dict]: A list of dictionaries containing author details.
    """
    author_ids = get_author_id_from_title(title)
    
    if not author_ids:
        return []
    
    results = []
    for aid in author_ids:
        author_info = get_author_info_by_id(aid)
        if author_info:
            results.append(author_info)
    
    return results
        

def get_author_id_from_title(paper_title: str) -> List[str]:
    """
    Fetches author IDs from Semantic Scholar API based on a given paper title.
    
    Args:
        paper_title (str): The title of the paper.
    
    Returns:
        list: A list of author IDs if found, else an empty list.
    """
    url = "http://api.semanticscholar.org/graph/v1/paper/search"
    query_params = {
        "query": paper_title,
        "fields": "title,authors.name,authors.authorId,authors.affiliations",
        "limit": 1
    }
    
    try:
        response = requests.get(url, params=query_params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        
        try:
            response_data = response.json()
        except ValueError:
            print("Error: Failed to decode JSON response.")
            return []
        
        author_ids = []
        papers = response_data.get("data", [])
        if papers:
            paper = papers[0]  # Assuming the first result is the most relevant
            for author in paper.get("authors", []):
                a_id = author.get("authorId")
                if a_id:
                    author_ids.append(a_id)
        else:
            print("No papers found with the specified title.")
            return []
        
        return author_ids
    
    except requests.exceptions.Timeout:
        print("Error: The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request: {e}")
    
    return []



def get_author_info_by_id(author_id: str) -> Optional[Dict[str, str]]:
    """
    Fetches author details from Semantic Scholar API based on author ID.
    
    Args:
        author_id (str): The ID of the author.
    
    Returns:
        Optional[Dict[str, str]]: A dictionary containing author details if found, else None.
    """
    url = f"http://api.semanticscholar.org/graph/v1/author/{author_id}"
    query_params = {
        "fields": "name,affiliations,paperCount,citationCount,hIndex"
    }
    
    try:
        response = requests.get(url, params=query_params, timeout=10)
        response.raise_for_status()
        
        try:
            author_data = response.json()
        except ValueError:
            print("Error: Failed to decode JSON response.")
            return None
        
        author_info = {
            'aid': author_id,
            'name': author_data.get('name', 'N/A'),
            'affiliations': ', '.join(author_data.get('affiliations', [])),
            'paper_count': str(author_data.get('paperCount', 'N/A')),
            'citation': str(author_data.get('citationCount', 'N/A')),
            'h-index': str(author_data.get('hIndex', 'N/A'))
        }
        
        return author_info
    
    except requests.exceptions.Timeout:
        print("Error: The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request: {e}")
    
    return None

def get_ins_name(ins_name: str) -> str:
    key_words = ['university', 'hospital']
    names = ins_name.split(", ")
    for name in names:
        for kw in key_words:
            if kw in name.lower():return name
    result = names[1] if len(names)>1 else names[0]
    return result
    
def categorize_h_index(h_index):
    """
    Categorizes h-index values into five levels with reputation labels.

    Parameters:
        h_index (int): The h-index value to categorize.

    Returns:
        str: The level and reputation label corresponding to the h-index value.
    """
    if h_index < 0:
        raise ValueError("h-index cannot be negative")

    if 0 <= h_index <= 5:
        return f"author h-index: {h_index}, Emerging Researcher"
    elif 5 < h_index <= 15:
        return f"author h-index: {h_index}, Early Career Researcher"
    elif 15 < h_index <= 30:
        return f"author h-index: {h_index}, Established Researcher"
    elif 30 < h_index <= 45:
        return f"author h-index: {h_index}, Influential Researcher"
    else:
        return f"author h-index: {h_index}, Leading Expert"
    
    
def categorize_avg_citation(avg_citation):
    """
    Categorizes average citation per paper into five levels with institutional reputation labels.

    Parameters:
        avg_citation (float): The average number of citations per paper.

    Returns:
        str: The level and reputation label corresponding to the average citation value.
    """
    avg_citation = round(avg_citation, 0)
    if avg_citation < 0:
        raise ValueError("Average citation cannot be negative")

    if 0 <= avg_citation <= 5:
        return f"institution average citation: {avg_citation}, Developing Institution"
    elif 5 < avg_citation <= 15:
        return f"institution average citation: {avg_citation}, Emerging Institution"
    elif 15 < avg_citation <= 30:
        return f"institution average citation: {avg_citation}, Established Institution"
    elif 30 < avg_citation <= 45:
        return f"institution average citation: {avg_citation}, Reputable Institution"
    else:
        return f"institution average citation: {avg_citation}, World-Class Institution"
    
    
def categorize_jcr_partition(jcr_partition):
    """
    Transforms JCR partition (quartile) into four levels with institutional reputation labels.

    Parameters:
        jcr_partition (int): The quartile partition (1, 2, 3, or 4) where a journal belongs.

    Returns:
        str: The level and reputation label corresponding to the JCR partition.

    Raises:
        ValueError: If the input is not between 1 and 4 (inclusive).
    """

    if jcr_partition == "Q1":
        return "journal JCR: Q1, Top Level Journal"
    elif jcr_partition == "Q2":
        return "journal JCR: Q2, High Level Journal"
    elif jcr_partition == "Q3":
        return "journal JCR: Q3, Moderate Level Journal"
    else:  # jcr_partition == 4
        return "journal JCR: Q4, Low Level Journal"
    
    
def format_prompt(input_article, examples=[], k_shot=0):
    prompt = (
        "You are tasked with determining whether a given research paper should be retracted.\n"
        "To make this judgment, analyze the provided title, abstract, author information, "
        "institutional affiliation, and publishing journal.\n"
        f"Here are some factors to consider: (1) the reputation of the journal (whether it is a top journal with a rigorous peer review process)\n"
        f"(2) the reputation of the authors and their affiliations (whether the authors tend to have misconduct in their research)\n"
        f"(3) the integrity of the title and abstract (e.g., research topic, using made-up data, plagiarism, etc)\n"
        f"In addition, if check if Email addresses are provided, check if it conforms to institutional format. Otherwise, no need to make comments about the Email adresses\n"
        ""
    )
    for example in examples[:k_shot]:
        prompt += "Use the examples below as guidance:\n"
        prompt += (
            f"Example:\n"
            f"Title: {example['Title']}\n"
            f"Abstract: {example['Abstract']}\n"
            f"Authors: {example['Authors']}\n"
            f"Institutions: {example['Institutions']}\n"
            f"Journal: {example['Journal']}\n"
            f"Label: {example['IsRetracted']}\n\n"
        )
    prompt += (
        "Analyze the following paper:\n"
        f"Title: {input_article['Title']}\n"
        f"Abstract: {input_article['Abstract']}\n"
        f"Authors: {input_article['Authors']}\n"
        f"Institutions: {input_article['Institutions']}\n"
        f"Journal: {input_article['Journal']}\n"
        f"Please first provide your prediction of whether this paper should be retracted and then provide your assessment and explanation.\n"
        "Label (answer Yes or No): "
    )
    return prompt


def extract_answer(input_string):

    # Define the pattern to extract text between the assistant's start and end tags
    pattern = r"<\|im_start\|>assistant\n(.*?)(?:<\|im_end\|>|$)"

    # Search for the pattern in the input string
    match = re.search(pattern, input_string, re.DOTALL)

    # Check if a match is found and extract the response
    if match:
        assistant_response = match.group(1).strip()
        #print("Assistant's response:", assistant_response)
        return assistant_response
    else:
        return None
