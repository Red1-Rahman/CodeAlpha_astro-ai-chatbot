import json
from pathlib import Path

def load_faqs():
    """
    Loads the FAQ data from the JSON file.
    Returns a list of FAQ dictionaries.
    """
    # __file__ gets the path of this current script.
    # .resolve().parent.parent navigates up from /chatbot to the root directory.
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "data" / "faqs.json"
    
    try:
        # I use both windows and linux so I will do utf-8 encoding for cross-platform consistency
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file) 
            # I guess I only need the "faqs" array for the chatbot brain
            return data.get("faqs", [])
            
    except FileNotFoundError:
        print(f"CRITICAL ERROR: FAQ file not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"CRITICAL ERROR: Invalid JSON format in {file_path}")
        return []

# Quick test block: This only runs if i execute this file directly
if __name__ == "__main__":
    faqs = load_faqs()
    print(f"Successfully loaded {len(faqs)} FAQs from disk.")