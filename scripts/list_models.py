import google.generativeai as genai
import os

key_file = "01-system/configs/apis/API-Keys.md"
api_key = None
with open(key_file, 'r') as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break

if not api_key:
    print("No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
