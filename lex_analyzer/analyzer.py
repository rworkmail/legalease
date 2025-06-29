from lex_analyzer.grouped_extractors import extract_grouped_lexnlp
from lex_analyzer.contract_type import detect_contract_type

def analyze_text(text: str) -> dict:
    contract_type = detect_contract_type(text)
    grouped_data = extract_grouped_lexnlp(text)
    
    return {
        "contract_type": contract_type,
        "extracted_data": grouped_data
    }
