def generate_contract_summary(data: dict) -> str:
    parties = data.get("parties", [])
    dates = data.get("dates", [])
    duration = data.get("duration", [])
    money = data.get("payment_terms", {}).get("money", [])
    late_fees = data.get("late_payment_penalty", [])
    address = data.get("property_address", [])

    parts = []

    if parties:
        parts.append(f"between {', and '.join(parties)}")
    
    if address:
        parts.append(f"regarding the property at {address[0]}")
    
    if dates:
        parts.append(f"starting on {dates[0]}")
        if len(dates) > 1:
            parts.append(f"ending on {dates[-1]}")
    
    if duration:
        parts.append(f"lasting for {duration[0]}")

    if money:
        parts.append(f"with a payment of {money[0]}")
    
    if late_fees:
        parts.append(f"and a late fee of {late_fees[0]}")
    
    summary = "This contract is " + ", ".join(parts) + "."
    return summary
