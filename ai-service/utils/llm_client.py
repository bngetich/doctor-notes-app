import json
from openai import APIError, RateLimitError, APITimeoutError
from tenacity import retry, wait_exponential, stop_after_attempt
from config import client

@retry(
    wait=wait_exponential(min=1, max=8),
    stop=stop_after_attempt(3),
    retry_error_callback=lambda _: None
)
def call_llm(messages, model):
    """
    Safe LLM call with retry and backoff.
    Returns raw text or None if all retries fail.
    """
    try: 
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    
    except (RateLimitError, APITimeoutError, APIError) as e:
        print(f"LLM API error: {str(e)}")
        raise

def safe_json(raw: str):
    """
    Safely parse JSON from LLM.
    Returns dict or None.
    """
    try:
        return json.loads(raw)
    except Exception:
        print(f"Could not parse LLM JSON:\n{raw}")
        return None