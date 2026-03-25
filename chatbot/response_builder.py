import os
import urllib.parse
from chatbot.faq_loader import load_faqs

# Precompute FAQ ID → question map for O(1) related lookup
_faqs = load_faqs()
_faq_id_map = {item["id"]: item["question"] for item in _faqs}

# Config with environment overrides
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "redwanrahman2002@outlook.com")
GITHUB_REPO = os.getenv("GITHUB_REPO", "https://github.com/Red1-Rahman/Astro-AI")

def format_response(match_data: dict, user_query: str = "") -> dict:
    """
    Format matcher output into frontend API response.
    Resolves related_ids into human-readable questions.
    """
    score = round(match_data.get("score", 0.0), 2)

    if not match_data.get("success"):
        mail_subject = urllib.parse.quote("FAQ - Astro AI")

        fallback_msg = (
            "I'm sorry, I couldn't find a confident answer to your question in my knowledge base.\n\n"
            "You can escalate this by reaching out directly:\n"
            f"• 📧 [Email Support](mailto:{SUPPORT_EMAIL}?subject={mail_subject})\n"
            f"• 🐙 [Create an Issue on GitHub]({GITHUB_REPO}/issues/new)"
        )

        return {
            "answer": fallback_msg,
            "score": score,
            "related_questions": []
        }

    faq = match_data.get("faq", {})
    raw_related_ids = faq.get("related_ids", [])

    related_questions = []
    for r_id in raw_related_ids:
        question = _faq_id_map.get(r_id)
        if question:
            related_questions.append({
                "id": r_id,
                "question": question
            })

    return {
        "answer": faq.get("answer", "Error: Answer missing from knowledge base."),
        "score": score,
        "related_questions": related_questions
    }