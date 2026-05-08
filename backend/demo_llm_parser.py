import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer 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"}


payload = {"inputs": "Hello, my name is"}
response = requests.post(API_URL, headers=headers, json=payload)

print("Status code:", response.status_code)
print("Raw text:", response.text)  # <-- print raw response before parsing