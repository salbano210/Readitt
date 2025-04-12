import pyttsx3
import time

engine = pyttsx3.init()
voices = engine.getProperty("voices")

print("🔊 Speaking each English voice available:\n")

for v in voices:
    # Only play English voices
    if "en" in str(v.languages[0]).lower():
        print(f"- Voice: {v.name} ({v.id})")
        engine.setProperty("voice", v.id)
        engine.say(f"Hi, I'm {v.name}. This is how I sound.")
        engine.runAndWait()
        time.sleep(0.5)  # small pause between voices
