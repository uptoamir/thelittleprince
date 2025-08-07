# generate_scenes.py

import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not set in .env")

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN,
)

def generate_video(prompt: str, out_path: str):
    # Force a 2D cartoon storybook style
    cartoon_prompt = (
        "2D storybook illustration, hand-drawn cartoon style.\n"
        f"{prompt}"
    )

    result = client.text_to_video(
        cartoon_prompt,
        model="Wan-AI/Wan2.2-T2V-A14B",
        extra_body={            # pass cartoon hints via extra_body
            "resolution": "1280x720",
            "fps": 24,
            "duration": 5,
            "cartoon_optimization": True,
            "guidance_scale": 0.9,
            # optional preset if supported:
            "style_preset": "cartoon"
        }
    )

    # unwrap bytes / URL / dict as before...
    if isinstance(result, (bytes, bytearray)):
        video_bytes = result
    elif isinstance(result, str) and result.startswith("http"):
        import requests
        resp = requests.get(result); resp.raise_for_status()
        video_bytes = resp.content
    elif isinstance(result, dict):
        url = (result.get("video", {}) or {}).get("url") \
              or (result.get("generated_videos") or [{}])[0].get("url")
        if not url:
            raise RuntimeError(f"No URL in response: {result}")
        import requests
        resp = requests.get(url); resp.raise_for_status()
        video_bytes = resp.content
    else:
        raise RuntimeError(f"Unsupported return type: {type(result)}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(video_bytes)
    print(f"Saved: {out_path}")

def main():
    with open("4_output/scenes.json") as f:
        scenes = json.load(f)

    for sc in scenes:
        pid = sc["id"]
        prompt = sc["prompt"]
        out_file = f"4_output/chunks/scene_{pid}.mp4"
        print(f"Generating scene {pid} in cartoon style…")
        generate_video(prompt, out_file)

if __name__ == "__main__":
    main()
