# The Little Prince AI Movie Generator

This project creates a full end-to-end pipeline to turn **The Little Prince** PDF into a single continuous cartoon with narration and rudimentary sound design—all using Wan-AI's 2.2 model.

## Project Structure

```
little_prince_ai_movie/
├── .env                  # your HF_TOKEN & GEMINI_TOKEN
├── requirements.txt
├── TheLittlePrince.pdf
├── scene_segmentation.py
├── generate_scenes.py
├── generate_audio.py
├── assemble.py
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
GEMINI_TOKEN=your_google_gemini_key
HF_TOKEN=hf_your_huggingface_key
```

**Get your API keys:**
- **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- **HuggingFace**: Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)

### 3. Add The Little Prince PDF

Place your `TheLittlePrince.pdf` file in the project root directory.

## Usage

Run the pipeline in sequence:

```bash
# 1. Segment the book into scenes
python scene_segmentation.py
# → Creates 4_output/scenes.json

# 2. Generate all 5s video chunks
python generate_scenes.py
# → Creates 4_output/chunks/scene_*.mp4

# 3. Generate narration audio
python generate_audio.py
# → Creates 4_output/audio/scene_*.wav

# 4. Stitch into one continuous movie
python assemble.py
# → Creates 4_output/final/the_little_prince.mp4
```

## Output Structure

After running the pipeline, you'll have:

```
4_output/
├── scenes.json              # Scene segmentation data
├── chunks/                  # Individual video scenes
│   ├── scene_01.mp4
│   ├── scene_02.mp4
│   └── ...
├── audio/                   # Narration audio files
│   ├── scene_01.wav
│   ├── scene_02.wav
│   └── ...
└── final/                   # Final assembled movie
    └── the_little_prince.mp4
```

## How It Works

1. **Scene Segmentation** (`scene_segmentation.py`):
   - Extracts text from the PDF using PyPDF2
   - Uses Google Gemini 2.5 Pro to break the story into logical 5-second micro-scenes
   - Outputs JSON with scene prompts and narration text

2. **Video Generation** (`generate_scenes.py`):
   - Uses Wan-AI's 2.2 T2V model to generate 5-second video clips
   - Applies cartoon optimization for storybook-style illustrations
   - Outputs MP4 files for each scene

3. **Audio Generation** (`generate_audio.py`):
   - Uses HuggingFace TTS to synthesize narration for each scene
   - Outputs WAV files synchronized with video scenes

4. **Assembly** (`assemble.py`):
   - Combines all video chunks with their corresponding audio
   - Creates a single continuous MP4 movie
   - Uses MoviePy for video processing

## Technical Details

- **Video Resolution**: 1280x720 (HD)
- **Frame Rate**: 24 FPS
- **Scene Duration**: 5 seconds each
- **Audio Format**: WAV (16-bit)
- **Output Format**: MP4 (H.264 + AAC)

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `.env` file is properly configured
2. **PDF Not Found**: Make sure `TheLittlePrince.pdf` is in the project root
3. **Memory Issues**: The video generation can be resource-intensive; consider reducing batch size
4. **Audio Sync**: If audio/video are out of sync, check that all files were generated successfully

### Dependencies

- `google-genai`: Google Gemini API client
- `huggingface_hub`: HuggingFace API client
- `python-dotenv`: Environment variable management
- `PyPDF2`: PDF text extraction
- `moviepy`: Video processing and assembly
- `requests`: HTTP requests for API calls

## License

This project is for educational purposes. Please ensure you have the rights to use The Little Prince content in your jurisdiction.

