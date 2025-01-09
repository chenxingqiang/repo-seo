import spacy
import logging
from keybert import KeyBERT
from typing import List, Dict, Tuple

class ContentAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.keyword_model = KeyBERT()
        self.logger = logging.getLogger(__name__)

    def analyze_readme(self, content: str) -> Tuple[str, List[str], List[str]]:
        """
        Analyze README content to extract summary, topics, and named entities.
        
        Args:
            content: The README content to analyze
            
        Returns:
            Tuple containing (summary, topics, named_entities)
        """
        try:
            # Process the content with spaCy
            doc = self.nlp(content[:10000])  # Limit content length for processing
            
            # Extract main sentences for summary
            sentences = [sent.text.strip() for sent in doc.sents]
            summary = " ".join(sentences[:3]) if sentences else ""
            
            # Extract keywords using KeyBERT
            keywords = self.keyword_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                use_maxsum=True,
                nr_candidates=20,
                top_n=10
            )
            topics = [keyword[0] for keyword in keywords]
            
            # Extract named entities
            entities = []
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON", "WORK_OF_ART"]:
                    entities.append(ent.text)
            
            return summary, topics, list(set(entities))
            
        except Exception as e:
            self.logger.error(f"Error analyzing content: {str(e)}")
            return "", [], []

    def extract_topics(self, content: str) -> List[str]:
        """
        Extract main topics from content using KeyBERT.
        
        Args:
            content: The content to analyze
            
        Returns:
            List of extracted topics
        """
        try:
            keywords = self.keyword_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                use_maxsum=True,
                nr_candidates=10,
                top_n=5
            )
            return [keyword[0] for keyword in keywords]
        except Exception as e:
            self.logger.error(f"Error extracting topics: {str(e)}")
            return []

    def analyze_repository(self, repo_data: Dict) -> Dict:
        """
        Analyze repository data to extract relevant information.
        
        Args:
            repo_data: Dictionary containing repository information
            
        Returns:
            Dictionary with analyzed data
        """
        try:
            name = repo_data.get("name", "")
            description = repo_data.get("description", "")
            language = repo_data.get("primaryLanguage", {}).get("name", "")
            topics = repo_data.get("repositoryTopics", [])
            
            # Combine name and description for analysis
            content = f"{name} {description}"
            
            # Extract topics
            extracted_topics = self.extract_topics(content)
            
            # Combine with existing topics
            all_topics = list(set(extracted_topics + [t["name"] for t in topics if t]))
            
            return {
                "name": name,
                "description": description,
                "language": language,
                "topics": all_topics,
                "extracted_topics": extracted_topics
            }
        except Exception as e:
            self.logger.error(f"Error analyzing repository: {str(e)}")
            return {} 