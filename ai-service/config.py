import os
from dotenv import load_dotenv
from openai import OpenAI


# Load your .env variables
load_dotenv()

# Read environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_SUMMARY = os.getenv("OPENAI_MODEL_SUMMARY", "gpt-4o-mini")
OPENAI_MODEL_EXTRACT = os.getenv("OPENAI_MODEL_EXTRACT", "gpt-4o-mini")

# Sanity check
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file.")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
