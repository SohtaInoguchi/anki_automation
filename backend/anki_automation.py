from dotenv import load_dotenv
import os
import csv
import deepl
from serpapi import GoogleSearch
import requests
from typing import List, Dict

# Load local .env when present (harmless on Render where env vars are provided)
load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")


def _get_deepl_client():
    if not DEEPL_API_KEY:
        raise RuntimeError("DEEPL_API_KEY is not set in environment")
    return deepl.DeepLClient(DEEPL_API_KEY)


def translate_word(word: str, source: str = "EN", target: str = "FR") -> str:
    """Translate a single word using DeepL and return the translated text."""
    client = _get_deepl_client()
    result = client.translate_text(word, source_lang=source, target_lang=target)
    # result may be an object; return its text representation
    return str(result)


def download_image(query: str, filename: str, image_dir: str = ".") -> str:
    """Download first image for `query` using SerpAPI and save to `image_dir/filename`.
    Returns the saved filepath or empty string on failure.
    """
    api_key = SERP_API_KEY
    if not api_key:
        return ""

    params = {
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": api_key,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    try:
        image_url = results["images_results"][0]["original"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        img_data = response.content
        # Basic magic-number check for JPEG/PNG
        if not (img_data[:3] == b"\xff\xd8\xff" or img_data[:4] == b"\x89PNG"):
            return ""

        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, filename)
        with open(path, "wb") as handler:
            handler.write(img_data)
        return path
    except Exception:
        return ""


def _is_running_on_render() -> bool:
    """Detect if running in Render by checking common Render env vars."""
    render_env_vars = [
        "RENDER",
        "RENDER_SERVICE_ID",
        "RENDER_INTERNAL_HOST",
        "RENDER_REGION",
    ]
    return any(var in os.environ for var in render_env_vars)


def _default_image_dir() -> str:
    """Return a sensible default image directory depending on environment.

    - On Render use `/tmp/anki_images` (writable ephemeral storage).
    - Locally use a project-relative `images` folder.
    """
    if _is_running_on_render():
        return "/tmp/anki_images"
    return os.path.join(os.getcwd(), "images")


def generate_anki_cards(english_words: List[str], source: str = "EN", target: str = "FR", image_dir: str | None = None) -> List[Dict[str, str]]:
    """Generate translations and download images for a list of English words.

    Returns a list of dicts: {"word": ..., "translation": ..., "image": <filepath or "">}
    """
    if image_dir is None:
        image_dir = _default_image_dir()

    results = []
    for word in english_words:
        try:
            translation = translate_word(word, source, target)
        except Exception:
            translation = ""

        image_filename = f"{word}.jpeg"
        image_path = download_image(word, image_filename, image_dir=image_dir)

        results.append({
            "word": word,
            "translation": translation,
            "image": image_path,
        })

    return results


def export_cards_to_csv(cards: List[Dict[str, str]], csv_filepath: str = "anki_cards.csv") -> str:
    """Export generated cards to CSV file with columns:
    word | translation | Blank | image_filename | Blank
    
    Returns the filepath of the created CSV file.
    """
    try:
        # Create directory if it doesn't exist
        csv_dir = os.path.dirname(csv_filepath) or "."
        os.makedirs(csv_dir, exist_ok=True)
        
        with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write data rows (no header)
            for card in cards:
                image_filename = os.path.basename(card["image"]) if card["image"] else ""
                writer.writerow([
                    card["translation"],
                    card["word"],
                    "",  # Blank column
                    image_filename,
                    ""   # Blank column
                ])
        
        return csv_filepath
    except Exception as e:
        raise RuntimeError(f"Failed to export cards to CSV: {e}")


if __name__ == "__main__":
    # Example usage when running the module directly
    sample_words = ["cat", "dog", "school"]
    cards = generate_anki_cards(sample_words)
    print(f"Generated {len(cards)} cards")