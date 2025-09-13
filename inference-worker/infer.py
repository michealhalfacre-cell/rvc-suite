import os
import subprocess
import tempfile
from pydub import AudioSegment

RVC_ROOT = "/workspace/rvc"

def load_model(model_dir: str):
    return {"model_dir": model_dir}

def _ensure_wav_44k_mono(in_path: str) -> str:
    audio = AudioSegment.from_file(in_path)
    audio = audio.set_channels(1).set_frame_rate(44100)
    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    audio.export(tmp, format="wav")
    return tmp

def _rvc_cli_exists() -> bool:
    candidates = [
        os.path.join(RVC_ROOT, "infer_cli.py"),
        os.path.join(RVC_ROOT, "inference_cli.py"),
        os.path.join(RVC_ROOT, "infer.py")
    ]
    return any(os.path.isfile(p) for p in candidates)

def convert_audio(model, input_audio_path: str, semitones: int = 0, out_format: str = "wav") -> str:
    in44 = _ensure_wav_44k_mono(input_audio_path)

    model_dir = model["model_dir"]
    out_suffix = ".wav" if out_format.lower() == "wav" else ".mp3"
    fd, out_path = tempfile.mkstemp(suffix=out_suffix)
    os.close(fd)
    os.remove(out_path)

    if _rvc_cli_exists():
        try:
            cmd = [
                "python3",
                os.path.join(RVC_ROOT, "infer_cli.py"),
                "--model_dir", model_dir,
                "--input", in44,
                "--output", out_path,
                "--transpose", str(semitones),
                "--format", out_format.lower()
            ]
            subprocess.run(cmd, check=True)
            if os.path.isfile(out_path):
                return out_path
        except Exception:
            pass

    export_path = out_path if out_path.endswith(".wav") else out_path.replace(".mp3", ".wav")
    AudioSegment.from_file(in44).export(export_path, format="wav")
    return export_path
