"""
backend/services/ai_service.py
All Groq API calls live here. Every other file calls this — never calls Groq directly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

# Single shared client
client = Groq(api_key=GROQ_API_KEY)

def chat_completion(messages: list[dict], temperature: float = 0.7) -> str:
    """
    Core function — send messages to Groq, get text back.
    messages = [{"role": "system/user/assistant", "content": "..."}]
    """
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def single_prompt(prompt: str, temperature: float = 0.3) -> str:
    """One-shot prompt — no history needed."""
    return chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
