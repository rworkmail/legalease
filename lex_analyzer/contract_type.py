import re

def detect_contract_type(text: str) -> str:
    lowered = text.lower()

    if re.search(r"\b(deed of sale|bill of sale)\b", lowered):
        return "deed_of_sale"
    elif re.search(r"\b(lease agreement|lessor|lessee)\b", lowered):
        return "lease"
    elif re.search(r"\b(rental agreement|tenant|landlord|rent)\b", lowered):
        return "rent"
    else:
        return "unknown"
