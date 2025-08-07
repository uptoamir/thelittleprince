import os
import json
import re
from PyPDF2 import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
if not GEMINI_TOKEN:
    raise RuntimeError("Please set GEMINI_TOKEN in your .env")

client = genai.Client(api_key=GEMINI_TOKEN)

def extract_text(pdf_path="TheLittlePrince.pdf"):
    reader = PdfReader(pdf_path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)

def extract_json_block(text: str) -> str:
    """Pull the first {...} block from text."""
    m = re.search(r"(\{(?:[^{}]|(?R))*\})", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in response")
    return m.group(1)

def segment_scenes(book_text: str, max_scenes=50):
    instruction = (
        "You are a storyboarding AI. Break the following book text into up to "
        f"{max_scenes} micro-scenes. For each scene, return a JSON array of "
        "objects with keys:\n"
        "  id (two-digit),\n"
        "  prompt (for a 5-sec video in storybook-illustration style),\n"
        "  narration (one-sentence summary).\n"
        "Output _only_ valid JSON."
    )
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[
            types.Part.from_text(text=instruction),
            types.Part.from_text(text=book_text)
        ]
    )

    raw = response.text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("⚠️ Raw Gemini response not JSON—attempting to extract block:")
        print(raw[:500], "…")  # show first 500 chars
        cleaned = extract_json_block(raw)
        return json.loads(cleaned)

def main():
    print("🔍 Extracting text from PDF…")
    text = extract_text("TheLittlePrince.pdf")

    print("🗂 Segmenting scenes with Gemini…")
    scenes = segment_scenes(text)

    os.makedirs("4_output", exist_ok=True)
    out_file = "4_output/scenes.json"
    with open(out_file, "w") as f:
        json.dump(scenes, f, indent=2)
    print(f"✅ Wrote {len(scenes)} scenes to {out_file}")

if __name__ == "__main__":
    main()
