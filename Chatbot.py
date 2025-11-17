import nltk
from nltk.chat.util import Chat, reflections
import speech_recognition as sr
import datetime

# ---------- NLTK DATA SETUP (RUN ONCE IF NEEDED) ----------
# Uncomment these lines the first time you run the script if you don't have the data.
# nltk.download('punkt')
# nltk.download('wordnet')

# ---------- PATTERNS (STEP 3 + TASK 1) ----------
patterns = [
    (r'hi|hello|hey', ['Hello!', 'Hi there!', 'Hey!']),
    (r'how are you\??', ["I'm good, thank you!", "I'm doing well."]),
    (r'what is your name\??', ['You can call me ChatGPT.']),

    # Task 1: new pattern for "What can you do?"
    (r'what can you do\??', [
        "I can respond to simple text patterns and voice commands.",
        "Right now I can chat with you using both text and voice, and answer a few basic questions."
    ]),

    (r'bye|goodbye', ['Goodbye!', 'See you later!']),

    # Fallback pattern (always keep this last)
    (r'(.*)', ["I'm not sure how to respond to that."])
]

chatbot = Chat(patterns, reflections)

# ---------- VOICE INPUT FUNCTION (STEP 4 + TASK 2 & 3) ----------
def voice_input_chat(timeout=5, phrase_time_limit=10):
    """
    Capture a single utterance from the microphone and convert it to text.
    timeout: how long to wait for the user to start speaking (seconds)
    phrase_time_limit: max length of a phrase (seconds) to handle long pauses
    """
    recognizer = sr.Recognizer()

    # Optional: reduce background noise
    try:
        with sr.Microphone() as mic:
            print("Adjusting for ambient noise... please wait.")
            recognizer.adjust_for_ambient_noise(mic, duration=1)

            print("Say something...")
            # Task 3: handle long pauses using timeout and phrase_time_limit
            audio = recognizer.listen(mic, timeout=timeout, phrase_time_limit=phrase_time_limit)

        # Use Google's free speech API
        text = recognizer.recognize_google(audio)
        print(f"[Recognized voice input]: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        print("No speech detected (timeout).")
        return None
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except OSError as e:
        print(f"Microphone error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during voice recognition: {e}")
        return None

# ---------- LOGGING FUNCTION (TASK 5) ----------
def text_and_voice_log(log_list, mode, user_input, bot_response):
    """
    Append a log entry for each interaction.

    log_list: list to hold in-memory logs
    mode: 'text' or 'voice'
    user_input: original user text
    bot_response: chatbot response
    """
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    entry = {
        "time": timestamp,
        "mode": mode,
        "user": user_input,
        "bot": bot_response
    }
    log_list.append(entry)

# ---------- SAVE TRANSCRIPT TO FILE (TASK 4) ----------
def save_transcript(log_list, filename="chat_transcript.txt"):
    """
    Save the conversation transcript to a text file.
    Each line includes timestamp, mode, user text, and bot response.
    """
    if not log_list:
        print("No conversation to save.")
        return

    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n--- New Session ---\n")
            for entry in log_list:
                line = (
                    f"[{entry['time']}] "
                    f"[{entry['mode'].upper()}] "
                    f"User: {entry['user']} | Bot: {entry['bot']}\n"
                )
                f.write(line)
        print(f"Transcript saved to {filename}")
    except Exception as e:
        print(f"Error saving transcript: {e}")

# ---------- MAIN CHAT LOOP (STEP 5 + TASK 2 INTEGRATION) ----------
def run_chatbot():
    print("Simple Text and Voice Chatbot")
    print("Choose input mode: 1. Text  2. Voice")
    print("Type 'exit' (in text mode) or say 'stop talking' (in voice mode) to end.\n")

    # In-memory log of the current session
    conversation_log = []

    while True:
        mode = input("Enter 1/2 or 'exit': ").strip().lower()

        if mode == 'exit':
            print("Exiting chatbot (text exit).")
            break

        if mode not in ('1', '2'):
            print("Invalid choice. Please enter 1, 2, or 'exit'.")
            continue

        if mode == '1':
            # Text mode
            user_input = input("You (text): ").strip()
            if user_input.lower() == 'exit':
                print("Exiting chatbot (text exit).")
                break

            response = chatbot.respond(user_input)
            print("ChatGPT:", response)

            # Log interaction
            text_and_voice_log(conversation_log, mode="text",
                               user_input=user_input, bot_response=response)

        elif mode == '2':
            # Voice mode
            user_input = voice_input_chat()

            if user_input is None:
                # Could not understand or timeout; skip this turn
                continue

            # Task 2: exit automatically if user says 'stop talking'
            if 'stop talking' in user_input:
                print("Detected 'stop talking' command. Exiting chatbot.")
                break

            response = chatbot.respond(user_input)
            print("ChatGPT:", response)

            # Log interaction
            text_and_voice_log(conversation_log, mode="voice",
                               user_input=user_input, bot_response=response)

    # At the end of the session, save transcript (Task 4)
    save_transcript(conversation_log)


if __name__ == "__main__":
    run_chatbot()