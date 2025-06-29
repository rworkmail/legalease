from fastapi import FastAPI
from pydantic import BaseModel
from lex_analyzer.analyzer import analyze_text

app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.post("/analyze")
def analyze_contract(data: TextInput):
    return analyze_text(data.text)
