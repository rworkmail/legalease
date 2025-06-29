from fastapi import FastAPI
from pydantic import BaseModel
import nltk

# ✅ Verified extractors
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.percents import get_percents
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.conditions import get_conditions
from lexnlp.extract.en.constraints import get_constraints
from lexnlp.extract.en.citations import get_citations
from lexnlp.extract.en.segments.headers import get_section_headers
from lexnlp.extract.en.acts import get_act_list
from lexnlp.extract.en.pii import get_pii
from lexnlp.extract.en.regulations import get_regulations
from lexnlp.extract.en.amounts import get_amounts

# NLTK resources required by lexnlp
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
    return {
        "money": [str(m) for m in get_money(text)],
        "dates": [str(d) for d in get_dates(text)],
        "percents": [str(p) for p in get_percents(text)],
        "durations": [str(d) for d in get_durations(text)],
        "definitions": list(get_definitions(text)),
        "conditions": list(get_conditions(text)),
        "constraints": list(get_constraints(text)),
        "citations": list(get_citations(text)),
        "sections": list(get_section_headers(text)),
        "acts": list(get_act_list(text)),
        "pii": list(get_pii(text)),
        "regulations": list(get_regulations(text)),
        "amounts": list(get_amounts(text)),
    }
