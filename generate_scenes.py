# generate_scenes.py

import os
import json
import requests
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Reload .env every time
load_dotenv(dotenv_path=".env", override=True)
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not set in .env")

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN,
)

def generate_video(prompt: str, out_path: str):
    # Prepend the cartoon style hint
    cartoon_prompt = (
        "2D storybook illustration, hand-drawn cartoon style.\n"
        f"{prompt}"
    )

    # Call Fal-AI text_to_video
    result = client.text_to_video(
        cartoon_prompt,
        model="Wan-AI/Wan2.2-T2V-A14B"
    )

    # If result is raw bytes, we're done
    if isinstance(result, (bytes, bytearray)):
        video_bytes = result

    # If result is a URL string, fetch it
    elif isinstance(result, str) and result.startswith("http"):
        resp = requests.get(result); resp.raise_for_status()
        video_bytes = resp.content

    # If result is a dict, inspect its keys
    elif isinstance(result, dict):
        data = result
        # try top-level "video" key
        url = None
        if "video" in data and isinstance(data["video"], dict):
            url = data["video"].get("url")
        # try old "generated_videos" list
        if not url and "generated_videos" in data:
            vids = data["generated_videos"]
            if vids and isinstance(vids[0], dict):
                url = vids[0].get("url")
        # try generic "videos" list
        if not url and "videos" in data:
            vids = data["videos"]
            if vids and isinstance(vids[0], dict):
                url = vids[0].get("url")

        if not url:
            # Debug output
            print("⚠️ Unexpected JSON structure from text_to_video:")
            print(json.dumps(data, indent=2))
            raise RuntimeError("Failed to find video URL in response")

        # Download the MP4
        resp = requests.get(url); resp.raise_for_status()
        video_bytes = resp.content

    else:
        raise RuntimeError(f"Unsupported response type: {type(result)}")

    # Save to disk
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(video_bytes)

    print(f"✅ Saved: {out_path}")

def main():
    with open("4_output/scenes.json") as f:
        scenes = json.load(f)

    for sc in scenes:
        pid = sc["id"]
        prompt = sc["prompt"]
        out_file = f"4_output/chunks/scene_{pid}.mp4"
        print(f"--- Generating scene {pid} ---")
        generate_video(prompt, out_file)

if __name__ == "__main__":
    main()
