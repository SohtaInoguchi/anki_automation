from dotenv import load_dotenv
import os
import csv
import deepl
from serpapi import GoogleSearch
from gtts import gTTS
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
    try:
        client = _get_deepl_client()
        result = client.translate_text(word, source_lang=source, target_lang=target)
        translated = str(result)
        if not translated.strip():
            print(f"Warning: DeepL returned empty translation for '{word}' ({source} -> {target})")
            return ""
        return translated
    except Exception as e:
        print(f"Error translating '{word}' from {source} to {target}: {type(e).__name__}: {e}")
        return ""


def download_image(query: str, filename: str, image_dir: str = ".", search_lang: str | None = None) -> str:
    """Download first image for `query` using SerpAPI and save to `image_dir/filename`.
    If `search_lang` is provided (e.g. 'FR'), the SerpAPI `lr` parameter will be set to
    `lang_<lang>` to bias results toward that language. Returns the saved filepath or
    empty string on failure.
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
    if search_lang:
        params["lr"] = f"lang_{search_lang.lower()}"

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
            print(f"Warning: Downloaded data for '{query}' is not a valid JPEG/PNG image")
            return ""

        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, filename)
        with open(path, "wb") as handler:
            handler.write(img_data)
        return path
    except Exception as e:
        print(f"Error downloading image for '{query}': {type(e).__name__}: {e}")
        return ""


def generate_audio(text: str, filename: str, lang: str, audio_dir: str = ".") -> str:
    """Generate MP3 audio for `text` using gTTS and save to `audio_dir/filename`.
    Returns the saved filepath or empty string on failure.
    """
    try:
        tts = gTTS(text, lang=lang)
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, filename)
        tts.save(path)
        return path
    except Exception as e:
        print(f"Error generating audio for '{text}' in language '{lang}': {type(e).__name__}: {e}")
        return ""


def _deepl_to_gtts_lang(deepl_lang: str) -> str:
    """Map DeepL language code to gTTS language code."""
    mapping = {
        "EN": "en",
        "FR": "fr",
        # extend as needed in future
    }
    return mapping.get(deepl_lang.upper(), "en")


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


def _default_audio_dir() -> str:
    """Return a sensible default audio directory depending on environment.

    - On Render use `/tmp/anki_audio` (writable ephemeral storage).
    - Locally use a project-relative `audio` folder.
    """
    if _is_running_on_render():
        return "/tmp/anki_audio"
    return os.path.join(os.getcwd(), "audio")


def generate_anki_cards(words_input: List[str], target_language: str = "FR", learning_language: str = "EN", words_in_target_lang: bool = False, image_dir: str | None = None, audio_dir: str | None = None) -> List[Dict[str, str]]:
    """Generate translations, download images, and generate audio for flashcards.
    
    Args:
        words_input: List of words to create cards from
        target_language: Language the user is learning (e.g., "FR" for French)
        learning_language: Language the user learns in (e.g., "EN" for English)
        words_in_target_lang: If True, words_input are in target_language. If False, they're in learning_language
        image_dir: Directory to save images
        audio_dir: Directory to save audio files
    
    Returns:
        List of dicts with: {"front_text": ..., "back_text": ..., "image": ..., "audio_front": ..., "audio_back": ...}
    """
    print(f"Generating {len(words_input)} cards: target_lang={target_language}, learning_lang={learning_language}, words_in_target={words_in_target_lang}")
    
    if image_dir is None:
        image_dir = _default_image_dir()
    if audio_dir is None:
        audio_dir = _default_audio_dir()

    # Get gTTS language codes
    target_lang_code = _deepl_to_gtts_lang(target_language)
    learning_lang_code = _deepl_to_gtts_lang(learning_language)

    results = []
    for word in words_input:
        if words_in_target_lang:
            # Word is already in target language; translate to learning language for back
            front_text = word
            back_text = translate_word(word, target_language, learning_language)
            if not back_text:
                print(f"Warning: No translation available for '{word}' ({target_language} -> {learning_language})")
                back_text = word  # fallback only for empty results, not exceptions
            search_term = word
            search_lang = target_language
        else:
            # Word is in learning language; translate to target language for front
            back_text = word
            front_text = translate_word(word, learning_language, target_language)
            if not front_text:
                print(f"Warning: No translation available for '{word}' ({learning_language} -> {target_language})")
                front_text = word  # fallback only for empty results, not exceptions
            search_term = front_text or word
            search_lang = target_language

        # Download image based on the word/translation
        image_filename = f"{word.replace(' ', '_').replace('/', '_')}.jpeg"
        image_path = download_image(search_term, image_filename, image_dir=image_dir, search_lang=search_lang)

        # Generate audio: front in target language, back in learning language
        front_audio_lang = target_language
        back_audio_lang = learning_language

        front_audio_code = _deepl_to_gtts_lang(front_audio_lang)
        back_audio_code = _deepl_to_gtts_lang(back_audio_lang)

        audio_front_filename = f"{(front_text or word).replace(' ', '_').replace('/', '_')}_{front_audio_lang.lower()}.mp3"
        audio_front_path = generate_audio(front_text, audio_front_filename, lang=front_audio_code, audio_dir=audio_dir)

        audio_back_filename = f"{(back_text or word).replace(' ', '_').replace('/', '_')}_{back_audio_lang.lower()}.mp3"
        audio_back_path = generate_audio(back_text, audio_back_filename, lang=back_audio_code, audio_dir=audio_dir)

        results.append({
            "front_text": front_text,
            "back_text": back_text,
            "image": image_path,
            "audio_front": audio_front_path,
            "audio_back": audio_back_path,
        })

    return results


def export_cards_to_csv(cards: List[Dict[str, str]], csv_filepath: str = "anki_cards.csv") -> str:
    """Export generated cards to CSV file with headers:
    Text for front of card |Text for back of card | List of tags, comma separated | File name for image on front of card | File name for image on back of card | File name of audio file for front of card | File name of audio file for back of card
    
    Returns the filepath of the created CSV file.
    """
    try:
        # Create directory if it doesn't exist
        csv_dir = os.path.dirname(csv_filepath) or "."
        os.makedirs(csv_dir, exist_ok=True)
        
        with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header row
            writer.writerow([
                "Text for front of card",
                "Text for back of card",
                "List of tags, comma separated",
                "File name for image on front of card",
                "File name for image on back of card",
                "File name of audio file for front of card",
                "File name of audio file for back of card"
            ])
            
            # Write data rows
            for card in cards:
                image_filename = os.path.basename(card["image"]) if card["image"] else ""
                audio_front_filename = os.path.basename(card["audio_front"]) if card["audio_front"] else ""
                audio_back_filename = os.path.basename(card["audio_back"]) if card["audio_back"] else ""
                writer.writerow([
                    card["front_text"],
                    card["back_text"],
                    "",  # Blank column for tags
                    image_filename,
                    "",  # Blank column for back image
                    audio_front_filename,
                    audio_back_filename
                ])
        
        return csv_filepath
    except Exception as e:
        raise RuntimeError(f"Failed to export cards to CSV: {e}")


if __name__ == "__main__":
    # Example usage when running the module directly
    sample_words = ["cat", "dog", "school"]
    cards = generate_anki_cards(sample_words)
    print(f"Generated {len(cards)} cards")
    csv_path = export_cards_to_csv(cards)
    print(f"Exported to {csv_path}")