import os, json
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

def main():
    with open("4_output/scenes.json") as f:
        scenes = json.load(f)
    clips = []
    for sc in scenes:
        v = VideoFileClip(f"4_output/chunks/scene_{sc['id']}.mp4")
        a = AudioFileClip(f"4_output/audio/scene_{sc['id']}.wav")
        clips.append(v.set_audio(a))
    final = concatenate_videoclips(clips, method="compose")
    os.makedirs("4_output/final", exist_ok=True)
    out = "4_output/final/the_little_prince.mp4"
    final.write_videofile(out, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Final movie saved to {out}")

if __name__ == "__main__":
    main()
