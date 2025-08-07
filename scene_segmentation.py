import os, json
from PyPDF2 import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
client = genai.Client(api_key=GEMINI_TOKEN)

def extract_text(pdf_path="TheLittlePrince.pdf"):
    reader = PdfReader(pdf_path)
    return "\n\n".join(page.extract_text() for page in reader.pages)

def segment_scenes(text, max_scenes=50):
    """
    Ask Gemini Pro to split the book into logical 5-sec micro-scenes.
    Outputs JSON: [{ "id": "01", "prompt": "...", "narration": "..." }, …]
    """
    instruction = (
        "You are a story-boarding AI. "
        "Break the following book text into a sequence of up to "
        f"{max_scenes} micro-scenes. For each scene, return a JSON entry "
        "with fields: id (two-digit), prompt (for a 5-sec video in a "
        "storybook illustration style), and narration (one sentence)."
    )
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[
            instruction,
            types.Part.from_text(text=text)
        ]
    )
    # assume response.text is raw JSON
    scenes = json.loads(response.text)
    return scenes

def main():
    text = extract_text()
    scenes = segment_scenes(text)
    os.makedirs("4_output", exist_ok=True)
    with open("4_output/scenes.json", "w") as f:
        json.dump(scenes, f, indent=2)
    print(f"✅ Wrote {len(scenes)} scenes to 4_output/scenes.json")

if __name__ == "__main__":
    main()
