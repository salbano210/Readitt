import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

print("Available English Voices:")
for v in voices:
    if "en" in str(v.languages[0]).lower():
        print(f"- {v.name} ({v.id})")