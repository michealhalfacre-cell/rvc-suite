#!/usr/bin/env python3
"""
RunPod Serverless Handler for RVC-Suite
Real-time Voice Conversion processing
"""

import os
import json
import time
import base64
import traceback
from typing import Dict, Any, Optional, List
import requests
import numpy as np
import torch
import torchaudio
import runpod

# Import your RVC modules here
# from rvc_infer import RVCInference
# from rvc_utils import load_model, process_audio

class RVCHandler:
    """Handler for RVC voice conversion tasks"""
    
    def __init__(self):
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sample_rate = int(os.environ.get('SAMPLE_RATE', '48000'))
        self.model_path = os.environ.get('MODEL_PATH', '/workspace/models')
        self.cache_dir = os.environ.get('CACHE_DIR', '/workspace/cache')
        
        print(f"RVC Handler initialized. Device: {self.device}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load an RVC model into memory"""
        try:
            if model_name in self.models:
                return {"status": "success", "message": "Model already loaded"}
            
            model_file = os.path.join(self.model_path, f"{model_name}.pth")
            if not os.path.exists(model_file):
                return {"status": "error", "message": f"Model file not found: {model_name}"}
            
            # Load your RVC model here
            # self.models[model_name] = load_model(model_file, self.device)
            
            # Placeholder for actual model loading
            self.models[model_name] = {"name": model_name, "loaded": True}
            
            return {
                "status": "success",
                "model_loaded": True,
                "model_name": model_name
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def download_audio(self, audio_url: str) -> Optional[str]:
        """Download audio from URL"""
        try:
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            # Save to temp file
            temp_file = os.path.join(self.cache_dir, f"temp_{int(time.time())}.wav")
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            return temp_file
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
    
    def convert_voice(self, audio_input: Any, model_name: str, **params) -> Dict[str, Any]:
        """
        Perform voice conversion
        
        Args:
            audio_input: URL, base64 string, or file path
            model_name: Name of the RVC model to use
            **params: Additional conversion parameters
        """
        try:
            # Load model if not already loaded
            if model_name not in self.models:
                load_result = self.load_model(model_name)
                if load_result["status"] != "success":
                    return load_result
            
            # Get audio file
            if isinstance(audio_input, str):
                if audio_input.startswith('http'):
                    audio_file = self.download_audio(audio_input)
                elif audio_input.startswith('data:'):
                    # Handle base64 audio
                    audio_data = base64.b64decode(audio_input.split(',')[1])
                    audio_file = os.path.join(self.cache_dir, f"temp_{int(time.time())}.wav")
                    with open(audio_file, 'wb') as f:
                        f.write(audio_data)
                else:
                    audio_file = audio_input
            else:
                return {"status": "error", "message": "Invalid audio input type"}
            
            if not audio_file or not os.path.exists(audio_file):
                return {"status": "error", "message": "Failed to load audio file"}
            
            # Load audio
            waveform, sr = torchaudio.load(audio_file)
            
            # Resample if necessary
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
            
            # Extract parameters
            pitch_shift = params.get('pitch_shift', 0)
            feature_ratio = params.get('feature_ratio', 0.75)
            filter_radius = params.get('filter_radius', 3)
            rms_mix_rate = params.get('rms_mix_rate', 0.25)
            protect_voiceless = params.get('protect_voiceless', 0.33)
            
            # Perform conversion (placeholder - implement actual RVC inference)
            # converted_audio = self.models[model_name].infer(
            #     waveform,
            #     pitch_shift=pitch_shift,
            #     feature_ratio=feature_ratio,
            #     filter_radius=filter_radius,
            #     rms_mix_rate=rms_mix_rate
            # )
            
            # For now, just return the input as output
            converted_audio = waveform
            
            # Save output
            output_file = os.path.join(self.cache_dir, f"output_{int(time.time())}.wav")
            torchaudio.save(output_file, converted_audio, self.sample_rate)
            
            # Convert to base64 for response
            with open(output_file, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Clean up temp files
            if audio_file.startswith(self.cache_dir):
                os.remove(audio_file)
            
            return {
                "status": "success",
                "audio_base64": audio_base64,
                "audio_url": f"data:audio/wav;base64,{audio_base64}",
                "sample_rate": self.sample_rate,
                "duration": converted_audio.shape[1] / self.sample_rate
            }
            
        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def batch_convert(self, audio_urls: List[str], model_name: str, **params) -> Dict[str, Any]:
        """Process multiple audio files"""
        results = []
        for url in audio_urls:
            result = self.convert_voice(url, model_name, **params)
            results.append(result)
        
        successful = sum(1 for r in results if r["status"] == "success")
        return {
            "status": "success",
            "processed": len(audio_urls),
            "successful": successful,
            "failed": len(audio_urls) - successful,
            "results": results
        }

# Initialize handler
handler = RVCHandler()

def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "models_loaded": list(handler.models.keys())
    }

def process_request(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process RunPod job request
    
    Args:
        job: RunPod job dictionary containing 'input' field
    """
    try:
        job_input = job.get('input', {})
        action = job_input.get('action', 'convert')
        
        if action == 'health':
            return health_check()
        
        elif action == 'load_model':
            model_name = job_input.get('model_name')
            if not model_name:
                return {"error": "Missing required parameter: model_name"}
            return handler.load_model(model_name)
        
        elif action == 'convert':
            audio_url = job_input.get('audio_url') or job_input.get('audio_base64')
            model_name = job_input.get('model_name', 'default')
            
            if not audio_url:
                return {"error": "Missing required parameter: audio_url or audio_base64"}
            
            return handler.convert_voice(
                audio_url,
                model_name,
                pitch_shift=job_input.get('pitch_shift', 0),
                feature_ratio=job_input.get('feature_ratio', 0.75),
                filter_radius=job_input.get('filter_radius', 3),
                rms_mix_rate=job_input.get('rms_mix_rate', 0.25),
                protect_voiceless=job_input.get('protect_voiceless', 0.33)
            )
        
        elif action == 'batch_convert':
            audio_urls = job_input.get('audio_urls', [])
            model_name = job_input.get('model_name', 'default')
            
            if not audio_urls:
                return {"error": "Missing required parameter: audio_urls"}
            
            return handler.batch_convert(audio_urls, model_name, **job_input)
        
        else:
            return {"error": f"Unknown action: {action}"}
            
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

# RunPod serverless handler
def handler_runpod(job):
    """RunPod serverless handler function"""
    try:
        result = process_request(job)
        return result
    except Exception as e:
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    # Start RunPod serverless worker
    runpod.serverless.start({
        "handler": handler_runpod
    })