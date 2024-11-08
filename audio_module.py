import speech_recognition as sr
import whisper

# Initialize models
recognizer = sr.Recognizer()
whisper_model = whisper.load_model("base")

def handle_audio(audio_path):
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        # Transcribe using Whisper
        result = whisper_model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        return f"Error transcribing audio: {e}"
