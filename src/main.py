import atexit
import time

from commands import Command, extract_commands
from thymio import thymio_send, thymio_start, thymio_stop
from voice import record_voice, transcribe_voice

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------

LANG = "fr" # language for speech recognition
PROMPT = "Tu es Thymio, un robot." # prompt to help speech recognition
SILENCE_DURATION_THRESHOLD = 0.5  # seconds at low volume for silence detection
SILENCE_VOLUME_THRESHOLD = 80  # volume threshold for silence detection
AUDIO_MIN_DURATION = 0.5  # minimum duration of non-silence recording before stopping

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------


def run() -> None:
    atexit.register(thymio_stop)
    thymio_start("src-thymio/program.py")

    chat = []

    while True:
        audio_path = record_voice(
            silence_duration_threshold=SILENCE_DURATION_THRESHOLD,
            silence_volume_threshold=SILENCE_VOLUME_THRESHOLD,
            audio_min_duration=AUDIO_MIN_DURATION,
        )

        if not audio_path:
            continue

        text = transcribe_voice(audio_path, lang=LANG, prompt=PROMPT)
        chat.append(text)

        for command in extract_commands(chat):
            process_command(command)


def process_command(command: Command) -> None:
    if command.name == "wait":
        time.sleep(command.params[0] / 60)
    elif command.name == "sound":
        thymio_send(command.name, command.params)
        time.sleep(command.params[1] / 60)
    else:
        thymio_send(command.name, command.params)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
