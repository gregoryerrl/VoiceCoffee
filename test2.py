import re
import json
import pyaudio
from vosk import Model, KaldiRecognizer
# Importing additional library for playing audio
import wave
import time

# Merged dictionary for interpretation
interpretation_dict = {
    # Numbers
    'oh': 2, 'who': 2, 'two': 2, 'you': 2, 'to': 2, 'brew': 2, 'one': 1,
    'three': 3, 'read': 3, 'he': 3, 'me': 3, 'or': 4, 'for': 4,
    # Items
    'coffee': 'coffee', 'murphy': 'coffee', 'copy': 'coffee', 'sugar': 'sugar', 'sure were': 'sugar',
    'sherborne': 'sugar', 'shiver': 'sugar', 'sure where': 'sugar', 'cream': 'cream', 'dream': 'cream',
    'rim': 'cream', 'when': 'cream', 'queen': 'cream', 'free': 'cream', 'really': 'cream', 'real': 'cream',
    'pm': 'cream', 'green': 'cream', 'korean': 'three', 'korea': 'three', 'bream': 'cream',
    # Specific Phrases (like "Hey Joe")
    'hey joe': 'hey joe', 'a joe': 'hey joe', 'a job': 'hey joe', 'hey job': 'hey joe', 'a joke': 'hey joe', 'hey joke': 'hey joe'
    # Add more interpretations as needed
}

# Order data
orderedCoffee = 0
orderedCream = 0
orderedSugar = 0

# State constants
STATE_WAITING_FOR_TRIGGER = 1
STATE_WAITING_FOR_RESPONSE = 2
STATE_WAITING_FOR_COFFEE = 3
STATE_WAITING_FOR_CREAM = 4
STATE_WAITING_FOR_SUGAR = 5
STATE_REPEAT_ORDER = 6
STATE_WAITING_FOR_CONFIRMATION = 7
STATE_MAKING_COFFEE = 8

# Current state variable
current_state = STATE_WAITING_FOR_TRIGGER

# Function to interpret words
def interpret_word(word):
    return interpretation_dict.get(word, word)

# Function to play audio file without terminating PyAudio
def play_audio(file_path, py_audio_instance):
    try:
        wf = wave.open(file_path, 'rb')
        playback_stream = py_audio_instance.open(format=py_audio_instance.get_format_from_width(wf.getsampwidth()),
                                                 channels=wf.getnchannels(),
                                                 rate=wf.getframerate(),
                                                 output=True)
        data = wf.readframes(1024)
        while data:
            playback_stream.write(data)
            data = wf.readframes(1024)
        playback_stream.stop_stream()
        playback_stream.close()
    except Exception as e:
        print(f"Error in play_audio: {e}")

# Initialize VOSK model
model_path = "vosk-model-small-en-us-0.15"  # Update with the path to your VOSK model
model = Model(model_path)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Initialize PyAudio for speech recognition
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Create a recognizer object
recognizer = KaldiRecognizer(model, 16000)

print("Waiting for 'Hey Joe'...")

try:
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            recognized_text = result['text']
            interpreted_text = interpret_word(recognized_text.lower())

            if current_state == STATE_WAITING_FOR_TRIGGER and interpreted_text == "hey joe":
                print("Playing intro.wav")
                play_audio("feedback/1_wake.wav", p)
                print("Reinitializing voice recognition stream")
                stream.stop_stream()
                stream.close()
                stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                stream.start_stream()
                current_state = STATE_WAITING_FOR_RESPONSE
                print("Say 'Yes' to order or 'No' to cancel...")

            elif current_state == STATE_WAITING_FOR_RESPONSE:
                if interpreted_text == "yes":
                    play_audio("feedback/2.1_choose_coffee.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_WAITING_FOR_COFFEE
                    print("Coffee")
                elif interpreted_text == "no":
                    play_audio("feedback/8.2_cancel.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_WAITING_FOR_TRIGGER
                    print("Waiting for 'Hey Joe'...")

            elif current_state == STATE_WAITING_FOR_COFFEE:
                if interpreted_text > 0:
                    orderedCoffee = interpreted_text
                    play_audio("feedback/3_cream.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_WAITING_FOR_CREAM
                    print(orderedCoffee)
                    print("Cream")
            elif current_state == STATE_WAITING_FOR_CREAM:
                if interpreted_text > 0:
                    orderedCream = interpreted_text
                    play_audio("feedback/4_sugar.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_WAITING_FOR_SUGAR
                    print(orderedCream)
                    print("Sugar")
            elif current_state == STATE_WAITING_FOR_SUGAR:
                if interpreted_text > 0:
                    orderedSugar = interpreted_text
                    play_audio("feedback/5_repeat_order.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_REPEAT_ORDER
                    print(orderedSugar)
                    print("REPEATING ORDER")

        elif current_state == STATE_REPEAT_ORDER:
            play_audio("feedback/5/" + str(orderedCoffee) + ".wav", p)
            play_audio("feedback/5/Coffee.wav", p)
            play_audio("feedback/5/" + str(orderedCream) + ".wav", p)
            play_audio("feedback/5/Cream.wav", p)
            play_audio("feedback/5/" + str(orderedSugar) + ".wav", p)
            play_audio("feedback/5/Sugar.wav", p)
            time.sleep(1)
            play_audio("feedback/7_proceed_question.wav", p)
            stream.stop_stream()
            stream.close()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
            stream.start_stream()
            current_state = STATE_WAITING_FOR_CONFIRMATION

        elif current_state == STATE_WAITING_FOR_CONFIRMATION:
                if interpreted_text == "yes":
                    play_audio("feedback/8.1_please_wait.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_MAKING_COFFEE
                    print("Coffee")
                elif interpreted_text == "no":
                    play_audio("feedback/8.2_cancel.wav", p)
                    stream.stop_stream()
                    stream.close()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
                    stream.start_stream()
                    current_state = STATE_WAITING_FOR_TRIGGER
                    print("Waiting for 'Hey Joe'...")


        elif current_state == STATE_MAKING_COFFEE:
            time.sleep(3)
            play_audio("feedback/9_done.wav", p)
            stream.stop_stream()
            stream.close()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
            stream.start_stream()
            current_state = STATE_WAITING_FOR_TRIGGER
            print("Waiting for 'Hey Joe'...")



except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    try:
        if stream.is_active():
            stream.stop_stream()
    except Exception as e:
        print(f"Error stopping stream: {e}")
    stream.close()
    p.terminate()