from dotenv import load_dotenv
import os
import deepl
from serpapi import GoogleSearch
import requests

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

deepl_client = deepl.DeepLClient(DEEPL_API_KEY)

english_words = ["cat", "dog", "school"]
data = []

def translate_word(word, source, target):
    result = deepl_client.translate_text(word, source_lang=source, target_lang=target)
    return result

def download_image(query, filename):
    params = {
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": SERP_API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    try:
        image_url = results["images_results"][0]["original"]
        # Add User-Agent header to avoid 403 errors
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        img_data = response.content
        
        # Verify it's actually an image (JPEG starts with FFD8FF, PNG with 89504E47)
        if not (img_data[:3] == b'\xff\xd8\xff' or img_data[:4] == b'\x89PNG'):
            print(f"Downloaded content is not a valid image for {query}")
            return ""
        
        with open(filename, "wb") as handler:
            handler.write(img_data)
        print(f"Successfully downloaded image: {filename}")
        return filename
    except Exception as e:
        print(f"Image not found for {query}: {e}")
        return ""

for word in english_words:
    fr = translate_word(word, "EN", "FR")
    data.append(fr)

download_image("cat", "cat.jpeg")
print("image file created")