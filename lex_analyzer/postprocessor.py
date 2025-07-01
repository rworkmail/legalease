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

# Utility functions
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

def clean_late_fee(fees):
    return [
        re.sub(r"(?i)(late fee|penalty)( of)?( late fee( of)?)*", "", fee).strip(",. ")
        for fee in fees
    ]

def extract_property_address(text: str):
    return [m.strip() for m in ADDRESS_PATTERN.findall(text)]

def find_start_date(text: str, dates: list) -> str:
    for date in dates:
        if any(k in text.lower() for k in ["start", "commence", "commencing"]) and re.search(date, text):
            return date
    return dates[0] if dates else ""

def find_end_date(text: str, dates: list) -> str:
    for date in reversed(dates):
        if any(k in text.lower() for k in ["end", "terminate", "expiration", "expires"]) and re.search(date, text):
            return date
    return dates[-1] if dates else ""

def generate_summary(data: dict, text: str) -> str:
    parties = data["parties"]
    address = data.get("property_address", [])
    start_date = find_start_date(text, data.get("dates", []))
    end_date = find_end_date(text, data.get("dates", []))
    duration = ", ".join(data.get("duration", []))
    amount = next((m for m in data["payment_terms"].get("money", []) if m.strip("$").isdigit()), None)
    late_fee = ", ".join(clean_late_fee(data.get("late_payment_penalty", [])))

    summary_parts = [
        f"This contract is between {', and '.join(parties)}" if parties else "",
        f"regarding the property at {address[0]}" if address else "",
        f"starting on {start_date}" if start_date else "",
        f"ending on {end_date}" if end_date else "",
        f"lasting for {duration}" if duration else "",
        f"with a payment of {amount}" if amount else "",
        f"and a late fee of {late_fee}" if late_fee else ""
    ]
    return ", ".join(part for part in summary_parts if part).strip(", ")

def enhance_extraction(original: dict, text: str) -> dict:
    enhanced = original.copy()
    extracted = enhanced["extracted_data"]

    extracted["payment_terms"]["money"] = extract_money_regex(text)
    extracted["duration"] = extract_durations_regex(text)

    if not extracted["parties"]:
        extracted["parties"] = extract_parties_spacy(text)

    for recur in extract_recurring_payments(text):
        extracted["constraints"].append(["recurring", recur, ""])

    late_fees = extract_late_fee(text)
    if late_fees:
        extracted["late_payment_penalty"] = late_fees

    addresses = extract_property_address(text)
    if addresses:
        extracted["property_address"] = addresses

    enhanced["summary"] = generate_summary(extracted, text)
    return enhanced
