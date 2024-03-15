from vosk import Model, KaldiRecognizer
import pyaudio
import json

model_path = "vosk-model-small-en-us-0.15"  # Replace with your model path
model = Model(model_path)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open a stream
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Create a recognizer object
recognizer = KaldiRecognizer(model, 16000)

print("Speak now...")

while True:
    data = stream.read(4096, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        print(result['text'])

# Stop and close the stream and PyAudio
stream.stop_stream()
stream.close()
p.terminate()
