import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print(f"Testing models with API Key ending in ...{api_key[-4:]}")

working_model = None

# Get all models that support generation
models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

print(f"Found {len(models)} candidate models.")

# Prioritize flash/pro models likely to work
priority_order = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-flash-001",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-pro-latest",
    "models/gemini-pro",
    "models/gemini-1.0-pro"
]

# Sort models: priority ones first, then others
sorted_models = []
for p in priority_order:
    for m in models:
        if m.name == p:
            sorted_models.append(m)

for m in models:
    if m not in sorted_models:
        sorted_models.append(m)

for m in sorted_models:
    print(f"Testing {m.name}...", end=" ", flush=True)
    try:
        model = genai.GenerativeModel(m.name)
        response = model.generate_content("Test")
        print("SUCCESS! ✅")
        working_model = m.name
        break
    except Exception as e:
        print(f"FAILED ❌ ({str(e)[:50]}...)")
        time.sleep(1) # Be gentle

if working_model:
    print(f"\nFOUND WORKING MODEL: {working_model}")
    # Write it to a file so we can read it easily or just see output
else:
    print("\nNO WORKING MODELS FOUND.")
