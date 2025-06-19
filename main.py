import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from openai import OpenAI
from graph import ktane_graph
from schemas.schemas import *
from utils import load_enhanced_pages, load_module_descriptions
from audio_handler import Recorder

# Load environment variables
load_dotenv()


def play_next_action_audio(next_action_text):
    """Convert NextAction text to speech and play it"""
    try:
        elevenlabs = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )

        audio = elevenlabs.text_to_speech.convert(
            text=next_action_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        play(audio)

    except Exception as e:
        print(f"🔇 Audio playback failed: {e}")

def transcribe_audio(filename, client):
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
    return transcription.text


def run_ktane_chat():
    """Interactive chat loop for KTANE bomb defusal"""

    # Load resources once
    print("🔧 Loading KTANE manual and modules...")
    enhanced_pages = load_enhanced_pages()
    descriptions = load_module_descriptions()
    recorder = Recorder()
    client = OpenAI()

    # Initialize state
    state = {
        "current_module": "",
        "current_module_description": "",
        "route": "module_recognition",
        "bomb_state": BombState(),
        "known_information": KnownInformation(
            known="",
            unknown="",
            unsure="False"
        ),
        "user_input": "",
        "messages": [],
        "manual_context": "",
        "next_action": None,
        "module_descriptions": descriptions,
        "enhanced_manual_pages": enhanced_pages,
        "retrieve_data_retries": 0
    }

    print("💣 KTANE Bomb Defusal Assistant")
    print("Type 'quit' to exit, 'reset' to start over")
    print("-" * 50)

    while True:
        # Get user input
        wav_file = recorder.listen_and_record()
        user_input = transcribe_audio(wav_file, client)
        print(user_input)

        # Handle special commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Stay safe out there!")
            break
        elif user_input.lower() == 'reset':
            print("🔄 Resetting bomb state...")
            state = {
                "bomb_state": BombState(),
                "known_information": KnownInformation(known="", unknown="", unsure="False"),
                "user_input": "",
                "messages": [],
                "manual_context": "",
                "next_action": None,
                "module_descriptions": descriptions,
                "enhanced_manual_pages": enhanced_pages,
                "retrieve_data_retries": 0
            }
            continue
        elif user_input == '':
            continue

        # Add user message to conversation history
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        state["user_input"] = user_input

        try:
            # Process through the graph
            print("🤖 Analyzing...")
            result = ktane_graph.invoke(state)

            # Update state with results (important for memory!)
            state.update(result)

            # Display and play the response
            if result.get("next_action"):
                next_action_text = result['next_action'].action
                print(f"🎯 Next Action: {next_action_text}")
                print("🔊 Playing audio...")
                play_next_action_audio(next_action_text)

            # Optional: Show current knowledge state
            if result["known_information"].known:
                print(f"✅ Known: {result['known_information'].known}")
            if result["known_information"].unknown:
                print(f"❓ Unknown: {result['known_information'].unknown}")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with different input.")

        # Reset retry counter for next input
        state["retrieve_data_retries"] = 0


# Run the chat
if __name__ == "__main__":
    run_ktane_chat()