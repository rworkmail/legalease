import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Regex patterns
MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)
RECURRING_PATTERN = re.compile(r"\b(?:monthly|annually|weekly|biweekly|quarterly)\b", re.IGNORECASE)
LATE_FEE_PATTERN = re.compile(r"(?:late fee|penalty).*?\$[\d,]+(?:\.\d{2})?", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(
    r"(\d+\s+[^,\n]+(?:Street|Avenue|Road|Lane|Drive|Boulevard|St\.?|Ave\.?|Rd\.?|Blvd\.?|Dr\.?))",
    re.IGNORECASE
)

def clean_money(text: str) -> str:
    return text.rstrip(",. ").replace(",", "")

def extract_money_regex(text: str):
    return [clean_money(match.group()) for match in MONEY_REGEX.finditer(text)]

def extract_durations_regex(text: str):
    return [match.group().strip("., ") for match in DURATION_REGEX.finditer(text)]

def extract_parties_spacy(text: str):
    doc = nlp(text)
    parties = {
        ent.text.strip() for ent in doc.ents
        if ent.label_ in ("PERSON", "ORG")
        and len(ent.text.strip().split()) <= 4
        and ent.text.strip().lower() not in {"buyer", "seller", "lessor", "lessee"}
        and not ent.text.strip().lower().endswith(("contract", "agreement"))
    }
    return sorted(parties)

def extract_recurring_payments(text: str):
    return [match.group().lower() for match in RECURRING_PATTERN.finditer(text)]

def extract_late_fee(text: str):
    return [match.strip() for match in LATE_FEE_PATTERN.findall(text)]

def extract_property_address(text: str):
    return [match.strip() for match in ADDRESS_PATTERN.findall(text)]

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()

    # Fix money and durations
    enhanced["extracted_data"]["payment_terms"]["money"] = extract_money_regex(text)
    enhanced["extracted_data"]["duration"] = extract_durations_regex(text)

    # Improve party extraction
    if not enhanced["extracted_data"]["parties"]:
        enhanced["extracted_data"]["parties"] = extract_parties_spacy(text)

    # Add recurring constraint
    for recur in extract_recurring_payments(text):
        enhanced["extracted_data"]["constraints"].append(["recurring", recur, ""])

    # Add late payment penalty
    late_fees = extract_late_fee(text)
    if late_fees:
        enhanced["extracted_data"]["late_payment_penalty"] = late_fees

    # Add property address
    property_addrs = extract_property_address(text)
    if property_addrs:
        enhanced["extracted_data"]["property_address"] = property_addrs

    return enhanced
