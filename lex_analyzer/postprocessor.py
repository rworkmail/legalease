import re
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Regex patterns
MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)


def extract_money_regex(text: str):
    return [match.group() for match in MONEY_REGEX.finditer(text)]


def extract_durations_regex(text: str):
    return [match.group() for match in DURATION_REGEX.finditer(text)]


def extract_parties_spacy(text: str):
    doc = nlp(text)
    return [
        ent.text for ent in doc.ents
        if ent.label_ in ("PERSON", "ORG") and len(ent.text.split()) <= 3
    ]


def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()

    # Enhance values
    enhanced["extracted_data"]["payment_terms"]["money"] = extract_money_regex(text)
    enhanced["extracted_data"]["duration"] = extract_durations_regex(text)

    if not enhanced["extracted_data"]["parties"]:
        enhanced["extracted_data"]["parties"] = extract_parties_spacy(text)

    return enhanced
