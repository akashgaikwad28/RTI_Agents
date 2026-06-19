def rti_compliance_score(formal_query: str) -> float:
    text = formal_query.lower()
    score = 0.0
    score += 0.25 if "right to information" in text or "rti" in text else 0
    score += 0.25 if "certified" in text or "copies" in text or "information" in text else 0
    score += 0.25 if "period" in text or "year" in text or "date" in text else 0
    score += 0.25 if len(formal_query) > 80 else 0
    return score

