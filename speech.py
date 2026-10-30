from faster_whisper import WhisperModel
from pydub import AudioSegment
import os

# Load model once (global)
model = WhisperModel("base", device="cpu", compute_type="int8")

def convert_ogg_to_wav(input_path):
    output_path = input_path.replace(".ogg", ".wav")
    audio = AudioSegment.from_ogg(input_path)
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(file_path):
    wav_path = convert_ogg_to_wav(file_path)

    segments, info = model.transcribe(wav_path)

    full_text = ""
    for segment in segments:
        full_text += segment.text + " "

    # Cleanup temp wav
    if os.path.exists(wav_path):
        os.remove(wav_path)

    return full_text.strip()