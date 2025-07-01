import re

def detect_contract_type(text: str) -> str:
    text_lower = text.lower()

    if "deed of sale" in text_lower or "sold to" in text_lower:
        return "deed_of_sale"
    elif "rental agreement" in text_lower or "tenant" in text_lower or "landlord" in text_lower:
        return "rental_agreement"
    elif "lease agreement" in text_lower or "lessee" in text_lower or "lessor" in text_lower:
        return "lease_agreement"
    else:
        return "unknown"
