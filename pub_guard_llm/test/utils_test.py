# test/utils_test.py
import unittest
from source.model import utils

class TestUtils(unittest.TestCase):
    def test_journal_jcr(self):
        journal_jcr = utils.load_cache_journal("data/journal_cache.jsonl")
        mock_data = "NATURE".casefold()
        expected_result = "Q1"
        self.assertEqual(journal_jcr[mock_data], expected_result)
        
    def test_institution_avg_citation(self):
        institution_avg_citation = utils.load_cache_affiliation("data/affiliation_cache.jsonl")
        mock_data = "harvard university".casefold()
        expected_result = 64
        self.assertEqual(int(institution_avg_citation[mock_data]), expected_result)
        
    def test_get_author_info_by_title(self):
        
        mock_data = "Challenges in diagnosis and management of diabetes in the young."
        expected_result = 3
        author_info = utils.get_author_info_by_title(mock_data)
        self.assertEqual(len(author_info), expected_result)
        
        
    def test_metadata(self):
        input_article = {
        'Title':"Challenges in diagnosis and management of diabetes in the young.",
        'Abstract':"The prevalence of diabetes in children and adolescents is increasing worldwide, with profound implications on the long-term health of individuals, societies, and nations. The diagnosis and management of diabetes in youth presents several unique challenges. Although type 1 diabetes is more common among children and adolescents, the incidence of type 2 diabetes in youth is also on the rise, particularly among certain ethnic groups. In addition, less common types of diabetes such as monogenic diabetes syndromes and diabetes secondary to pancreatopathy (in some parts of the world) need to be accurately identified to initiate the most appropriate treatment. A detailed patient history and physical examination usually provides clues to the diagnosis. However, specific laboratory and imaging tests are needed to confirm the diagnosis. The management of diabetes in children and adolescents is challenging in some cases due to age-specific issues and the more aggressive nature of the disease. Nonetheless, a patient-centered approach focusing on comprehensive risk factor reduction with the involvement of all concerned stakeholders (the patient, parents, peers and teachers) could help in ensuring the best possible level of diabetes control and prevention or delay of long-term complications. ",
        'Authors':["Ranjit Unnikrishnan", "Viral N Shah", "Viswanathan Mohan"],
        'Institutions':["Barbara Davis Center for Diabetes, University of Colorado Anschutz Campus, Aurora, CO USA", "Madras Diabetes Research Foundation & Dr Mohan's Diabetes Specialties Centre, Who Collaborating Centre for Non-Communicable Diseases Prevention and Control, 4, Conran Smith Road, Gopalapuram, Chennai, 600 086 India."],
        'Journal':'Frontiers in Cell and Developmental Biology',
        }
        metadata = utils.Metadata()
        article = metadata.get_external_knowledge(input_article)
        expected_result = "Frontiers in Cell and Developmental Biology (journal JCR: Q4, Low Level Journal)"
        self.assertEqual(article['Journal'], expected_result)
        
if __name__ == '__main__':
    unittest.main()
