import subprocess
import os

def ensure_pcm_wav(in_path: str, out_path: str):
    if os.path.exists(out_path):
        return out_path

    cmd = [
        "ffmpeg", "-y",
        "-i", in_path,
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        out_path
    ]
    subprocess.run(cmd, check=True)
    return out_path