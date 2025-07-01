import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Regex patterns
MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)
RECURRING_PATTERN = re.compile(r"\b(monthly|annually|weekly|biweekly|quarterly)\b", re.IGNORECASE)
LATE_FEE_PATTERN = re.compile(r"(?:late fee|penalt(?:y|ies)).{0,40}?\$[\d,]+(?:\.\d{2})?", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(
    r"\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(Street|Avenue|Road|Lane|Drive|Boulevard|St\.?|Ave\.?|Rd\.?|Blvd\.?|Dr\.?))",
    re.IGNORECASE
)

ADDRESS_NOISE_KEYWORDS = {"$", "day", "month", "week", "business", "rent", "payment", "paid"}


def clean_money(text: str) -> str:
    return text.rstrip(",. ").replace(",", "")

def extract_money_regex(text: str):
    return [clean_money(match.group()) for match in MONEY_REGEX.finditer(text)]

def extract_durations_regex(text: str):
    return [match.group().strip("., ") for match in DURATION_REGEX.finditer(text)]

def extract_parties_spacy(text: str):
    doc = nlp(text)
    parties = set()

    for ent in doc.ents:
        full_text = ent.text.strip()
        if (
            ent.label_ == "PERSON"
            and 2 <= len(full_text.split()) <= 4
            and full_text.lower() not in {"buyer", "seller", "lessor", "lessee"}
            and not full_text.lower().endswith(("contract", "agreement", "lease", "deed"))
        ):
            parties.add(full_text)

    # Add organizations separately
    for ent in doc.ents:
        full_text = ent.text.strip()
        if ent.label_ == "ORG" and len(full_text.split()) <= 4:
            parties.add(full_text)

    return sorted(parties)

def extract_recurring_payments(text: str):
    return [match.group().lower() for match in RECURRING_PATTERN.finditer(text)]

def extract_late_fee(text: str):
    return [match.strip() for match in LATE_FEE_PATTERN.findall(text)]

def extract_property_address(text: str):
    all_matches = [match.strip("., ") for match in ADDRESS_PATTERN.findall(text)]
    return [
        match for match in all_matches
        if not any(keyword in match.lower() for keyword in ADDRESS_NOISE_KEYWORDS)
    ]

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()

    data = enhanced.get("extracted_data", {})
    data.setdefault("parties", [])
    data.setdefault("payment_terms", {}).setdefault("money", [])
    data.setdefault("duration", [])
    data.setdefault("constraints", [])

    data["payment_terms"]["money"] = extract_money_regex(text)
    data["duration"] = extract_durations_regex(text)

    if not data["parties"]:
        data["parties"] = extract_parties_spacy(text)

    for recur in extract_recurring_payments(text):
        data["constraints"].append(["recurring", recur, ""])

    late_fees = extract_late_fee(text)
    if late_fees:
        data["late_payment_penalty"] = late_fees

    property_addrs = extract_property_address(text)
    if property_addrs:
        data["property_address"] = property_addrs

    enhanced["extracted_data"] = data
    return enhanced
