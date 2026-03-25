import spacy
import sys

# Load the lightweight English NLP model.
# wrap this in a try-except block just in case...
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("CRITICAL ERROR: SpaCy model 'en_core_web_sm' not found.")
    print("Please run this in your terminal: python -m spacy download en_core_web_sm")
    sys.exit(1)

def preprocess_text(text: str) -> str:
    """
    Cleans the input text using SpaCy.
    - Removes stop words (the, is, at, which)
    - Removes punctuation and extra whitespace
    - Lemmatizes words (e.g., 'installing' -> 'install')
    - Converts to lowercase
    """
    # Pass the raw text through the SpaCy pipeline
    doc = nlp(text)
    
    cleaned_tokens = []
    for token in doc:
        # Filter out stop words, punctuation, and raw spaces
        if not token.is_stop and not token.is_punct and not token.is_space:
            # Note:  purposely KEEP numbers. because in my Astro-AI context, 
            # terms like "21cm", "3.10", or "4GB" are highly relevant keywords
            cleaned_tokens.append(token.lemma_.lower())
            
    # Scikit-Learn's TF-IDF vectorizer expects a single string of space-separated words, not a Python list.
    return " ".join(cleaned_tokens)

# Quick test block
if __name__ == "__main__":
    sample_query = "What are the core dependencies for Astro-AI in 2026?"
    print(f"Original: {sample_query}")
    print(f"Cleaned:  {preprocess_text(sample_query)}")