import json
import os
from typing import List


def thymio_start(program: str) -> None:
    print("[thymio] Starting robot")
    os.system(f"python -m tdmclient run --nosleep {program}")


def thymio_stop() -> None:
    print("[thymio] Stopping robot")
    os.system("python -m tdmclient run --stop")


def thymio_send(name: str, args: List[int]) -> None:
    print(f"[thymio] Sending event '{name}' with args {args}")
    event = f"--event {name}"
    data = f"--data '{json.dumps(args)}'" if len(args) > 0 else ""
    os.system(f"python -m tdmclient sendevent {event} {data}")
