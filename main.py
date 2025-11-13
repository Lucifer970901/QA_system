from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
import re

app = FastAPI(title="Member Question Answering API")

API_URL = "https://november7-730026606190.europe-west1.run.app/messages"

def fetch_messages():
    """Fetch all messages from the provided public API."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def extract_member_name(question: str):
    """Extract probable member name using regex."""
    match = re.search(r"(?:is|does|are|was|’s|s)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", question)
    if match:
        return match.group(1)
    match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", question)
    return match.group(1) if match else None

def find_related_messages(member_name: str, messages: list):
    """Filter messages mentioning the member."""
    related = []
    for m in messages:
        if member_name.lower() in m.get("content", "").lower() or member_name.lower() in m.get("sender_name", "").lower():
            related.append(m)
    return related

def infer_answer(question: str, messages: list):
    """Simple rule-based inference logic."""
    question = question.strip().lower()

    # Identify member name
    member = extract_member_name(question)
    if not member:
        return "Sorry, I couldn't identify the member's name."

    related = find_related_messages(member, messages)
    if not related:
        return f"No data found for {member}."

    # Example patterns
    if "trip" in question or "travel" in question:
        for msg in related:
            if "trip" in msg["content"].lower() or "travel" in msg["content"].lower():
                return msg["content"]
        return f"{member}'s trip details not found."

    elif "car" in question:
        for msg in related:
            if "car" in msg["content"].lower():
                return msg["content"]
        return f"No information found about {member}'s cars."

    elif "restaurant" in question or "food" in question:
        for msg in related:
            if "restaurant" in msg["content"].lower() or "food" in msg["content"].lower():
                return msg["content"]
        return f"No favorite restaurant details found for {member}."

    else:
        # Fallback: return any message that mentions the member
        return related[0]["content"]

@app.get("/ask")
def ask(question: str = Query(..., description="Natural language question")):
    """Main endpoint to answer questions."""
    data = fetch_messages()
    answer = infer_answer(question, data)
    return JSONResponse(content={"answer": answer})