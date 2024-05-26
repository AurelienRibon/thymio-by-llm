import atexit
import time

from commands import Command, extract_commands
from thymio import thymio_send, thymio_start, thymio_stop
from voice import record_voice, transcribe_voice


def run() -> None:
    atexit.register(thymio_stop)
    thymio_start("src-thymio/program.py")

    while True:
        audio_path = record_voice()
        if not audio_path:
            continue

        text = transcribe_voice(audio_path, lang="fr")
        commands = extract_commands(text)

        for command in commands:
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
