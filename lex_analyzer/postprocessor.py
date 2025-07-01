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
    return list({clean_money(m.group()) for m in MONEY_REGEX.finditer(text)})

def extract_durations_regex(text: str):
    durations = [d.group().strip("., ") for d in DURATION_REGEX.finditer(text)]
    return list(dict.fromkeys(durations))  # Remove duplicates, preserve order

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
    return list({m.strip() for m in LATE_FEE_PATTERN.findall(text)})

def extract_property_address(text: str):
    return list({m.strip() for m in ADDRESS_PATTERN.findall(text)})

def quote(value: str) -> str:
    return f'"{value}"'

def generate_summary(data: dict) -> str:
    parties = [quote(p) for p in data.get("parties", [])]
    address = data.get("property_address", [])
    start_date = next((d for d in data.get("dates", []) if re.search(r"\d{4}-\d{2}-\d{2}", d)), None)
    duration = ", ".join(data.get("duration", []))
    amount = next((m for m in data["payment_terms"].get("money", []) if m.strip("$").replace('.', '').isdigit()), None)
    late_fee = next(iter(data.get("late_payment_penalty", [])), "")

    parts = []
    if parties:
        parts.append(f"This contract is between {', and '.join(parties)}")
    if address:
        parts.append(f"regarding the property at {address[0]}")
    if start_date:
        parts.append(f"starting on {start_date}")
    if duration:
        parts.append(f"lasting for {duration}")
    if amount:
        parts.append(f"with a payment of {quote(amount)}")
    if late_fee:
        clean_late_fee = re.sub(r"^(late fee of|penalty of)?\s*", "", late_fee, flags=re.IGNORECASE)
        parts.append(f"and a late fee of {quote(clean_late_fee)}")

    return ", ".join(parts).strip(", ")

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

    # Add contract summary
    enhanced["summary"] = generate_summary(enhanced["extracted_data"])

    return enhanced
