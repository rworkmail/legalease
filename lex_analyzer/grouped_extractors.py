import nltk
from decimal import Decimal
from lexnlp.extract.en.money import get_money
from lexnlp.extract.en.dates import get_dates
from lexnlp.extract.en.percents import get_percents
from lexnlp.extract.en.durations import get_durations
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.extract.en.conditions import get_conditions
from lexnlp.extract.en.constraints import get_constraints
from lexnlp.extract.en.citations import get_citations

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

def extract_grouped_lexnlp(text: str) -> dict:
    return {
        "parties": list(get_definitions(text)),  # not 100% accurate but okay as base
        "payment_terms": {
            "money": [str(m) for m in get_money(text)],
            "percents": [str(p) for p in get_percents(text)],
        },
        "duration": [str(d) for d in get_durations(text)],
        "dates": [str(d) for d in get_dates(text)],
        "conditions": list(get_conditions(text)),
        "constraints": list(get_constraints(text)),
        "citations": list(get_citations(text)),
    }
