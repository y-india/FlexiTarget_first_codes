# ResumeRefresh

### Important local-backend setup

The extension calls the local processing API at `http://127.0.0.1:8000/process`.
The manifest now grants access to both `127.0.0.1:8000` and `localhost:8000`.

After replacing the old extension with this build:

1. Open `chrome://extensions`.
2. Remove the previous ResumeRefresh unpacked extension, or use Reload if replacing the files in place.
3. Load the `ResumeRefresh_Extension` folder from this ZIP.
4. Keep the Python backend running:
   `python -m uvicorn server:app --host 127.0.0.1 --port 8000`
5. Verify `http://127.0.0.1:8000/health` returns JSON.
6. Press `Ctrl+Shift+Y` and test Submit.

If Submit still reports a connectivity error, the extension now includes the browser error detail so the next message will identify whether the failure is network, CORS, or the endpoint itself.
