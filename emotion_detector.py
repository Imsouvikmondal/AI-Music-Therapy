
import os
import threading
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from typing import Optional

from efficientface_model import EfficientFace


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHECKPOINT_PATH = os.path.join(
    BASE_DIR,
    "model_checkpoints",
    "EfficientFace_RAFDB_best.pth.tar"
)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

CLASS_NAMES = [
    "neutral",
    "happy",
    "sad",
    "surprise",
    "fear",
    "disgust",
    "angry",
]

_LAST_ERROR: Optional[str] = None

# Prevent simultaneous EfficientFace inference calls from
# Streamlit and WebRTC callback threads.
_INFERENCE_LOCK = threading.Lock()


# ============================================================
# CHECKPOINT COMPATIBILITY
# ============================================================

class RecorderMeter(object):
    """
    Compatibility class required because the original training
    checkpoint contains a serialized RecorderMeter object.
    """

    def __init__(self, total_epoch=100):
        self.total_epoch = total_epoch


# ============================================================
# PREPROCESSING
# Exact RAF-DB test preprocessing used during evaluation
# ============================================================

TEST_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.57535914, 0.44928582, 0.40079932],
        std=[0.20735591, 0.18981615, 0.18132027]
    )
])


# ============================================================
# FACE DETECTOR
# ============================================================

_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)


# ============================================================
# MODEL LOADING
# ============================================================

def _load_model():

    print(
        f"[emotion_detector] Loading EfficientFace on {DEVICE}"
    )

    model = EfficientFace.efficient_face()

    model.fc = nn.Linear(1024, 7)

    model = torch.nn.DataParallel(model)

    # The original training checkpoint serialized RecorderMeter
    # under __main__, so register the compatibility class there
    # before loading the checkpoint.
    import __main__
    __main__.RecorderMeter = RecorderMeter

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=DEVICE,
        weights_only=False
    )

    model.load_state_dict(
        checkpoint["state_dict"]
    )

    model = model.to(DEVICE)

    model.eval()

    print(
        "[emotion_detector] EfficientFace loaded successfully"
    )

    return model


_MODEL = _load_model()


# ============================================================
# ERROR HANDLING
# ============================================================

def _set_error(message: str):

    global _LAST_ERROR

    _LAST_ERROR = message

    print(
        f"[emotion_detector] Error: {message}"
    )


def get_last_detection_error() -> Optional[str]:

    return _LAST_ERROR


# ============================================================
# FACE DETECTION
# ============================================================

def _detect_largest_face(
    frame_bgr: np.ndarray
):

    gray = cv2.cvtColor(
        frame_bgr,
        cv2.COLOR_BGR2GRAY
    )

    faces = _FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    if len(faces) == 0:
        return None

    return max(
        faces,
        key=lambda box: box[2] * box[3]
    )


# ============================================================
# FACE EXTRACTION
# ============================================================

def _extract_face(
    frame_bgr: np.ndarray
):

    face_box = _detect_largest_face(
        frame_bgr
    )

    if face_box is None:
        return None

    x, y, w, h = face_box

    face = frame_bgr[
        y:y + h,
        x:x + w
    ]

    if face.size == 0:
        return None

    return face


# ============================================================
# EFFICIENTFACE INFERENCE
# ============================================================

def _predict_face(
    face_bgr: np.ndarray
):

    face_rgb = cv2.cvtColor(
        face_bgr,
        cv2.COLOR_BGR2RGB
    )

    face_pil = Image.fromarray(
        face_rgb
    )

    input_tensor = (
        TEST_TRANSFORM(face_pil)
        .unsqueeze(0)
        .to(DEVICE)
    )

    with _INFERENCE_LOCK:
        with torch.inference_mode():

            output = _MODEL(
                input_tensor
            )

            probabilities = F.softmax(
                output,
                dim=1
            )[0]

    predicted_index = int(
        torch.argmax(
            probabilities
        ).item()
    )

    confidence = float(
        probabilities[
            predicted_index
        ].item()
    )

    emotion = CLASS_NAMES[
        predicted_index
    ]

    return (
        emotion,
        confidence,
        probabilities.cpu().numpy()
    )


# ============================================================
# PUBLIC FUNCTION USED BY app.py
# ============================================================

def analyze_frame(
    frame_bgr: np.ndarray
) -> Optional[str]:

    global _LAST_ERROR

    _LAST_ERROR = None

    if (
        frame_bgr is None
        or frame_bgr.size == 0
    ):

        _set_error(
            "Empty image frame provided"
        )

        return None


    try:

        face = _extract_face(
            frame_bgr
        )

        if face is None:

            print(
                "[emotion_detector] No face detected; "
                "using full image as fallback"
            )

            face = frame_bgr


        (
            emotion,
            confidence,
            probabilities

        ) = _predict_face(
            face
        )


        print(
            f"[emotion_detector] "
            f"Prediction: {emotion} "
            f"({confidence:.2%})"
        )


        return emotion


    except Exception as exc:

        _set_error(
            f"EfficientFace inference failed: {exc}"
        )

        return None
