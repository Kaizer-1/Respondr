# src/streaming/audio_chunker.py

import wave
import math
import os

def chunk_wav(
    wav_path: str,
    chunk_duration_sec: float = 3.0,
    hop_duration_sec: float = 1.5,
    out_dir: str = "tmp_chunks"
):
    os.makedirs(out_dir, exist_ok=True)

    with wave.open(wav_path, "rb") as wf:
        rate = wf.getframerate()
        frames_per_chunk = int(rate * chunk_duration_sec)
        frames_per_hop = int(rate * hop_duration_sec)

        total_frames = wf.getnframes()
        chunk_paths = []

        pos = 0
        idx = 0

        while pos < total_frames:
            wf.setpos(pos)
            frames = wf.readframes(frames_per_chunk)

            if not frames:
                break

            out_path = f"{out_dir}/chunk_{idx:03d}.wav"
            with wave.open(out_path, "wb") as out:
                out.setnchannels(wf.getnchannels())
                out.setsampwidth(wf.getsampwidth())
                out.setframerate(rate)
                out.writeframes(frames)

            chunk_paths.append(out_path)
            pos += frames_per_hop
            idx += 1

    return chunk_paths