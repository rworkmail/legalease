from fastapi import FastAPI
from pydantic import BaseModel
import re
import nltk
import spacy
from typing import List, Dict, Union
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.percents import get_percents
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.conditions import get_conditions
from lexnlp.extract.en.constraints import get_constraints
from lexnlp.extract.en.citations import get_citations
import spacy.cli
spacy.cli.download("en_core_web_sm")


nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

nlp = spacy.load("en_core_web_sm")

app = FastAPI()

class TextInput(BaseModel):
    text: str

def detect_contract_type(text: str) -> str:
    lower = text.lower()
    if "deed of sale" in lower:
        return "deed_of_sale"
    elif "lease agreement" in lower or "lessee" in lower:
        return "lease"
    elif "rental agreement" in lower or "rent" in lower:
        return "rent"
    return "unknown"

def extract_parties(text: str) -> List[str]:
    doc = nlp(text)
    return list({ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG"]})

def extract_payment_terms(text: str) -> Dict[str, List[str]]:
    return {
        "money": [str(m) for m in get_money(text)],
        "percents": [str(p) for p in get_percents(text)]
    }

def extract_constraints(text: str) -> List[List[str]]:
    matches = []
    patterns = [
        (r'within\s+(\d+[\s\w]+)', "within"),
        (r'after\s+(\d+[\s\w]+)', "after"),
        (r'on or before\s+(\w+\s+\d{1,2},\s+\d{4})', "before")
    ]
    for pattern, label in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append([label, match.group(0), ""])
    return matches

@app.post("/analyze")
def analyze_contract(data: TextInput):
    text = data.text

    contract_type = detect_contract_type(text)

    return {
        "contract_type": contract_type,
        "extracted_data": {
            "parties": extract_parties(text),
            "payment_terms": extract_payment_terms(text),
            "duration": [str(d) for d in get_durations(text)],
            "dates": [str(d) for d in get_dates(text)],
            "conditions": list(get_conditions(text)),
            "constraints": extract_constraints(text),
            "citations": list(get_citations(text))
        }
    }
