import whisper

#load the whisper model
model = whisper.load_model("base")

#transcribe the audio file
result = model.transcribe("lesson_recording.mp3", fp16=False)

print('Transcription: ', result["text"])