# generate_scenes.py

import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not set in .env")

# Initialize the Fal-AI client
client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN,
)

def generate_video(prompt: str, out_path: str):
    """
    Generates a 5-second video clip from `prompt` using Wan-AI/Wan2.2-T2V-A14B
    and writes it to `out_path`.
    """
    # Fal-AI InferenceClient returns either bytes, URL or dict
    result = client.text_to_video(
        prompt,
        model="Wan-AI/Wan2.2-T2V-A14B",
    )

    # Handle the various return types:
    if isinstance(result, (bytes, bytearray)):
        video_bytes = result
    elif isinstance(result, str) and result.startswith("http"):
        # download from URL
        import requests
        resp = requests.get(result)
        resp.raise_for_status()
        video_bytes = resp.content
    elif isinstance(result, dict):
        # look for the URL in common keys
        url = None
        if "video" in result and isinstance(result["video"], dict):
            url = result["video"].get("url")
        elif "generated_videos" in result and result["generated_videos"]:
            url = result["generated_videos"][0].get("url")
        if not url:
            raise RuntimeError(f"Cannot find video URL in response: {result}")
        import requests
        resp = requests.get(url)
        resp.raise_for_status()
        video_bytes = resp.content
    else:
        raise RuntimeError(f"Unsupported response type: {type(result)}")

    # Save to disk
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(video_bytes)
    print(f"Saved: {out_path}")

def main():
    # load the auto‐segmented scene definitions
    with open("4_output/scenes.json", "r") as f:
        scenes = json.load(f)

    for sc in scenes:
        pid = sc["id"]
        prompt = sc["prompt"]
        out_file = f"4_output/chunks/scene_{pid}.mp4"
        print(f"Generating scene {pid}…")
        generate_video(prompt, out_file)

if __name__ == "__main__":
    main()
