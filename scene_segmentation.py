import os
import json
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
    """
    Pull out the first JSON array [...], from the response text.
    """
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in response")
    return text[start:end+1]

def segment_scenes(book_text: str, max_scenes=50):
    instruction = (
        "You are a storyboarding AI. Break the following book text into up to "
        f"{max_scenes} micro-scenes. Return _only_ a JSON array of objects "
        "with keys: id (two-digit), prompt (5-sec storybook illustration), "
        "narration (one sentence)."
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
        print("⚠️ Raw response not JSON, extracting [...] block…")
        snippet = raw[:500].replace("\n", " ")
        print("RAW SNIPPET:", snippet, "…")
        clean = extract_json_block(raw)
        return json.loads(clean)

def main():
    print("🔍 Extracting PDF text…")
    text = extract_text("TheLittlePrince.pdf")

    print("🗂 Segmenting scenes…")
    scenes = segment_scenes(text)

    os.makedirs("4_output", exist_ok=True)
    out_path = "4_output/scenes.json"
    with open(out_path, "w") as f:
        json.dump(scenes, f, indent=2)
    print(f"✅ Wrote {len(scenes)} scenes → {out_path}")

if __name__ == "__main__":
    main()
