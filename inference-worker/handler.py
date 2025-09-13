import os, base64, tempfile, requests
import runpod
from rvc_infer import load_model, convert_audio

MODELS_DIR = os.getenv("MODELS_DIR", "/models")
RETURN_BASE64 = os.getenv("RETURN_BASE64", "true").lower() == "true"
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "wav")

_model_cache = {}

def _download_to_tmp(url: str) -> str:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def _write_bytes_to_tmp(b: bytes) -> str:
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(b)
    return path

def handler(job):
    inp = job.get("input", {}) or {}

    # Health test for Hub
    if inp.get("healthcheck") is True:
        return {"status": "ok"}

    model_name = inp.get("model_name")
    if not model_name:
        return {"error": "model_name is required"}

    model_path = os.path.join(MODELS_DIR, model_name)
    if not os.path.isdir(model_path):
        return {"error": f"model not found at {model_path}"}

    if model_name not in _model_cache:
        _model_cache[model_name] = load_model(model_path)

    audio_b64 = inp.get("audio_b64")
    audio_url = inp.get("audio_url")
    if not audio_b64 and not audio_url:
        return {"error": "Provide audio_b64 (base64) or audio_url"}

    try:
        if audio_b64:
            raw = base64.b64decode(audio_b64)
            in_path = _write_bytes_to_tmp(raw)
        else:
            in_path = _download_to_tmp(audio_url)
    except Exception as e:
        return {"error": f"Failed to load input audio: {e}"}

    semitones = int(inp.get("semitones", 0))

    try:
        out_path = convert_audio(
            model=_model_cache[model_name],
            input_audio_path=in_path,
            semitones=semitones,
            out_format=OUTPUT_FORMAT
        )
    except Exception as e:
        return {"error": f"inference failed: {e}"}

    if RETURN_BASE64:
        with open(out_path, "rb") as f:
            b = f.read()
        b64 = base64.b64encode(b).decode("utf-8")
        return {"output_format": OUTPUT_FORMAT, "audio_b64": b64}

    return {"output_format": OUTPUT_FORMAT, "message": "Stored locally (no URL configured)"}

runpod.serverless.start({"handler": handler})
