# RVC Fast Inference (Serverless)

Serverless API for RVC voice conversion on RunPod. Send input audio + `model_name`, get cloned audio back.

## Inputs
- `model_name`: folder under `/models/<model_name>` (trained weights live here)
- `audio_b64` (base64) or `audio_url` (http/https)
- `semitones` (int, optional)

## Env (hub.json)
- `MODELS_DIR` (default `/models`)
- `OUTPUT_FORMAT` (`wav` or `mp3`, default `wav`)
- `RETURN_BASE64` (default `true`)

## Healthcheck
Request:
```json
{ "input": { "healthcheck": true } }

## Example job
```json
{
  "input": {
    "model_name": "my_voice_v1",
    "audio_url": "https://example.com/input.wav",
    "semitones": 0
  }
}

That’s all — the `Models` section is just plain text guidance for the user. Nothing else goes inside it.

