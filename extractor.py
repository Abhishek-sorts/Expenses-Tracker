import re
from datetime import datetime

CATEGORIES = {
    "food": ["food", "lunch", "dinner", "tea", "coffee", "snacks"],
    "transport": ["petrol", "fuel", "auto", "bus", "uber", "ola"],
    "entertainment": ["movie", "netflix", "game"],
    "shopping": ["shopping", "amazon", "clothes"],
    "health": ["medicine", "doctor", "hospital"]
}

def detect_category(text):
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        for word in keywords:
            if word in text_lower:
                return category.capitalize()
    return "Other"

def extract_amount(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return 0

def extract_expense(text):
    amount = extract_amount(text)
    category = detect_category(text)
    date = datetime.now().strftime("%Y-%m-%d")

    return {
        "date": date,
        "amount": amount,
        "category": category,
        "description": text,
        "raw_text": text
    }
