import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import custom modules
from chatbot.faq_loader import load_faqs
from chatbot.nlp_processor import preprocess_text

class FAQMatcher:
    def __init__(self):
        # Load the raw data
        self.faqs = load_faqs()
        self.vectorizer = TfidfVectorizer()
        self.corpus_matrix = None
        self.threshold = 0.4 # I will try different thresholds during testing, but 0.4 is a common starting point
        # Prepare the math matrix immediately upon startup
        self._prepare_corpus()

    def _prepare_corpus(self):
        """
        Builds the text corpus from the loaded FAQs and fits the TF-IDF vectorizer.
        We combine the question, intent, and keywords to create a richer target for matching.
        """
        if not self.faqs:
            print("WARNING: No FAQs loaded. Matcher will not work.")
            return

        corpus = []
        for item in self.faqs: 
            # Combine the question, intent, and keywords for a much higher accuracy rate.
            keywords_str = " ".join(item.get("keywords", []))
            raw_text = f"{item.get('question', '')} {item.get('intent', '')} {keywords_str}"
            
            # Clean the combined text using SpaCy processor
            cleaned_text = preprocess_text(raw_text)
            corpus.append(cleaned_text)
            
        # Fit the vectorizer on the entire FAQ corpus and transform it into a mathematical matrix
        self.corpus_matrix = self.vectorizer.fit_transform(corpus)

    def get_best_match(self, user_query: str) -> dict:
        """
        Takes a raw user query, cleans it, vectorizes it, and finds the most similar FAQ.
        Returns a dictionary with the matched FAQ and the similarity score.
        """
        if not self.faqs or self.corpus_matrix is None:
            return {"success": False, "score": 0.0, "message": "Knowledge base offline."}

        # 1. Clean the user's input
        cleaned_query = preprocess_text(user_query)
        
        # 2. Convert the cleaned query into a TF-IDF vector
        query_vector = self.vectorizer.transform([cleaned_query])
        
        # 3. Calculate cosine similarity between the query and all FAQs
        # This returns an array of scores, e.g., [[0.1, 0.8, 0.2, ...]]
        similarities = cosine_similarity(query_vector, self.corpus_matrix)[0]
        
        # 4. Find the index of the highest score
        best_index = np.argmax(similarities)
        best_score = similarities[best_index]
        
        # 5. Check if the score meets the minimum confidence threshold
        if best_score >= self.threshold:
            matched_faq = self.faqs[best_index]
            return {
                "success": True,
                "score": float(best_score),
                "faq": matched_faq
            }
        else:
            return {
                "success": False,
                "score": float(best_score),
                "message": "I'm sorry, I don't have information on that specific topic yet. Could you rephrase your question?"
            }

# Instantiate the matcher globally so it only loads and fits the corpus once
# when the FastAPI server starts.
matcher = FAQMatcher()

# Quick test block
if __name__ == "__main__":
    test_queries = [
        "How do I install Astro-AI from scratch?",
        "Explain the red fraction in clusters",
        "What is the capital of Bangladesh?" # This should fail the 0.4 threshold
    ]
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        result = matcher.get_best_match(q)
        if result.get("success"):
            print(f"Matched ID: {result['faq']['id']} (Score: {result['score']:.2f})")
            print(f"Answer snippet: {result['faq']['answer'][:50]}...")
        else:
            print(f"No match. Highest score was: {result['score']:.2f}")
            print(f"Fallback: {result['message']}")