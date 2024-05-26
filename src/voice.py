import os
import wave

import openai
import pyaudio
import pydub

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
BYTES_PER_SECOND = 44100
BYTES_PER_BUFFER = 1024


def record_voice(*, silence_duration_threshold=0.5, silence_volume_threshold=80, audio_min_duration=0.5) -> str:
    audio, stream = _start_audio_stream()
    buffers = []
    silence_duration = 0
    _print_record_start()

    while True:
        # Read a buffer of audio data
        buffer = stream.read(BYTES_PER_BUFFER)
        buffers.append(buffer)

        # Calculate the average volume of the buffer
        buffer_avg = sum(buffer) // len(buffer)
        _print_record_buffer(buffer_avg, silence_volume_threshold)

        # If the volume is above the threshold, we continue recording
        if buffer_avg > silence_volume_threshold:
            silence_duration = 0
            continue

        # Else, we increment the silence duration
        silence_duration += BYTES_PER_BUFFER / BYTES_PER_SECOND

        # While silence duration is low, we continue recording
        if silence_duration < silence_duration_threshold:
            continue

        # We got a silence, but we need to check if the buffers contain anything
        # meaningful. For that we trim leading and trailing silence.
        print("\n[voice] Silence detected.")
        buffers = _trim_leading_silence(buffers, silence_volume_threshold)
        buffers = _trim_trailing_silence(buffers, silence_volume_threshold)

        # Once leading and trailing silence is trimmed, we check if the
        # recording is long enough. If not, we continue recording.
        duration = len(buffers) * BYTES_PER_BUFFER / BYTES_PER_SECOND
        if duration < audio_min_duration:
            print(f"[voice] Recording too short ({duration:.2f}s), continuing.")
            _print_record_start()
            buffers = []
            silence_duration = 0.0
        else:
            print(f"[voice] Recording long enough ({duration:.2f}s), stopping.")
            _stop_audio_stream(audio, stream)
            return _write_mp3_file(buffers)


def transcribe_voice(audio_file_path: str, lang: str, prompt: str) -> str:
    with open(audio_file_path, "rb") as file:
        client = openai.OpenAI()
        response = client.audio.transcriptions.create(
            file=file,
            language=lang,
            model="whisper-1",
            temperature=0.2,
            prompt=prompt,
        )

        text = response.text.strip()
        print(f"[voice] Transcription: {text}")

        return text


# ------------------------------------------------------------------------------
# HELPERS: FRAMES
# ------------------------------------------------------------------------------


def _trim_leading_silence(buffers, silence_volume_threshold):
    for i, buffer in enumerate(buffers):
        avg = sum(buffer) / len(buffer)
        if avg > silence_volume_threshold:
            return buffers[i:]
    return []


def _trim_trailing_silence(buffers, silence_volume_threshold):
    frames_reversed = reversed(buffers)
    for i, buffer in enumerate(frames_reversed):
        avg = sum(buffer) / len(buffer)
        if avg > silence_volume_threshold:
            return buffers[: len(buffers) - i]
    return []


# ------------------------------------------------------------------------------
# HELPERS: STREAM
# ------------------------------------------------------------------------------


def _start_audio_stream():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=AUDIO_FORMAT,
        channels=AUDIO_CHANNELS,
        rate=BYTES_PER_SECOND,
        input=True,
        frames_per_buffer=BYTES_PER_BUFFER,
    )
    return audio, stream


def _stop_audio_stream(audio, stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()


# ------------------------------------------------------------------------------
# HELPERS: OUTPUT
# ------------------------------------------------------------------------------


def _print_record_start():
    print("[voice] Recording: ", end="", flush=True)


def _print_record_buffer(avg, silence_volume_threshold):
    msg = f"{avg}! " if avg > silence_volume_threshold else f"{avg} "
    print(msg, end="", flush=True)


def _write_mp3_file(buffers):
    file_wave = "out/output.wav"
    file_mp3 = "out/output.mp3"

    # Ensure folder
    os.makedirs("out", exist_ok=True)

    # Save the recorded data as a WAV file
    wf = wave.open(file_wave, "wb")
    wf.setnchannels(AUDIO_CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(AUDIO_FORMAT))
    wf.setframerate(BYTES_PER_SECOND)
    wf.writeframes(b"".join(buffers))
    wf.close()

    # Convert WAV to MP3
    sound = pydub.AudioSegment.from_wav(file_wave)
    sound.export(file_mp3, format="mp3")

    # Delete the WAV file
    os.remove(file_wave)

    # Read mp3 as a byte array
    return file_mp3


# ------------------------------------------------------------------------------
# TEST
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    audio_file_path = record_voice()
    if audio_file_path:
        text = transcribe_voice(audio_file_path, lang="fr", prompt="Tu es Thymio.")
        print(f"[voice] Transcribed: {text}")
    else:
        print("[voice] Recording failed.")
