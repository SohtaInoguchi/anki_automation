from dotenv import load_dotenv
import os
import deepl

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

deepl_client = deepl.DeepLClient(DEEPL_API_KEY)

english_words = ["cat", "dog", "school"]
data = []

def translate_word(word, source, target):
    result = deepl_client.translate_text(word, source_lang=source, target_lang=target)
    return result

for word in english_words:
    fr = translate_word(word, "EN", "FR")
    data.append(fr)

print(data[0], data[1], data[2])