// ResumeRefresh client configuration.
// Keep the OpenRouter API key OUT of this file. It belongs only in the backend .env file.
const APP_CONFIG = Object.freeze({
  PROCESSING_API_URL: 'https://resume-refresh-prototype-for-check-2-api-ssqy.onrender.com/process',
  APPS_SCRIPT_URL: 'https://script.google.com/macros/s/AKfycbwzSzFq6dSGvTVUb4XtgfPe7qLTxiYdolaGPZhOrb9ksxotS7beM1BF-vG8tBgkh6lk/exec',
  DEMO_MODE: false,
  MAX_RESUME_BYTES: 8 * 1024 * 1024,
  ALLOWED_RESUME_TYPES: [
    'application/pdf'
  ]
});
