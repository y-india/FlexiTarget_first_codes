# ResumeRefresh backend

1. Copy `.env.example` to `.env`.
2. Add your OpenRouter API key and Apps Script `/exec` URL.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run: `python -m uvicorn server:app --host 127.0.0.1 --port 8000`.
5. Check `http://127.0.0.1:8000/health`. It should return JSON and show both integrations as configured.

The OpenRouter API key stays on this backend and is never put in the Chrome extension.
