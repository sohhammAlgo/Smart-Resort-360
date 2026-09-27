"""Agent 4 — Guest Sentiment: aspect-level sentiment from review text.

BLOCKER (AGENT_CONTEXT.md): no network access to a pretrained sentiment
checkpoint. A transparent lexicon-based aspect analyzer is used instead behind
the same interface.
"""

POSITIVE_WORDS = {"loved", "great", "excellent", "amazing", "good", "clean", "friendly"}
NEGATIVE_WORDS = {"terrible", "bad", "dirty", "broken", "rude", "slow", "awful"}
ASPECT_KEYWORDS = {
    "food": ["food", "restaurant", "breakfast", "dinner"],
    "room": ["room", "bed", "ac", "air conditioning", "bathroom"],
    "service": ["staff", "service", "reception", "concierge"],
    "amenities": ["pool", "spa", "gym"],
}


def analyze_sentiment(review_text: str) -> dict:
    text = review_text.lower()
    sentences = [s.strip() for s in text.replace("!", ".").split(".") if s.strip()]
    aspects = {}
    for sentence in sentences:
        pos = any(w in sentence for w in POSITIVE_WORDS)
        neg = any(w in sentence for w in NEGATIVE_WORDS)
        label = (
            "POSITIVE"
            if pos and not neg
            else "NEGATIVE" if neg and not pos else "NEUTRAL"
        )
        for aspect, keywords in ASPECT_KEYWORDS.items():
            if any(kw in sentence for kw in keywords):
                aspects[aspect] = label
    overall = "NEUTRAL"
    labels = list(aspects.values())
    if labels:
        overall = (
            "POSITIVE"
            if labels.count("POSITIVE") >= labels.count("NEGATIVE")
            else "NEGATIVE"
        )
    return {"overall_sentiment": overall, "aspects": aspects}
