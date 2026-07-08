# Enabling Hume-based Emotion Detection on Streamlit Cloud

To run emotion detection inside Streamlit without installing TensorFlow/DeepFace, use Hume's hosted API.

Steps:
1. Get a Hume API key: https://platform.hume.ai/settings/keys
2. In your Streamlit Cloud app settings, add a secret named `HUME_API_KEY` with the key value.
3. Also add an environment variable `USE_HUME=1` (or set in `.env` locally for testing).
4. The app will prefer the Hume-backed detector (`emotion_detector_fixed.py`) when `HUME_API_KEY` is present.

Notes:
- Streamlit Cloud will install the `hume` package (it's in `requirements.txt`).
- Hume incurs API costs; monitor usage.
- If you want local TF/DeepFace instead, deploy using the provided Dockerfiles and install `requirements-optional.txt`.

Troubleshooting
- If emotion detection still shows as unavailable, open the app logs and look for `emotion_detector` dependency errors in the UI; ensure `HUME_API_KEY` is set in the app's Secrets/Env.
- For testing locally, place the API key in `.env` or export `HUME_API_KEY` in your shell.
