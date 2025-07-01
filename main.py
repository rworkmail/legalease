import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
import nltk

from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.percents import get_percents
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.conditions import get_conditions
from lexnlp.extract.en.constraints import get_constraints
from lexnlp.extract.en.citations import get_citations

from lex_analyzer.postprocessor import enhance_extraction
from lex_analyzer.classifier import detect_contract_type
from lex_analyzer.summary import generate_contract_summary  # ✅ NEW

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/analyze")
def analyze_contract(data: TextInput):
    text = data.text

    base_output = {
        "contract_type": detect_contract_type(text),
        "extracted_data": {
            "parties": [],
            "payment_terms": {
                "money": [str(m) for m in get_money(text)],
                "percents": [str(p) for p in get_percents(text)],
            },
            "duration": [str(d) for d in get_durations(text)],
            "dates": [str(d) for d in get_dates(text)],
            "definitions": list(get_definitions(text)),
            "conditions": list(get_conditions(text)),
            "constraints": list(get_constraints(text)),
            "citations": list(get_citations(text)),
        }
    }

    # Apply regex + spaCy post-processing
    enhanced = enhance_extraction(base_output, text)

    # ✅ Add contract summary
    summary = generate_contract_summary(enhanced["extracted_data"])
    enhanced["summary"] = summary

    return enhanced
