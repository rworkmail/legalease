import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Regex patterns
MONEY_REGEX = re.compile(r"\$[\d,]+(?:\.\d{2})?")
DURATION_REGEX = re.compile(r"\b(?:\d+|\w+)\s+(?:days?|weeks?|months?|years?|business days?)\b", re.IGNORECASE)
RECURRING_PATTERN = re.compile(r"\b(?:monthly|annually|weekly|biweekly|quarterly)\b", re.IGNORECASE)
LATE_FEE_PATTERN = re.compile(r"(?:late fee|penalty).*?\$[\d,]+(?:\.\d{2})?", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+[\w\s]{2,50}?\s(?:Street|Avenue|Road|Lane|Drive|Boulevard|St\.?|Ave\.?|Rd\.?|Blvd\.?|Dr\.?)\b",
    re.IGNORECASE
)

# Utility
def clean_money(text: str) -> str:
    return text.rstrip(",. ").replace(",", "")

def extract_money_regex(text: str):
    return [clean_money(m.group()) for m in MONEY_REGEX.finditer(text)]

def extract_durations_regex(text: str):
    return [d.group().strip("., ") for d in DURATION_REGEX.finditer(text)]

def extract_parties_spacy(text: str):
    doc = nlp(text)
    return sorted({
        ent.text.strip() for ent in doc.ents
        if ent.label_ in ("PERSON", "ORG")
        and len(ent.text.strip().split()) <= 4
        and ent.text.strip().lower() not in {"buyer", "seller", "lessor", "lessee"}
        and not ent.text.strip().lower().endswith(("contract", "agreement"))
    })

def extract_recurring_payments(text: str):
    return [m.group().lower() for m in RECURRING_PATTERN.finditer(text)]

def extract_late_fee(text: str):
    return [m.strip() for m in LATE_FEE_PATTERN.findall(text)]

def extract_property_address(text: str):
    return [m.strip() for m in ADDRESS_PATTERN.findall(text)]

def generate_summary(data: dict) -> str:
    parties = data["parties"]
    address = data.get("property_address", [])
    start_date = next((d for d in data["dates"] if re.search(r"\d{4}-\d{2}-\d{2}", d)), None)
    duration = ", ".join(data.get("duration", []))
    amount = next((m for m in data["payment_terms"].get("money", []) if m.strip("$").isdigit()), None)
    late_fee = ", ".join(data.get("late_payment_penalty", []))

    summary_parts = [
        f"This contract is between {', and '.join(parties)}" if parties else "",
        f"regarding the property at {address[0]}" if address else "",
        f"starting on {start_date}" if start_date else "",
        f"lasting for {duration}" if duration else "",
        f"with a payment of {amount}" if amount else "",
        f"and a {late_fee}" if late_fee else ""
    ]
    return ", ".join(part for part in summary_parts if part).strip(", ")

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()

    enhanced["extracted_data"]["payment_terms"]["money"] = extract_money_regex(text)
    enhanced["extracted_data"]["duration"] = extract_durations_regex(text)

    if not enhanced["extracted_data"]["parties"]:
        enhanced["extracted_data"]["parties"] = extract_parties_spacy(text)

    for recur in extract_recurring_payments(text):
        enhanced["extracted_data"]["constraints"].append(["recurring", recur, ""])

    late_fees = extract_late_fee(text)
    if late_fees:
        enhanced["extracted_data"]["late_payment_penalty"] = late_fees

    property_addrs = extract_property_address(text)
    if property_addrs:
        enhanced["extracted_data"]["property_address"] = property_addrs

    # Contract Summary
    enhanced["summary"] = generate_summary(enhanced["extracted_data"])

    return enhanced
