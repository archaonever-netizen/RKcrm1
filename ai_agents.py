def classify_offer(text: str) -> dict:
    # Заглушка. При наличии GIGACHAT_API_KEY можно раскомментировать запрос к API
    return {"type": "акция", "discount": "10%", "deadline": "31.12.2026"}

def summarize_document(text: str) -> str:
    return "Краткое содержание (заглушка)"
