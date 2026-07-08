"""
Lightweight Face++ (Face Plus Plus) emotion detector adapter.

Usage: set `FACEPP_API_KEY` and `FACEPP_API_SECRET` in env or Streamlit Secrets.

This module sends the uploaded frame to Face++ Detect API and returns a normalized
emotion label compatible with the app (`calm`, `happy`, `sad`, `angry`, `fearful`, `surprised`, `focused`).
"""
import os
import io
import cv2
import requests
import numpy as np
from typing import Optional

_LAST_ERROR: Optional[str] = None

FACEPP_API_KEY = os.getenv("FACEPP_API_KEY", "")
FACEPP_API_SECRET = os.getenv("FACEPP_API_SECRET", "")
FACEPP_ENDPOINT = os.getenv("FACEPP_ENDPOINT", "https://api-us.faceplusplus.com/facepp/v3/detect")

def get_last_detection_error() -> Optional[str]:
    return _LAST_ERROR

def _set_error(msg: str):
    global _LAST_ERROR
    _LAST_ERROR = msg

def _map_facepp_emotion(facepp_emotion: dict) -> str:
    # facepp_emotion keys: anger, disgust, fear, happiness, neutral, sadness, surprise
    # Choose the highest scoring emotion and map to our normalized set
    if not facepp_emotion:
        return "calm"
    best = max(facepp_emotion.items(), key=lambda x: x[1])
    label = best[0]
    mapping = {
        'happiness': 'happy',
        'neutral': 'calm',
        'sadness': 'sad',
        'anger': 'angry',
        'fear': 'fearful',
        'surprise': 'surprised',
        'disgust': 'focused',
    }
    return mapping.get(label, 'calm')

def analyze_frame(frame_bgr: np.ndarray) -> Optional[str]:
    """Send the frame to Face++ and return a normalized emotion label.
    Returns None on failure.
    """
    global _LAST_ERROR
    _LAST_ERROR = None

    if not FACEPP_API_KEY or not FACEPP_API_SECRET:
        _set_error("Face++ API credentials missing")
        return None

    try:
        # Encode image to JPG bytes
        _, buf = cv2.imencode('.jpg', frame_bgr)
        files = {'image_file': ('frame.jpg', io.BytesIO(buf.tobytes()), 'image/jpeg')}
        data = {
            'api_key': FACEPP_API_KEY,
            'api_secret': FACEPP_API_SECRET,
            'return_attributes': 'emotion'
        }
        resp = requests.post(FACEPP_ENDPOINT, data=data, files=files, timeout=10)
        if resp.status_code != 200:
            _set_error(f"Face++ HTTP {resp.status_code}: {resp.text}")
            return None
        j = resp.json()
        faces = j.get('faces', [])
        if not faces:
            _set_error('Face++: no face detected')
            return None
        # Use largest face by bounding box area if multiple
        best_face = max(faces, key=lambda f: (f.get('face_rectangle', {}).get('width',0) * f.get('face_rectangle', {}).get('height',0)))
        emotions = best_face.get('attributes', {}).get('emotion', {})
        if not emotions:
            _set_error('Face++: no emotion attributes')
            return None
        mapped = _map_facepp_emotion(emotions)
        return mapped

    except Exception as e:
        _set_error(str(e))
        return None


if __name__ == '__main__':
    print('Run inside Streamlit; this module provides `analyze_frame(frame_bgr)`')
