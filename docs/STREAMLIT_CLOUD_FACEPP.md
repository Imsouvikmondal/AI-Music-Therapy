# Using Face++ (Face Plus Plus) with Streamlit

Face++ offers a simple REST API (API key + secret) that returns emotion attributes for detected faces.

1. Sign up at https://console.faceplusplus.com/ and get `API_KEY` and `API_SECRET`.
2. Add the following Secrets / environment variables in your Streamlit Cloud app settings:
   - `FACEPP_API_KEY` = your API key
   - `FACEPP_API_SECRET` = your API secret
3. The app will automatically use Face++ (via `emotion_detector_facepp.py`) when keys are present.

Notes:
- Face++ returns per-face scores for `anger, disgust, fear, happiness, neutral, sadness, surprise`.
- Network latency and API rates apply; monitor and cache results when possible.
- Face++ has free tier / trial; upgrade for production scale.

Security:
- Keep API secret in Streamlit Secrets, not in source code or public repo.

If you prefer I can implement server-side caching or a microservice wrapper to reduce API calls and latency — say yes and I'll scaffold it.
