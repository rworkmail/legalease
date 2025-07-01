import re
import spacy

nlp = spacy.load("en_core_web_sm")

MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)

def extract_money_regex(text: str):
    return [match.group() for match in MONEY_REGEX.finditer(text)]

def extract_durations_regex(text: str):
    matches = DURATION_REGEX.findall(text)
    filtered = [m for m in matches if not re.search(r"\b(?:1st|2nd|3rd|[4-9]th|[1-2][0-9]th|30th|31st)\s+day\b", m, re.IGNORECASE)]
    return filtered

def extract_parties_spacy(text: str):
    doc = nlp(text)
    return list(set(
        ent.text for ent in doc.ents
        if ent.label_ in ("PERSON", "ORG") and len(ent.text.split()) <= 3
    ))

def clean_constraints(constraints):
    filtered = []
    for c in constraints:
        if len(c) != 3:
            continue
        typ, middle, trailing = c
        if not middle.strip():
            continue
        if len(trailing.strip()) > 150:
            continue
        filtered.append(c)
    return filtered

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()
    enhanced["extracted_data"]["payment_terms"]["money"] = extract_money_regex(text)
    enhanced["extracted_data"]["duration"] = extract_durations_regex(text)

    if not enhanced["extracted_data"]["parties"]:
        enhanced["extracted_data"]["parties"] = extract_parties_spacy(text)
    else:
        enhanced["extracted_data"]["parties"] = list(set(enhanced["extracted_data"]["parties"]))

    if "constraints" in enhanced["extracted_data"]:
        enhanced["extracted_data"]["constraints"] = clean_constraints(enhanced["extracted_data"]["constraints"])

    return enhanced
