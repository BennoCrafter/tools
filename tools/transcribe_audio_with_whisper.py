"""
Transcribe audio using Whisper.
"""

import argparse


def transcribe_audio_with_whisper(
    audio_file,
    output_file,
    model_size="base",
    language: str = "en",
    verbose: bool = False,
):
    print("Initializing Whisper...")
    import whisper

    try:
        print(f"Loading Whisper model '{model_size}'...")
        model = whisper.load_model(model_size)

        print("Transcribing audio...")
        result = model.transcribe(audio=audio_file, language=language, verbose=verbose)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(str(result.get("text", "")))

        print(f"Transcript saved to {output_file}")

    except FileNotFoundError:
        print(f"The file {audio_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio using Whisper")
    parser.add_argument(
        "audio_file", help="Path to the audio file to transcribe", type=str
    )
    parser.add_argument("output_file", help="Path where to save the transcript")
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper model size to use (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--language", default="en", help="Language code (e.g. en, de, fr)"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    transcribe_audio_with_whisper(
        args.audio_file, args.output_file, args.model, args.language, args.verbose
    )
