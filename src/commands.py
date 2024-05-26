import json
from typing import List

import openai


class Command:
    def __init__(self, name: str, params: List[int]):
        self.name = name
        self.params = params


def extract_commands(text: str) -> List[Command]:
    client = openai.OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        model="gpt-4o",
        response_format={"type": "json_object"},
    )

    reply = chat_completion.choices[0].message.content

    commands_json = json.loads(reply)
    print(f"[commands] Extracted commands: {json.dumps(commands_json)}")

    return _json_to_commands(commands_json)


# ------------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------------


def _json_to_commands(json_object: dict) -> List[Command]:
    commands = []
    for command_data in json_object["commands"]:
        name = command_data[0]
        params = command_data[1]

        if isinstance(name, str) and isinstance(params, list) and all(isinstance(param, int) for param in params):
            command = Command(name, params)
            commands.append(command)
        else:
            print(f"[commands] Invalid command: {json.dumps(command_data)}")

    return commands


# ------------------------------------------------------------------------------
# PROMPT
# ------------------------------------------------------------------------------


prompt = """
You are a simple robot engine, controlling the Thymio robot.
Based on the user message, respond with the appropriate command array, using the
following JSON output:
```json
{
    "commands": [
        [ "<command_name>", [command_params] ],
        ...
    ]
}
```

Commands are:
- name "move.forward" // starts the motors
  params [speed]: one integer from 20 to 300
- name "move.backward" // starts the motors
  params [speed]: one integer from 20 to 300
- name "stop" // stops the motors
  params []: empty array
- name "light" // sets the top LEDs color
  params [red, green, blue]: 3 integers from 0 to 32
- name "sound" // plays a sound for the given duration
  params [frequency, duration]: frequency in Hz and duration in 60th of a second
- name "wait" // waits for the given duration before executing the next command
  params [duration]: duration in 60th of a second

Ideas:
Use the "sound" command to communicate feelings with the user.
Chain multiple "sound" commands to play a melody!
Prefer short sounds, 10/60th of seconds, like piano notes, for a better user experience.
You can use multiple commands in a single response, be creative!
You can return an empty array if there is nothing to do.

Examples:
- User: "Play a DO-RE-MI melody!"
- You: { "commands": [["sound", [261, 30]], ["sound": [293, 30]], ["sound": [329, 30]]] }
"""
