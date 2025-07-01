import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Regex patterns
MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)
RECURRING_PATTERN = re.compile(r"\b(?:monthly|annually|weekly|biweekly|quarterly)\b", re.IGNORECASE)
LATE_FEE_PATTERN = re.compile(r"(?:late fee|penalty).*?\$[\d,]+(?:\.\d{2})?", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(
    r"\d+\s+[\w\s]+(?:Street|Avenue|Road|Lane|Drive|Boulevard|St\.?|Ave\.?|Rd\.?|Blvd\.?|Dr\.?)",
    re.IGNORECASE
)

def clean_money(text: str) -> str:
    return text.rstrip(",. ").replace(",", "")

def extract_money_regex(text: str):
    raw = [clean_money(m.group()) for m in MONEY_REGEX.finditer(text)]
    return sorted(set(raw), key=raw.index)

def extract_durations_regex(text: str):
    return sorted(set([m.group().strip("., ") for m in DURATION_REGEX.finditer(text)]))

def extract_parties_spacy(text: str):
    doc = nlp(text)
    parties = {
        ent.text.strip() for ent in doc.ents
        if ent.label_ in {"PERSON", "ORG"}
        and 2 <= len(ent.text.strip().split()) <= 4
        and ent.text.strip().lower() not in {"buyer", "seller", "lessor", "lessee"}
        and not ent.text.strip().lower().endswith(("contract", "agreement"))
    }
    return sorted(parties)

def extract_recurring_payments(text: str):
    return sorted(set(match.group().lower() for match in RECURRING_PATTERN.finditer(text)))

def extract_late_fee(text: str):
    return sorted(set(match.strip() for match in LATE_FEE_PATTERN.findall(text)))

def extract_property_address(text: str):
    return sorted(set(match.strip() for match in ADDRESS_PATTERN.findall(text)))

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()

    # Deduplicated money + duration
    enhanced["extracted_data"]["payment_terms"]["money"] = extract_money_regex(text)
    enhanced["extracted_data"]["duration"] = extract_durations_regex(text)

    # Parties
    if not enhanced["extracted_data"]["parties"]:
        enhanced["extracted_data"]["parties"] = extract_parties_spacy(text)

    # Recurring
    for recur in extract_recurring_payments(text):
        enhanced["extracted_data"]["constraints"].append(["recurring", recur, ""])

    # Late fees
    late = extract_late_fee(text)
    if late:
        enhanced["extracted_data"]["late_payment_penalty"] = late

    # Property address
    addr = extract_property_address(text)
    if addr:
        enhanced["extracted_data"]["property_address"] = addr

    return enhanced
