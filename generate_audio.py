import os, json, requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"

def synthesize(text, out_path):
    API = f"https://api-inference.huggingface.co/models/{TTS_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(API, headers=headers, json={"inputs": text})
    r.raise_for_status()
    audio_bytes = r.content
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

def main():
    with open("4_output/scenes.json") as f:
        scenes = json.load(f)
    os.makedirs("4_output/audio", exist_ok=True)
    for sc in scenes:
        wav_path = f"4_output/audio/scene_{sc['id']}.wav"
        print(f"→ Synthesizing audio for {sc['id']}")
        synthesize(sc["narration"], wav_path)
    print("✅ All narration audio generated.")

if __name__ == "__main__":
    main()
